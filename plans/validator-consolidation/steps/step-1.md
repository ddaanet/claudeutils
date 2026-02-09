# Step 1

**Plan**: `plans/validator-consolidation/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1: Create Validation Package + Common Utilities + Tests

**Objective**: Create package structure and shared `find_project_root()` utility.

**Execution Model**: Haiku

**Implementation**:

1. Create package directory: `src/claudeutils/validation/`

2. Create `src/claudeutils/validation/__init__.py`:
   - Empty initially (updated in Step 7 with public API exports)

3. Create `src/claudeutils/validation/common.py`:
   - Port `find_project_root()` from any existing validator (they all have it)
   - Function signature: `find_project_root(start: Path | None = None) -> Path`
   - If `start` is None, use `Path.cwd()`
   - Walk up directory tree looking for `CLAUDE.md` (C-2)
   - Raise `FileNotFoundError` if root not found (don't silently fall back to cwd)

4. Create `tests/test_validation_common.py`:
   - Test: finds root when CLAUDE.md exists in parent
   - Test: finds root when CLAUDE.md exists in current dir
   - Test: raises FileNotFoundError when CLAUDE.md not found
   - Test: works from nested subdirectory
   - Test: custom start path parameter

**Expected Outcome**: Package importable, `find_project_root()` works correctly.

**Success Criteria**:
- `from claudeutils.validation.common import find_project_root` works
- All tests pass: `pytest tests/test_validation_common.py -q`
- `mypy src/claudeutils/validation/` clean

---
