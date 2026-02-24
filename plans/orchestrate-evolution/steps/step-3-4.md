# Cycle 3.4

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

## Cycle 3.4: verify-red.sh creation and testing

**RED Phase:**

**Test:** `test_verify_red_confirms_failing_test` and `test_verify_red_rejects_passing_test`
**File:** `tests/test_verify_red.py` (create)
**Prerequisite:** Read design section "Ping-Pong TDD Orchestration (D-5)" for RED gate contract. Confirm `agent-core/skills/orchestrate/scripts/` directory exists (created in Phase 2 alongside verify-step.sh); if absent, the directory must be created alongside the script.

**Assertions (failing test = RED confirmed):**
- Script at `agent-core/skills/orchestrate/scripts/verify-red.sh` exists and is executable
- Given a test file containing a test that FAILS (assert False): script exits 0
- stdout contains "RED" or "CONFIRMED"

**Assertions (passing test = RED rejected):**
- Given a test file containing a test that PASSES (assert True): script exits 1
- stdout contains "FAIL" or "REJECTED" or indicates test unexpectedly passed

**Assertions (missing test):**
- Given a nonexistent test file path: script exits 1
- stdout contains error indication

**Test setup:** Create real Python test files in `tmp_path`:
- Failing test: `def test_example(): assert False`
- Passing test: `def test_example(): assert True`
- Run `verify-red.sh <test_file>` via subprocess in each case

**Expected failure:** FileNotFoundError or similar — script doesn't exist yet

**Why it fails:** `agent-core/skills/orchestrate/scripts/verify-red.sh` hasn't been created

**Verify RED:** `pytest tests/test_verify_red.py -v`

**GREEN Phase:**

**Implementation:** Create verify-red.sh script

**Behavior:**
- Accept test file path as argument
- Run `pytest <test_file> --no-header -q`
- If pytest exits non-zero (test fails) → script exits 0 with "RED CONFIRMED" on stdout
- If pytest exits zero (test passes) → script exits 1 with "RED REJECTED: test passed unexpectedly" on stdout
- If test file doesn't exist → script exits 1 with error message
- Validate argument count (exactly 1 argument required)

**Approach:** Write bash script using token-efficient pattern (`exec 2>&1; set -xeuo pipefail`). Validate input, run pytest, invert exit code logic.

**Changes:**
- File: `agent-core/skills/orchestrate/scripts/verify-red.sh` (create)
  Action: Create RED gate verification script per design contract
  Location hint: new file

**Verify GREEN:** `just check && just test`
