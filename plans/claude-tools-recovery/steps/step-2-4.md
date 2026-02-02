# Cycle 2.4

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.4: Test account api writes provider selection

**Objective**: Verify account api command writes selected provider and generates credentials
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py::test_account_api already verifies provider file, strengthen to test claude-env content

**Expected failure:**
```
AssertionError: assert "OPENROUTER_API_KEY" in claude_env_content
(may write empty or wrong provider credentials)
```

**Why it fails:** CLI may not generate provider-specific claude-env

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_api -v
```
- Edit test to read claude-env file, assert OPENROUTER_API_KEY present
- Mock keystore get_openrouter_api_key to return "test-openrouter-key"
- Test should FAIL if wrong provider or empty file

---

**GREEN Phase:**

**Implementation:** Update account api to create provider-specific claude-env

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: In api(), create provider based on --provider argument (factory function), generate claude-env with provider.claude_env_vars()
- File: tests/test_cli_account.py
  Action: Test with --provider=openrouter, mock keystore, assert OPENROUTER_API_KEY in claude-env

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_api -v
```
- Test passes with correct provider credentials

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI account tests pass

---

**Expected Outcome**: account api test verifies correct provider credentials written
**Error Conditions**: Wrong provider used → check provider factory logic
**Validation**: Test verifies provider-specific env vars
**Success Criteria**: account api generates claude-env with selected provider
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-4-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review CLI test quality, fixture patterns, mock locations. Commit fixes.
3. Functional review: Verify CLI commands use real filesystem reads (get_account_state), not hardcoded stubs. Check claude-env file generation uses providers. If stubs remain, STOP and report.

---
