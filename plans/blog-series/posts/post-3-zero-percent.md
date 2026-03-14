# Post 3: "Zero Percent"

## Opening Hook

129 recall tool invocations. 69 sessions. 265 session files scanned.

Spontaneous agent-initiated lookups: zero.

Every single invocation was either mandated by a skill step (87.6%) or initiated by the user (12.4%). The agent had the tools. The agent had the instructions. The agent had 366 indexed entries loaded in context. The agent never once independently decided to consult the reference material.

(Source: `plans/measure-agent-recall/report.md`, Mar 2026)

## Core Argument

### Building a Memory System

The problem is concrete: each Claude Code session starts from zero. No memory of prior sessions, prior decisions, prior mistakes. Every session, the agent makes the same errors you already corrected.

The first response was simple — rules in a file. `rules.md` (Sep 2025): human-written, agent-consumed, 14 rules. oklch-theme (Nov 2025) added agent self-update: "At the end of each session, perform a retrospective and update this file with reusable feedback." home (Jan 2026) distributed memory across files by content type: behavioral direction (AGENTS.md), session context (session.md), design rationale (design-decisions.md), artifacts (plans/).

By February 2026: memory-index.md — 366 entries seeded from 4 domains (behavioral rules, workflows, decisions, tools). Always-loaded via `@`-reference in CLAUDE.md. 3.7k tokens consumed every session. The idea: agents see the index, recognize relevant situations, look up the decision.

### The First Measurement

February 20, 2026. 801 sessions scanned across 71 project directories. The `/when` skill (active lookup via fuzzy matching) was invoked in 4.1% of post-merge sessions. Direct decision file reads: unchanged at 21.2% → 21.8%. Total recall improvement: 1.1x — noise.

The diagnosis from the session (session `f9e199ea`): "The mechanism that fails is not 'recognition of /when as a tool' but 'recognition of uncertainty as a state requiring action.' No amount of skill description tuning fixes that because the bottleneck is metacognition, not tool awareness."

The comparison is revealing: `/commit` succeeds because its trigger is a clear action boundary ("commit this"). `/when` fails because its trigger is "you might be wrong about how to handle this situation." The first requires recognizing an action. The second requires recognizing uncertainty about a decision you're currently making confidently.

(Commit `c4b1e043`)

### What the 4.1% Actually Measured

The 4.1% figure included user-initiated testing — users trying out `/when` to see if it worked. It measured skill invocations, not agent behavior. The actual question: does the agent, working autonomously, ever independently decide to consult its reference material?

The March 2026 measurement answered definitively. 129 recall tool invocations classified:

| Category | Count | % |
|----------|-------|---|
| Skill-procedural | 113 | 87.6% |
| User-triggered | 16 | 12.4% |
| Hook-injected | 0 | 0% |
| Spontaneous | 0 | 0% |

All 37 initially-classified "spontaneous" hits were reclassified on manual review: discussion-grounding (11), test-execution (7), orchestration-phase (6), user-triggered (5), non-recall (5), skill-procedural (3). Every single one traced back to either a skill step mandating the lookup or a user directing it.

### The Recognition Bottleneck

The "actionable index" concept — entries loaded in context that would self-trigger agent recognition — did not produce spontaneous recall behavior. The model has the information. The model has the tools. The model has instructions saying to use them. Zero usage.

Why: "An agent that's about to handle errors incorrectly doesn't think 'I should check the error handling decision' — it just handles errors the way it would by default." (Session `f9e199ea`)

LLMs produce the next token that's linguistically consistent with the preceding context. If the preceding context is an error-handling situation, the model generates error-handling code that fits the pattern — its training-data default. Recognizing that this specific situation has a project-specific override requires metacognitive awareness: "I'm in a situation where my default might be wrong, and I should check." That's not pattern-matching for linguistic consistency. That's confidence-monitoring. LLMs don't have it.

### What Actually Works: Handoff

The memory system that works isn't recall — it's structured carry-forward.

session.md: working memory. Tasks with metadata (command, model, restart flag). Blockers. Context notes. Pending tasks are carry-forward verbatim — not summarized, not reworded. The handoff skill writes it; the next session reads it.

learnings.md: append-only semantic memory. Anti-pattern / correct pattern / rationale format. Soft limit of 80 lines. When approaching the limit, the codify skill consolidates older learnings into permanent documentation (behavioral rules → fragments, technical details → decisions/).

The key: handoff works because it's procedural. The `/handoff` skill runs at session end and writes the file. No metacognitive recognition needed. No "should I save this?" judgment — the skill always runs, captures everything structured, and the next session always reads it.

### Forced Injection

The system pivoted from "give agents better lookup tools" to "make infrastructure do the recalling." UserPromptSubmit hooks detect topic keywords and inject relevant decisions into context. The memory-index becomes a backing store queried by scripts, not by agents.

Prior evidence supported this: forced-eval hooks achieved substantially higher activation than voluntary mechanisms. The design choice: forced injection beats voluntary recall at 0%.

The full arc:

```
Human-written flat rules (Sep 2025)
  → Agent self-update (Nov 2025)
    → Structured file taxonomy (Jan 2026)
      → Always-loaded memory index (Feb 2026)
        → Active lookup tools /when, /how (Feb 2026)
          → 4.1% measured, recognition bottleneck named (Feb 20)
            → Recall gate inventory: 61% prose-only (Feb 24)
              → Tool-call-anchored gates (Feb 25)
                → Forced injection via hooks (Mar 1)
                  → 0% spontaneous recall confirmed (Mar 2026)
```

Every approach that relied on agent recognition failed. The only approaches that achieved recall were procedural (mandated by skill steps) or infrastructural (forced by hooks).

## Evidence Chain

| Claim | Evidence |
|-------|----------|
| 0% spontaneous recall across 129 invocations | `plans/measure-agent-recall/report.md` |
| 87.6% skill-procedural, 12.4% user-triggered | Same report |
| 4.1% /when invocation rate (included user testing) | Commit `c4b1e043` |
| 801 sessions scanned, 71 directories | Commit `c4b1e043` body |
| Recognition bottleneck diagnosis | Session `f9e199ea` |
| `/commit` succeeds (action trigger) vs `/when` fails (metacognitive trigger) | Session `f9e199ea` |
| 31 recall gates, 61% prose-only | Commit `7ee9d0c0` |
| Forced-eval hooks: substantially higher activation than voluntary | Prior learnings (cited in session `f9e199ea`) |
| Memory-index: 366 entries, 3.7k tokens | Commit `6e88a294`, later measurements |

## Transition to Post 4

Zero percent spontaneous recall. But at least the agent has the information when procedurally forced to look at it. What happens when the agent *does* look, tests *do* pass, and the output is still wrong? The next post covers a case where 385 automated checks passed and 8 bugs shipped.
