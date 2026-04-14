#!/usr/bin/env python3
"""
Blog Knowledge Linter — health checks on compiled wiki.

Identifies:
- Content gaps (topics covered poorly)
- Potential contradictions between posts
- Outdated claims (EU AI Act dates, pricing, tool names)
- Missing internal links

Reads: ~/clawd/skills/blog-knowledge-compiler/data/wiki/
Writes: ~/clawd/skills/blog-knowledge-compiler/data/reports/health-check-<date>.md

Usage:
    python3 lint.py
"""
import json
import os
import re
import sqlite3
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Paths
SKILL_DIR = Path(__file__).parent.parent
WIKI_DIR = SKILL_DIR / "data" / "wiki"
REPORTS_DIR = SKILL_DIR / "data" / "reports"
DATA_DIR = Path(os.path.expanduser("~/clawd/data/blog-knowledge"))
DB_PATH = DATA_DIR / "blog_posts.db"

# Patterns for detecting outdated info
OUTDATED_PATTERNS = [
    (r"202[0-4]", "Year reference may be outdated"),
    (r"(Q[1-4] )?2025", "2025 reference — verify if still accurate"),
    (r"€?\d{1,2}(,\d{2})? (million|billion)", "Pricing claim — verify current"),
    (r"(before|until|by) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{4}", "Date-bound claim — may expire"),
    (r"(currently|now|today|as of \d{4})", "Time-sensitive claim"),
]

# Contradiction detection: look for opposing claims
CONTRADICTION_PAIRS = [
    ("should", "should not"),
    ("must", "optional"),
    ("always", "never"),
    ("best", "worst"),
    ("recommended", "avoid"),
    ("cheap", "expensive"),
]


@dataclass
class HealthIssue:
    severity: str  # "high", "medium", "low"
    category: str  # "outdated", "contradiction", "gap", "link"
    post_slug: str
    description: str
    context: str
    suggestion: str


def load_wiki_summaries() -> dict[str, str]:
    """Load all summary files."""
    summaries = {}
    summaries_dir = WIKI_DIR / "summaries"
    if not summaries_dir.exists():
        return summaries
    for f in summaries_dir.glob("*.md"):
        summaries[f.stem] = f.read_text()
    return summaries


def detect_outdated_claims(slug: str, content: str) -> list[HealthIssue]:
    """Find time-sensitive or potentially outdated claims."""
    issues = []
    for pattern, reason in OUTDATED_PATTERNS:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        for match in matches[:3]:  # Limit per pattern
            start = max(0, match.start() - 50)
            end = min(len(content), match.end() + 50)
            context = content[start:end].strip()
            issues.append(HealthIssue(
                severity="medium",
                category="outdated",
                post_slug=slug,
                description=reason,
                context=f"...{context}...",
                suggestion="Review and update or add 'As of YYYY-MM' qualifier",
            ))
    return issues


def detect_contradictions(summaries: dict[str, str]) -> list[HealthIssue]:
    """Find potential contradictions across posts."""
    issues = []
    
    # Build claim index: concept -> list of (slug, claim_text)
    concept_claims = defaultdict(list)
    for slug, content in summaries.items():
        lines = content.split("\n")
        for line in lines:
            if line.startswith("## Key Claims"):
                # Extract claims section
                for claim_line in lines[lines.index(line)+1:]:
                    if claim_line.startswith("- "):
                        concept_claims[slug].append(claim_line[2:].strip())
    
    # Check for contradiction pairs
    for slug1, claims1 in concept_claims.items():
        for slug2, claims2 in concept_claims.items():
            if slug1 >= slug2:
                continue
            for c1 in claims1:
                for c2 in claims2:
                    for pos, neg in CONTRADICTION_PAIRS:
                        if pos.lower() in c1.lower() and neg.lower() in c2.lower():
                            issues.append(HealthIssue(
                                severity="high",
                                category="contradiction",
                                post_slug=f"{slug1} ↔ {slug2}",
                                description=f"Potential contradiction: '{pos}' vs '{neg}'",
                                context=f"Post A: {c1[:100]}...\nPost B: {c2[:100]}...",
                                suggestion="Review both posts — one may need updating or clarification",
                            ))
                            break
    return issues[:10]  # Limit


def detect_content_gaps(summaries: dict[str, str]) -> list[HealthIssue]:
    """Identify topics that are mentioned but not covered well."""
    issues = []
    
    # Count mentions of key concepts
    concept_counts = defaultdict(list)
    for slug, content in summaries.items():
        content_lower = content.lower()
        for concept in ["EU AI Act", "hallucination", "token budget", "golden set", 
                       "observability", "FinOps", "evaluation", "RAG"]:
            if concept.lower() in content_lower:
                concept_counts[concept].append(slug)
    
    # Find concepts with few posts (< 3)
    for concept, slugs in concept_counts.items():
        if len(slugs) < 3:
            issues.append(HealthIssue(
                severity="low",
                category="gap",
                post_slug="knowledge-base",
                description=f"Concept '{concept}' covered in only {len(slugs)} post(s)",
                context=f"Posts: {', '.join(slugs)}",
                suggestion=f"Consider writing 1-2 more posts about {concept}",
            ))
    
    return issues


def detect_missing_links(summaries: dict[str, str]) -> list[HealthIssue]:
    """Find posts that could benefit from more internal linking."""
    issues = []
    
    # Count outbound links per post
    for slug, content in summaries.items():
        link_count = content.count("]]")  # Wiki-style links
        if link_count < 2 and len(content) > 500:
            issues.append(HealthIssue(
                severity="low",
                category="link",
                post_slug=slug,
                description=f"Only {link_count} internal links",
                context="Post has substantial content but few cross-references",
                suggestion="Add 3-5 internal links to related posts",
            ))
    
    return issues[:15]


def run_lint() -> list[HealthIssue]:
    """Run all health checks."""
    print("Loading wiki summaries...")
    summaries = load_wiki_summaries()
    print(f"  Loaded {len(summaries)} summaries")
    
    all_issues: list[HealthIssue] = []
    
    print("\nChecking for outdated claims...")
    for slug, content in summaries.items():
        issues = detect_outdated_claims(slug, content)
        all_issues.extend(issues)
    print(f"  Found {len([i for i in all_issues if i.category == 'outdated'])} outdated claims")
    
    print("\nChecking for contradictions...")
    contradictions = detect_contradictions(summaries)
    all_issues.extend(contradictions)
    print(f"  Found {len(contradictions)} potential contradictions")
    
    print("\nChecking for content gaps...")
    gaps = detect_content_gaps(summaries)
    all_issues.extend(gaps)
    print(f"  Found {len(gaps)} content gaps")
    
    print("\nChecking for missing links...")
    links = detect_missing_links(summaries)
    all_issues.extend(links)
    print(f"  Found {len(links)} posts needing more links")
    
    return all_issues


def generate_report(issues: list[HealthIssue]) -> str:
    """Generate markdown health check report."""
    lines = [
        "# Blog Knowledge Health Check\n\n",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
        f"**Total issues:** {len(issues)}\n\n",
        "---\n\n",
    ]
    
    # Group by severity
    by_severity = defaultdict(list)
    for issue in issues:
        by_severity[issue.severity].append(issue)
    
    for severity in ["high", "medium", "low"]:
        severity_issues = by_severity.get(severity, [])
        if not severity_issues:
            continue
        
        emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}[severity]
        lines.append(f"## {emoji} {severity.upper()} ({len(severity_issues)})\n\n")
        
        for issue in severity_issues[:10]:  # Limit per section
            lines.append(f"### [{issue.category}] {issue.post_slug}\n\n")
            lines.append(f"**Issue:** {issue.description}\n\n")
            lines.append(f"**Context:**\n> {issue.context}\n\n")
            lines.append(f"**Suggestion:** {issue.suggestion}\n\n")
            lines.append("---\n\n")
    
    return "".join(lines)


if __name__ == "__main__":
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    issues = run_lint()
    report = generate_report(issues)
    
    report_path = REPORTS_DIR / f"health-check-{datetime.now().strftime('%Y-%m-%d')}.md"
    report_path.write_text(report)
    
    print(f"\n{'='*60}")
    print(f"Health check complete: {len(issues)} issues found")
    print(f"Report: {report_path}")
