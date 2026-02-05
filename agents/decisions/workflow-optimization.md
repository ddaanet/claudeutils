# Workflow Optimization Patterns

Patterns for efficient workflow execution, delegation, and resource usage.

## Handoff Workflow

### Handoff Tail-Call Pattern

**Handoff tail-call:**

**Decision Date:** 2026-02-01

**Decision:** All tiers (1/2/3) must end with `/handoff --commit`, never bare `/commit`.

**Anti-pattern:** Tier 1/2 skip handoff because "no session restart needed"

**Correct pattern:** Always tail-call `/handoff --commit` — handoff captures session context and learnings regardless of tier

**Rationale:** Handoff is about context preservation, not just session restart. Even direct implementations produce learnings and update pending task state.

**Impact:** Consistent workflow termination across all tier levels.

### Handoff Commit Assumption

**Handoff commit assumption:**

**Decision Date:** 2026-02-01

**Decision:** session.md reflects post-commit state when `--commit` flag is used.

**Anti-pattern:** Writing "Ready to commit" in Status or "pending commit" in footer when `--commit` flag is active

**Correct pattern:** Write status reflecting post-commit state — the tail-call makes commit atomic with handoff

**Rationale:** Next session reads session.md post-commit. Stale commit-pending language causes agents to re-attempt already-completed commits. The rule against commit tasks in Pending/Next Steps must extend to ALL sections.

**Impact:** Prevents duplicate commit attempts in subsequent sessions.

## Workflow Efficiency

### Delegation with Context

**Delegation with context:**

**Decision Date:** 2026-02-01

**Decision:** Don't delegate when context is already loaded.

**Anti-pattern:** Reading files, gathering context, then delegating to another agent (which re-reads everything)

**Correct pattern:** If you already have files in context, execute directly — delegation adds re-reading overhead

**Rationale:** Token economy. Agent overhead (context setup + re-reading) exceeds cost of continuing in current model.

**Corollary:** Delegate when task requires *new* exploration you haven't done yet.

**Impact:** Reduces token waste from redundant context loading.

### Routing Layer Efficiency

**Single-layer complexity:**

**Decision Date:** 2026-02-01

**Decision:** Single-layer complexity assessment, not double assessment.

**Anti-pattern:** Entry point skill assesses complexity, then routes to planning skill which re-assesses complexity (tier assessment)

**Correct pattern:** Single entry point with triage that routes directly to the appropriate depth — no intermediate routing layer

**Rationale:** Each assessment reads files, analyzes scope, produces output. Two assessments for the same purpose is pure waste.

**Example:** Oneshot assessed simple/moderate/complex, then /plan-adhoc re-assessed Tier 1/2/3 — same function, different labels.

**Impact:** Eliminates redundant analysis overhead.

### Vet Agent Context Usage

**Decision Date:** 2026-02-01

**Decision:** Leverage vet agent context for fixes instead of launching new agents.

**Anti-pattern:** When removal agent makes mistakes and vet catches them, launching a new fix agent (which re-reads everything)

**Correct pattern:** If vet agent has context of what's wrong, leverage it. If caller also has context (from reading vet report), apply fixes directly.

**Rationale:** Tier 1/2 pattern — caller reads report, applies fixes with full context. No need for another agent round-trip.

**Impact:** Faster fix cycles without redundant context loading.

## Design and Planning Patterns

### Outline-First Design Workflow

**Outline-first design workflow:**

**Decision Date:** 2026-02-04

**Decision:** Produce freeform outline first, iterate with user via incremental deltas, then generate full design after validation.

**Anti-pattern:** Producing full design.md in a single pass, then discovering user wanted different approach.

**Escape hatch:** If user already specified approach/decisions/scope, compress outline+discussion into single validation.

**Rationale:** Early validation prevents wasted effort on wrong direction. Iterative refinement captures user intent accurately.

**Impact:** Higher quality designs aligned with user expectations, less re-work.

### Model Selection for Design Guidance

**Model selection design guidance:**

**Decision Date:** 2026-02-04

**Decision:** Haiku for explicit edits with exact text provided, sonnet for generating markdown from design guidance.

**Anti-pattern:** Assigning haiku to tasks requiring interpretation of design intent ("add escape hatch if...").

**Rationale:** Haiku executes what's specified, sonnet interprets intent and produces explicit text.

**Trade-off:** Sonnet costs more but prevents re-work from under-specified haiku tasks.

**Impact:** Appropriate model selection reduces execution errors and re-work.

### Design Review Uses Opus

**Decision Date:** 2026-02-04 (superseded by design-vet-agent)

**Original Decision:** Use `Task(subagent_type="general-purpose", model="opus")` for design review.

**Current Decision:** Use `Task(subagent_type="design-vet-agent")` — dedicated agent with opus model.

**Anti-pattern:** Using vet-agent for design review (vet is implementation-focused — code quality, patterns, correctness).

**Rationale:** General-purpose agent strengths (architecture analysis, multi-file exploration, complex investigation) align with design review needs.

**Benefits:** Artifact-return pattern (detailed report to file), specialized review protocol, consistent with vet-agent/vet-fix-agent structure.

**Impact:** Three-agent vet system: vet-agent (code, sonnet), vet-fix-agent (code + fixes, sonnet), design-vet-agent (architecture, opus).

### Vet Catches Structure Misalignments

**Vet catches structure misalignments:**

**Decision Date:** 2026-02-04

**Decision:** Vet agent validates file paths AND structural assumptions via Glob/Read during review.

**Anti-pattern:** Writing runbook steps based on assumed structure ("lines ~47-78") without reading actual files.

**Example:** plan-adhoc Point 0.5 actually at line 95, plan-tdd uses "Actions:" not "Steps:".

**Impact:** Prevented execution failures from incorrect section identification. Vet review with path validation is a blocker-prevention mechanism, not just quality check.

**Critical:** Always validate structural assumptions during vet reviews.

## Orchestration Patterns

### Agent-Creator Reviews in Orchestration

**Agent-creator reviews in orchestration:**

**Decision Date:** 2026-02-04

**Decision:** Task agent creates file from spec, then `plugin-dev:agent-creator` reviews and fixes (YAML syntax, description quality, prompt structure).

**Anti-pattern:** Only using agent-creator for interactive agent creation from scratch.

**Mechanism:** Custom `## Orchestrator Instructions` in runbook specifies per-step subagent_type override. prepare-runbook.py already extracts custom orchestrator sections.

**Confirmed empirically:** agent-creator is cooperative in review mode, has Write access.

**Impact:** Higher quality agent files through specialized review.

### Template Commit Contradiction

**Template commit contradiction:**

**Decision Date:** 2026-02-04

**Problem:** quiet-task.md says "NEVER commit unless task explicitly requires" while prepare-runbook.py appends "Commit all changes before reporting success".

**Root cause:** Baseline template designed for ad-hoc delegation (no auto-commit), but orchestrated execution requires clean tree after every step.

**Fix:** Qualified quiet-task.md line 112 to add "or a clean-tree requirement is specified".

**Broader lesson:** Appended context at bottom of agent file has weak positional authority vs bolded NEVER in core constraints section — contradictions resolve in favor of the structurally prominent directive.

**Impact:** Resolved directive conflict, clarified when commits are required.

### Orchestrator Model Mismatch

**Orchestrator model mismatch:**

**Decision Date:** 2026-02-04

**Problem:** Using orchestrator's own model (haiku) for all step agent Task invocations.

**Root cause:** Orchestrate skill said "model: [from orchestrator metadata, typically haiku]" — ambiguous, conflated orchestrator model with step execution model.

**Correct pattern:** Read each step file's "Execution Model" field and pass that to Task tool's model parameter.

**Impact:** Haiku step agents skip complex behaviors (vet delegation, commit sequences) that sonnet would follow.

**Fix:** Clarified orchestrate skill Section 3.1 — model comes from step file, not orchestrator default.

## Testing and TDD Patterns

### Happy Path First TDD

**Happy path first TDD:**

**Decision Date:** 2026-02-04

**Decision:** Start with simplest happy path that exercises real behavior; test edge cases only when they need special handling.

**Anti-pattern:** Testing empty/degenerate cases first (cycle 1: empty list returns []; stub never replaced).

**Rationale:** Empty-first ordering produces stubs that satisfy tests but never get replaced with real implementations.

**Impact:** Test-driven implementations that exercise actual behavior from first cycle.

## Runbook Artifacts

### Runbook Outline Format

**Decision Date:** 2026-02-05

**Decision:** Use structured outline format for runbook planning with requirements mapping and phase organization.

**Format:**

```markdown
# Runbook Outline: <name>

**Design:** plans/<job>/design.md
**Type:** tdd | general

.## Requirements Mapping

| Requirement | Phase | Steps/Cycles | Notes |
|-------------|-------|--------------|-------|
| FR-1 | 1 | 1.1, 1.2 | Core functionality |
| FR-2 | 2 | 2.1-2.3 | Error handling |

.## Phase Structure

.### Phase 1: <name>
**Objective:** <what this phase accomplishes>
**Complexity:** Low/Medium/High
**Steps:**
- 1.1: <title>
- 1.2: <title>

.### Phase 2: <name>
**Objective:** <what this phase accomplishes>
**Complexity:** Low/Medium/High
**Steps:**
- 2.1: <title>
- 2.2: <title>

.## Key Decisions Reference
- Decision 1: <from design> → affects Phase 1
- Decision 2: <from design> → affects Phase 2
```

**Purpose:**
- Requirements mapping table ensures all design requirements are implemented
- Phase structure provides high-level roadmap before detailed expansion
- Enables early review and validation (outline feedback before full runbook)
- Supports phase-by-phase expansion with incremental reviews

**Usage:**
- Referenced in `/plan-adhoc` Point 0.75
- Referenced in `/plan-tdd` Phase 1.5

**Impact:** Provides holistic view for cross-phase coherence while enabling incremental development with earlier feedback.

