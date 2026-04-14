# Contributing

This scaffold is meant to evolve. If you build something useful, share it.

## What to Contribute

### Skills
New skills that solve a specific problem:
- Clear `SKILL.md` with usage examples
- Safety rules and boundaries
- Test cases or example runs

### Workflows
Multi-step automations:
- YAML workflow file
- Parameters documented
- Gate checks (daily/weekly limits)
- Example invocation

### Scripts
Infrastructure tools:
- Single responsibility
- CLI flags for configuration
- JSON output for composability
- Error handling

### Templates
Workspace files for different personas:
- CTO at startup
- Solo founder
- Freelancer
- Researcher

## How to Contribute

1. **Fork** the repo
2. **Build** your thing
3. **Test** it in your actual setup
4. **Document** it (README, examples, gotchas)
5. **PR** with clear description

## What Not to Contribute

- Generic scripts that already exist
- Skills without safety boundaries
- Workflows without gate checks
- Anything that exfiltrates data
- Credentials, API keys, tokens

## Code Style

**Python:**
- Type hints where practical
- JSON output for composability
- Exit codes: 0 = success, 1 = failure
- Log to stdout/stderr, not files

**YAML:**
- Descriptive step names
- Timeout on every step
- `continue_on_error` where appropriate
- Gate checks for recurring jobs

**Markdown:**
- Headers for structure
- Code blocks for examples
- Tables for comparisons
- Links to related docs

## Testing

Before submitting:
- [ ] Works in your setup
- [ ] Documented clearly
- [ ] No hardcoded secrets
- [ ] No data exfiltration
- [ ] Safety boundaries defined

## Questions?

Open an issue or reach out: [tuiizzyy@gmail.com](mailto:tuiizzyy@gmail.com)

---

**Philosophy:** Build in public. Share patterns, not prescriptions. Make it easy for the next person to stand on your shoulders.
