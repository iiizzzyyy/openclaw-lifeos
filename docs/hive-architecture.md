# Hive Architecture

## Overview

The Hive is a multi-agent system where specialized workers share state through a central bus. Instead of one generalist agent trying to do everything, you have specialists:

- **scout** — Research, competitive intel, lead discovery
- **writer** — Content creation, blog posts, social drafts
- **coder** — Implementation, debugging, infrastructure
- **ops** — Email, health checks, CRM updates

**Main** acts as the dispatcher, routing tasks to the right worker.

## State Bus

`hive/state.json` is the shared awareness layer. Every worker reads and writes to it:

```json
{
  "timestamp": "2026-04-14T19:00:00Z",
  "workers": {
    "scout": {
      "status": "idle",
      "last_task": "competitor_research",
      "findings": ["Competitor X launched feature Y"]
    },
    "writer": {
      "status": "working",
      "current_task": "blog_post_draft",
      "progress": 0.6
    },
    "coder": {
      "status": "idle",
      "last_task": "bug_fix",
      "commits": 3
    },
    "ops": {
      "status": "idle",
      "last_task": "health_check",
      "alerts": 0
    }
  },
  "shared_context": {
    "priority_leads": ["Company A", "Company B"],
    "blog_topics_queue": ["LLM costs", "EU AI Act"],
    "system_alerts": []
  }
}
```

## Task Chains

Predefined workflows that route through multiple workers:

### 1. blog_promo
```
scout → finds trending topics
writer → drafts platform-native posts
ops → schedules delivery
```

### 2. new_blog_post
```
scout → researches topic
writer → drafts full post
ops → creates Google Doc, shares
```

### 3. lead_research
```
scout → discovers companies matching ICP
scout → deep research on each
writer → drafts personalized outreach
ops → saves to CRM
```

### 4. competitor_alert
```
scout → monitors competitors
writer → drafts response/positioning
ops → alerts user if urgent
```

### 5. morning_pipeline
```
ops → checks calendar, emails
scout → overnight news/research
writer → drafts briefing
ops → delivers to user
```

### 6. health_report
```
ops → runs health checks
coder → analyzes failures
ops → compiles cost breakdown
writer → formats report
ops → delivers weekly
```

## Cost Optimization

**Model routing:**
- Simple tasks (file edits, searches) → Sonnet (~$0.015/msg)
- Complex tasks (architecture, code review) → Opus (~$0.05/msg)

**Toggle:**
```bash
python3 hive/dispatcher.py mode cost-conscious
```

Flips all workers to Sonnet. Use when budget is tight.

## Memory Isolation

```
hive/shared/              # All agents can read/write
hive/private/scout/       # Scout's private memory
hive/private/writer/      # Writer's private memory
hive/private/coder/       # Coder's private memory
hive/private/ops/         # Ops' private memory
hive/private/main/        # Dispatcher's personal memory
```

**Rules:**
- Shared: common context, task queues, alerts
- Private: worker-specific learnings, preferences
- Never cross-reference private folders between workers

## Dashboard

```bash
python3 hive/status.py
```

Shows:
- Worker status (idle/working/error)
- Current tasks and progress
- Task chain execution history
- Cost breakdown by worker
- Shared context contents

## Adding a Worker

1. Create worker config: `hive/workers/<name>.json`
2. Define responsibilities and model preference
3. Add to dispatcher routing logic
4. Create private memory folder
5. Update status dashboard

Example:
```json
{
  "name": "analyst",
  "model": "opus",
  "responsibilities": ["data_analysis", "metrics_reporting"],
  "private_memory": "hive/private/analyst/"
}
```

## Failure Handling

**Circuit breakers:**
- 2 consecutive failures → auto-disable worker
- $10/day cost limit per worker → pause

**Recovery:**
```bash
python3 ~/clawd/scripts/circuit_breaker.py reset <worker_name>
```

**Logging:**
- All actions logged to `~/clawd/logs/actions.jsonl`
- Failures include reason and stack trace
- Run `action_stats.py --patterns` to detect recurring issues

---

**Customization:**
- Add/remove workers based on your needs
- Adjust task chains for your workflows
- Set cost limits appropriate for your budget
