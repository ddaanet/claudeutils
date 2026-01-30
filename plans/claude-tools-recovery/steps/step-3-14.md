# Cycle 3.14

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 3.14: Wire statusline command to format JSON input

**Objective**: Read stdin JSON and output ANSI-formatted statusline

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Strengthened test from Cycle 2.10 should fail

**Expected failure:**
```
AssertionError: expected ANSI codes, got "OK"
```

**Why it fails:** Command returns stub

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Update statusline command to read stdin and format with StatuslineFormatter

**Changes:**
- File: claudeutils/statusline/cli.py
  Action: Update statusline() command:
    - Read: sys.stdin or Click input
    - Parse: JSON to dict
    - Call: StatuslineFormatter.format(data)
    - Output: ANSI-formatted result

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Command reads JSON and outputs ANSI

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Implementation formats JSON, test passes

**Report Path**: plans/claude-tools-recovery/reports/cycle-3-14-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review implementation quality (error handling, edge cases). Commit fixes.
3. Functional review: Verify all I/O wired (filesystem, keychain, stdin). Check for remaining stubs.

---
