# Cycle 2.3

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

## Cycle 2.3: max_turns extraction from step metadata

**RED Phase:**

**Test:** `test_max_turns_extraction_and_propagation`
**File:** `tests/test_prepare_runbook_orchestrator.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` `extract_step_metadata` (line 878) — understand current metadata extraction for model and report_path

**Assertions:**
- `extract_step_metadata` returns `max_turns` key when `**Max Turns**: 25` present in content
- `extract_step_metadata` returns `max_turns: 30` (default) when no Max Turns field present
- Orchestrator plan step entries include max_turns value from metadata: `- step-1-1.md | Phase 1 | sonnet | 25`
- Default max_turns (30) appears in step entries when not specified in content

**Expected failure:** AssertionError — `extract_step_metadata` doesn't look for Max Turns field

**Why it fails:** Current metadata extraction only handles Execution Model and Report Path

**Verify RED:** `pytest tests/test_prepare_runbook_orchestrator.py::test_max_turns_extraction_and_propagation -v`

**GREEN Phase:**

**Implementation:** Add Max Turns extraction to `extract_step_metadata` and propagate to orchestrator plan

**Behavior:**
- Parse `**Max Turns**:\s*(\d+)` from step content (case-insensitive)
- Default to 30 when not specified
- Include max_turns in orchestrator plan step entries

**Approach:** Add regex to `extract_step_metadata` alongside existing model/report_path extraction. Pass extracted max_turns through to `generate_default_orchestrator` step list generation.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add max_turns regex extraction to `extract_step_metadata`
  Location hint: line 878, after report_path extraction

- File: `agent-core/bin/prepare-runbook.py`
  Action: Include max_turns in step list entries in `generate_default_orchestrator`
  Location hint: in the step list formatting loop

**Verify GREEN:** `just check && just test`

---
