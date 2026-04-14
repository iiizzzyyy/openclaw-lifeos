#!/usr/bin/env python3
"""
Blog Knowledge Compiler — main runner.

Usage:
    python3 run.py              # Full compile + lint
    python3 run.py --compile-only
    python3 run.py --lint-only
"""
import sys
import argparse
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

from compile import compile_wiki
from lint import run_lint, generate_report
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Blog Knowledge Compiler")
    parser.add_argument("--compile-only", action="store_true", help="Only compile wiki")
    parser.add_argument("--lint-only", action="store_true", help="Only run health checks")
    parser.add_argument("--output-report", action="store_true", help="Output report path")
    args = parser.parse_args()
    
    if args.compile_only and args.lint_only:
        print("Error: --compile-only and --lint-only are mutually exclusive")
        sys.exit(1)
    
    posts = []
    issues = []
    
    if not args.lint_only:
        print("=" * 60)
        print("COMPILING WIKI")
        print("=" * 60)
        posts = compile_wiki()
        print()
    
    if not args.compile_only:
        print("=" * 60)
        print("RUNNING HEALTH CHECKS")
        print("=" * 60)
        issues = run_lint()
        
        # Generate and save report
        report_path = Path(__file__).parent.parent / "data" / "reports" / f"health-check-{datetime.now().strftime('%Y-%m-%d')}.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(generate_report(issues))
        
        print()
        print("=" * 60)
        print(f"HEALTH CHECK COMPLETE: {len(issues)} issues")
        print(f"Report: {report_path}")
        print("=" * 60)
    
    if args.output_report and issues:
        # Print summary for daily briefing
        high = len([i for i in issues if i.severity == "high"])
        medium = len([i for i in issues if i.severity == "medium"])
        low = len([i for i in issues if i.severity == "low"])
        print(f"\n📊 Summary: {high} high, {medium} medium, {low} low priority issues")


if __name__ == "__main__":
    main()
