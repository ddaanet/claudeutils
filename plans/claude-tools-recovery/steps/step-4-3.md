# Cycle 4.3

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.3: Test invalid JSON on statusline stdin

**Objective**: Verify error message (not crash) on invalid JSON

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test statusline with invalid JSON input shows error

**Expected failure:**
```
FAILED - Expected error message, got crash or unclear output
```

**Why it fails:** JSON error handling not implemented

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_invalid_json -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Catch JSON parse errors and show clear message

**Changes:**
- File: claudeutils/statusline/cli.py
  Action: Update statusline():
    - Catch: json.JSONDecodeError
    - Output: "Error: Invalid JSON input" with exit code 1

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_invalid_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Clear error on invalid JSON

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Error message is clear, non-zero exit

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-3-notes.md

---
