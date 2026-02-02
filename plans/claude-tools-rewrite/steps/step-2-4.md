# Cycle 2.4

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 2.4: Parse comment metadata (tiers)

**Objective**: Extract tier tags (haiku, sonnet, opus) from comment line
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** parse_model_entry() extracts tiers from comment

**Expected failure:**
```
AssertionError: assert model.tiers == []
Expected: ['haiku', 'sonnet']
```

**Why it fails:** Tier parsing not implemented

**Verify RED:** `pytest tests/test_model_config.py::test_parse_model_entry_tiers -xvs`
- Must fail with empty tiers
- If passes, STOP - tier parsing may already exist

---

**GREEN Phase:**

**Implementation:** Add tier extraction from comment line

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Extend parse_model_entry() to regex-extract tier tags from comment
- File: tests/test_model_config.py
  Action: Test with entry having "# haiku,sonnet - arena:5" comment

**Verify GREEN:** `pytest tests/test_model_config.py::test_parse_model_entry_tiers -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-4-notes.md

---
