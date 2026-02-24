# Cycle 2.2

**Plan**: `plans/orchestrate-evolution/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

**Scope:** New structured orchestrator plan format with metadata fields. verify-step.sh creation with E2E tests.

**Files:** `agent-core/bin/prepare-runbook.py`, `agent-core/skills/orchestrate/scripts/verify-step.sh` (create), `tests/test_prepare_runbook_orchestrator.py` (extend), `tests/test_verify_step.py` (create)

**Depends on:** Phase 1 (agent naming used in orchestrator plan header)

**Key constraints:**
- Orchestrator plan format: structured metadata, not prose instructions
- Step list: `- filename | Phase N | model | max_turns [| PHASE_BOUNDARY]`
- Header fields: `**Agent:**`, `**Corrector Agent:**`, `**Type:**`
- INLINE marker for inline phases
- Phase summaries with IN/OUT scope
- verify-step.sh: deterministic script (non-cognitive → script, per recall "When Choosing Script vs Agent Judgment")
- Shell script testing: real git repos in tmp_path (per recall "When Preferring E2E Over Mocked Subprocess")

---

---

## Cycle 2.2: PHASE_BOUNDARY markers and phase summaries

**RED Phase:**

**Test:** `test_orchestrator_plan_boundaries_and_summaries`
**File:** `tests/test_prepare_runbook_orchestrator.py`
**Prerequisite:** Read current `generate_default_orchestrator` — understand how `is_phase_boundary` is currently detected (line 1160) and how phase boundary markers currently work

**Assertions:**
- Last step entry of each phase has `| PHASE_BOUNDARY` appended
- Inline phases appear as `- INLINE | Phase N | —` (no filename, no model/max_turns)
- Plan contains `## Phase Summaries` section after Steps section
- Each phase has a `### Phase N: title` subsection with `- IN:` and `- OUT:` bullet items
- Phase summary count matches number of distinct phases in the step list

**Expected failure:** AssertionError — new structured format from Cycle 2.1 doesn't yet have PHASE_BOUNDARY markers or Phase Summaries section

**Why it fails:** Cycle 2.1 produces step list but no boundary markers or summaries

**Verify RED:** `pytest tests/test_prepare_runbook_orchestrator.py::test_orchestrator_plan_boundaries_and_summaries -v`

**GREEN Phase:**

**Implementation:** Add PHASE_BOUNDARY markers and Phase Summaries section to orchestrator plan

**Behavior:**
- Detect phase boundaries: last item before phase number changes (same logic as current `is_phase_boundary`)
- Append `| PHASE_BOUNDARY` to those entries
- Format inline phases: `- INLINE | Phase N | —`
- Generate `## Phase Summaries` section from phase descriptions
- Each phase summary has placeholder IN/OUT that will be populated from runbook phase descriptions

**Approach:** Phase boundary detection already exists in current code. Add PHASE_BOUNDARY suffix to pipe-delimited entries. For summaries, extract from phase preambles (passed via `phase_preambles` parameter) or generate placeholder if not available.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add PHASE_BOUNDARY suffix and Phase Summaries section to `generate_default_orchestrator`
  Location hint: in the step list generation loop and after the loop

**Verify GREEN:** `just check && just test`

---
