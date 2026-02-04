# Cycle 2.6

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-2-6-notes.md`

---

## Cycle 2.6: Calculate context tokens from current_usage (primary path)

**Objective**: calculate_context_tokens() sums 4 token fields from StatuslineInput.context_window.current_usage when present
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_context.py creates StatuslineInput with current_usage containing 4 token values (100, 50, 25, 25), asserts calculate_context_tokens() returns 200

**Expected failure:**
```
AttributeError: module 'claudeutils.statusline.context' has no attribute 'calculate_context_tokens'
```

**Why it fails:** calculate_context_tokens() function doesn't exist yet

**Verify RED:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_current_usage -xvs
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Add calculate_context_tokens(input_data: StatuslineInput) → int that sums 4 token fields when current_usage is not None

**Changes:**
- File: src/claudeutils/statusline/context.py
  Action: Add calculate_context_tokens() function, check if current_usage exists, sum input_tokens + output_tokens + cache_creation_input_tokens + cache_read_input_tokens

**Verify GREEN:** pytest tests/test_statusline_context.py::test_calculate_context_tokens_from_current_usage -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-2-6-notes.md

---
