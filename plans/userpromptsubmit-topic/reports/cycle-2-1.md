# Cycle 2.1: Cache build and store

**Date**: 2026-03-01
**Status**: GREEN_VERIFIED
**Commit**: 6fb2ac09

## Cycle Execution

### RED Phase
- **Test**: `test_cache_stores_index_to_project_tmp`
- **Expected Failure**: `NameError: name 'get_or_build_index' is not defined`
- **Result**: FAIL as expected ✓

### GREEN Phase
- **Implementation**: Added `get_or_build_index()` function with cache write logic to `src/claudeutils/recall/topic_matcher.py`
- **Key changes**:
  - `_entries_to_json_serializable()` — Convert IndexEntry list to JSON-compatible format (frozenset → sorted list)
  - `_dict_to_index()` — Convert inverted index to JSON-compatible format
  - `_get_cache_path()` — Generate SHA256-based cache filename in `project_dir/tmp/`
  - `_save_index_cache()` — Write cache with entries, inverted_index, and timestamp; silent fail on error
  - `get_or_build_index()` — Public API: parse index, build inverted index, cache, return tuple
- **Result**: PASS ✓
- **Regression check**: All 1373 tests pass (1 xfail expected) ✓

### REFACTOR Phase

#### Lint Results
- **Format**: 2 files reformatted (tests, src)
- **Ruff checks**:
  - PERF401: Used list comprehension instead of loop (fixed)
  - PTH123: Used `Path.open()` instead of `open()` (fixed)
  - BLE001: Caught specific exceptions instead of blind `Exception` (fixed)
  - PLC0415: Moved `import json` to module top-level (fixed)
- **Mypy**: Fixed missing type parameters for dict return types (fixed)
- **Result**: PASS ✓

#### Precommit Validation
- `just precommit` — PASS ✓
- No warnings or complexity issues

#### Code Quality
- Helper functions private (`_`) — appropriate encapsulation
- JSON serialization handles frozenset → list conversion correctly
- Error handling: catches OSError, IOError, JSONDecodeError (not blind Exception)
- Silent cache failure maintains graceful degradation (existing pattern from userpromptsubmit-shortcuts.py)
- Timestamp capture from source mtime for future cache invalidation logic

## Files Modified
- `src/claudeutils/recall/topic_matcher.py` — Added cache logic (4 helper functions + 1 public API)
- `tests/test_recall_topic_matcher.py` — Added test + imports

## Design Notes
- Cache path uses SHA256(index_path + project_dir)[:16] for unique identification per index/project pair
- Cache structure: `{"entries": [...], "inverted_index": {...}, "timestamp": float}`
- Timestamp stored for Phase 2.2 (cache validation) — will check source mtime against cached timestamp
- Silent failure pattern matches existing continuation-registry cache in hooks (userpromptsubmit-shortcuts.py:456-458)
- Phase 2.2 will implement cache reading and mtime validation (forms the basis for performance optimization)

## Next Cycle
Phase 2.2: Cache read and validation
- Load cache from disk
- Validate cache structure
- Check mtime and invalidate if stale
- Return cached index if valid, else rebuild
