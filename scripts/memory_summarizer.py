#!/usr/bin/env python3
"""Memory Summarizer: create compressed summaries of old daily files and archive stale ones."""

import argparse
import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path

MEMORY_DIR = os.path.expanduser("~/clawd/memory")
SUMMARIES_DIR = os.path.join(MEMORY_DIR, "summaries")
ARCHIVE_DIR = os.path.join(MEMORY_DIR, "archive")

DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}\.md$')

# Lines matching these are considered "important" for extractive summarization
# Memory expiry defaults (minimum 90 days)
EXPIRY_DEFAULTS = {
    "decision": 180,
    "event": 90,
    "preference": None,  # never expires
    "lesson": None,       # never expires
    "tool": 90,
}
DEFAULT_EXPIRY_DAYS = 90  # untagged entries

EXPIRY_TAG_PATTERN = re.compile(r'\[expires?:(\d{4}-\d{2}-\d{2})\]')
EPISODIC_TAG_PATTERN = re.compile(r'\[(decision|event|preference|lesson|tool)\]')
SOURCE_TAG_PATTERN = re.compile(r'\[(human|web|api|moltbook|agent|inferred)\]')

# Import surprise scorer
try:
    from surprise_scorer import score_surprise
except ImportError:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("surprise_scorer", os.path.join(os.path.dirname(__file__), "surprise_scorer.py"))
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    score_surprise = _mod.score_surprise

SURPRISE_TAG_PATTERN = re.compile(r'\[surprise:(high|medium|low)\]')

IMPORTANT_PATTERNS = [
    re.compile(r'^##'),                          # Headers
    re.compile(r'\*\*.*?\*\*'),                  # Bold text
    re.compile(r'(?i)(decision|decided|chose)', re.IGNORECASE),
    re.compile(r'(?i)(important|critical|urgent)'),
    re.compile(r'(?i)(error|bug|fix|broke|broken|fail)'),
    re.compile(r'(?i)(lesson|learned|insight|takeaway)'),
    re.compile(r'(?i)(created|built|shipped|deployed|launched)'),
    re.compile(r'https?://\S+'),                 # URLs
    re.compile(r'(?i)(script|cron|config):?\s'),  # Technical references
    re.compile(r'- \*\*'),                        # Bold list items
    re.compile(r'\[(human|web|api|moltbook|agent|inferred)\]'),  # Source tags
]


def get_daily_files():
    """Find all YYYY-MM-DD.md files in memory dir."""
    files = []
    for f in os.listdir(MEMORY_DIR):
        if DATE_PATTERN.match(f):
            date_str = f.replace('.md', '')
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                files.append((date, os.path.join(MEMORY_DIR, f)))
            except ValueError:
                pass
    return sorted(files, key=lambda x: x[0])


def extract_summary(filepath, max_lines=20, file_age_days=0):
    """Extract important lines from a daily file, respecting surprise scores.
    
    Surprise-aware summarization:
    - high surprise → always preserved verbatim (never compressed)
    - medium surprise → summarized normally (included if important)
    - low surprise → aggressively compressed; dropped if file_age_days > 7
    """
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
    except Exception:
        return []

    high_surprise = []  # Always kept
    important = []       # Normal summarization
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        
        surprise = score_surprise(stripped)
        
        # High surprise: always preserve verbatim
        if surprise == "high":
            high_surprise.append(stripped)
            continue
        
        # Low surprise: drop if older than 7 days
        if surprise == "low" and file_age_days > 7:
            continue
        
        # Medium/low: use existing importance heuristics
        for pattern in IMPORTANT_PATTERNS:
            if pattern.search(stripped):
                important.append(stripped)
                break

    # Deduplicate while preserving order
    seen = set()
    unique = []
    # High surprise entries first (always included)
    for line in high_surprise:
        if line not in seen:
            seen.add(line)
            unique.append(line)
    # Then important entries up to max_lines
    for line in important:
        if line not in seen and len(unique) < max_lines:
            seen.add(line)
            unique.append(line)

    return unique[:max(max_lines, len(high_surprise))]  # Never truncate high-surprise


def summarize_file(date, filepath, dry_run=False):
    """Create a summary for a daily file."""
    date_str = date.strftime('%Y-%m-%d')
    summary_path = os.path.join(SUMMARIES_DIR, f"{date_str}.md")

    if os.path.exists(summary_path):
        return None  # Already summarized

    age_days = (datetime.now().date() - date).days
    summary_lines = extract_summary(filepath, file_age_days=age_days)
    if not summary_lines:
        return None

    content = f"# Summary: {date_str}\n\n"
    content += "\n".join(f"- {line}" if not line.startswith('#') else line for line in summary_lines)
    content += "\n"

    if not dry_run:
        os.makedirs(SUMMARIES_DIR, exist_ok=True)
        with open(summary_path, 'w') as f:
            f.write(content)

    return summary_path


def archive_file(date, filepath, dry_run=False):
    """Move a daily file to archive."""
    date_str = date.strftime('%Y-%m-%d')
    archive_path = os.path.join(ARCHIVE_DIR, f"{date_str}.md")
    summary_path = os.path.join(SUMMARIES_DIR, f"{date_str}.md")

    # Only archive if summary exists
    if not os.path.exists(summary_path):
        return None

    if os.path.exists(archive_path):
        return None  # Already archived

    if not dry_run:
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        shutil.move(filepath, archive_path)

    return archive_path


def main():
    parser = argparse.ArgumentParser(description='Summarize and archive old memory files')
    parser.add_argument('--dry-run', action='store_true', help='Show what would happen without doing it')
    parser.add_argument('--days', type=int, default=3, help='Summarize files older than N days (default: 3)')
    parser.add_argument('--archive-days', type=int, default=30, help='Archive files older than N days (default: 30)')
    parser.add_argument('--gc', action='store_true', help='Run garbage collection on MEMORY.md (remove expired entries)')
    parser.add_argument('--heat-report', action='store_true', help='Show memory heat report (access patterns)')
    args = parser.parse_args()

    if args.heat_report:
        try:
            from memory_heat_tracker import heat_report
            heat_report()
        except ImportError:
            # Try with full path
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "memory_heat_tracker",
                os.path.join(os.path.dirname(__file__), "memory_heat_tracker.py")
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            mod.heat_report()
        return

    today = datetime.now().date()
    daily_files = get_daily_files()

    summarized = 0
    archived = 0
    skipped = 0

    prefix = "[DRY RUN] " if args.dry_run else ""

    print(f"📊 Memory Summarizer {'(dry run)' if args.dry_run else ''}")
    print(f"   Found {len(daily_files)} daily files")
    print(f"   Summarize threshold: {args.days} days")
    print(f"   Archive threshold: {args.archive_days} days")
    print()

    # Load heat tracker for heat-adjusted archiving
    heat_tracker = None
    try:
        import importlib.util
        ht_spec = importlib.util.spec_from_file_location(
            "memory_heat_tracker",
            os.path.join(os.path.dirname(__file__), "memory_heat_tracker.py")
        )
        ht_mod = importlib.util.module_from_spec(ht_spec)
        ht_spec.loader.exec_module(ht_mod)
        heat_tracker = ht_mod
    except Exception:
        pass  # Heat tracking unavailable — use standard TTL

    for date, filepath in daily_files:
        age = (today - date).days

        # Summarize files older than threshold
        if age > args.days:
            result = summarize_file(date, filepath, dry_run=args.dry_run)
            if result:
                print(f"  {prefix}📝 Summarized: {date} → {os.path.basename(result)}")
                summarized += 1
            else:
                skipped += 1

        # Heat-adjusted archive threshold
        effective_archive_days = args.archive_days
        if heat_tracker:
            try:
                # Use date string as a proxy hash for the file
                file_hash = heat_tracker.entry_hash(date.strftime('%Y-%m-%d'))
                adj = heat_tracker.ttl_adjustment(file_hash)
                effective_archive_days = max(7, args.archive_days + adj)  # floor at 7 days
                if adj != 0:
                    print(f"  🌡️  {date}: heat adjustment {adj:+d}d (effective archive: {effective_archive_days}d)")
            except Exception:
                pass

        # Archive files older than (heat-adjusted) archive threshold
        if age > effective_archive_days:
            result = archive_file(date, filepath, dry_run=args.dry_run)
            if result:
                print(f"  {prefix}📦 Archived: {date} → archive/{os.path.basename(result)}")
                archived += 1

    print(f"\n{'Would summarize' if args.dry_run else 'Summarized'}: {summarized} files")
    print(f"{'Would archive' if args.dry_run else 'Archived'}: {archived} files")
    print(f"Skipped (already done): {skipped} files")

    if args.gc:
        gc_memory_md(dry_run=args.dry_run)


def gc_memory_md(dry_run=False):
    """Garbage collect expired entries from MEMORY.md."""
    memory_path = os.path.join(MEMORY_DIR, "..", "MEMORY.md")
    memory_path = os.path.normpath(memory_path)
    if not os.path.exists(memory_path):
        memory_path = os.path.join(os.path.expanduser("~/clawd"), "MEMORY.md")
    if not os.path.exists(memory_path):
        print("  ℹ️  MEMORY.md not found, skipping GC")
        return 0

    with open(memory_path, "r") as f:
        lines = f.readlines()

    today = datetime.now().date()
    expired = []
    kept = []
    gc_log_entries = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue

        # Check explicit expiry tag
        expiry_match = EXPIRY_TAG_PATTERN.search(stripped)
        if expiry_match:
            exp_date = datetime.strptime(expiry_match.group(1), "%Y-%m-%d").date()
            if exp_date < today:
                expired.append((i + 1, stripped))
                gc_log_entries.append(f"- Line {i+1}: expired {expiry_match.group(1)} — `{stripped[:80]}`")
                continue

        kept.append(line)

    prefix = "[DRY RUN] " if dry_run else ""
    line_count = sum(1 for l in lines if l.strip())
    print(f"\n🧹 MEMORY.md GC: {line_count} non-empty lines, {len(expired)} expired entries")
    if line_count > 200:
        print(f"  ⚠️  MEMORY.md has {line_count} lines (target: <200). Consider manual pruning.")

    if expired:
        for ln, text in expired:
            print(f"  {prefix}🗑️  Line {ln}: {text[:80]}")
        if not dry_run:
            with open(memory_path, "w") as f:
                f.writelines(kept)
            # Log to gc-log.md
            gc_log_path = os.path.join(MEMORY_DIR, "gc-log.md")
            with open(gc_log_path, "a") as f:
                f.write(f"\n## GC Run {today}\n")
                f.write("\n".join(gc_log_entries) + "\n")

    return len(expired)


if __name__ == '__main__':
    main()
