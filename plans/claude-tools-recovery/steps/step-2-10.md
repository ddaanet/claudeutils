# Cycle 2.10

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 2.10: Strengthen statusline command test

**Objective**: Pipe JSON input, assert ANSI-formatted output (not "OK" stub)

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Test statusline produces ANSI output from JSON input

**Expected failure:**
```
AssertionError: expected ANSI escape codes in output, got "OK"
```

**Why it fails:** Stub returns "OK" string

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must fail (no ANSI codes in output)
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Pipe JSON via CliRunner stdin, assert output contains ANSI codes

**Changes:**
- File: tests/test_statusline.py
  Action: Create/update test_statusline_formats_json:
    - Fixture: JSON string with statusline data (e.g., `{"mode": "plan", "usage": {...}}`)
    - Run: `statusline` via CliRunner with input=json_fixture
    - Assert: Output contains ANSI escape codes (e.g., `\x1b[` pattern)
    - Assert: Output is NOT just "OK"

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_formats_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Test verifies JSON parsing and ANSI formatting

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Test asserts ANSI codes in output, not stub

**Report Path**: plans/claude-tools-recovery/reports/cycle-2-10-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review CLI test quality (mocking, assertions). Commit fixes.
3. Functional review: Verify tests mock real I/O (filesystem, keychain, stdin), assert on output content.

---
