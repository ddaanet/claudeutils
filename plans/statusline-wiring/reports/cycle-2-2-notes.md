### Cycle 2.2: Detect dirty git status with porcelain output

**Status:** GREEN_VERIFIED

**Test command:** `pytest tests/test_statusline_context.py::test_get_git_status_dirty -xvs`

**RED result:** FAIL as expected
- AssertionError: assert False == True
- Test correctly fails because dirty detection not implemented

**GREEN result:** PASS
- Test passes after adding `git status --porcelain` call to context.py
- dirty = bool(result.stdout.strip()) correctly detects non-empty output

**Regression check:** 10/10 passed
- All statusline tests pass including updated test_get_git_status_in_repo
- No regressions introduced

**Refactoring:** none
- Lint: OK
- Precommit: OK
- No quality warnings to address

**Files modified:**
- src/claudeutils/statusline/context.py (added git status --porcelain call)
- tests/test_statusline_context.py (added test_get_git_status_dirty, updated test_get_git_status_in_repo)

**Stop condition:** none

**Decision made:** none
