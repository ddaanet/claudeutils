# Requirements Skill: Design Outline

## Problem

Two gaps in the current workflow:
1. **Mid-conversation capture:** After ad-hoc discussions about what to build, no structured capture step exists. Requirements live only in conversation context and are lost or degraded on session end.
2. **Cold-start elicitation:** When starting new work, no structured step guides requirements gathering before jumping to `/design`.

Both result in `/design` Phase A.0 either re-discovering intent from scratch or working from vague input.

## Approach: Dual-Mode Requirements Skill

`/requirements <job>` operates in two modes based on conversation state:

**Extract mode** (mid-conversation — substantive discussion preceded invocation):
- Extract requirements from conversation context
- Lightweight codebase discovery to ground requirements
- Structure into standard format
- Gap-fill: ask targeted questions only for empty critical sections
- Write `plans/<job>/requirements.md`

**Elicit mode** (cold-start — invoked at start of conversation or with minimal context):
- Guide user through structured requirements questions (scope, constraints, NFRs)
- Lightweight codebase discovery to inform scope
- Structure responses into standard format
- Write `plans/<job>/requirements.md`

**Mode detection:** If conversation contains substantive discussion about a feature/task → extract mode. If conversation is fresh or `/requirements` is the first substantive action → elicit mode. Same output format regardless of mode.

## Lightweight Codebase Discovery

Quick, focused scan to ground requirements in reality — NOT deep exploration.

**What discovery does:**
- Scan `plans/` for related work (avoid duplicating existing plans)
- Check what modules/files exist in the relevant area (informs scope)
- Read existing patterns to inform constraints

**What discovery does NOT do:**
- Deep architectural analysis (that's `/design` Phase A)
- Context7 or web research
- Quiet-explore agent delegation

**Rationale:** Satisfies NFR-1 (lightweight, no duplication) while making requirements less naive than pure conversation capture.

## Workflow Positioning (FR-2)

```
/requirements → /design (seeds A.0 with structured input)
/requirements → /handoff (document intent for later)
/requirements → /runbook (direct to planning, if clear enough)
/requirements (standalone — just capture intent)
```

## Standard Artifact Format

```markdown
# <Job Name>

## Requirements

### Functional Requirements
**FR-1: <requirement>**
<details, acceptance criteria>

### Non-Functional Requirements
**NFR-1: <requirement>**
<details>

### Constraints
**C-1: <constraint>**
<rationale>

### Out of Scope
- <item> — <rationale>

### Dependencies
- <dependency> — <impact>

### Open Questions
- Q-1: <unresolved item from conversation>
```

## Key Decisions

1. **Dual-mode** — Extract (mid-conversation) or elicit (cold-start), same output format
2. **Lightweight discovery** — Quick codebase scan to ground requirements, not deep exploration
3. **Gap-fill sparingly** — Ask questions only when critical sections are entirely empty after extraction
4. **Standard format** — Consistent structure enables Design A.0 to consume reliably
5. **Skill dependency flagging** — Scan output for hook/agent/skill/plugin mentions, note for Design
6. **Model tier: opus** — Extract mode requires synthesizing nuanced conversation; sonnet misses implicit requirements in complex discussions

## Scope

**In scope:**
- SKILL.md with dual-mode procedure (extract + elicit)
- Standard requirements.md format specification
- Lightweight codebase discovery procedure
- Gap detection for empty critical sections
- Skill dependency indicator scanning
- Integration with existing Design A.0 checkpoint (already consumes requirements.md)

**Out of scope:**
- Automated requirements validation
- Requirements-to-code traceability
- Changes to `/design` or `/runbook` skills
- Deep exploration (quiet-explore, Context7, web research)

## Risk Assessment

**Primary risk:** Redundancy with just writing requirements.md manually. Value-add is structured extraction + gap detection + discovery + dependency scanning.

**Secondary risk:** Discovery scope creep into full exploration. Skill must cap discovery at direct reads — no agent delegation.

## Implementation Notes

- Tier 1 (direct implementation, <6 files)
- Pure procedural skill — 1 SKILL.md file, possibly 1 reference for elicitation patterns
- No code artifacts, no scripts
