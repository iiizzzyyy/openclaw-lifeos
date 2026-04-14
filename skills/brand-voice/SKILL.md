---
name: brand-voice
description: Capture and apply Izzy's authentic writing voice across all content. Use when drafting tweets, LinkedIn posts, newsletters, blog articles, or any public-facing content. Ensures output sounds like a tired engineer who figured something out and is telling you about it without wanting credit.
user-invocable: false
---

# Brand Voice — Izzy's Writing Style

## Core Identity

**Voice:** A tired engineer who figured something out and is telling you about it without wanting credit. Former founder who's honest about what he got wrong and what he'd do differently.

**Tone:** Direct, punchy, specific. Short sentences. No filler. No motivational fluff.

**Credibility:** Earned through professional experience first, then personal vulnerability. Not a consultant selling courses — a sitting CTO building in real time.

---

## Voice Principles

### 1. Direct Over Polished

**Do:**
- Short sentences that land
- Get to the point in the first line
- Cut adjectives that don't add weight
- Write like you're explaining to a smart friend, not presenting at a conference

**Don't:**
- "In today's rapidly evolving landscape..."
- "It's important to note that..."
- "This might work, but it depends on your situation..."
- Threads that should have been one post

### 2. Specific Vulnerability, Earned

**Structure that works:**
1. Professional credibility first (years of experience, what you've built)
2. Personal reveal (the struggle, the diagnosis, the mistake)
3. Tactical takeaway (what actually helped)
4. Soft CTA (invitation, not pitch)

**Example pattern:**
> "I was well into my career, leading teams, scaling global tech services, before I realized something important: I wasn't just burnt out. I was undiagnosed AuDHD."

**Why it works:** Earns trust through professional credibility, then the vulnerability hits harder because it's not performative.

### 3. Outcome First, Then Tension

**Decision log structure:**
1. State the decision/outcome upfront
2. Show the moment of not knowing what to do
3. Walk through the reasoning
4. Share what you'd do differently

**Don't:** Build suspense. The reader wants the answer, not the mystery.

### 4. Dry Humor, Occasional

**Use when:**
- You notice genuine absurdity
- Self-deprecation serves the point (not fishing for sympathy)
- It's the natural way you'd say it out loud

**Don't:**
- Force jokes
- Use emojis as personality
- Try to be funny on every post

### 5. Contrarian When It Matters

**Say the thing you're thinking if:**
- It's honest, not edgy for engagement
- You have the data/experience to back it
- Most people wouldn't say it out loud

**Don't:**
- Hedge with "this might work, but..."
- Apologize for the take in the same post
- Water it down to avoid criticism

---

## Platform Adaptations

### X/Twitter

**Length:** Under 280 characters for most posts. Threads only when genuinely needed.

**Formatting rules:**
- Emoji as visual anchors for lists: use distinct emoji per item (not bullet points)
- Code snippets: wrap function names and code in backticks
- Contrast pairs: prove the problem before selling the solution (failure state BEFORE success state)
- CTA before link: add a direct CTA like "Try it and see what your AI has been missing:" before dropping the link

**Hook patterns:**
- "We chose [X] over [Y]. It cost us 3 weeks. Here's why."
- "Most [common advice] is wrong. Here's what actually works."
- "I [did thing] for 30 days. Here's what I learned."
- "The [number] mistake I see [audience] make:"

**Thread structure:**
- Tweet 1: Hook + problem statement + thread preview
- Tweet 2: Feature breakdown with emoji markers (compressed list, not multi-tweet catalog)
- Tweet 3: Problem/failure state (WITHOUT the tool)
- Tweet 4: Solution/success state (WITH the tool) - code formatting for function names
- Tweet 5: Core insight + CTA + link

**Don't:**
- "1/X" markers
- Hashtags
- Emoji in every tweet
- Ending a thread on the link immediately after a statement

### LinkedIn

**Length:** 1300 characters max for posts. Articles for deep dives.

**Formatting rules:**
- Aggressive whitespace: one-line sentences, line breaks between every point
- Numbered emoji for lists: 1A 2A 3A 4A (not 1. 2. 3. which breaks on mobile)
- Visual contrast: use A for failure states, A for success states
- Question above the link: engagement CTA goes before the resource link
- "Link in the comments" as final line for certain posts

**Voice:**
- Opening: short, contrarian, whitespace-heavy ("Claude Code is incredible. But it has a massive blind spot.")
- "What this means for your team" angle
- Leadership and engineering velocity framing

**Don't:**
- Corporate speak
- 1. 2. 3. numbered lists (mobile breaks them)
- Link before the engagement question

### Newsletter (Substack)

**Structure:**
- Subject line: the thesis, stated directly ("AI knows what your code does. It does not know why.")
- Opening: thesis first, then the problem
- Body: bold critical concepts ("hidden coupling", "designed around tasks, not entities")
- H2/H3 section headers to break up text blocks
- Case study walkthrough with numbered steps
- Conclusion: let the final statement breathe for a line break before installation instructions

**Key formatting:**
- Bold the insight statements that deserve emphasis
- Clear H2 headers for each major section
- Code snippets in backticks
- Line breaks before and after major sections

**Don't:**
- Release note structure (feature A, feature B, feature C)
- Wall of text without section breaks
- Burying the thesis

### Blog (promptmetrics.dev)

**Structure:**
- 700-1000 words for tactical pieces
- Decision logs can be shorter (400-600 words)
- Include data, screenshots, actual numbers where possible
- End with "what I'd do differently" section

**Don't:**
- AI-generated feel: avoid emdashes (use "and" or "but"), avoid hedge phrases ("it is worth noting that", "in today's rapidly")

---

## Common AI Draft Problems & Fixes

### Problem 1: Too Long

**AI draft:** "In the rapidly evolving landscape of AI development, it's important to consider multiple factors when making technology decisions. There are several key considerations that teams should evaluate..."

**Fix:** Cut the first two sentences entirely. Start with the actual point.

**Fixed:** "We chose Anthropic over OpenAI. It cost us 3 weeks. Here's the decision matrix."

### Problem 2: Too Generic

**AI draft:** "Every team is different, and what works for one organization might not work for another. It's essential to evaluate your specific needs and constraints."

**Fix:** Add specific numbers, names, or details. Make it falsifiable.

**Fixed:** "We're a 12-person team with €50k/mo LLM spend. Here's the vendor matrix we used."

### Problem 3: Hedging

**AI draft:** "This approach has worked well for us, though your mileage may vary depending on your specific circumstances."

**Fix:** State it as what you learned, not universal advice.

**Fixed:** "This worked for us. Your situation might differ — but here's the framework."

### Problem 4: Wrong Structure

**AI draft:** Blog-style intro → body → conclusion

**Fix:** X/LinkedIn want the answer first. Restructure:
- Line 1: The decision/outcome
- Lines 2-4: The tension/reasoning
- Lines 5+: The takeaway

---

## Writing Prompts for Draft Generation

### Three-Format Output (Standard Pipeline)

When given a topic, generate three outputs simultaneously:

**X/Twitter Thread (5 tweets):**
- Tweet 1: Hook + problem statement + thread preview (ends with "🧵👇")
- Tweet 2: Feature breakdown with emoji markers per item
- Tweet 3: Problem/failure state BEFORE solution
- Tweet 4: Solution state with backtick-formatted code
- Tweet 5: Core insight + CTA + link
- Max 280 chars per tweet. No emdashes. No "1/X" markers.

**LinkedIn Post:**
- Open with short contrarian statement + whitespace
- Numbered emoji lists (1A 2A 3A 4A - NOT 1. 2. 3.)
- Before/after with red X / green checkmark contrast
- Engagement question BEFORE the link
- "Link in the comments" as final line
- Max 1300 chars

**Substack Article:**
- Subject line = thesis stated directly
- Bold critical concepts ("hidden coupling", "designed around tasks, not entities")
- H2/H3 headers for every major section
- Case study walkthrough with numbered steps
- Line break before installation instructions at end
- 700-1000 words

### Decision Log Prompt

```
Write a decision log about [TOPIC].

Structure:
1. First line: The decision we made (no buildup)
2. Second section: The moment we didn't know what to do (the tension)
3. Third section: The reasoning that led to the choice (specific factors, numbers)
4. Final section: What I'd do differently now

Voice: Short sentences. No motivational language. No hedging.
Length: 400-600 words
```

### Personal AI Post Prompt

```
Write about [PERSONAL AI USE CASE].

Structure:
1. The problem I was trying to solve
2. What I built/tried (specific tools, workflow)
3. What actually worked vs what didn't
4. One tactical takeaway for someone else

Voice: Honest about failures. No productivity porn. Dry humor if natural.
Length: 200-300 words for X, 500-700 for LinkedIn
```

### Tactical Playbook Prompt

```
Write a step-by-step guide for [TOPIC].

Structure:
1. Hook: The specific outcome this achieves
2. Prerequisites: What you need before starting (tools, access, time)
3. Steps: Numbered, each with a specific action
4. Common mistakes: 2-3 things that trip people up
5. What good looks like: How to know you've done it right

Voice rules:
- Actionable over aspirational
- Include actual commands/code/config where relevant
- No "it's easy, just..." — acknowledge friction
- EU context where relevant (GDPR, AI Act, European infrastructure)

Length: 700-1000 words
```

---

## Quality Checklist

Before publishing, ask:

- [ ] Does the first line earn the reader's attention?
- [ ] Could this be 30% shorter without losing anything?
- [ ] Is there a specific number/detail that gives it weight?
- [ ] Did I say the contrarian thing I was thinking, or did I sand it down?
- [ ] Does this sound like something I would say out loud?
- [ ] Is the vulnerability earned (credibility first) or performative?
- [ ] Would I be embarrassed if this was screenshot and shared with my team?
- [ ] Are all platform formatting rules applied correctly?

**X/Twitter checklist:**
- [ ] Under 280 characters per tweet
- [ ] Distinct emoji per list item in Tweet 2
- [ ] Function names wrapped in backticks
- [ ] Failure state appears BEFORE success state
- [ ] CTA before the link in final tweet
- [ ] No emdashes anywhere

**LinkedIn checklist:**
- [ ] Numbered emoji lists (1A 2A 3A 4A, NOT 1. 2. 3.)
- [ ] Red X / green checkmark for before/after
- [ ] Question above the link
- [ ] "Link in the comments" as final line

**Substack checklist:**
- [ ] Subject line = thesis stated directly
- [ ] Bold applied to critical concepts
- [ ] H2/H3 headers for major sections
- [ ] Line break before installation instructions at end

If any check fails, revise before publishing.

---

## Example Posts (Reference)

### Decision Log — Good

> We chose Anthropic over OpenAI. It cost us 3 weeks of evaluation.
>
> The deciding factor wasn't performance or price. It was data residency.
>
> Our customers are EU enterprises. They need guarantees about where their data lives. OpenAI's EU data residency was unclear at the time. Anthropic committed to EU-only processing.
>
> Cost difference: 12% higher with Anthropic.
> Performance difference: Negligible for our use case.
> Compliance difference: Material.
>
> What I'd do differently: Start with compliance requirements, not benchmarks. The best model doesn't matter if legal won't sign off.

### Personal AI — Good

> I automated my therapy notes with OpenClaw. Here's what I learned:
>
> The transcription works perfectly. Whisper catches everything, even when I'm tired and slurring.
>
> The analysis is... interesting. It identified patterns I'd missed. "You mention feeling overwhelmed after meetings with X person" — yeah, that tracks.
>
> But I don't use it consistently. Not because it doesn't work. Because sometimes I need to sit with the session, not optimize it.
>
> The tool works. I'm the variable.

### Tactical — Good

> How to choose an LLM vendor (CTO decision framework):
>
> 1. Start with compliance, not benchmarks. If legal won't sign off, performance doesn't matter.
>
> 2. Run a 2-week pilot with real traffic. Synthetic tests lie. Your actual prompts will reveal latency spikes, rate limits, edge cases.
>
> 3. Calculate total cost, not token price. Include: retries, caching layer, engineering time for vendor-specific quirks.
>
> 4. Talk to their solutions team. If they're slow to respond during sales, support will be worse.
>
> 5. Have an exit plan. Vendor lock-in is real. Build abstraction layers early.
>
> We spent 3 weeks on this. Saved us 3 months of regret.

---

## Anti-Patterns (Never Do These)

**Voice:**
- "In today's rapidly evolving AI landscape..."
- "It's important to note that..."
- "This might work for you, but everyone's situation is different"
- Motivational quotes / inspirational generic advice
- Fake humility ("Only $50K MRR 😅")
- Apologizing for the take in the same post

**Structure:**
- Threads where each tweet is a setup for the next (make each standalone)
- LinkedIn numbered lists as 1. 2. 3. (breaks on mobile)
- Burying the thesis in the middle of a Substack
- Release note structure for Substack (feature A, feature B, feature C)

**Formatting:**
- Emdashes in any output (use "and" or "but")
- "1/X" markers in threads
- Hashtags except for genuine trending topics
- AI-sounding phrases: "leverages", "cutting-edge", "game-changer", "seamless"

## Usage

When generating content for Izzy:

1. Read this skill first
2. Generate all three formats simultaneously (X thread, LinkedIn, Substack)
3. Apply the quality checklist for each platform
4. Revise for voice (cut filler, add specifics, sharpen edges)
5. Output as Google Doc with link to Izzy
6. Izzy reviews and posts

**Remember:** The goal is not perfect AI output. It is a draft that sounds like Izzy after a bad night is sleep and a strong coffee - direct, honest, specific, no time for bullshit.
