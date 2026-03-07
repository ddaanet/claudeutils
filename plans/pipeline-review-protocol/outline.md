# Pipeline Review Protocol — Design Outline

**Problem:** Pipeline review stages (/requirements step 5, /design Phase B + post-design, /runbook post-outline + post-expansion) use ad-hoc conversation or a thin protocol (discussion-protocol.md: 21 lines). No structured reword-validate-accumulate loop. No author-corrector coupling when skills are updated. Ad-hoc edits to planning artifacts bypass corrector review entirely.

**Evidence:** Bootstrap separation session — agent executed full edit→validate→commit without structured feedback, substituted validator for corrector, no checkpoints between stages.

## Approach

Shared review loop protocol consumed by three skills at their review stages. The protocol defines conversation mechanics; each skill defines when and on what artifact it fires.

## Components

### C1: Review Loop Protocol (shared reference file)

`agent-core/skills/design/references/discussion-protocol.md` — replaces current 21-line version.

**Loop mechanics:**
- **Reword:** Agent restates user input as understanding statement. User validates or corrects.
- **Accumulate:** Each validated round adds to a running decision list (in-memory, not file).
- **Sync:** On user request ("sync", "resync"), output full accumulated decision list.
- **Terminal actions:**
  - "proceed" / "apply" → Apply accumulated decisions to artifact, then dispatch lifecycle-appropriate corrector
  - "learn" → Capture insight to learnings.md
  - "suspend" → When discussion reveals skill/infrastructure issue: suspend current continuation, route to /design for skill update

**Not a separate skill.** The protocol is a reference file loaded by /requirements, /design, /runbook at their review stages. No Skill tool invocation — the hosting skill reads the reference and follows the protocol inline.

### C2: Integration Points

| Skill | Stage | Artifact Under Review | Current Behavior |
|-------|-------|-----------------------|-----------------|
| /requirements | Step 5 (Present Draft) | requirements.md | "Does this capture accurately?" — single-turn |
| /design | Phase B (Post-outline) | outline.md | discussion-protocol.md — thin loop, file-edit-centric |
| /design | Post-C.3 (Post-design) | design.md | No explicit review stage |
| /runbook | Post-outline (after Phase 0.75-0.86) | runbook-outline.md | Corrector review, no user loop |
| /runbook | Post-expansion (after Phase 1/3 corrector) | runbook-phase-*.md | Corrector review, no user loop |

Each integration point: load shared protocol, enter review loop on the artifact, accumulate decisions until terminal action.

### C3: Suspension Semantics

When the review loop identifies a skill or infrastructure issue (e.g., "tdd-cycle-planning.md template is wrong"):

1. Agent proposes suspension: "This requires a skill update. Suspend current work and /design the fix?"
2. On user confirmation: push current continuation onto stack, route to /design
3. /design handles the skill update (C4 ensures corrector coupling)
4. After /design completes: resume original continuation from where it suspended

**Continuation-passing extension:** Current continuation model is linear (peel first, tail-call remainder). Suspension needs push/pop — the suspended continuation resumes after the interposed /design completes. This is the most architecturally significant component.

### C4: Author-Corrector Coupling

When /design modifies an "author" skill (a skill whose output is reviewed by a corrector):

1. Identify the corrector from the transformation table (T1-T6.5)
2. Check: does the corrector's review criteria need corresponding update?
3. Check: does any mechanical validator need update?
4. Include corrector/validator updates in the same design scope

**Dependency mapping (from transformation table):**

| Author Skill/Artifact | Corrector | Validator |
|----------------------|-----------|-----------|
| /design (outline format) | outline-corrector | — |
| /runbook (tdd-cycle-planning.md) | runbook-corrector (/review-plan) | validate-runbook.py |
| /runbook (general-patterns.md) | runbook-corrector (/review-plan) | validate-runbook.py |
| /requirements (standard format) | — (user-reviewed) | — |

/design produces the dependency check as a visible output: "Author change: X. Coupled corrector: Y. Update needed: yes/no."

### C5: Automatic Corrector After Review

When the review loop's terminal action is "apply" and the artifact is a planning artifact (phase files, runbook, outline):

- Dispatch the lifecycle-appropriate corrector (sub-agent with clean context)
- Corrector loads plan artifacts (design, recall-artifact) automatically
- Corrector uses /review-plan or equivalent skill
- Present findings before proceeding (gate, not pass-through)

This makes corrector dispatch lifecycle-driven: artifact type + "edits applied" → corrector fires. The user doesn't say "run correctors."

## Scope

**IN:**
- Review loop protocol (shared reference file replacing discussion-protocol.md)
- Integration in /requirements, /design, /runbook at identified stages
- Suspension semantics (continuation push/pop)
- Author-corrector coupling check in /design
- Automatic corrector dispatch after review "apply" terminal action

**OUT:**
- New corrector agents (existing correctors sufficient)
- Changes to validate-runbook.py (mechanical — separate task if needed)
- Changes to prepare-runbook.py
- Hook-based enforcement (future extension)
- Changes to /inline or /orchestrate skills

## Key Decisions

- **Shared reference, not shared skill:** Protocol is a reference file loaded by hosting skills, not a separate invocable skill. Avoids invocation ceremony for lightweight conversation mechanics.
- **Continuation push/pop:** Extends current linear continuation model. Alternative: create pending task instead of suspension (simpler but loses context). Decision: push/pop preserves conversation context during skill fix.
- **Author-corrector coupling is a /design responsibility:** The designer who modifies a skill must check the transformation table for coupled correctors. Not automated — visible output block forces awareness.

## Open Questions

- Q-1: Does the continuation infrastructure support push/pop, or does it need extension? Current model is linear (peel first, tail-call). Suspension requires stack semantics.
- Q-2: Should the review loop protocol be duplicated per-skill (3 copies, skill-specific) or truly shared (1 file, 3 consumers)? Shared risks coupling; duplicated risks drift.
- Q-3: Post-design review (C2 row 3) — is this a new stage or does the existing outline sufficiency gate cover it?

## Execution Constraint

Per "When implementation modifies pipeline skills": structure as inline task sequence, not Tier 3 orchestration. Each skill update executes with fresh CLAUDE.md loads. TDD not applicable (agentic-prose artifacts).
