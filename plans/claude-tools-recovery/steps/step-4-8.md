# Cycle 4.8

**Plan**: `plans/claude-tools-recovery/runbook.md`
**Common Context**: See plan file for context

---

## Cycle 4.8: Integration test - statusline with realistic JSON

**Objective**: Test statusline with realistic statusline JSON input

**Script Evaluation**: Direct execution (TDD cycle)

**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** Statusline with complete JSON structure

**Expected failure:**
```
AssertionError: realistic JSON not formatted correctly
```

**Why it fails:** Edge cases in formatting not handled

**Verify RED:** Run `pytest tests/test_statusline.py::test_statusline_realistic_json -v`
- Must fail
- If passes, STOP

---

**GREEN Phase:**

**Implementation:** Create realistic statusline integration test

**Changes:**
- File: tests/test_statusline.py
  Action: Create test_statusline_realistic_json:
    - Fixture: JSON with mode, provider, usage stats, plan stats, API stats (realistic structure)
    - Run: `statusline` with fixture input
    - Assert: Output contains ANSI codes
    - Assert: Output is formatted (not just JSON dump)
    - Assert: All fields represented in output

**Verify GREEN:** `pytest tests/test_statusline.py::test_statusline_realistic_json -v`
- Must pass

**Verify no regression:** `pytest tests/test_statusline.py`
- All tests pass

---

**Expected Outcome**: Statusline handles realistic JSON

**Error Conditions**: RED passes → STOP; GREEN fails → Debug

**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓

**Success Criteria**: Realistic input produces formatted output

**Report Path**: plans/claude-tools-recovery/reports/cycle-4-8-notes.md

---

**Checkpoint**

1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Vet: Review error handling and integration tests. Commit fixes.
3. Functional review: Verify all features functional with real I/O. Test CLI commands manually if possible.

---
