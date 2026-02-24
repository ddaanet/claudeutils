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
