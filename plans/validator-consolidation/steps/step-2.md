# Step 2

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 2: Port Learnings Validator + Tests

**Objective**: Port learnings validation (FR-2: title format, word count, duplicates, empty).

**Execution Model**: Haiku

**Source**: `agent-core/bin/validate-learnings.py` (~80 lines)

**Implementation**:

1. Create `src/claudeutils/validation/learnings.py`:
   - Port `extract_titles()` and `validate()` functions
   - `validate(path: Path, root: Path, max_words: int = 5) -> list[str]`
   - Keep `TITLE_PATTERN`, `MAX_WORDS` constants
   - Keep preamble skip logic (first 10 lines)
   - Use absolute imports: `from claudeutils.validation.common import find_project_root`

2. Create `tests/test_validation_learnings.py`:
   - Test: valid learnings file returns no errors
   - Test: title exceeding max word count returns error
   - Test: duplicate titles detected (case-insensitive)
   - Test: preamble (first 10 lines) skipped
   - Test: empty file returns no errors
   - Import: `from claudeutils.validation.learnings import validate`

**Expected Outcome**: Learnings validator produces identical results to original script.

**Success Criteria**: `pytest tests/test_validation_learnings.py -q` passes, validates FR-2 checks.

---
