#!/usr/bin/env python3
"""
Context Death Watchdog — monitors context usage and auto-dumps state.

Designed to be called periodically during long sessions.
When context exceeds threshold, dumps recovery state to CONTINUATION.md.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

CONTINUATION_PATH = Path(os.path.expanduser("~/clawd/CONTINUATION.md"))
THRESHOLD_PCT = 65  # Default threshold


def check_continuation_state():
    """Check if CONTINUATION.md has recovery state."""
    if not CONTINUATION_PATH.exists():
        return False, ""
    
    content = CONTINUATION_PATH.read_text()
    # Check if there's content below the --- separator
    parts = content.split("---", 1)
    if len(parts) > 1 and parts[1].strip():
        return True, parts[1].strip()
    return False, ""


def clear_continuation():
    """Clear recovery state from CONTINUATION.md."""
    header = """# CONTINUATION.md

Emergency state dump for context death recovery.
When context usage hits ~65%, current state is auto-dumped below the line.
On next session: if content exists below ---, load it, resume, then clear.

---
"""
    CONTINUATION_PATH.write_text(header)
    print("✅ CONTINUATION.md cleared")


def dump_state(working_on, progress, next_action, key_context, include_now=False):
    """Write recovery state to CONTINUATION.md."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    
    header = """# CONTINUATION.md

Emergency state dump for context death recovery.
When context usage hits ~65%, current state is auto-dumped below the line.
On next session: if content exists below ---, load it, resume, then clear.

---
"""
    state = f"""
## Recovery State ({now})
- **Working on:** {working_on}
- **Progress:** {progress}
- **Next action:** {next_action}
- **Key context:** {key_context}
"""

    # Include NOW.md content if requested
    if include_now:
        now_path = Path(os.path.expanduser("~/clawd/NOW.md"))
        if now_path.exists():
            try:
                now_content = now_path.read_text().strip()
                if now_content:
                    state += f"""

## NOW.md Snapshot
{now_content}
"""
            except Exception as e:
                state += f"""

## NOW.md Snapshot  
(Error reading NOW.md: {e})
"""
    
    CONTINUATION_PATH.write_text(header + state)
    suffix = " (with NOW.md)" if include_now else ""
    print(f"💾 State dumped to CONTINUATION.md{suffix} at {now}")


def main():
    parser = argparse.ArgumentParser(description="Context Death Watchdog")
    parser.add_argument("--check", action="store_true", help="Check if recovery state exists")
    parser.add_argument("--clear", action="store_true", help="Clear recovery state")
    parser.add_argument("--dump", action="store_true", help="Dump state")
    parser.add_argument("--now", action="store_true", help="Include NOW.md content in state dumps")
    parser.add_argument("--working-on", default="unknown", help="Current task")
    parser.add_argument("--progress", default="unknown", help="What's done")
    parser.add_argument("--next-action", default="unknown", help="Next step")
    parser.add_argument("--context", default="", help="Key context")
    args = parser.parse_args()

    if args.check:
        has_state, state = check_continuation_state()
        if has_state:
            print("⚠️  Recovery state found in CONTINUATION.md:")
            print(state)
        else:
            print("✅ No recovery state — clean start")
    elif args.clear:
        clear_continuation()
    elif args.dump:
        dump_state(args.working_on, args.progress, args.next_action, args.context, args.now)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
