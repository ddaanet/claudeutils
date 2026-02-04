# Cycle 1.1

**Plan**: `plans/statusline-wiring/runbook.md`
**Execution Model**: haiku
**Report Path**: `plans/statusline-wiring/reports/cycle-1-1-notes.md`

---

## Cycle 1.1: Create StatuslineInput model with Claude Code JSON schema

**Objective**: Define Pydantic model for parsing Claude Code stdin JSON
**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

**RED Phase:**

**Test:** tests/test_statusline_models.py parses valid Claude Code JSON into StatuslineInput model with 8 fields (model.display_name, workspace.current_dir, transcript_path, context_window.current_usage, context_window.context_window_size, cost.total_cost_usd, version, session_id)

**Expected failure:**
```
ModuleNotFoundError: No module named 'claudeutils.statusline.models'
```

**Why it fails:** models.py doesn't exist yet

**Verify RED:** pytest tests/test_statusline_models.py::test_parse_valid_json -xvs
- Must fail with ModuleNotFoundError
- If passes, STOP - models.py may already exist

---

**GREEN Phase:**

**Implementation:** Create src/claudeutils/statusline/models.py with StatuslineInput Pydantic model matching Claude Code JSON schema (8 fields, nested structures for model/workspace/context_window/cost)

**Changes:**
- File: src/claudeutils/statusline/models.py
  Action: Create with StatuslineInput, ContextUsage, ModelInfo, WorkspaceInfo, ContextWindowInfo, CostInfo Pydantic models

**Verify GREEN:** pytest tests/test_statusline_models.py::test_parse_valid_json -xvs
- Must pass

**Verify no regression:** pytest tests/test_statusline_*.py
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/statusline-wiring/reports/cycle-1-1-notes.md

---
