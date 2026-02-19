# Step 1.2

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 1

---

## Step 1.2: Extend error-classification.md — taxonomy + behavioral dimensions

**Objective**: Extend the 4-category taxonomy to 5 categories with fault/failure vocabulary (Avižienis), add retryable/non-retryable dimension, and add tier-aware classification guidance.
**Script Evaluation**: Prose (25-100 lines — substantial additions to 131-line fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-classification.md` — understand existing 4-category taxonomy table, decision tree (4 steps), and common patterns sections.

**Implementation — Part A (taxonomy, apply first)**:

1. Add fault/failure vocabulary to the taxonomy section header or as a subsection immediately after the taxonomy table:
   - Categories 1 (Prerequisite Failure) and 4 (Ambiguity Error) are **faults** (root causes: environment fault, specification fault respectively). Response: prevention-oriented (validate, clarify before executing).
   - Categories 2 (Execution Error) and 3 (Unexpected Result) are **failures** (observable deviations: service deviation, output deviation respectively). Response: tolerance-oriented (retry if retryable, escalate, compensate).
   - Grounding: Avižienis Fault-Error-Failure chain (FEF).

2. Add Category 5 (Inter-agent misalignment) — new row in taxonomy table:
   - Definition: Agent deviates from specification, ignores provided context, reasoning-action mismatch, premature termination, incomplete verification
   - Examples: vet confabulation (invented test claim), agent skipping steps, over-escalation
   - Trigger Conditions: Agent output contradicts specification; review pipeline catches deviation; agent terminates without meeting step criteria
   - Escalation Path: Sonnet verification → if confirmed misalignment → plan correction or re-execution with stronger constraints
   - Add step 5 to the decision tree: "5. Does agent output contradict specification, ignore provided context, or skip required verification? YES → INTER_AGENT_MISALIGNMENT (escalate to sonnet for verification)"
   - Add indicators to "Common Patterns" section: agent returns success without evidence of verification, output missing required sections specified in step, agent ignores explicit constraints in step definition

**Implementation — Part B (behavioral dimensions, apply after Part A)**:

3. Add retryable/non-retryable classification — add column to taxonomy table OR add subsection "Retryable vs Non-Retryable" after the table:
   - Prerequisite Failure: non-retryable (missing resource is deterministic — won't fix itself)
   - Execution Error: retryable if transient (env issue, write conflict, timeout); non-retryable if deterministic (test logic error, build configuration wrong)
   - Unexpected Result: non-retryable (output deviation persists without fix)
   - Ambiguity Error: non-retryable (requires plan update, not retry)
   - Inter-agent misalignment: non-retryable (re-running same agent with same context reproduces deviation)

4. Add tier-aware classification note at the TOP of the "Error Classification Logic for Agents" decision tree section:
   - Sonnet/opus execution agents: self-classify using decision tree below — report BOTH category AND retryable/non-retryable determination with rationale
   - Haiku execution agents: report raw error + observed facts only; orchestrator applies decision tree for classification
   - Rationale: classification requires judgment that haiku cannot reliably provide; orchestrator already knows agent model tier

**Expected Outcome**:
- Taxonomy table has 5 rows (Categories 1-5)
- Fault/failure labels visible on categories 1-4
- Each category has retryable/non-retryable classification
- Decision tree has 5 steps
- Tier-aware note at decision tree top

**Error Conditions**:
- If table structure becomes unclear with added column, use separate subsection instead
- Part B must be applied after Part A (category 5 must exist before it can be classified as retryable/non-retryable)

**Validation**:
- `grep -c "INTER_AGENT_MISALIGNMENT\|Category 5\|Inter-agent" agent-core/fragments/error-classification.md` returns > 0
- Decision tree section has 5 numbered steps
- "tier-aware" or "haiku" or "self-classify" language present in decision tree header
- Fault/failure labels present for categories 1-4

---

*(Independent of Phase 3 — run in parallel after Phase 1 completes)*
