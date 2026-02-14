# Workflow RCA Fixes — Design

## Problem Statement

Five root cause analyses identified 18 process gaps in the agent workflow pipeline. All gaps are prose defects in skill definitions, agent definitions, decision documents, and fragments. No code changes required.

**Source:** `plans/workflow-rca-fixes/requirements.md` (18 FRs, 4 constraints)

## Requirements

**Functional:**
- FR-1: Restructure runbook-review.md as type-agnostic — Phase 2
- FR-2: Expand review-plan Section 11 with general detection — Phase 2
- FR-3: Add LLM failure mode gate to Phase 0.95 fast-path — Phase 2
- FR-4: Add general-step reference material — Phase 5
- FR-5: Outline growth validation gate — Phase 4
- FR-6: Delete Phase 1.4 (file size awareness) — Phase 6
- FR-7: Vet status taxonomy (4-status) — Phase 3
- FR-8: Investigation-before-escalation protocol — Phase 3
- FR-9: UNFIXABLE validation in detection protocol — Phase 3
- FR-10: Orchestrate template enforcement — Phase 3
- FR-11: Semantic propagation checklist — Phase 4
- FR-12: Agent convention injection via skills — Phase 1
- FR-13: Memory index injection for sub-agents — Phase 1
- FR-14: Design skill Phase C density checkpoint — Phase 5
- FR-15: Design-time repetition helper prescription — Phase 5
- FR-16: Deliverable review as workflow step — Phase 5
- FR-17: Execution-to-planning feedback requirement — Phase 6
- FR-18: Review-fix integration rule — Phase 3

**Constraints:**
- C-1: All prose edits. No code changes.
- C-2: Native `skills:` mechanism for agent composition.
- C-3: Fragment-wrapping skills must pass skill-reviewer.
- C-4: FR-17 documents requirement only; implementation deferred to `wt/error-handling`.

**Out of scope:** Code changes, error-handling framework implementation, upstream plugin-dev docs, formal workflow verification.

## Architecture

### Reflexive Bootstrapping

Phase ordering follows the tool-usage dependency graph. Each agent improvement is applied before that agent is used in subsequent phases. This collapses design→plan→execute into design→apply for prose-edit work.

**Dependency chain:**
1. Agent composition (Phase 1) → all downstream agents get conventions
2. Runbook review (Phase 2) → plan-reviewer reviews with updated logic
3. Vet overhaul (Phase 3) → vet-fix-agent validates with new taxonomy
4. Outline review (Phase 4) → outline-review-agent validates with growth gates
5. Design + runbook skills (Phase 5) → design/runbook skills updated
6. Cleanup + feedback (Phase 6) → final deletions and documentation

### Three-Layer Validation

Each artifact edit passes through:
1. **Domain-specific reviewer with autofix** — skill-reviewer for skills, agent-creator (plugin-dev) for agents, vet-fix-agent for decisions/fragments
2. **Optional interactive opus diagnostic** — session stops primed with methodology + prompts, user switches to opus. Enabled for Phases 1-4 (self-referential improvements), skipped for Phases 5-6 (content edits). NOT delegated — opus needs full conversation context.
3. **Restart and proceed** — agent/fragment frontmatter changes require restart before next phase

**Research grounding:** MAR (Multi-Agent Reflexion) shows single-LLM self-reflection exhibits "degeneration of thought." Separating mechanical review (sonnet) from analytical critique (opus, interactive) avoids this. Flow-of-Action shows SOP-constrained RCA reduces hallucinations.

### Convention Injection via Skills

**project-conventions skill** (~400 tokens): Bundles deslop + token-economy + tmp-directory. CC sub-agents receive no prose quality rules — gap analysis confirmed zero coverage for these three areas.

**error-handling skill** (~100 tokens): Separate for bash-heavy agents only. CC sub-agents get no error suppression guidance.

**memory-index skill**: Wraps `agents/memory-index.md` with transport prolog. Sub-agents invoke `agent-core/bin/when-resolve.py when "<trigger>"` via Bash (not Skill tool).

**Rationale:** Anthropic context engineering recommends focused task context over comprehensive information. ACE framework shows 10.6% gain from strategic knowledge injection. These skills inject exactly what sub-agents lack.

### Vet Status Taxonomy

Replace binary FIXED/UNFIXABLE with four statuses:

| Status | Meaning | Blocks? |
|--------|---------|---------|
| FIXED | Applied | No |
| DEFERRED | Real issue, explicitly out of scope | No |
| OUT-OF-SCOPE | Not relevant to current review | No |
| UNFIXABLE | Technical blocker requiring user decision | **Yes** |

UNFIXABLE requires subcategory (U-REQ, U-ARCH, U-DESIGN) and investigation summary. Investigation-before-escalation protocol gates UNFIXABLE classification behind mandatory checklist: (1) check scope OUT, (2) check design for deferral, (3) Glob/Grep for existing patterns.

**Grounding:** ODC research supports orthogonal classification — defect type × trigger prevents conflation. 3 of 7 UNFIXABLE labels across historical reports were organizational deferrals.

### Review-Fix Integration Rule (FR-18)

When review agent recommendations target an existing section (by heading match), merge into that section rather than appending parallel section. Applies to outline-review-agent, vet-fix-agent, plan-reviewer.

**Grounding:** Outline-review-agent Round 1 appended "## Expansion Guidance (from outline review)" when "## Expansion Guidance" already existed 60 lines above.

## Phase Specifications

### Phase 1: Agent Composition (FR-12, FR-13)

**Prerequisites:** Load `plugin-dev:skill-development` and `plugin-dev:agent-development`. Read continuation passing section of orchestrate/SKILL.md and existing `user-invocable: false` skills (review-plan, plugin-dev-validation, handoff-haiku).

**Deliverables:**

| Artifact | Action | FR |
|----------|--------|-----|
| `agent-core/skills/project-conventions/SKILL.md` | Create: deslop + token-economy + tmp-directory | FR-12 |
| `agent-core/skills/error-handling/SKILL.md` | Create: error suppression rules for bash-heavy agents | FR-12 |
| `agent-core/skills/memory-index/SKILL.md` | Create: memory-index wrapper with Bash transport prolog | FR-13 |
| `agent-core/agents/vet-fix-agent.md` | Add `skills: [project-conventions, error-handling, memory-index]` | FR-12, FR-13 |
| `agent-core/agents/design-vet-agent.md` | Add `skills: [project-conventions]` | FR-12 |
| `agent-core/agents/outline-review-agent.md` | Add `skills: [project-conventions]` | FR-12 |
| `agent-core/agents/plan-reviewer.md` | Add `skills: [project-conventions]` (already has review-plan) | FR-12 |
| `agent-core/agents/refactor.md` | Add `skills: [project-conventions, error-handling]` | FR-12 |

**Review:** skill-reviewer for each new SKILL.md, agent-creator for each modified agent definition.
**Restart required:** Yes (agent frontmatter changes).
**Diagnostic review:** Yes (improving review tools).

### Phase 2: Runbook Review Overhaul (FR-1, FR-2, FR-3)

**Deliverables:**

| Artifact | Action | FR |
|----------|--------|-----|
| `agents/decisions/runbook-review.md` | Restructure 4 axes as type-agnostic with TDD/General bullets, add behavioral vacuity detection, add file growth as 5th axis, use "item (cycle or step)" | FR-1 |
| `agent-core/skills/review-plan/SKILL.md` | Expand Section 11.1-11.3 with `**General:**` detection bullets | FR-2 |
| `agent-core/skills/runbook/SKILL.md` | Add LLM failure mode gate to Phase 0.95 fast-path | FR-3 |

**FR-1 behavioral vacuity detection:** For each cycle pair (N, N+1) on same function, verify N+1's RED assertion would fail given N's GREEN. If not, cycles are behaviorally vacuous. Heuristic: cycles > LOC/20 signals consolidation.

**FR-3 fast-path gate:** Before Phase 0.95 promotion, check vacuity, ordering, density, checkpoints inline. Fix before promotion.

**Review:** vet-fix-agent for runbook-review.md, skill-reviewer for SKILL.md edits.
**Restart required:** Yes (runbook-review.md loaded via CLAUDE.md @-ref).
**Diagnostic review:** Yes (improving review logic).

### Phase 3: Vet Agent Overhaul (FR-7, FR-8, FR-9, FR-10, FR-18)

**Deliverables:**

| Artifact | Action | FR |
|----------|--------|-----|
| `agent-core/agents/vet-fix-agent.md` | Add four-status taxonomy with criteria, examples, subcategory codes, Deferred Items report section | FR-7 |
| `agent-core/agents/vet-fix-agent.md` | Add investigation-before-escalation protocol: 4-gate checklist before UNFIXABLE | FR-8 |
| `agent-core/agents/vet-fix-agent.md` | Add review-fix integration rule: merge into existing sections by heading match | FR-18 |
| `agent-core/fragments/vet-requirement.md` | Add UNFIXABLE validation: subcategory code check, investigation summary check, scope OUT cross-reference, resume agent for reclassification if invalid | FR-9 |
| `agent-core/fragments/vet-requirement.md` | Strengthen execution context: structured IN/OUT scope fields, fail loudly if empty | FR-10 |
| `agent-core/skills/orchestrate/SKILL.md` | Add checkpoint delegation template enforcement guidance | FR-10 |

**Review:** agent-creator for vet-fix-agent.md, vet-fix-agent for vet-requirement.md (uses updated taxonomy).
**Restart required:** Yes (agent definition + fragment changes).
**Diagnostic review:** Yes (improving vet tools).

### Phase 4: Outline Review Agent (FR-5, FR-11)

**Deliverables:**

| Artifact | Action | FR |
|----------|--------|-----|
| `agent-core/agents/outline-review-agent.md` | Add outline growth validation: projected sizes vs 400-line threshold, split phases before 350 cumulative, flag >10 cycles same file without projection | FR-5 |
| `agent-core/agents/outline-review-agent.md` | Add semantic propagation checklist: grep-based classification of files as producer (rewrite) or consumer (update) when design introduces new terminology/types | FR-11 |

**Review:** agent-creator for outline-review-agent.md.
**Restart required:** Yes (agent definition changes).
**Diagnostic review:** Yes (improving outline review).

### Phase 5: Design + Runbook Skill Fixes (FR-4, FR-14, FR-15, FR-16)

**Deliverables:**

| Artifact | Action | FR |
|----------|--------|-----|
| `agent-core/skills/runbook/references/general-patterns.md` | Create: granularity criteria, prerequisite validation patterns, composable vs atomic | FR-4 |
| `agent-core/skills/runbook/references/anti-patterns.md` | Add general-step anti-patterns section | FR-4 |
| `agent-core/skills/runbook/references/examples.md` | Add complete general-step example | FR-4 |
| `agent-core/skills/design/SKILL.md` Phase C.1 | Add density checkpoint | FR-14 |
| `agent-core/skills/design/SKILL.md` Phase C.1 | Add repetition helper prescription | FR-15 |
| `agent-core/fragments/workflows-terminology.md` | Add deliverable review as post-orchestration workflow step | FR-16 |

**Review:** skill-reviewer for SKILL.md edits, vet-fix-agent for fragments.
**Restart required:** No (skill content resolves at spawn time; workflows-terminology.md loaded via @-ref requires restart only for structural changes).
**Diagnostic review:** No (content edits, not self-referential improvements).

### Phase 6: Cleanup + Feedback Requirement (FR-6, FR-17)

**Deliverables:**

| Artifact | Action | FR |
|----------|--------|-----|
| `agent-core/skills/runbook/SKILL.md` | Delete Phase 1.4 section (file size awareness) | FR-6 |
| `agents/decisions/orchestration-execution.md` | Document execution-to-planning feedback requirement: local recovery vs global replanning escalation, handoff to `wt/error-handling` | FR-17 |

**Review:** vet-fix-agent for orchestration-execution.md.
**Restart required:** No.
**Diagnostic review:** No.

## Key Design Decisions

1. **Reflexive bootstrapping order** — improve each tool before using it downstream. Dependency: composition → review logic → vet logic → outline review → content edits → cleanup.

2. **Convention injection via skills** — `skills:` frontmatter injects full SKILL.md at agent spawn. ~300-400 tokens per small skill, 2-3 per agent manageable (~5-10% overhead). Native mechanism, no build step.

3. **Four-status vet taxonomy** — FIXED/DEFERRED/OUT-OF-SCOPE/UNFIXABLE with investigation gates. Prevents over-escalation (3/7 historical UNFIXABLE were deferrals). ODC-grounded orthogonal classification.

4. **Review-fix integration** — merge into existing sections by heading match, not append. Prevents structural duplication from append-only fix application.

5. **Diagnostic review as interactive opus session** — NOT delegated to sub-agent. Opus needs full conversation context. Enabled for self-referential phases (1-4), skipped for content phases (5-6). MAR research shows single-model self-reflection degenerates.

6. **All general phase types** — no TDD phases. All changes are prose edits with no behavioral code changes.

7. **Execution model** — sonnet for edits, opus for diagnostic review (Phases 1-4 only).

8. **Behavioral vacuity detection** — cycle N+1 RED must fail given cycle N GREEN. Addresses both scaffolding vacuity (existence-only tests) and behavioral vacuity (entailed assertions).

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/runbook-review.md` — current review axes (Phase 2 target)
- `agents/decisions/pipeline-contracts.md` — T1-T6 defect classification, review gates
- `agents/decisions/orchestration-execution.md` — current orchestration patterns (Phase 3, 6 targets)
- `agent-core/agents/vet-fix-agent.md` — current vet agent (Phase 3 target)
- `agent-core/agents/outline-review-agent.md` — current outline review (Phase 4 target)
- `agent-core/skills/runbook/SKILL.md` — current runbook skill (Phase 2, 5, 6 targets)
- `agent-core/skills/design/SKILL.md` — current design skill (Phase 5 target)
- `agent-core/skills/review-plan/SKILL.md` — current review-plan skill (Phase 2 target)
- `agent-core/fragments/vet-requirement.md` — current vet requirement (Phase 3 target)
- `agent-core/fragments/workflows-terminology.md` — current workflow route (Phase 5 target)
- `plans/workflow-rca-fixes/reports/explore-target-files.md` — target file structures
- `plans/workflow-rca-fixes/reports/explore-skills-frontmatter.md` — skills injection mechanism
- `plans/workflow-rca-fixes/reports/explore-review-plan-skill.md` — Section 11 analysis
- `plans/workflow-rca-fixes/reports/explore-agent-knowledge-gaps.md` — CC system prompt gaps

**Skill-loading directives:**
- Load `plugin-dev:skill-development` before planning (skills creation in FR-12, FR-13)
- Load `plugin-dev:agent-development` before planning (agent modifications in all phases)

**Execution model directive:** Opus required for diagnostic review sessions (Phases 1-4).

## Diagnostic Review Methodology

### When Enabled

Phases 1-4 (improving review/vet/outline tools). Skip Phases 5-6 (content edits).

### Protocol

**Priming (before stopping session):** Output diagnostic primer containing:
- What was edited and why (FR reference, acceptance criteria)
- Reviewer report path and summary
- Methodology to apply (per artifact type, see below)
- Suggested prompts: "review using [methodology]", "RCA", "RCA deeper"
- Files to examine

**Methodology per artifact type:**
- Skills/agents: `plugin-dev:agent-development` and `plugin-dev:skill-development` patterns
- Runbook review artifacts: `agents/decisions/runbook-review.md` (four axes → five after FR-1)
- Vet/pipeline artifacts: `agents/decisions/pipeline-contracts.md` (T1-T6 defect classification)
- Design artifacts: pipeline-contracts + alignment verification (no formal methodology yet)

**Interactive RCA protocol (user drives in opus session):**
1. Surface pass — review changes and reviewer output, find missed issues
2. "RCA" — trace each finding to pipeline stage (T1-T6)
3. "RCA deeper" — trace systemic patterns to process root cause
4. Stop criterion — user judgment, no new findings or findings loop

**Feedback paths:**
- Current job → edit artifacts in opus session (reflexive bootstrapping)
- Workflow infrastructure → append to learnings.md
- Other jobs → append as pending tasks to session.md

### Methodology Gap

No formal `design-review-methodology.md` or `agent-review-methodology.md` exists. This job uses pipeline-contracts + plugin-dev patterns as interim. Creating formal methodology documents is follow-on work (diagnostic opus review methodology task).

## Next Steps

1. `/runbook plans/workflow-rca-fixes/design.md` — generate execution runbook
2. Load `plugin-dev:skill-development` and `plugin-dev:agent-development` before planning
3. Opus required for diagnostic review sessions during execution (Phases 1-4)
