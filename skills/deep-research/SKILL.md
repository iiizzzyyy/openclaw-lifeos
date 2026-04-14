---
name: deep-research
description: "Execute autonomous multi-step research using Google Gemini Deep Research. Uses the Gemini CLI (no API key needed) for agentic research tasks. For: market analysis, competitive landscaping, literature reviews, technical research, due diligence. Takes 2-10 minutes but produces detailed, cited reports."
---

# Gemini Deep Research Skill

Uses the **Gemini CLI** for deep research — no API key required, uses cached credentials.

## Quick Usage

```bash
gemini "Research [topic]. Find recent trends, statistics, competing viewpoints, and real-world examples."
```

For non-interactive (headless/cron) use:
```bash
gemini -p "Research [topic]"
```

## Setup

1. Install Gemini CLI: `npm install -g @google/gemini-cli`
2. Authenticate once: `gemini` (opens browser OAuth flow)
3. That's it — credentials are cached at `~/.gemini/credentials.json`

No API key needed. The CLI handles authentication automatically.

## Requirements

- Gemini CLI (`npm install -g @google/gemini-cli`)
- Node.js 18+

## Usage (Full API Script)

### Start a research task
```bash
python3 scripts/research.py --query "Research the history of Kubernetes"
```

### With structured output format
```bash
python3 scripts/research.py --query "Compare Python web frameworks" \
  --format "1. Executive Summary\n2. Comparison Table\n3. Recommendations"
```

### Stream progress in real-time
```bash
python3 scripts/research.py --query "Analyze EV battery market" --stream
```

### Start without waiting
```bash
python3 scripts/research.py --query "Research topic" --no-wait
```

### Check status of running research
```bash
python3 scripts/research.py --status <interaction_id>
```

### Wait for completion
```bash
python3 scripts/research.py --wait <interaction_id>
```

### Continue from previous research
```bash
python3 scripts/research.py --query "Elaborate on point 2" --continue <interaction_id>
```

### List recent research
```bash
python3 scripts/research.py --list
```

## Output Formats

- **Default**: Human-readable markdown report
- **JSON** (`--json`): Structured data for programmatic use
- **Raw** (`--raw`): Unprocessed API response

## Cost & Time

| Metric | Value |
|--------|-------|
| Time | 2-10 minutes per task |
| Cost | $2-5 per task (varies by complexity) |
| Token usage | ~250k-900k input, ~60k-80k output |

## Best Use Cases

- Market analysis and competitive landscaping
- Technical literature reviews
- Due diligence research
- Historical research and timelines
- Comparative analysis (frameworks, products, technologies)

## Workflow

1. User requests research → Run `--query "..."`
2. Inform user of estimated time (2-10 minutes)
3. Monitor with `--stream` or poll with `--status`
4. Return formatted results
5. Use `--continue` for follow-up questions

## Exit Codes

- **0**: Success
- **1**: Error (API error, config issue, timeout)
- **130**: Cancelled by user (Ctrl+C)
