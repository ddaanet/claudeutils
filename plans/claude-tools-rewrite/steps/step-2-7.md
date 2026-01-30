# Cycle 2.7

**Plan**: `plans/claude-tools-rewrite/runbook.md`
**Common Context**: See plan file for context

---

### Cycle 2.7: Filter models by tier

**Objective**: Add filter_by_tier() returning models matching tier
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** filter_by_tier(models, "haiku") returns only haiku-tier models

**Expected failure:**
```
AttributeError: module 'claudeutils.model.config' has no attribute 'filter_by_tier'
```

**Why it fails:** Function doesn't exist

**Verify RED:** `pytest tests/test_model_config.py::test_filter_by_tier -xvs`
- Must fail with AttributeError
- If passes, STOP - function may already exist

---

**GREEN Phase:**

**Implementation:** Create filter_by_tier() function

**Changes:**
- File: src/claudeutils/model/config.py
  Action: Create filter_by_tier(models, tier) returning [m for m in models if tier in m.tiers]
- File: tests/test_model_config.py
  Action: Test filtering list of models by tier

**Verify GREEN:** `pytest tests/test_model_config.py::test_filter_by_tier -xvs`
- Must pass

**Verify no regression:** `pytest`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/claude-tools-rewrite/reports/cycle-2-7-notes.md

---
