# Cycle 1.3

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-1-3-notes.md`

---

## Cycle 1.3: Validate ContextUsage has 4 token fields

**Objective**: Ensure ContextUsage model has all 4 token fields (input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens)
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_models.py parses JSON with all 4 token fields in current_usage and sums them correctly

**Expected failure:**
```
AttributeError: 'ContextUsage' object has no attribute 'cache_read_input_tokens'
```

**Why it fails:** ContextUsage missing one or more token fields

**Verify RED:** pytest tests/test_statusline_models.py::test_context_usage_has_four_token_fields -xvs
- Must fail with AttributeError
- If passes, STOP - all fields may already exist

---

**GREEN Phase:**

**Implementation:** Define ContextUsage model with 4 int fields

**Changes:**
- File: src/claudeutils/statusline/models.py
  Action: Add ContextUsage(BaseModel) with input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens: int fields

**Verify GREEN:** pytest tests/test_statusline_models.py::test_context_usage_has_four_token_fields -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-1-3-notes.md

---
