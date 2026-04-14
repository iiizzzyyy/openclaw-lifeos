---
name: blog-knowledge-compiler
description: "Compile blog knowledge base into structured wiki with summaries, cross-links, and concept categories. Runs health checks for content gaps, contradictions, and outdated claims. Wires to newsletter-to-content (input) and Obsidian vault (output)."
user-invocable: true
---

# Blog Knowledge Compiler

Compiles raw blog content into a structured knowledge wiki, then runs health checks to identify gaps and inconsistencies.

## What It Does

**1. Compile** — Reads raw `.md` files from `data/blog-knowledge/`, extracts structured metadata, builds:
- `wiki/index.md` — master index with all posts, categories, concepts
- `wiki/summaries/<slug>.md` — per-post structured summaries
- `wiki/concepts/<category>.md` — category-level concept maps
- `wiki/concept-index.md` — cross-cutting topic index

**2. Lint** — Health-checks the knowledge base:
- Identifies content gaps (topics you cover poorly)
- Flags potential contradictions between posts
- Detects outdated claims (EU AI Act dates, pricing info, tool names)
- Suggests internal link opportunities
- Recommends new article angles

**3. Sync** — Optionally syncs outputs to Obsidian vault

## Trigger

```bash
# Full compile + lint
python3 ~/clawd/skills/blog-knowledge-compiler/scripts/run.py

# Compile only (faster)
python3 ~/clawd/skills/blog-knowledge-compiler/scripts/run.py --compile-only

# Lint only
python3 ~/clawd/skills/blog-knowledge-compiler/scripts/run.py --lint-only

# On demand
/brainstorm
```

## Cron (Recommended)

Daily or after newsletter-to-content runs. Hook into existing pipeline:
```bash
# After newsletter-to-content, add to cron:
0 11 * * * cd ~/clawd/skills/blog-knowledge-compiler && python3 scripts/run.py
```

## Data Flow

```
data/blog-knowledge/*.md (raw posts)
         ↓
   compile.py
         ↓
data/wiki/
  ├── index.md                    # Master index
  ├── summaries/<slug>.md         # Structured summaries
  ├── concepts/
  │   ├── ai-cost-management.md
  │   ├── ai-quality-evaluation.md
  │   └── ai-governance-compliance.md
  └── concept-index.md            # Cross-topic index
         ↓
   lint.py (health checks)
         ↓
data/reports/health-check-<date>.md  # Issues + recommendations
         ↓
   Daily briefing or /brainstorm review
```

## Output Files

| File | Purpose |
|------|---------|
| `wiki/index.md` | All posts indexed by category, date, concept |
| `wiki/summaries/<slug>.md` | One-line summary + key claims + related posts |
| `wiki/concepts/<cat>.md` | Category-level synthesis of all posts in that category |
| `wiki/concept-index.md` | Posts indexed by topic tag (cross-cutting) |
| `reports/health-check-<date>.md` | Gaps, contradictions, outdated claims |

## Categories (from blog_posts.db)

- AI Cost Management & FinOps
- AI Quality, Evaluation & Reliability
- AI Governance, Compliance & Strategy

## Key Concepts

Topics that appear across multiple posts (from cross-linking analysis):
- EU AI Act compliance, hallucination, token budgets, golden set, LLM observability, prompt engineering, cost monitoring, RAG, vendor lock-in
