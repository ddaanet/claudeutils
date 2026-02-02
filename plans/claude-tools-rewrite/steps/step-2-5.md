# Cycle 2.5

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 2.5: Parse comment metadata (arena rank and pricing)

**Objective**: Extract arena rank and pricing from comment
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** parse_model_entry() extracts arena_rank, input_price, output_price from comment

**Expected failure:**
```
AssertionError: assert model.arena_rank is None
Expected: 5
```

**Why it fails:** Arena/pricing parsing not implemented

**Verify RED:** `pytest tests/test_model_config.py::test_parse_model_entry_metadata -xvs`
- Must fail with None values
- If passes, STOP - metadata parsing may already exist

---

**GREEN Phase:**

**Implementation:** Add arena rank and pricing extraction

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Extend parse_model_entry() to extract arena:N, $X.XX/$Y.YY from comment
- File: tests/test_model_config.py
  Action: Test with entry having "arena:5 - $0.25/$1.25" in comment

**Verify GREEN:** `pytest tests/test_model_config.py::test_parse_model_entry_metadata -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-5-notes.md

---
