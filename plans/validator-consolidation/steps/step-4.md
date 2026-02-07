# Step 4

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 4: Port Decision Files Validator + Tests

**Objective**: Port decision file structural validation (organizational sections must be marked structural).

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-decision-files.py` (~145 lines)

**Implementation**:

1. Create `src/claudeutils/validation/decision_files.py`:
   - Port `parse_heading()`, `analyze_file()`, `validate()` functions
   - `validate(root: Path) -> list[str]`
   - Keep `CONTENT_THRESHOLD = 2`, `DECISION_GLOBS` patterns
   - Preserve action message format (A: mark structural, B: add content)

2. Create `tests/test_validation_decision_files.py`:
   - Test: section with content before sub-headings → no violation
   - Test: section with only sub-headings → violation (needs structural marker)
   - Test: structural marker (`.` prefix) → no violation
   - Test: content threshold (≤2 substantive lines before sub-heading → violation)
   - Test: nested heading levels handled correctly
   - Test: no decision files → no errors

**Expected Outcome**: Decision files validator identical behavior to original.

**Success Criteria**: `pytest tests/test_validation_decision_files.py -q` passes.

**Phase 1 Checkpoint**: Run `pytest tests/test_validation_common.py tests/test_validation_learnings.py tests/test_validation_jobs.py tests/test_validation_decision_files.py -q` and `mypy src/claudeutils/validation/`. All must pass before proceeding.

---
