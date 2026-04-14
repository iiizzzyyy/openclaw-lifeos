# Scheduling — Posting Calendar + Batch Workflow

## Core Principle
Consistency beats intensity. Batch creation beats daily scrambling.

---

## Posting Frequency by Platform

| Platform | Min/Week | Max/Week | Best Days | Best Times (CET) |
|----------|----------|----------|-----------|------------------|
| X | 3x | 7x | Daily | 8-9am, 12-1pm, 5-7pm |
| LinkedIn | 2x | 5x | Tue-Thu | 8-9am, 12-1pm, 5-6pm |
| Instagram | 2x | 4x | Mon, Wed, Fri | 9-11am, 7-9pm |
| TikTok | 2x | 5x | Tue-Thu, Sat | 7-9am, 12-1pm, 7-9pm |
| YouTube | 1x | 2x | Tue-Thu, Sat | 2-4pm |
| Newsletter | 1x | 2x | Tue or Wed | 6-8am (audience local) |
| Threads | 3x | 7x | Daily | 9-11am, 2-4pm, 8-10pm |
| Facebook | 2x | 3x | Mon, Wed, Fri | 8-10am, 7-9pm |

---

## Priority Order (When Time is Limited)

**Tier 1 (Non-negotiable):**
1. LinkedIn (core audience: EU CTOs/VPs)
2. X (real-time engagement, community)
3. Newsletter (deep relationship building)

**Tier 2 (Important but flexible):**
4. YouTube (SEO, long-term value)
5. Threads (growing, early adopter)

**Tier 3 (Nice to have):**
6. Instagram (visual, requires design time)
7. TikTok (high effort, younger demo)
8. Facebook (community groups, situational)

**If you only have 2 hours/week:** LinkedIn (1hr) + X (30min) + Newsletter (30min)

---

## Batch Workflow (Weekly, 3-4 hours)

### Monday Morning (90 min) — Creation
```
1. Read last week's hook performance (15 min)
2. Pick 1 blog topic or core insight (15 min)
3. Generate 8 platform outputs using skill graph (45 min)
4. Quick review + edits (15 min)
```

### Monday Afternoon (30 min) — Scheduling
```
1. Schedule LinkedIn (Tue-Thu posts)
2. Schedule X (3-5 posts for week)
3. Queue Newsletter (if sending this week)
4. Add Instagram/TikTok to design queue (if using Canva)
```

### Wednesday (30 min) — Engagement
```
1. Reply to LinkedIn comments (15 min)
2. Reply to X mentions/threads (15 min)
3. Note any topics sparking conversation (for future content)
```

### Friday (30 min) — Review
```
1. Check hook performance (15 min)
2. Update hooks.md with winners (15 min)
3. Plan next week's topics (optional)
```

---

## Content Calendar Structure

**Weekly themes (optional but helpful):**
- **Monday:** Build-in-public / metrics ("this post shows how we reduced X by Y%")
- **Tuesday:** Educational thread (longer, more detailed X thread)
- **Wednesday:** Data/research angles
- **Thursday:** Product-focused ("here's the feature behind this post")
- **Friday:** Retrospective / weekly insights
- **Weekend:** Lighter, conversational (or skip)

**Monthly themes (for strategic alignment):**
- Week 1: Compliance/governance focus
- Week 2: Cost optimization focus
- Week 3: Prompt engineering focus
- Week 4: Build-in-public / metrics

---

## Peak-Time Prioritization

**For maximum engagement:**

| UTC Time | Local (CET) | Priority | Quality Level |
|----------|-------------|----------|---------------|
| 5:00 | 7:00am | Low | Lighter content OK |
| 8:00 | 10:00am | **HIGH** | Strongest content |
| 11:00 | 1:00pm | Medium | Medium effort |
| 14:00 | 4:00pm | **HIGH** | Strong content |
| 17:00 | 7:00pm | **HIGH** | Strong content |
| 20:00 | 10:00pm | Low | Lighter or skip |

**Rule:** Put extra effort on 8, 14, 17 UTC runs. These are prime windows.

---

## Cron Job Schedule (Automated)

**Blog Promotion (6x daily):**
- Schedule: `0 5,8,11,14,17,20 * * *`
- Agent: `writer`
- Skill graph: Enabled
- Priority: 8, 14, 17 UTC = strongest content

**Newsletter (weekly):**
- Schedule: `0 6 * * 2` (Tuesday 6am)
- Agent: `writer`
- Manual review: Required before send

**YouTube (weekly):**
- Schedule: `0 14 * * 3` (Wednesday 2pm)
- Agent: `writer` + video production
- Manual: Script review + recording

---

## Seasonal Adjustments

**Q1 (Jan-Mar):** High engagement, planning season → Increase frequency
**Q2 (Apr-Jun):** Steady, conference season → Maintain + event content
**Q3 (Jul-Sep):** Summer slump (EU) → Reduce frequency, evergreen content
**Q4 (Oct-Dec):** Year-end rush → Increase, retrospective content

**Holidays to note:**
- Christmas/New Year (Dec 20 - Jan 5): Reduce or pause
- Summer (Aug in EU): Lighter content, reduce frequency
- Major conferences: Align content with event themes

---

## Burnout Prevention

**Signs you're overdoing it:**
- Creating content daily without batch workflow
- Skipping the Friday review (no learning loop)
- Posting on all 8 platforms every week
- Engaging with every comment (pick your battles)

**Minimum viable presence:**
- LinkedIn: 2x/week
- X: 3x/week
- Newsletter: 2x/month
- Everything else: Optional

**Remember:** One great post beats 7 mediocre ones. The skill graph is meant to reduce work, not increase it.

---

## Tools + Automation

**Scheduling:**
- Buffer (multi-platform)
- Typefully (X + LinkedIn)
- ConvertKit (newsletter)
- Native schedulers (LinkedIn, X Premium)

**Tracking:**
- Google Sheets (hook performance)
- Mixpanel (traffic from social)
- Platform analytics (native insights)

**Automation:**
- Blog promo cron (6x daily)
- Hook performance tracker (weekly)
- Content calendar reminders (Monday 9am)

---

## Weekly Checklist

**Monday:**
- [ ] Pick core topic/insight
- [ ] Generate 8 platform outputs
- [ ] Schedule LinkedIn + X for week
- [ ] Queue newsletter (if sending)

**Wednesday:**
- [ ] Reply to comments (LinkedIn + X)
- [ ] Note conversation topics

**Friday:**
- [ ] Review hook performance
- [ ] Update hooks.md with winners
- [ ] Plan next week's topics

**Monthly:**
- [ ] Review platform performance (which drove traffic/leads?)
- [ ] Adjust frequency based on ROI
- [ ] Archive underperforming content types
