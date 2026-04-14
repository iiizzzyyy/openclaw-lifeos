#!/usr/bin/env python3
"""Track costs per workflow by parsing OpenClaw session transcripts (JSONL v3)."""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

SESSIONS_DIR = Path(os.path.expanduser("~/.openclaw/agents/main/sessions"))
COST_LOG = Path(os.path.expanduser("~/clawd/logs/cost-by-workflow.jsonl"))

# Map session IDs to labels from OpenClaw's session list
# We'll build this mapping from the sessions API or file naming
LABEL_CACHE = {}


def parse_since(since_str):
    unit = since_str[-1]
    val = int(since_str[:-1])
    if unit == 'h': return timedelta(hours=val)
    if unit == 'd': return timedelta(days=val)
    raise ValueError(f"Unknown unit: {unit}")


def get_session_labels():
    """Get session labels from OpenClaw sessions.json registry."""
    registry = Path(os.path.expanduser("~/.openclaw/agents/main/sessions/sessions.json"))
    labels = {}
    try:
        with open(registry) as f:
            data = json.load(f)
        if isinstance(data, dict):
            for key, info in data.items():
                sid = info.get("sessionId", "")
                label = info.get("label", "")
                if sid:
                    if label:
                        # Normalize cron labels
                        if label.startswith("Cron: "):
                            labels[sid] = label.replace("Cron: ", "").split(" (")[0].strip()
                        else:
                            labels[sid] = label
                    elif ":cron:" in key:
                        labels[sid] = "cron-unlabeled"
                    elif ":subagent:" in key:
                        labels[sid] = "subagent-unlabeled"
                    elif key == "agent:main:main":
                        labels[sid] = "main-session"
    except Exception:
        pass
    return labels


def classify_session(session_file, labels_map):
    """Classify a session by its label/type."""
    sid = session_file.stem
    if sid in labels_map:
        label = labels_map[sid]
        # Normalize cron labels
        if label.startswith("Cron: "):
            return label.replace("Cron: ", "").split(" (")[0].strip()
        return label
    
    # Fallback: try to detect from content
    try:
        with open(session_file) as f:
            for line in f:
                d = json.loads(line.strip())
                if d.get("type") == "session":
                    continue
                # Check for model to distinguish
                msg = d.get("message", {})
                if isinstance(msg, dict) and msg.get("model"):
                    model = msg["model"]
                    if "sonnet" in model:
                        return "subagent-sonnet"
                    elif "opus" in model:
                        return "main-or-cron-opus"
                break
    except Exception:
        pass
    return "unknown"


def extract_costs(session_file, cutoff=None):
    """Extract total cost from a session transcript."""
    total_cost = 0.0
    total_input = 0
    total_output = 0
    total_cache_read = 0
    models = set()
    first_ts = None
    last_ts = None
    message_count = 0

    try:
        # Quick mtime check
        mtime = datetime.fromtimestamp(session_file.stat().st_mtime, tz=timezone.utc)
        if cutoff and mtime < cutoff:
            return None

        with open(session_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if entry.get("type") != "message":
                    continue

                msg = entry.get("message", {})
                if not isinstance(msg, dict):
                    continue

                # Timestamp
                ts_val = msg.get("timestamp") or entry.get("timestamp")
                if ts_val:
                    if isinstance(ts_val, (int, float)):
                        ts = datetime.fromtimestamp(ts_val / 1000 if ts_val > 1e12 else ts_val, tz=timezone.utc)
                    elif isinstance(ts_val, str):
                        try:
                            ts = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
                        except ValueError:
                            ts = None
                    else:
                        ts = None

                    if ts:
                        if cutoff and ts < cutoff:
                            continue
                        if not first_ts:
                            first_ts = ts
                        last_ts = ts

                # Model
                if msg.get("model"):
                    models.add(msg["model"])

                # Usage
                usage = msg.get("usage", {})
                if not usage:
                    continue

                cost = usage.get("cost", {})
                if isinstance(cost, dict):
                    total_cost += cost.get("total", 0) or 0
                elif isinstance(cost, (int, float)):
                    total_cost += cost

                total_input += usage.get("input", 0) or 0
                total_output += usage.get("output", 0) or 0
                total_cache_read += usage.get("cacheRead", 0) or 0
                message_count += 1

    except IOError:
        return None

    if total_cost == 0 and message_count == 0:
        return None

    return {
        "cost": round(total_cost, 6),
        "input_tokens": total_input,
        "output_tokens": total_output,
        "cache_read_tokens": total_cache_read,
        "models": list(models),
        "messages": message_count,
        "first_ts": first_ts.isoformat() if first_ts else None,
        "last_ts": last_ts.isoformat() if last_ts else None,
    }


def analyze_costs(since="7d"):
    """Analyze costs across all sessions."""
    cutoff = datetime.now(timezone.utc) - parse_since(since)
    labels_map = get_session_labels()

    workflow_costs = defaultdict(lambda: {
        "total_cost": 0.0,
        "sessions": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "messages": 0,
        "models": set(),
    })

    if not SESSIONS_DIR.exists():
        return {}

    for session_file in SESSIONS_DIR.glob("*.jsonl"):
        costs = extract_costs(session_file, cutoff)
        if not costs:
            continue

        label = classify_session(session_file, labels_map)
        wf = workflow_costs[label]
        wf["total_cost"] += costs["cost"]
        wf["sessions"] += 1
        wf["input_tokens"] += costs["input_tokens"]
        wf["output_tokens"] += costs["output_tokens"]
        wf["cache_read_tokens"] += costs["cache_read_tokens"]
        wf["messages"] += costs["messages"]
        wf["models"].update(costs["models"])

    result = {}
    for label, data in workflow_costs.items():
        result[label] = {
            **data,
            "total_cost": round(data["total_cost"], 4),
            "models": list(data["models"]),
        }
    return result


def show_leaderboard(costs, since):
    """Display cost leaderboard."""
    if not costs:
        print(f"📊 No session data found for the last {since}")
        return

    total = sum(c["total_cost"] for c in costs.values())
    total_sessions = sum(c["sessions"] for c in costs.values())
    sorted_costs = sorted(costs.items(), key=lambda x: x[1]["total_cost"], reverse=True)

    print(f"💰 Cost Leaderboard (last {since})")
    print(f"   Total: ${total:.4f} across {total_sessions} sessions")
    print("━" * 70)
    print(f"{'Workflow':<30} {'Cost':>8} {'Sess':>5} {'Msgs':>5} {'Out Tok':>9} {'%':>5}")
    print("-" * 70)

    for label, data in sorted_costs:
        pct = (data["total_cost"] / total * 100) if total > 0 else 0
        print(f"{label[:30]:<30} ${data['total_cost']:>7.4f} {data['sessions']:>5} {data['messages']:>5} {data['output_tokens']:>9,} {pct:>4.0f}%")

    print("-" * 70)
    print(f"{'TOTAL':<30} ${total:>7.4f} {total_sessions:>5}")


def export_for_sheets(costs, since):
    """Export as TSV for Google Sheets."""
    print("Workflow\tCost ($)\tSessions\tMessages\tOutput Tokens\tModels")
    sorted_costs = sorted(costs.items(), key=lambda x: x[1]["total_cost"], reverse=True)
    for label, data in sorted_costs:
        models = ", ".join(data["models"])
        print(f"{label}\t{data['total_cost']:.4f}\t{data['sessions']}\t{data['messages']}\t{data['output_tokens']}\t{models}")


AGENT_PATTERNS = {
    "main": ["main-session"],
    "scout": ["Reddit Digest", "Daily Research", "reddit", "research", "scout"],
    "scribe": ["Blog Promo", "Newsletter", "Content", "scribe", "LinkedIn", "Twitter"],
    "coder": ["Priority Tasks Sprint", "Nightly Build", "coder", "Morning Briefing"],
}


def classify_agent(label):
    """Map a workflow label to an agent name."""
    lower = label.lower()
    for agent, patterns in AGENT_PATTERNS.items():
        for pat in patterns:
            if pat.lower() in lower:
                return agent
    return "other"


def show_by_agent(costs, since):
    """Display costs grouped by agent."""
    agent_totals = defaultdict(lambda: {"cost": 0.0, "sessions": 0, "messages": 0})
    for label, data in costs.items():
        agent = classify_agent(label)
        agent_totals[agent]["cost"] += data["total_cost"]
        agent_totals[agent]["sessions"] += data["sessions"]
        agent_totals[agent]["messages"] += data["messages"]

    total = sum(a["cost"] for a in agent_totals.values())
    sorted_agents = sorted(agent_totals.items(), key=lambda x: x[1]["cost"], reverse=True)

    print(f"🤖 Cost by Agent (last {since})")
    print(f"   Total: ${total:.4f}")
    print("━" * 50)
    print(f"{'Agent':<15} {'Cost':>10} {'Sessions':>10} {'Msgs':>8} {'%':>6}")
    print("-" * 50)
    for agent, data in sorted_agents:
        pct = (data["cost"] / total * 100) if total > 0 else 0
        print(f"{agent:<15} ${data['cost']:>9.4f} {data['sessions']:>10} {data['messages']:>8} {pct:>5.0f}%")
    print("-" * 50)
    print(f"{'TOTAL':<15} ${total:>9.4f}")


def show_by_job(costs, since):
    """Display costs for cron jobs only."""
    job_costs = {k: v for k, v in costs.items() if k != "main-session" and k != "unknown"}
    if not job_costs:
        print(f"📋 No cron job costs found for the last {since}")
        return

    total = sum(c["total_cost"] for c in job_costs.values())
    sorted_jobs = sorted(job_costs.items(), key=lambda x: x[1]["total_cost"], reverse=True)

    print(f"📋 Cost by Cron Job (last {since})")
    print(f"   Total job spend: ${total:.4f}")
    print("━" * 60)
    print(f"{'Job':<35} {'Cost':>8} {'Runs':>5} {'$/Run':>8}")
    print("-" * 60)
    for label, data in sorted_jobs:
        per_run = data["total_cost"] / data["sessions"] if data["sessions"] > 0 else 0
        print(f"{label[:35]:<35} ${data['total_cost']:>7.4f} {data['sessions']:>5} ${per_run:>7.4f}")
    print("-" * 60)


def main():
    parser = argparse.ArgumentParser(description="Track costs per workflow")
    parser.add_argument("--since", default="7d", help="Time window (e.g., 24h, 7d, 30d)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--tsv", action="store_true", help="TSV output (for sheets)")
    parser.add_argument("--save", action="store_true", help="Save snapshot to cost log")
    parser.add_argument("--by-agent", action="store_true", help="Group costs by agent")
    parser.add_argument("--by-job", action="store_true", help="Show costs per cron job")
    args = parser.parse_args()

    costs = analyze_costs(since=args.since)

    if args.json:
        print(json.dumps(costs, indent=2, default=str))
    elif args.tsv:
        export_for_sheets(costs, args.since)
    elif args.by_agent:
        show_by_agent(costs, args.since)
    elif args.by_job:
        show_by_job(costs, args.since)
    else:
        show_leaderboard(costs, args.since)

    if args.save:
        os.makedirs(COST_LOG.parent, exist_ok=True)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "period": args.since,
            "total_cost": round(sum(c["total_cost"] for c in costs.values()), 4),
            "workflows": {k: {"cost": v["total_cost"], "sessions": v["sessions"]} for k, v in costs.items()},
        }
        with open(COST_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"\n📝 Snapshot saved to {COST_LOG}")


if __name__ == "__main__":
    main()
