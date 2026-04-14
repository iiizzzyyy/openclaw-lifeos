# Setup Checklist

**Time:** 30-45 minutes
**Prerequisites:** OpenClaw installed, Obsidian (optional), Google account (for Docs/Calendar)

---

## Phase 1: Interview & Workspace Setup (15 min)

### 1.1 Send the Setup Prompt

Send this to your OpenClaw:

```
Read the OpenClaw Life OS scaffold at https://github.com/tuiizzyy/openclaw-lifeos
and use it to set up my workspace.
```

### 1.2 Complete the Interview

The assistant will ask you questions in small batches. Answer honestly — this shapes your entire system.

**Typical questions:**
- What's your role? (CTO, founder, solo builder?)
- What gets forgotten between sessions?
- Do you want content automation? Lead research? Code help?
- What should it never automate without asking?
- What's your communication style?

### 1.3 Review Generated Workspace

After the interview, the assistant creates tailored workspace files:
- `workspace/AGENTS.md`
- `workspace/SOUL.md`
- `workspace/USER.md`
- `workspace/MEMORY.md`
- `workspace/HEARTBEAT.md`

**Action:** Copy these to your OpenClaw root directory.

```bash
cp workspace/*.md ~/clawd/
```

---

## Phase 2: Install Core Skills (10 min)

### 2.1 Choose Your Skills

Not all skills are for everyone. Start with these:

**Content creators:**
- `blog-knowledge-compiler`
- `content-skill-graph`
- `brand-voice`

**Builders:**
- `test-driven-development`
- `deep-research`

**Ops-focused:**
- `healthcheck`
- `session-logs`

### 2.2 Copy Skills

```bash
# Example: copy blog-knowledge-compiler
cp -r skills/blog-knowledge-compiler ~/.openclaw/skills/

# Verify installation
openclaw skills list | grep blog-knowledge-compiler
```

### 2.3 Configure Skill-Specific Settings

Some skills need config:

**blog-knowledge-compiler:**
```bash
# Set your Obsidian vault path
echo "OBSIDIAN_VAULT=~/Obsidian" >> ~/.openclaw/config.env
```

**brand-voice:**
```bash
# Edit voice profile
nano ~/.openclaw/skills/brand-voice/voice-profile.md
```

---

## Phase 3: Set Up Workflows (5 min)

### 3.1 Copy Workflow Templates

```bash
cp workflows/*.yaml ~/clawd/workflows/
```

### 3.2 Configure Workflow Parameters

Edit each workflow to match your setup:

**blog-generate.yaml:**
```yaml
# Change template paths to your blog templates
prompt_file: /YOUR/PATH/config/prompts/blog-generate.md
```

**lead-research.yaml:**
```yaml
# Update ICP criteria
icp: "YOUR ideal customer profile"
```

### 3.3 Test One Workflow

```bash
python3 ~/clawd/scripts/run_workflow.py blog-generate --param type=problems
```

---

## Phase 4: Set Up Crons (10 min)

### 4.1 Review Cron Templates

```bash
cat cron/jobs.template.json
```

### 4.2 Customize for Your Needs

Edit the templates:
- Change delivery times to your timezone
- Update Telegram/email addresses
- Adjust frequency based on your needs

### 4.3 Install Crons

```bash
# Copy to your cron directory
cp cron/jobs.template.json ~/clawd/cron/jobs/

# Or use OpenClaw's cron manager
openclaw cron import ~/clawd/cron/jobs.template.json
```

### 4.4 Verify Cron Registration

```bash
openclaw cron list
```

You should see your new jobs listed.

---

## Phase 5: Install Infrastructure Scripts (5 min)

### 5.1 Copy Scripts

```bash
cp scripts/*.py ~/clawd/scripts/
chmod +x ~/clawd/scripts/*.py
```

### 5.2 Initialize Data Structures

```bash
# Create circuit breaker state
python3 ~/clawd/scripts/circuit_breaker.py status

# Initialize cost tracker
python3 ~/clawd/scripts/cost_tracker.py --since 7d

# Set up action logger
python3 ~/clawd/scripts/action_logger.py --action "setup" --outcome success
```

### 5.3 Test Observability

```bash
# Check circuit breakers
python3 ~/clawd/scripts/circuit_breaker.py status

# Check costs (should be empty initially)
python3 ~/clawd/scripts/cost_tracker.py --since 7d

# Check action log
tail ~/clawd/logs/actions.jsonl
```

---

## Phase 6: First Run & Validation (5 min)

### 6.1 Start a New Session

```bash
openclaw session new
```

### 6.2 Verify Memory Persistence

Ask: "What do you know about me?"

It should read from USER.md and MEMORY.md and give you personalized answers.

### 6.3 Test HEARTBEAT

```bash
# Send a heartbeat message
# Expected response: HEARTBEAT_OK (if nothing needs attention)
```

### 6.4 Run One Automated Task

```bash
# Example: morning briefing
python3 ~/clawd/scripts/daily_briefing.py
```

---

## Troubleshooting

### "Skills not found"
- Verify OpenClaw skills directory: `openclaw skills list`
- Check file permissions: `ls -la ~/.openclaw/skills/`

### "Cron jobs not running"
- Check cron daemon: `openclaw gateway status`
- Verify job config: `openclaw cron list`
- Check logs: `tail ~/clawd/logs/cron.log`

### "Memory not persisting"
- Ensure files are in correct location: `ls ~/clawd/*.md`
- Check file permissions
- Verify CONTINUATION.md is being written on session end

### "Circuit breaker tripped"
```bash
# View status
python3 ~/clawd/scripts/circuit_breaker.py status

# Reset a breaker
python3 ~/clawd/scripts/circuit_breaker.py reset <job_name>
```

---

## Next Steps

1. **Add your own skills** — Build for your specific workflows
2. **Customize voice** — Edit SOUL.md to match your personality
3. **Expand memory** — Add domain-specific knowledge to MEMORY.md
4. **Build dashboards** — Set up Mission Control or custom observability
5. **Join the community** — Share your setup at [OpenClaw Discord](https://discord.com/invite/clawd)

---

**Questions?** Reach out: [tuiizzyy@gmail.com](mailto:tuiizzyy@gmail.com) or [@tuiizzyy](https://twitter.com/tuiizzyy)
