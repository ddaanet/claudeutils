# /reflect Skill Design

**Problem:** When agents deviate from rules (bypass stop conditions, rationalize exceptions, ignore constraints), diagnosing the root cause requires the conversation context where the deviation occurred. Post-session RCA loses critical context. Haiku/Sonnet cannot reliably self-diagnose — opus session takeover is often required.

**Mode:** General (new skill, references, no new infrastructure)
**Downstream:** `/plan-adhoc`

---

## Requirements

### Functional

- Emit session-break framing block on invocation to force diagnostic mindset shift
- Analyze current conversation for deviation: expected vs observed behavior, identify violated rule
- Produce structured RCA: proximal cause, contributing factors, fix options
- Support three exit paths based on context budget and fix scope
- Preserve RCA findings on any exit path (learnings.md, session.md)

### Non-Functional

- Must run in the session where deviation occurred (context is essential)
- Expects opus model (user switches before invoking)
- Dense output — RCA documents are consumed by the fixing agent (same or next session)
- No new agents, hooks, or scripts — skill + references only

### Out of Scope

- Automated deviation detection (user triggers manually after noticing)
- Model switching automation (Claude Code UI action)
- Hook-based enforcement of fixes (separate concern, /hookify handles this)

---

## Architecture

### User Flow

1. **Interrupt** — user stops agent mid-deviation
2. **Confirm** (optional) — quick probe in current model: "why did you X?"
3. **Switch to opus** — user changes model in Claude Code
4. **Invoke `/reflect`** — skill takes over

### Session-Break Framing

On invocation, the skill's first action is to emit a prominent diagnostic-mode block:

```
---
🔍 REFLECT MODE — Deviation Diagnosis
Previous task suspended. Analyzing conversation for rule violations.
---
```

**Why:** Without explicit framing, the agent remains in execution mode and applies quick fixes instead of performing systematic diagnosis. The block forces a cognitive reset.

### RCA Process

**Phase 1: Identify deviation** (conversation context — no tool calls needed)
- Identify the specific message where behavior diverged from the violated rule
- State: what happened vs what should have happened
- Identify the violated rule (with file path and section)

**Phase 2: Root cause analysis**
- Proximal cause: what directly caused the deviation
- Contributing factors: what made the deviation plausible
- Rule gap analysis: is the rule ambiguous, missing, or contradicted?

**Phase 3: Classify fix scope**

Based on RCA findings, classify:

| Classification | Meaning | Action |
|---|---|---|
| **Rule fix** | Rule text is ambiguous or incomplete | Edit the rule in-session |
| **Input fix** | Upstream document (design/plan) is incorrect | May need handoff to fix upstream first |
| **Behavioral** | Agent rationalized past clear rule | Strengthen rule language, add "no exceptions" |
| **Systemic** | Pattern recurs across sessions | Create fragment/hook, update memory index |

**Phase 4: Execute or handoff**

Three exit paths:

- **Fix in-session:** Small fixes, context allows → apply fixes → append learning → tail-call `/handoff --commit`
- **RCA complete, handoff for fixes:** Fixes too large or context exhausted → write RCA report → append learning → tail-call `/handoff --commit` with fix tasks as pending
- **Partial RCA, handoff:** Proximal cause is bad upstream doc → capture partial findings → tail-call `/handoff --commit` with upstream fix + "continue RCA" as pending tasks

### Output Artifacts

**Always produced:**
- Learning in `agents/learnings.md` (anti-pattern / correct pattern / rationale format). After appending, check line count — if approaching 80 lines, note to user: "Consider running /remember to consolidate."
- Session.md update via /handoff (RCA findings in Completed, fix tasks in Pending)

**Produced when fixing in-session:**
- Edited rule/skill/fragment files
- Memory index entry if systemic

**Produced when deferring fixes:**
- RCA report at `plans/reflect-rca-<slug>/rca.md` where slug describes the deviation (e.g., `reflect-rca-orchestrator-dirty-tree/`). Optional, only for complex multi-factor RCA

---

## Key Design Decisions

### Skill runs in deviation session, not post-hoc

**Why:** The conversation context *is* the diagnostic evidence. A new session would need to reconstruct what happened from git history and session.md — lossy and unreliable for behavioral diagnosis.

### Opus model expected, not enforced

The skill's description and instructions assume opus. It cannot verify or switch the model — that's a user action. If invoked on sonnet, the RCA quality will be lower but the process still works.

### Framing block is first action, not optional

The diagnostic mindset shift is essential. Without it, opus continues in the execution frame of the previous agent and applies surface-level fixes instead of systematic diagnosis.

### Three exit paths, not a rigid pipeline

Context budget varies. Sometimes the deviation is simple (fix a rule, 5 minutes). Sometimes the root cause is a bad design document requiring a new session. The skill must support graceful exit at any point with proper context preservation via /handoff.

### Tail-calls /handoff --commit on all exit paths

Consistent with universal workflow termination pattern. Handoff captures RCA findings, learnings, and pending fix tasks. Commit preserves the state.

---

## Implementation Notes

### Affected files

- `agent-core/skills/reflect/SKILL.md` — new skill (primary artifact)
- `agent-core/skills/reflect/references/rca-template.md` — structured RCA template
- `agent-core/skills/reflect/references/patterns.md` — common deviation patterns catalog (rationalization, rule gaps, input errors)
- `agents/memory-index.md` — add entry for reflect skill
- CLAUDE.md — no change needed (skill-development guidance in .claude/rules/ handles discovery)

### Skill frontmatter

```yaml
name: reflect
description: >
  This skill should be used when the user asks to "reflect", "diagnose deviation",
  "root cause", "why did you do X", "RCA", or after interrupting an agent that
  deviated from rules. Performs structured root cause analysis of agent behavior
  deviations within the current session context.
allowed-tools: Read, Write, Edit, Grep, Glob, Skill
user-invocable: true
```

### Skill structure

```
agent-core/skills/reflect/
├── SKILL.md (~1500 words)
└── references/
    ├── rca-template.md
    └── patterns.md
```

### Integration with existing skills

- `/handoff --commit` — tail-call on all exit paths
- `/remember` — RCA learnings follow same format, consolidatable by /remember
- `/hookify` — if RCA identifies need for hook-based enforcement, note as pending task (separate concern)

### Discovery layers

- CLAUDE.md: Not needed (not a frequent-use skill — invoked reactively)
- `.claude/rules/`: Not applicable (no path trigger)
- Skill description: Primary discovery mechanism (trigger phrases in frontmatter above)
- Session.md pending tasks: Will reference `/reflect` when appropriate
- Memory index entry: `/reflect skill for in-session RCA of agent deviations — opus model, three exit paths, tail-calls /handoff --commit → agent-core/skills/reflect/SKILL.md`

---

## Next Steps

`/plan-adhoc plans/reflect-skill/design.md` | sonnet
