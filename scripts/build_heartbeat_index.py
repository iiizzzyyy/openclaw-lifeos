#!/usr/bin/env python3
"""
Build heartbeat-index.json - ultra-compact (~150 token) health summary.

Layer 1 of 3-layer heartbeat compression:
  L1: heartbeat-index.json (150 tokens) - read always
  L2: knowledge-index.json (500 tokens) - read if L1 flags something
  L3: Full file reads - only for active investigation

Usage:
  python3 build_heartbeat_index.py          # Build index
  python3 build_heartbeat_index.py --check  # Show current
"""
import json
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

CLAWD = Path(os.path.expanduser("~/clawd"))
HB_INDEX = CLAWD / "hive" / "heartbeat-index.json"
STATE_PATH = CLAWD / "hive" / "state.json"
TASKS_PATH = CLAWD / "tasks" / "active.json"
CONTEXT_PATH = CLAWD / "CONTEXT.md"
CB_SCRIPT = CLAWD / "scripts" / "circuit_breaker.py"


def check_openclaw_tasks():
    """Return (issues, detail) from openclaw tasks audit --json."""
    try:
        result = subprocess.run(
            ["openclaw", "tasks", "audit", "--json"],
            capture_output=True, text=True, timeout=5
        )
        # Output may start with plugin banners — find the first '{' and parse from there
        stdout = result.stdout.strip()
        json_start = stdout.find('{')
        if json_start >= 0:
            stdout = stdout[json_start:]
        data = json.loads(stdout)
        findings = data.get("findings", [])
        errors = data.get("errors", [])
        warnings = data.get("warnings", [])
        total = len(findings) + len(errors) + len(warnings)
        return total, f"{len(findings)} findings, {len(errors)} errors, {len(warnings)} warnings"
    except json.JSONDecodeError as e:
        return 0, f"parse error (ok — likely clean): {e}"
    except Exception as e:
        return -1, str(e)


def check_circuit_breakers():
    """Return count of open circuit breakers."""
    try:
        result = subprocess.run(
            ["python3", str(CB_SCRIPT), "status"],
            capture_output=True, text=True, timeout=5
        )
        # Count lines with "🔴" or "OPEN"
        open_count = sum(1 for line in result.stdout.split('\n') if '🔴' in line or 'OPEN' in line)
        return open_count
    except Exception:
        return -1  # unknown


def check_stalled_tasks():
    """Return count of tasks with checkinsWithoutProgress >= 3."""
    if not TASKS_PATH.exists():
        return 0
    data = json.loads(TASKS_PATH.read_text())
    return sum(1 for t in data.get("tasks", [])
               if t.get("checkinsWithoutProgress", 0) >= 3
               and t.get("status") in ("active",))


def check_worker_errors():
    """Check if any workers are in error state."""
    if not STATE_PATH.exists():
        return []
    state = json.loads(STATE_PATH.read_text())
    errors = []
    for name, info in state.get("workers", {}).items():
        if info.get("status") == "error":
            errors.append(name)
    return errors


def check_context_freshness():
    """Check if CONTEXT.md was updated in last 24h."""
    if not CONTEXT_PATH.exists():
        return False
    mtime = datetime.fromtimestamp(CONTEXT_PATH.stat().st_mtime)
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    return age_hours <= 24


def build_index():
    """Build ultra-compact heartbeat index."""
    openclaw_task_issues, task_detail = check_openclaw_tasks()
    open_breakers = check_circuit_breakers()
    stalled = check_stalled_tasks()
    worker_errors = check_worker_errors()
    context_fresh = check_context_freshness()

    # Determine overall health
    needs_attention = (
        openclaw_task_issues > 0 or
        open_breakers > 0 or
        stalled > 0 or
        len(worker_errors) > 0 or
        not context_fresh
    )

    index = {
        "ts": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "health": "🔴 NEEDS_ATTENTION" if needs_attention else "🟢 OK",
        "openclawTasks": openclaw_task_issues,
        "openclawTaskDetail": task_detail,
        "circuitBreakers": open_breakers,
        "stalledTasks": stalled,
        "workerErrors": worker_errors,
        "contextFresh": context_fresh,
        "flags": []
    }

    # Add specific flags for what needs attention
    if openclaw_task_issues > 0:
        index["flags"].append(f"OpenClaw tasks: {task_detail}")
    if open_breakers > 0:
        index["flags"].append(f"{open_breakers} circuit breaker(s) open")
    if stalled > 0:
        index["flags"].append(f"{stalled} stalled task(s)")
    if worker_errors:
        index["flags"].append(f"Workers in error: {', '.join(worker_errors)}")
    if not context_fresh:
        index["flags"].append("CONTEXT.md stale (>24h)")

    HB_INDEX.parent.mkdir(parents=True, exist_ok=True)
    HB_INDEX.write_text(json.dumps(index, indent=2))
    return index


if __name__ == "__main__":
    if "--check" in sys.argv:
        if HB_INDEX.exists():
            print(HB_INDEX.read_text())
        else:
            print("No heartbeat index. Run without --check to build.")
    else:
        index = build_index()
        text = json.dumps(index)
        tokens = len(text) // 4
        print(f"Built heartbeat-index.json: {len(text)} chars, ~{tokens} tokens")
        print(f"Health: {index['health']}")
        if index['flags']:
            print(f"Flags: {', '.join(index['flags'])}")
