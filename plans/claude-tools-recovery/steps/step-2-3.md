# Cycle 2.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.3: Test account plan generates claude-env with credentials

**Objective**: Verify account plan command generates claude-env file with provider credentials
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_cli_account.py::test_account_plan should verify claude-env file contains provider credentials

**Expected failure:**
```
AssertionError: assert "ANTHROPIC_API_KEY" in claude_env_content
(current writes empty file)
```

**Why it fails:** CLI writes empty claude-env file, doesn't call provider

**Verify RED:**
```bash
pytest tests/test_cli_account.py::test_account_plan -v
```
- Edit test to read claude-env file content after command
- Assert file contains "ANTHROPIC_API_KEY=test-" (from mocked keystore)
- Mock keystore to return "test-anthropic-key"
- Test should FAIL (current writes empty file)

---

**GREEN Phase:**

**Implementation:** Update account plan command to generate claude-env with provider

**Changes:**
- File: src/claudeutils/account/cli.py
  Action: In plan(), create AnthropicProvider with Keychain, call claude_env_vars(), format as KEY=value lines, write to claude-env
- File: tests/test_cli_account.py
  Action: Mock Keychain.find at `claudeutils.account.state.Keychain.find`, assert claude-env contains credentials

**Verify GREEN:**
```bash
pytest tests/test_cli_account.py::test_account_plan -v
```
- Test passes with claude-env containing credentials

**Verify no regression:**
```bash
pytest tests/test_cli_account.py -v
```
- All CLI account tests pass

---

**Expected Outcome**: account plan test verifies claude-env file content
**Error Conditions**: Missing env vars → verify provider.claude_env_vars() call
**Validation**: Test reads file, asserts credential presence
**Success Criteria**: account plan generates claude-env with provider credentials
**Report Path**: plans/claude-tools-recovery/reports/cycle-2-3-notes.md

---
