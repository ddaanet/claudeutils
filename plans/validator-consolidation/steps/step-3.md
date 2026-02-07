# Step 3

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 3: Port Jobs Validator + Tests

**Objective**: Port jobs.md validation against plans/ directory structure.

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-jobs.py` (~110 lines)

**Implementation**:

1. Create `src/claudeutils/validation/jobs.py`:
   - Port `parse_jobs_md()` and `get_plans_directories()` functions
   - Main function: `validate(root: Path) -> list[str]`
   - Preserve: skip `.`-prefixed entries, skip `plans/claude/`, skip `README.md`, skip complete plans when checking missing directories

2. Create `tests/test_validation_jobs.py`:
   - Test: valid jobs.md with matching plans/ returns no errors
   - Test: plan in directory but not in jobs.md → error
   - Test: plan in jobs.md but not in directory (non-complete) → error
   - Test: complete plans exempt from directory check
   - Test: table parsing handles standard format
   - Test: missing jobs.md → error

**Expected Outcome**: Jobs validator identical behavior to original.

**Success Criteria**: `pytest tests/test_validation_jobs.py -q` passes.

---
