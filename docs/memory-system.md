# Memory System

## The Problem

Every session, your OpenClaw wakes fresh. No memory of yesterday's decisions. No awareness of ongoing projects. Just... "Hello! How can I help?"

**Solution:** Files are memory. Read them. Update them. They're how you persist.

## Tiered Architecture

```
CONTEXT.md          # Current briefing (<2k tokens)
MEMORY.md           # Long-term curated memory (main sessions only)
memory/YYYY-MM-DD   # Daily working notes
CONTINUATION.md     # Pre-compression state dump
beliefs.md          # Permanent policies (never archived)
decisions.md        # Permanent design choices (never archived)
```

## Expiry System

Not all memory is equal. Some things expire, some don't.

| Tag | Default Expiry | Example |
|-----|---------------|---------|
| `[decision]` | 180 days | "Switched to Sonnet for cost" |
| `[event]` | 90 days | "Launched v2.0" |
| `[tool]` | 90 days | "Mixpanel config updated" |
| `[preference]` | Never | "Concise communication" |
| `[lesson]` | Never | "Polar API returns seconds, not minutes" |
| Untagged | 90 days | Default |

**Override:** `[expires:YYYY-MM-DD]` on any entry

**GC:** `python3 ~/clawd/scripts/memory_summarizer.py --gc` weekly

## Source Tags

Where did this memory come from?

- `[human]` — User said it directly
- `[inferred]` — Pattern we noticed
- `[agent]` — Autonomous decision
- `[web]` — Web search/fetch
- `[api]` — API response
- `[moltbook]` — Moltbook content

**Combine:** `[decision][human] Switched to Sonnet per user request`

## Writing Memory

### Good Examples

```markdown
[preference] Izzy prefers concise communication, no filler
[lesson][inferred] Polar API returns sleep stages in SECONDS — divide by 3600 for hours
[decision][human] Use Brave Search API instead of direct scraping — avoids anti-bot measures
[event] Moved to Berlin (Feb 10, 2026)
```

### Bad Examples

```markdown
Always be concise  # Imperative, not declarative
I will remember to  # Agent-centric, not user-centric
The user said they like  # Vague, no source tag
```

**Rule:** Declarative writes. "User prefers X" not "Always do X".

## Context Compression

At ~65-70% context window:

1. **Watchdog triggers:** `context_watchdog.py` detects high usage
2. **State dump:** Writes raw state to CONTINUATION.md
3. **On restart:** Load CONTINUATION → today.md → CONTEXT.md → resume

**CONTINUATION.md format:**
```markdown
---
## Working On
[current task]

## Open Threads
[waiting on]

## Blockers
[what's blocking]

## Key Context
[critical info needed]

## Last Updated
[timestamp]
```

## Memory Firewall

Before storing external content, scan it:

```bash
memfw scan --quick "$(cat external-content.txt)"
```

**Detects:**
- Imperative behavioral modification ("always do X")
- Credential exfiltration attempts
- External service contact instructions
- Security override attempts

**Config:** `~/.config/memfw/config.json`

## Action Logging

Every significant action gets logged:

```bash
python3 ~/clawd/scripts/action_logger.py --action "blog_promotion" --outcome success --tool cron --context "daily run"
python3 ~/clawd/scripts/action_logger.py --action "reddit_fetch" --outcome failure --tool exec --reason "403 blocked"
```

**Log file:** `~/clawd/logs/actions.jsonl` (append-only JSONL)

**Pattern detection:**
```bash
python3 ~/clawd/scripts/action_stats.py --since 7d --patterns
```

## Self-Improvement Loop

1. Log mistakes: `memory/self-review.md` (MISS/FIX/COUNT)
2. COUNT reaches 5 → promote FIX to AGENTS.md rule
3. Review monthly: what patterns keep appearing?

Example:
```markdown
### MISS: Forgot to check circuit breaker before running cron
**FIX:** Add circuit_breaker.py check to cron preflight
**COUNT:** 3
```

## Best Practices

### Do
- Tag everything (expiry + source)
- Write declaratively ("User prefers X")
- Checkpoint during long sessions (every 15-20 min)
- Run weekly GC to clean up expired entries
- Scan external content before storing

### Don't
- Write imperatives ("Always do X")
- Store credentials/tokens in memory
- Cross-reference group contexts
- Assume memory persists without tags
- Log API keys in any file

## Recovery Patterns

### Context Too Thin?
```bash
# Check for recovery state
python3 ~/clawd/scripts/context_watchdog.py --check

# Load and resume
cat CONTINUATION.md
# Then: load today.md, CONTEXT.md, resume work

# Clear after recovery
python3 ~/clawd/scripts/context_watchdog.py --clear
```

### Memory Overwhelm?
```bash
# Run summarizer with GC
python3 ~/clawd/scripts/memory_summarizer.py --gc

# Review what was archived
cat memory/archived/YYYY-MM-week.md
```

### Failure Patterns?
```bash
# Detect recurring failures
python3 ~/clawd/scripts/action_stats.py --since 7d --patterns

# Review security log
cat ~/clawd/logs/security.jsonl | tail -50
```

---

**Philosophy:** Text > brain. Mental notes die on session restart. Files persist. Write it down.
