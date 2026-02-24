# Cycle 3.2

**Plan**: `plans/orchestrate-evolution/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Phase Context

**Scope:** Extend prepare-runbook.py for ping-pong TDD: 4 agent types, step file splitting, orchestrator plan TDD markers, verify-red.sh.

**Files:** `agent-core/bin/prepare-runbook.py`, `agent-core/skills/orchestrate/scripts/verify-red.sh` (create), `tests/test_prepare_runbook_tdd_agents.py` (create), `tests/test_verify_red.py` (create)

**Depends on:** Phase 1 (agent caching model — `generate_task_agent` function, `read_baseline_agent`), Phase 2 (orchestrator plan format — pipe-delimited step list, `generate_default_orchestrator`)

**Key constraints:**
- TDD agents extend Phase 1's per-role model: 4 roles instead of 1 task + 1 corrector
- Agent naming: `<plan>-tester.md`, `<plan>-implementer.md`, `<plan>-test-corrector.md`, `<plan>-impl-corrector.md`
- Baseline selection: test-driver.md for tester/implementer, corrector.md for test-corrector/impl-corrector
- All 4 agents embed same Plan Context (design + outline) as task agent from Phase 1
- Generated only for TDD-typed runbooks (pure TDD or TDD phases in mixed)
- Step file splitting: each TDD cycle → `step-N-test.md` (RED) + `step-N-impl.md` (GREEN)
- Orchestrator plan TDD markers: TEST/IMPLEMENT role on step entries
- Tests in NEW file `tests/test_prepare_runbook_tdd_agents.py` — NOT in `test_prepare_runbook_agents.py` (354 lines, near 400-line threshold)
- verify-red.sh: deterministic script (non-cognitive → script, per recall "When Choosing Script vs Agent Judgment")
- Shell script testing: real git repos in tmp_path (per recall "When Preferring E2E Over Mocked Subprocess")

---

---

## Cycle 3.2: Step file splitting (test/impl per TDD cycle)

**RED Phase:**

**Test:** `test_tdd_cycle_splits_into_test_and_impl_files`
**File:** `tests/test_prepare_runbook_tdd_agents.py`
**Prerequisite:** Read `agent-core/bin/prepare-runbook.py` lines 1377-1390 (current TDD cycle step file generation) — understand how cycles currently produce single `step-N-M.md` files. Read lines 1031-1062 (`generate_cycle_file`) — understand current cycle file content structure with RED/GREEN sections.

**Assertions:**
- For a TDD runbook with cycle 1.1: two step files created, not one
- Files named `step-1-1-test.md` and `step-1-1-impl.md`
- Test file (`step-1-1-test.md`) contains RED phase content (test function name, assertions, expected failure)
- Test file does NOT contain GREEN phase content (implementation hints, verify GREEN command)
- Impl file (`step-1-1-impl.md`) contains GREEN phase content (implementation description, behavior, changes)
- Impl file does NOT contain RED phase content (test assertions, expected failure)
- Both files have metadata headers (runbook source, phase number, execution model)
- For a general runbook step: single `step-N-M.md` file (no splitting — existing behavior preserved)

**Expected failure:** AssertionError — current code generates single `step-N-M.md` per cycle

**Why it fails:** `generate_cycle_file` produces one file containing both RED and GREEN sections; no splitting logic exists

**Verify RED:** `pytest tests/test_prepare_runbook_tdd_agents.py::test_tdd_cycle_splits_into_test_and_impl_files -v`

**GREEN Phase:**

**Implementation:** Split TDD cycle step generation into test and impl files

**Behavior:**
- For TDD cycles: generate two files instead of one
- Test file contains: metadata header + RED phase content (extracted from cycle content)
- Impl file contains: metadata header + GREEN phase content (extracted from cycle content)
- RED/GREEN split point: content before "**GREEN Phase:**" marker → test file; content after → impl file
- Both files get same metadata headers (runbook source, phase, model)
- General steps unchanged (no splitting)

**Approach:** Modify the TDD cycle step generation loop in `validate_and_create` (lines 1377-1390). Add a `split_cycle_content` helper that separates RED from GREEN using the `**GREEN Phase:**` heading as delimiter. Generate two files per cycle using `generate_cycle_file` (or a variant) for each half.

**Changes:**
- File: `agent-core/bin/prepare-runbook.py`
  Action: Add `split_cycle_content` function to separate RED and GREEN sections
  Location hint: near `generate_cycle_file` (line 1020)

- File: `agent-core/bin/prepare-runbook.py`
  Action: Modify TDD cycle loop to generate two files per cycle
  Location hint: lines 1377-1390

**Verify GREEN:** `just check && just test`

---
