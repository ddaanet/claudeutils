# Cycle 2.2: Cache hit and invalidation

**Timestamp:** 2026-03-01

## Execution Report

### Status
GREEN_VERIFIED

### RED Phase
**Test command:** `just test tests/test_recall_topic_matcher.py::test_cache_behavior`

**Expected failure:** Cache hit test should fail because `get_or_build_index()` doesn't read from cache — it always calls `parse_memory_index`

**RED result:** FAIL as expected
- Case 1 (cache_hit): parse_call_count showed 2 calls instead of 1 (cache not read)
- Case 2 (cache_invalidation): PASS (cache invalidation not yet implemented)

### GREEN Phase
**Implementation:** Added cache-READ and mtime-validation logic to `get_or_build_index()` in `src/claudeutils/recall/topic_matcher.py`

**Changes made:**
1. Added `os` import for mtime operations
2. Implemented `_json_to_entries()` helper to reconstruct IndexEntry objects from JSON (frozenset keywords conversion)
3. Implemented `_json_to_inverted_index()` helper to reconstruct inverted index from JSON
4. Modified `get_or_build_index()` to:
   - Check cache existence before rebuilding
   - Load and validate source file mtime against cache timestamp
   - Reconstruct data structures from JSON if cache is valid (source not newer)
   - Rebuild and save cache if source is newer than cache or cache missing

**GREEN result:** PASS
- `just test tests/test_recall_topic_matcher.py::test_cache_behavior` → 2/2 passed
- Both cache_hit and cache_invalidation test cases pass

### Regression Check
**Command:** `just test`

**Result:** 1375/1376 passed, 1 xfail (expected)
- All existing tests still pass
- No regressions introduced
- Only known xfail in test_markdown_fixtures (pre-existing)

### Refactoring
**Linting:** `just lint` → All checks passed
- Code reformatting applied
- Ruff: All checks passed
- Mypy: All checks passed

**Precommit:** `just precommit` → OK
- Full validation suite passed
- No warnings or errors

### Files Modified
- `src/claudeutils/recall/topic_matcher.py`
  - Added: `os` import
  - Added: `_json_to_entries()` function
  - Added: `_json_to_inverted_index()` function
  - Modified: `get_or_build_index()` with cache-read and mtime validation

- `tests/test_recall_topic_matcher.py`
  - Added: Imports: `os`, `time`, `Path`, `parse_memory_index`
  - Added: `test_cache_behavior()` parametrized test (cache_hit and cache_invalidation cases)

### Stop Condition
None — cycle completed successfully

### Decision Made
Cache validation uses mtime comparison (source vs cache timestamp). Reconstruction from JSON preserves the inverted index structure with proper type conversions (keyword lists → frozensets).
