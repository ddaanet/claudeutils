# Cycle 3.15

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 3.15: Statusline CLI - basic structure

**Objective**: Implement `claudeutils statusline` reading stdin JSON
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** CLI command `claudeutils statusline` reads JSON from stdin

**Expected failure:**
```
AttributeError: 'MultiCommand' object has no attribute 'statusline'
```

**Why it fails:** statusline command doesn't exist

**Verify RED:** `pytest tests/test_cli_statusline.py::test_statusline_reads_stdin -xvs`
- Must fail with AttributeError
- If passes, STOP - command may already exist

---

**GREEN Phase:**

**Implementation:** Create statusline command

**Changes:**
- File: src/claudeutils/statusline/cli.py
  Action: Create Click command 'statusline' reading stdin JSON
- File: src/claudeutils/cli.py
  Action: Add statusline command
- File: tests/test_cli_statusline.py
  Action: Test with CliRunner, mock stdin

**Verify GREEN:** `pytest tests/test_cli_statusline.py::test_statusline_reads_stdin -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-3-15-notes.md

---

**Checkpoint**
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review CLI command structure, help text clarity, error handling. Commit fixes.

---
