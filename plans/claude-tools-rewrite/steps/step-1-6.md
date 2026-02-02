# Cycle 1.6

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 1.6: AccountState validation - LiteLLM requires proxy

**Objective**: Detect inconsistency when provider=litellm but proxy not running
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** validate_consistency() returns issue when LiteLLM provider without proxy

**Expected failure:**
```
AssertionError: assert [] == ['LiteLLM provider requires proxy to be running']
```

**Why it fails:** LiteLLM provider validation not implemented

**Verify RED:** `pytest tests/test_account_state.py::test_validate_litellm_requires_proxy -xvs`
- Must fail with assertion mismatch
- If passes, STOP - validation may already exist

---

**GREEN Phase:**

**Implementation:** Add LiteLLM proxy validation check

**Changes:**
- File: src/claudeutils/account/state.py
  Action: In validate_consistency(), add check: if provider == "litellm" and not litellm_proxy_running, append issue
- File: tests/test_account_state.py
  Action: Test LiteLLM provider without proxy returns specific issue

**Verify GREEN:** `pytest tests/test_account_state.py::test_validate_litellm_requires_proxy -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-1-6-notes.md

---
