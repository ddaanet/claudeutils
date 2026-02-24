# Recall Pass — Outline

## Approach

Extend existing pipeline context injection mechanisms. No new tools, no new agent types, no script changes. Each recall pass is a procedural addition to an existing skill. A persistent recall artifact file (`plans/<job>/recall-artifact.md`) carries selected entries forward through the pipeline.

**Core mechanism:** Recall entries flow through the runbook's existing Common Context and phase preamble sections. prepare-runbook.py already injects Common Context into agent system prompts and phase preambles into step files. The recall pass adds content to these sections — the delivery mechanism is unchanged.

## Key Decisions

**D-1: Integration via existing mechanisms, not new infrastructure**
Common Context for phase-neutral recall entries (project conventions, failure modes). Phase preambles for phase-specific entries (TDD learnings in TDD phases, review patterns in review-adjacent phases). prepare-runbook.py handles the rest. No script changes.

**D-2: C-5 dissolved — orchestrator doesn't filter recall content**
Recall content is baked into step files and agent definitions at planning time (sonnet/opus cognitive work). The orchestrator (even haiku) doesn't touch recall content at execution time. FR-8 (mechanical filterability) is unnecessary for V1 — uniform injection via Common Context replaces per-step filtering. FR-3's "orchestrator filters per phase/step" changes to "planner selects per phase/step at planning time."

**D-3: Token budget for recall in Common Context**
Common Context recall section: ≤1.5K tokens (ungrounded — needs empirical calibration after first use). This content replicates across N task agents. The full recall artifact can be larger — reference for design/review consumers running at opus with 200K windows. Eviction: planner removes least-specific entries when budget exceeded.

**D-4: Artifact format — structured markdown**
Entries with: heading name, source path, relevance note, content excerpt. Readable by humans, parseable by any model tier. No complex tag system — the planner curates at planning time, not the orchestrator at execution time.

**D-5: Staleness accepted with optional refresh**
Artifact reflects corpus state at design time. For multi-session pipelines, the planner can optionally regenerate during `/runbook` Phase 0.5. No automatic staleness detection for V1.

**D-6: Conflict resolution at planning time**
The planner (sonnet/opus) resolves conflicting entries when writing Common Context. This is cognitive work at an appropriate model tier. No mechanical tiebreaker system.

**D-7: Progressive recall within design**
Recall is not a one-shot cache fill at A.1. Each discovery phase (exploration, user discussion) changes what's relevant. Re-evaluate the recall artifact at A.5 (post-exploration: codebase findings change which entries matter) and C.1 (post-discussion: approach commitment changes which implementation/testing entries are relevant). The artifact is progressively refined, not front-loaded.

**D-8: Positional effectiveness**
Common Context → agent system prompt → early-mid zone after baseline agent template. Phase preambles → step files → "## Phase Context" section before step body. Both are acceptable positions for conventions and failure modes. Step-specific content (recency position) still dominates for implementation details.

**D-9: Format matches runbook consumer tier**
Planner writes recall entries in constraint format (DO/DO NOT) for haiku/sonnet consumers or rationale format for opus consumers. Decision made once at planning time per runbook.

**D-10: Incremental adoption — Pass 2+3 first**
Pass 2 (runbook planning) + Pass 3 (execution injection via Common Context) deliver highest impact for lowest effort. Pass 1 (design artifact) and Pass 4 (review recall) can follow independently.

## Requirements Mapping

| Requirement | Resolution |
|---|---|
| FR-1: Design-stage recall | Design A.1 writes recall artifact |
| FR-2: Planning-stage recall | Runbook Phase 0.5 augments artifact, includes in Common Context |
| FR-3: Execution-stage injection | Common Context → prepare-runbook.py → agent definitions + step files (no orchestrator filtering) |
| FR-4: Review-stage recall | Checkpoint template + deliverable-review scope include review recall |
| FR-5: Persistent artifacts | `plans/<job>/recall-artifact.md` — file-based, auditable |
| FR-6: Reference forwarding | Each pass reads and augments the existing artifact |
| FR-7: Named enumeration | Entries identified by heading name + source path |
| FR-8: Mechanical filterability | Dissolved by D-2 — uniform injection replaces runtime filtering |
| FR-9: Model-tier formatting | Planner formats per runbook consumer tier (D-9) |
| FR-10: Content delivery guarantee | Content directly in agent system prompt and step files |
| NFR-1: Token economy | D-3 budget, multiplicative cost accounted |
| NFR-2: Incremental adoption | D-10 prioritization |
| NFR-3: Composability | Extends existing Common Context, not parallel channel |
| C-1: Prescriptive retrieval | Fixed pipeline points (A.1, Phase 0.5, checkpoint template, deliverable-review) |
| C-2: Existing corpus format | No corpus changes |
| C-3: Pipeline integration | Modifies existing skill procedures |
| C-4: Fire-and-forget | Content complete at injection time |
| C-5: Haiku orchestrator | Dissolved — orchestrator doesn't interact with recall content |

## Open Questions Resolved

- Q-1 (growth control): ≤1.5K token budget for Common Context section; planner curates
- Q-2 (conflict resolution): Planner resolves at planning time (cognitive, not mechanical)
- Q-3 (staleness): Accept; optional regeneration at `/runbook` Phase 0.5
- Q-4 (mid-design recall): Yes — re-evaluate at A.5 and C.1 (FR-11: new information changes what's relevant)
- Q-5 (positional effectiveness): Early-mid zone via Common Context → agent system prompt

## Scope

**IN:**
- Recall artifact format specification
- Design skill: A.1 produces recall artifact
- Runbook skill: Phase 0.5 reads/augments artifact, Common Context template gets recall section
- Orchestrate skill: checkpoint template gets review recall section
- Deliverable-review skill: Layer 2 scope includes recall context

**OUT:**
- prepare-runbook.py changes (existing mechanisms suffice)
- New agent definitions or types
- Vector DB, RL, UserPromptSubmit hook, cache optimization
- Corpus format changes
- Per-step filtering at orchestration time (dissolved by D-2)
- Automatic staleness detection
- Token budget calibration (empirical measurement deferred)

## Affected Files

All prose edits to architectural artifacts — opus execution model.

- `agent-core/skills/design/SKILL.md` — A.1 checkpoint addition: recall artifact generation
- `agent-core/skills/runbook/SKILL.md` — Phase 0.5 addition: artifact read/augment; Common Context template: recall section
- `agent-core/skills/orchestrate/SKILL.md` — Checkpoint template: review recall field
- `agent-core/skills/deliverable-review/SKILL.md` — Layer 2 scope: review recall context
