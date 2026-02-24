# Cycle 2.4

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

## Cycle 2.4: verify-step.sh creation and testing

**RED Phase:**

**Test:** `test_verify_step_clean_state` and `test_verify_step_dirty_states`
**File:** `tests/test_verify_step.py` (create)
**Prerequisite:** Read `agent-core/skills/orchestrate/SKILL.md` — confirm the `scripts/` subdirectory doesn't exist yet and will be created. Read design section "Verification Script" for contract.

**Assertions (clean state test):**
- Script at `agent-core/skills/orchestrate/scripts/verify-step.sh` exists and is executable
- In a clean git repo (all committed, no submodules out of sync): script exits 0
- stdout contains "CLEAN"

**Assertions (dirty state tests — parametrized):**
- Uncommitted changes (modified tracked file): script exits 1, stdout contains "DIRTY"
- Untracked files: script exits 1, stdout contains "DIRTY"
- Submodule pointer drift (submodule at different commit than recorded): script exits 1, stdout contains "SUBMODULE"

**Test setup:** Create real git repos in `tmp_path` using `git init`, `git add`, `git commit`. For submodule test: create two repos, add one as submodule, advance submodule HEAD without updating parent.

**Expected failure:** FileNotFoundError or similar — script doesn't exist yet

**Why it fails:** `agent-core/skills/orchestrate/scripts/verify-step.sh` hasn't been created

**Verify RED:** `pytest tests/test_verify_step.py -v`

**GREEN Phase:**

**Implementation:** Create verify-step.sh script

**Behavior:**
- Check `git status --porcelain` — any output means dirty tree
- Check `git submodule status` — lines starting with `+` mean pointer drift
- Run `just precommit` — non-zero exit means validation failure
- Exit 0 with "CLEAN" on stdout if all pass
- Exit 1 with diagnostic details on stdout if any fail

**Approach:** Write bash script using token-efficient pattern (`exec 2>&1; set -xeuo pipefail`). Three sequential checks, each with early exit on failure.

**Changes:**
- File: `agent-core/skills/orchestrate/scripts/verify-step.sh` (create)
  Action: Create verification script per design contract
  Location hint: new file

**Note on precommit test:** The `just precommit` check is hard to test in isolation (requires project tooling in tmp_path). The E2E tests cover git-clean and submodule checks. Precommit validation is tested implicitly through the existing test suite's precommit runs. If needed, mock `just precommit` as a simple script in the test fixture.

**Verify GREEN:** `just check && just test`


### Phase 3: TDD agent generation (type: tdd, model: sonnet)

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
