#!/usr/bin/env python3
"""Analyze action logs for patterns and failure detection"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta

LOG_PATH = os.path.expanduser("~/clawd/memory/action-log.jsonl")
DEPRECATED_PATH = os.path.expanduser("~/clawd/memory/deprecated-approaches.json")

def parse_since(since_str):
    """Parse '24h', '7d', '30d' into timedelta"""
    unit = since_str[-1]
    val = int(since_str[:-1])
    if unit == 'h':
        return timedelta(hours=val)
    elif unit == 'd':
        return timedelta(days=val)
    elif unit == 'm':
        return timedelta(minutes=val)
    raise ValueError(f"Unknown time unit: {unit}")

def load_entries(since=None, failures_only=False):
    if not os.path.exists(LOG_PATH):
        return []
    
    cutoff = None
    if since:
        cutoff = datetime.now(timezone.utc) - parse_since(since)

    entries = []
    with open(LOG_PATH) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entry = json.loads(line)
            ts = datetime.fromisoformat(entry["timestamp"])
            if cutoff and ts < cutoff:
                continue
            if failures_only and entry.get("outcome") != "failure":
                continue
            entries.append(entry)
    return entries

def show_summary(entries):
    by_action = defaultdict(lambda: Counter())
    for e in entries:
        by_action[e["action"]][e["outcome"]] += 1
    
    if not by_action:
        print("No actions logged in this period.")
        return

    print(f"{'Action':<30} {'Success':>8} {'Failure':>8} {'Skip':>6} {'Total':>6} {'Fail%':>6}")
    print("-" * 70)
    for action in sorted(by_action):
        c = by_action[action]
        total = sum(c.values())
        fail_pct = (c["failure"] / total * 100) if total else 0
        print(f"{action:<30} {c['success']:>8} {c['failure']:>8} {c['skip']:>6} {total:>6} {fail_pct:>5.0f}%")

def detect_patterns(entries, threshold=3):
    """Find actions that failed >= threshold times"""
    failures = Counter()
    reasons = defaultdict(list)
    for e in entries:
        if e.get("outcome") == "failure":
            failures[e["action"]] += 1
            if e.get("reason"):
                reasons[e["action"]].append(e["reason"])
    
    patterns = {}
    for action, count in failures.items():
        if count >= threshold:
            patterns[action] = {
                "status": "deprecated",
                "failure_count": count,
                "reasons": list(set(reasons.get(action, [])))[:5],
                "detected": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            }
    
    if patterns:
        # Update deprecated approaches file
        existing = {}
        if os.path.exists(DEPRECATED_PATH):
            with open(DEPRECATED_PATH) as f:
                existing = json.load(f)
        existing.update(patterns)
        with open(DEPRECATED_PATH, "w") as f:
            json.dump(existing, f, indent=2)
        
        print(f"\n⚠️  {len(patterns)} deprecated approach(es) detected:")
        for action, info in patterns.items():
            print(f"  - {action}: {info['failure_count']} failures")
            for r in info['reasons'][:3]:
                print(f"    → {r}")
    else:
        print("\n✓ No failure patterns detected.")
    
    return patterns

def main():
    parser = argparse.ArgumentParser(description="Analyze action logs")
    parser.add_argument("--since", default="24h", help="Time window (e.g., 24h, 7d)")
    parser.add_argument("--failures-only", action="store_true", help="Show only failures")
    parser.add_argument("--by-action", action="store_true", help="Group by action")
    parser.add_argument("--patterns", action="store_true", help="Detect failure patterns (3+ failures)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--threshold", type=int, default=3, help="Pattern detection threshold")
    args = parser.parse_args()

    entries = load_entries(since=args.since, failures_only=args.failures_only)

    if args.json:
        if args.patterns:
            patterns = {}
            failures = Counter()
            for e in entries:
                if e.get("outcome") == "failure":
                    failures[e["action"]] += 1
            for a, c in failures.items():
                if c >= args.threshold:
                    patterns[a] = {"failure_count": c}
            print(json.dumps({"entries": len(entries), "patterns": patterns}, indent=2))
        else:
            print(json.dumps(entries, indent=2))
        return

    print(f"📊 Action Stats (last {args.since}) — {len(entries)} entries\n")
    show_summary(entries)

    if args.patterns:
        detect_patterns(entries, threshold=args.threshold)

if __name__ == "__main__":
    main()
