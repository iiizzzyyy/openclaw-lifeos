#!/usr/bin/env python3
"""
Blog Knowledge Compiler — compile raw .md posts into structured wiki.

Reads: ~/clawd/data/blog-knowledge/*.md
Writes: ~/clawd/skills/blog-knowledge-compiler/data/wiki/

Usage:
    python3 compile.py [--compile-only]
"""
import json
import os
import re
import sys
import sqlite3
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


# Paths
SKILL_DIR = Path(__file__).parent.parent
WIKI_DIR = SKILL_DIR / "data" / "wiki"
REPORTS_DIR = SKILL_DIR / "data" / "reports"
DATA_DIR = Path(os.path.expanduser("~/clawd/data/blog-knowledge"))
DB_PATH = DATA_DIR / "blog_posts.db"

CATEGORIES = {
    "AI Cost Management & FinOps",
    "AI Quality, Evaluation & Reliability",
    "AI Governance, Compliance & Strategy",
}

KEY_CONCEPTS = [
    "EU AI Act", "hallucination", "token budget", "golden set",
    "LLM observability", "prompt engineering", "cost monitoring",
    "RAG", "vendor lock-in", "evaluation", "Fine-tuning", "RAG",
    "prompt caching", "context window", "multi-agent", "agentic AI",
    "observability", "FinOps", "benchmark", " hallucination",
]


@dataclass
class PostSummary:
    slug: str
    title: str
    category: str
    summary: str  # 1-2 sentence TLDR
    key_claims: list[str]
    concepts: list[str]
    related_slugs: list[str]
    publish_date: Optional[str]
    word_count: int


def extract_metadata_from_md(slug: str, content: str) -> dict:
    """Extract structured metadata from a blog post .md file."""
    lines = content.split("\n")
    
    # Title (first # heading)
    title = slug.replace("-", " ").title()
    for line in lines:
        if line.startswith("# "):
            title = line[2:].strip()
            break
    
    # Extract key sentences (for summary)
    sentences = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#") and not line.startswith("!") and len(line) > 30:
            # Skip very long lines (likely code blocks or lists)
            if len(line) < 300 and not line.startswith("- ") and not line.startswith("* "):
                sentences.append(line)
    
    # Find sentences that mention key concepts
    key_claims = []
    concept_hits = defaultdict(int)
    
    for sent in sentences[:20]:  # Check first 20 sentences
        sent_lower = sent.lower()
        for concept in KEY_CONCEPTS:
            if concept.lower() in sent_lower:
                concept_hits[concept] += 1
                if len(key_claims) < 5 and len(sent) < 200:
                    key_claims.append(sent)
    
    concepts = sorted(set(concept_hits.keys()), key=lambda c: concept_hits[c], reverse=True)[:8]
    summary = " ".join(sentences[:2])[:300] if sentences else ""
    
    return {
        "title": title,
        "summary": summary,
        "key_claims": list(dict.fromkeys(key_claims))[:5],
        "concepts": concepts,
        "word_count": len(content.split()),
    }


def get_category_from_db(slug: str) -> str:
    """Get category from blog_posts.db."""
    if not DB_PATH.exists():
        return "Uncategorized"
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.execute(
            "SELECT category FROM blog_posts WHERE slug = ? LIMIT 1",
            (slug,)
        )
        row = cur.fetchone()
        conn.close()
        return row[0] if row else "Uncategorized"
    except Exception:
        return "Uncategorized"


def build_wiki_index(posts: list[PostSummary]) -> str:
    """Build master wiki index."""
    by_category = defaultdict(list)
    by_concept = defaultdict(list)
    
    for post in posts:
        by_category[post.category].append(post)
        for concept in post.concepts:
            by_concept[concept].append(post.slug)
    
    lines = [
        "# Blog Knowledge Wiki — PromptMetrics\n",
        f"**Compiled:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n",
        f"**Posts:** {len(posts)}\n",
        "---\n",
        "\n## By Category\n",
    ]
    
    for cat in sorted(CATEGORIES):
        posts_in_cat = by_category.get(cat, [])
        lines.append(f"\n### {cat} ({len(posts_in_cat)} posts)\n")
        for p in sorted(posts_in_cat, key=lambda x: x.publish_date or "", reverse=True):
            date = p.publish_date or "draft"
            lines.append(f"- **{p.title}** — `{date}` [[summary::{p.slug}]]\n")
    
    lines.append("\n## By Concept\n")
    for concept in sorted(by_concept.keys(), key=lambda c: len(by_concept[c]), reverse=True)[:20]:
        slugs = by_concept[concept]
        lines.append(f"- **{concept}** ({len(slugs)}): {', '.join(slugs)}\n")
    
    return "".join(lines)


def build_summary(post: PostSummary) -> str:
    """Build per-post summary file."""
    lines = [
        f"# {post.title}\n\n",
        f"**Category:** {post.category}\n",
        f"**Date:** {post.publish_date or 'Draft'}\n",
        f"**Concepts:** {', '.join(post.concepts)}\n",
        f"**Word count:** {post.word_count}\n\n",
        "---\n\n",
        "## Summary\n\n",
        f"{post.summary}\n\n",
    ]
    
    if post.key_claims:
        lines.append("## Key Claims\n\n")
        for claim in post.key_claims:
            lines.append(f"- {claim}\n")
        lines.append("\n")
    
    if post.related_slugs:
        lines.append("## Related Posts\n\n")
        for slug in post.related_slugs[:5]:
            lines.append(f"- [[{slug}]]\n")
        lines.append("\n")
    
    return "".join(lines)


def compile_wiki() -> list[PostSummary]:
    """Compile all .md files in data/blog-knowledge/ into wiki."""
    WIKI_DIR.mkdir(parents=True, exist_ok=True)
    (WIKI_DIR / "summaries").mkdir(exist_ok=True)
    (WIKI_DIR / "concepts").mkdir(exist_ok=True)
    
    md_files = list(DATA_DIR.glob("*.md"))
    # Filter out non-post files
    md_files = [f for f in md_files if f.name not in [
        "cross-linking-report.md", "_sync-report-2026-02-28.json", 
        "_dedupe-report-2026-02-28.json"
    ]]
    
    print(f"Compiling {len(md_files)} blog posts...")
    posts: list[PostSummary] = []
    
    for md_file in md_files:
        slug = md_file.stem
        content = md_file.read_text()
        
        meta = extract_metadata_from_md(slug, content)
        category = get_category_from_db(slug)
        
        post = PostSummary(
            slug=slug,
            title=meta["title"],
            category=category,
            summary=meta["summary"],
            key_claims=meta["key_claims"],
            concepts=meta["concepts"],
            related_slugs=[],
            publish_date=None,
            word_count=meta["word_count"],
        )
        posts.append(post)
        
        # Write summary
        summary_path = WIKI_DIR / "summaries" / f"{slug}.md"
        summary_path.write_text(build_summary(post))
        
        print(f"  ✓ {slug}")
    
    # Build and write index
    index = build_wiki_index(posts)
    (WIKI_DIR / "index.md").write_text(index)
    
    # Build category concepts
    by_category = defaultdict(list)
    for post in posts:
        by_category[post.category].append(post)
    
    for cat, cat_posts in by_category.items():
        cat_slug = cat.lower().replace(" & ", "-").replace(" ", "-")
        cat_lines = [f"# {cat}\n\n"]
        for p in cat_posts:
            cat_lines.append(f"## {p.title}\n")
            cat_lines.append(f"{p.summary}\n\n")
        (WIKI_DIR / "concepts" / f"{cat_slug}.md").write_text("".join(cat_lines))
    
    print(f"\nWiki compiled: {len(posts)} posts")
    print(f"  Index: {WIKI_DIR / 'index.md'}")
    print(f"  Summaries: {WIKI_DIR / 'summaries/'}")
    print(f"  Concepts: {WIKI_DIR / 'concepts/'}")
    
    return posts


if __name__ == "__main__":
    compile_only = "--compile-only" in sys.argv
    posts = compile_wiki()
    print("\nCompile complete.")
