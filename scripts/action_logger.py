#!/usr/bin/env python3
"""Append structured action entries to action-log.jsonl"""

import argparse
import json
import os
from datetime import datetime, timezone

LOG_PATH = os.path.expanduser("~/clawd/memory/action-log.jsonl")

def log_action(action, outcome, tool=None, context=None, reason=None, duration_ms=None, level=None, cost_usd=None, trigger=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "outcome": outcome,
        "level": level or ("error" if outcome == "failure" else "info"),
    }
    if tool:
        entry["tool"] = tool
    if context:
        entry["context"] = context
    if reason:
        entry["reason"] = reason
    if duration_ms is not None:
        entry["duration_ms"] = duration_ms
    if cost_usd is not None:
        entry["cost_usd"] = cost_usd
    if trigger:
        entry["trigger"] = trigger

    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"✓ Logged: {action} → {outcome}")

def main():
    parser = argparse.ArgumentParser(description="Log an action outcome")
    parser.add_argument("--action", required=True, help="Action name (e.g., blog_promotion)")
    parser.add_argument("--outcome", required=True, choices=["success", "failure", "skip"], help="Outcome")
    parser.add_argument("--tool", help="Tool used (e.g., cron, exec)")
    parser.add_argument("--context", help="Brief context")
    parser.add_argument("--reason", help="Error/skip reason")
    parser.add_argument("--duration", type=int, help="Duration in ms")
    parser.add_argument("--level", choices=["info", "warn", "error"], help="Log level (auto-set from outcome if omitted)")
    parser.add_argument("--cost", type=float, help="Estimated cost in USD")
    parser.add_argument("--trigger", choices=["heartbeat", "cron", "human", "auto"], help="What triggered this action")
    args = parser.parse_args()

    log_action(args.action, args.outcome, args.tool, args.context, args.reason, args.duration, args.level, args.cost, args.trigger)

if __name__ == "__main__":
    main()
