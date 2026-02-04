# Cycle 2.8

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-8-notes.md`

---

## Cycle 2.8: Handle missing transcript file gracefully

**Objective**: calculate_context_tokens() returns 0 when transcript file doesn't exist (fail-safe per D8)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py creates StatuslineInput with current_usage=None and non-existent transcript_path, asserts calculate_context_tokens() returns 0 without raising exception

**Expected failure:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'nonexistent.json'
```

**Why it fails:** parse_transcript_context() doesn't handle missing file

**Verify RED:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_missing_transcript -xvs
- Must fail with FileNotFoundError
- If passes, STOP - exception handling may already exist

---

**GREEN Phase:**

**Implementation:** Wrap file open in try/except, catch FileNotFoundError, return 0

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add try/except around open() in parse_transcript_context(), catch FileNotFoundError, return 0

**Verify GREEN:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_missing_transcript -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-8-notes.md

---

**Light Checkpoint** (end of Phase 2)
1. Fix: Run `just dev`. Sonnet quiet-task fixes failures. Commit when green.
2. Functional: Review Phase 2 implementations against design. Check for stubs.

---
