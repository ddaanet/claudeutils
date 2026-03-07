# Pipeline Review Protocol — Design Outline

**Problem:** Pipeline review stages (/requirements step 5, /design Phase B + post-design, /runbook post-outline + post-expansion) use ad-hoc conversation or a thin protocol (discussion-protocol.md: 21 lines). No structured reword-validate-accumulate loop. No author-corrector coupling when skills are updated. Ad-hoc edits to planning artifacts bypass corrector review entirely.

**Evidence:** Bootstrap separation session — agent executed full edit→validate→commit without structured feedback, substituted validator for corrector, no checkpoints between stages.

## Approach

`/proof` — a standalone skill invoked by hosting skills (/design, /runbook, /requirements) at their review stages. The Skill tool invocation serves as the enforcement gate. Runs inline (no `context: fork`) — shares the hosting skill's context window, sees all loaded artifacts.

**Planstate:** `proof <artifact>.md` — plan enters this state when awaiting user validation (e.g., `proof outline.md`, `proof runbook-phase-2.md`).

## Components

### C1: `/proof` Skill

`agent-core/skills/proof/SKILL.md` — replaces current 21-line `discussion-protocol.md`.

**Loop mechanics:**
- **Reword:** Agent restates user input as understanding statement. User validates or corrects.
- **Accumulate:** Each validated round adds to a running decision list (in-memory, not file).
- **Sync:** On user request ("sync", "resync"), output full accumulated decision list.
- **Terminal actions:**
  - "proceed" / "apply" → Apply accumulated decisions to artifact, then dispatch lifecycle-appropriate corrector
  - "learn" → Capture insight to learnings.md
  - "suspend" → Prepend `/design plans/<skill-fix>` to current continuation (existing continuation-prepend mechanism), route to /design for skill update

**Why a skill, not a reference file:** Structure requires enforcement. Enforcement requires gates. Gates require tool calls (codified in "When Anchoring Gates With Tool Calls"). The Skill tool invocation is the gate — it forces protocol steps into attention focus. The current reference file failed to enforce (Bootstrap session evidence).

### C2: Integration Points

| Skill | Stage | Artifact Under Review | Current Behavior | Defect Class |
|-------|-------|-----------------------|-----------------|--------------|
| /requirements | Step 5 (Present Draft) | requirements.md | "Does this capture accurately?" — single-turn | Prevention — captures domain context before design |
| /design | Phase B (Post-outline) | outline.md | discussion-protocol.md — thin loop, file-edit-centric | Approach validation |
| /design | Post-C.3 (Post-design) | design.md | No explicit review stage | Design validation before /runbook consumes |
| /runbook | Post-outline (after Phase 0.75-0.86) | runbook-outline.md | Corrector review, no user loop | Structural validation |
| /runbook | Post-expansion (after Phase 1/3 corrector) | runbook-phase-*.md | Corrector review, no user loop | Systemic/novel defect detection — earliest point where defects become concrete |

Each integration point: invoke `/proof`, enter review loop on the artifact, accumulate decisions until terminal action.

**Layered defect model:** /requirements is the prevention layer (capturing domain context avoids defect classes entirely). Post-expansion is the detection layer (catches systemic defects that correctors cannot — novel defect classes not yet in corrector rules). Evidence: wrong-RED/bootstrap defect passed all correctors, detectable only by human review at expansion point.

### C3: Author-Corrector Coupling

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

### C4: Automatic Corrector After Proof

When `/proof`'s terminal action is "apply" and the artifact is a planning artifact (phase files, runbook, outline):

- Dispatch the lifecycle-appropriate corrector (sub-agent with clean context)
- Corrector loads plan artifacts (design, recall-artifact) automatically
- Corrector uses /review-plan or equivalent skill
- Present findings before proceeding (gate, not pass-through)

This makes corrector dispatch lifecycle-driven: artifact type + "edits applied" → corrector fires. The user doesn't say "run correctors."

## Scope

**IN:**
- `/proof` skill (replacing discussion-protocol.md reference file)
- `proof <artifact>.md` planstate
- Integration in /requirements, /design, /runbook at identified stages (5 integration points)
- Author-corrector coupling check in /design
- Automatic corrector dispatch after proof "apply" terminal action

**OUT:**
- New corrector agents (existing correctors sufficient)
- Changes to validate-runbook.py (mechanical — separate task if needed)
- Changes to prepare-runbook.py
- Hook-based enforcement (future extension)
- Changes to /inline or /orchestrate skills
- Continuation infrastructure changes (suspension uses existing prepend)

## Key Decisions

- **Skill, not reference file (D-1):** Enforcement requires gates. Gates require tool calls. Skill invocation is the gate. Evidence: current reference file failed (Bootstrap session).
- **Inline execution (D-2):** No `context: fork` — skill needs hosting skill's loaded context (artifacts, discussion history).
- **No continuation push/pop (D-4):** Mid-session suspension uses existing continuation-prepend. Session boundaries handled by design-context-gate (context budget check). No new infrastructure.
- **Post-expansion as integration point (D-5):** Earliest detection point for systemic/novel defects. Evidence: wrong-RED/bootstrap defect class.
- **Requirements as prevention layer (D-6):** /requirements captures domain context before design, preventing defect classes. Post-expansion detects what requirements missed. Complementary layers.
- **Name: proof (D-7):** Transparent validation semantics, thematically native to edify context.
- **Author-corrector coupling is a /design responsibility:** Designer checks transformation table for coupled correctors. Visible output block forces awareness.

## Open Questions

None — all resolved during Phase B discussion.

## Execution Constraint

Per "When implementation modifies pipeline skills": structure as inline task sequence, not Tier 3 orchestration. Each skill update executes with fresh CLAUDE.md loads. TDD not applicable (agentic-prose artifacts).
