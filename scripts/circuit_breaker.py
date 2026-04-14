#!/usr/bin/env python3
"""Circuit breaker for cron jobs. 3-state: closed → half-open → open.

States:
  - CLOSED: normal operation, failures counted
  - HALF-OPEN: retry once per interval; success → closed, fail → open
  - OPEN: blocked, waits for backoff period then transitions to half-open

Usage:
    python3 circuit_breaker.py check <job_name>
    # Exit 0 = OK (closed or half-open retry allowed), Exit 1 = blocked (open)

    python3 circuit_breaker.py success <job_name>
    python3 circuit_breaker.py failure <job_name> [--reason "error msg"]
    python3 circuit_breaker.py reset <job_name>
    python3 circuit_breaker.py status
    python3 circuit_breaker.py cost <job_name> <amount_usd>

    # New: configure backoff per job
    python3 circuit_breaker.py config <job_name> [--max-failures N] [--base-backoff SECS] [--max-backoff SECS]
"""
import json, os, sys, time, math
from datetime import datetime, timezone

STATE_FILE = os.path.expanduser("~/clawd/data/circuit-breaker.json")
MAX_CONSECUTIVE_FAILURES = 2  # default, overridable per job
DAILY_COST_THRESHOLD_USD = 10.0
DEFAULT_BASE_BACKOFF_SECS = 60       # 1 minute
DEFAULT_MAX_BACKOFF_SECS = 3600      # 1 hour
HALF_OPEN_RETRY_INTERVAL_SECS = 300  # 5 minutes between half-open retries


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"jobs": {}}


def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_job(state, name):
    if name not in state["jobs"]:
        state["jobs"][name] = {
            "consecutive_failures": 0,
            "state": "closed",  # closed | half-open | open
            # Legacy compat: is_open derived from state
            "is_open": False,
            "last_outcome": None,
            "last_failure_reason": None,
            "opened_at": None,
            "total_failures": 0,
            "total_successes": 0,
            "daily_cost_usd": 0.0,
            "cost_reset_date": None,
            # Backoff config
            "max_failures": MAX_CONSECUTIVE_FAILURES,
            "base_backoff_secs": DEFAULT_BASE_BACKOFF_SECS,
            "max_backoff_secs": DEFAULT_MAX_BACKOFF_SECS,
            # Half-open tracking
            "last_half_open_retry": None,
            "backoff_multiplier": 0,
        }
    else:
        # Migrate legacy entries
        job = state["jobs"][name]
        if "state" not in job:
            job["state"] = "open" if job.get("is_open") else "closed"
        job.setdefault("max_failures", MAX_CONSECUTIVE_FAILURES)
        job.setdefault("base_backoff_secs", DEFAULT_BASE_BACKOFF_SECS)
        job.setdefault("max_backoff_secs", DEFAULT_MAX_BACKOFF_SECS)
        job.setdefault("last_half_open_retry", None)
        job.setdefault("backoff_multiplier", 0)
    return state["jobs"][name]


def today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def current_backoff(job):
    """Calculate current backoff duration using exponential backoff."""
    base = job.get("base_backoff_secs", DEFAULT_BASE_BACKOFF_SECS)
    mult = job.get("backoff_multiplier", 0)
    max_bo = job.get("max_backoff_secs", DEFAULT_MAX_BACKOFF_SECS)
    return min(base * (2 ** mult), max_bo)


def seconds_since(iso_str):
    """Seconds elapsed since an ISO timestamp."""
    if not iso_str:
        return float('inf')
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - dt).total_seconds()
    except Exception:
        return float('inf')


def cmd_check(state, name):
    job = get_job(state, name)
    st = job["state"]

    # Check daily cost first
    if job.get("cost_reset_date") == today_str() and job["daily_cost_usd"] >= DAILY_COST_THRESHOLD_USD:
        print(f"💰 COST LIMIT for '{name}' — ${job['daily_cost_usd']:.2f} today (limit ${DAILY_COST_THRESHOLD_USD:.2f})")
        return 1

    if st == "closed":
        return 0

    if st == "open":
        # Check if backoff period has elapsed → transition to half-open
        elapsed = seconds_since(job.get("opened_at"))
        backoff = current_backoff(job)
        if elapsed >= backoff:
            job["state"] = "half-open"
            job["is_open"] = False
            save_state(state)
            print(f"🟡 HALF-OPEN for '{name}' — backoff elapsed ({backoff:.0f}s), allowing one retry")
            return 0
        else:
            remaining = backoff - elapsed
            print(f"🛑 OPEN for '{name}' — {job['consecutive_failures']} consecutive failures")
            print(f"   Backoff: {remaining:.0f}s remaining (of {backoff:.0f}s)")
            if job.get("last_failure_reason"):
                print(f"   Last reason: {job['last_failure_reason']}")
            print(f"   Run: python3 circuit_breaker.py reset {name}")
            return 1

    if st == "half-open":
        # Allow one retry per interval
        elapsed = seconds_since(job.get("last_half_open_retry"))
        if elapsed >= HALF_OPEN_RETRY_INTERVAL_SECS:
            job["last_half_open_retry"] = now_iso()
            save_state(state)
            print(f"🟡 HALF-OPEN for '{name}' — allowing retry probe")
            return 0
        else:
            remaining = HALF_OPEN_RETRY_INTERVAL_SECS - elapsed
            print(f"🟡 HALF-OPEN for '{name}' — next retry in {remaining:.0f}s")
            return 1

    return 0


def cmd_success(state, name):
    job = get_job(state, name)
    prev_state = job["state"]
    job["consecutive_failures"] = 0
    job["state"] = "closed"
    job["is_open"] = False
    job["last_outcome"] = "success"
    job["total_successes"] += 1
    job["opened_at"] = None
    job["backoff_multiplier"] = 0
    job["last_half_open_retry"] = None
    save_state(state)
    if prev_state == "half-open":
        print(f"✅ {name}: success in half-open → circuit CLOSED")
    else:
        print(f"✅ {name}: success recorded")


def cmd_failure(state, name, reason=None):
    job = get_job(state, name)
    prev_state = job["state"]
    job["consecutive_failures"] += 1
    job["total_failures"] += 1
    job["last_outcome"] = "failure"
    job["last_failure_reason"] = reason
    max_f = job.get("max_failures", MAX_CONSECUTIVE_FAILURES)

    if prev_state == "half-open":
        # Half-open failure → open with increased backoff
        job["state"] = "open"
        job["is_open"] = True
        job["opened_at"] = now_iso()
        job["backoff_multiplier"] = job.get("backoff_multiplier", 0) + 1
        backoff = current_backoff(job)
        print(f"🛑 HALF-OPEN → OPEN for '{name}' (retry failed)")
        print(f"   Next backoff: {backoff:.0f}s")
        if reason:
            print(f"   Reason: {reason}")
    elif job["consecutive_failures"] >= max_f:
        job["state"] = "open"
        job["is_open"] = True
        job["opened_at"] = now_iso()
        job["backoff_multiplier"] = 0
        backoff = current_backoff(job)
        print(f"🛑 CIRCUIT OPENED for '{name}' after {job['consecutive_failures']} consecutive failures")
        print(f"   Will auto-retry (half-open) after {backoff:.0f}s")
        if reason:
            print(f"   Reason: {reason}")
    else:
        print(f"⚠️ {name}: failure {job['consecutive_failures']}/{max_f}")
    save_state(state)


def cmd_reset(state, name):
    job = get_job(state, name)
    job["consecutive_failures"] = 0
    job["state"] = "closed"
    job["is_open"] = False
    job["opened_at"] = None
    job["last_failure_reason"] = None
    job["backoff_multiplier"] = 0
    job["last_half_open_retry"] = None
    save_state(state)
    print(f"🔄 {name}: circuit reset, job re-enabled")


def cmd_cost(state, name, amount):
    job = get_job(state, name)
    t = today_str()
    if job.get("cost_reset_date") != t:
        job["daily_cost_usd"] = 0.0
        job["cost_reset_date"] = t
    job["daily_cost_usd"] += amount
    save_state(state)
    if job["daily_cost_usd"] >= DAILY_COST_THRESHOLD_USD:
        print(f"💰 {name}: daily cost ${job['daily_cost_usd']:.2f} EXCEEDS limit ${DAILY_COST_THRESHOLD_USD:.2f}")
        return 1
    print(f"💵 {name}: daily cost ${job['daily_cost_usd']:.2f} / ${DAILY_COST_THRESHOLD_USD:.2f}")
    return 0


def cmd_config(state, name, args):
    job = get_job(state, name)
    if "--max-failures" in args:
        idx = args.index("--max-failures")
        if idx + 1 < len(args):
            job["max_failures"] = int(args[idx + 1])
    if "--base-backoff" in args:
        idx = args.index("--base-backoff")
        if idx + 1 < len(args):
            job["base_backoff_secs"] = float(args[idx + 1])
    if "--max-backoff" in args:
        idx = args.index("--max-backoff")
        if idx + 1 < len(args):
            job["max_backoff_secs"] = float(args[idx + 1])
    save_state(state)
    print(f"⚙️  {name} config: max_failures={job['max_failures']}, "
          f"base_backoff={job['base_backoff_secs']}s, max_backoff={job['max_backoff_secs']}s")


def cmd_status(state):
    if not state["jobs"]:
        print("No jobs tracked yet.")
        return
    print(f"{'Job':<25} {'State':<12} {'Fails':<8} {'Successes':<10} {'Backoff':<10} {'Cost Today':<12}")
    print("-" * 77)
    for name, job in sorted(state["jobs"].items()):
        st = job.get("state", "open" if job.get("is_open") else "closed")
        state_icon = {"closed": "✅ closed", "half-open": "🟡 half", "open": "🛑 open"}.get(st, st)
        cost = f"${job.get('daily_cost_usd', 0):.2f}" if job.get("cost_reset_date") == today_str() else "$0.00"
        backoff = f"{current_backoff(job):.0f}s" if st != "closed" else "—"
        print(f"{name:<25} {state_icon:<12} {job['total_failures']:<8} {job['total_successes']:<10} {backoff:<10} {cost:<12}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    state = load_state()

    if cmd == "status":
        cmd_status(state)
    elif cmd == "check" and len(sys.argv) >= 3:
        sys.exit(cmd_check(state, sys.argv[2]))
    elif cmd == "success" and len(sys.argv) >= 3:
        cmd_success(state, sys.argv[2])
    elif cmd == "failure" and len(sys.argv) >= 3:
        reason = None
        if "--reason" in sys.argv:
            idx = sys.argv.index("--reason")
            if idx + 1 < len(sys.argv):
                reason = sys.argv[idx + 1]
        cmd_failure(state, sys.argv[2], reason)
    elif cmd == "reset" and len(sys.argv) >= 3:
        cmd_reset(state, sys.argv[2])
    elif cmd == "cost" and len(sys.argv) >= 4:
        sys.exit(cmd_cost(state, sys.argv[2], float(sys.argv[3])))
    elif cmd == "config" and len(sys.argv) >= 3:
        cmd_config(state, sys.argv[2], sys.argv[3:])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
