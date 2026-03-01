# Review: UPS Topic Injection — Phase 2 (Cycles 2.1–2.2)

**Scope**: Cache build/store (Cycle 2.1), cache hit/invalidation (Cycle 2.2) in `src/claudeutils/recall/topic_matcher.py`
**Baseline**: ac5183be
**Date**: 2026-03-01
**Mode**: review + fix

## Summary

Phase 2 implements `get_or_build_index()` with project-local cache using mtime invalidation. The core cache logic is correct: `tmp/topic-index-{hash}.json`, SHA256 key from index path + project dir, mtime comparison, silent failure on cache errors. JSON round-trip is structurally sound. Three issues found: wrong exception type caught in `_save_index_cache`, code duplication between serialization helpers, and a test quality issue (parametrized `if/elif` dispatch pattern — same anti-pattern fixed in Phase 1 review).

**Overall Assessment**: Ready (all issues fixed)

---

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **`_save_index_cache` catches `json.JSONDecodeError` on write path**
   - Location: `src/claudeutils/recall/topic_matcher.py:252`
   - Note: `json.JSONDecodeError` is raised by `json.loads`/`json.load` (parse failures), never by `json.dump`. The write path can raise `TypeError` if data is non-serializable. The current except clause would miss a `TypeError` from dump, propagating it instead of silently failing. In practice the data is always serializable (all serialization helpers produce dicts/lists/strings/numbers), so this never triggers — but the exception is semantically wrong and misleading. Fix: replace `json.JSONDecodeError` with `ValueError` (which `JSONDecodeError` subclasses, broader for write) or add `TypeError`.
   - **Status**: FIXED

2. **`_dict_to_index` duplicates entry serialization logic from `_entries_to_json_serializable`**
   - Location: `src/claudeutils/recall/topic_matcher.py:173–189`
   - Note: The per-entry dict literal (key, description, referenced_file, section, keywords) appears inline in `_dict_to_index` rather than calling `_entries_to_json_serializable`. If `IndexEntry` fields change, both sites must be updated. Fix: call `_entries_to_json_serializable(entries)` inside `_dict_to_index`.
   - **Status**: FIXED

3. **`test_cache_behavior` uses `if/elif` dispatch inside parametrized test body**
   - Location: `tests/test_recall_topic_matcher.py:351–397`
   - Note: Same anti-pattern flagged in Phase 1 review (minor issue 2, fixed for `test_resolve_entries`). Two logically distinct scenarios (cache hit vs invalidation) share one test body with `if/elif` dispatch on `case` string. Split into `test_cache_hit_avoids_reparsing` and `test_cache_invalidation_triggers_rebuild`.
   - **Status**: FIXED

4. **`test_cache_stores_index_to_project_tmp` pre-creates `tmp/` directory unnecessarily**
   - Location: `tests/test_recall_topic_matcher.py:327–328`
   - Note: `_save_index_cache` calls `cache_path.parent.mkdir(parents=True, exist_ok=True)` internally. The test's explicit `tmp_subdir.mkdir(parents=True, exist_ok=True)` is redundant — it masks the mkdir path in the implementation and prevents the test from verifying that `get_or_build_index` creates the directory itself.
   - **Status**: FIXED

---

## Fixes Applied

- `src/claudeutils/recall/topic_matcher.py:252` — Changed `json.JSONDecodeError` to `(OSError, TypeError)` in `_save_index_cache` exception clause; `json.JSONDecodeError` is never raised by `json.dump`
- `src/claudeutils/recall/topic_matcher.py:178–188` — `_dict_to_index` now calls `_entries_to_json_serializable(entries)` instead of duplicating the serialization dict literal
- `tests/test_recall_topic_matcher.py:351–397` — Split `test_cache_behavior` parametrized test into two separate test functions: `test_cache_hit_avoids_reparsing` and `test_cache_invalidation_triggers_rebuild`
- `tests/test_recall_topic_matcher.py:327–328` — Removed redundant `tmp_subdir.mkdir()` from `test_cache_stores_index_to_project_tmp`

---

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-4: Cache inverted index with mtime invalidation | Satisfied | `get_or_build_index()` at topic_matcher.py:256; mtime comparison at line 279 |
| D-2: Inverted index cached alongside parsed entries (same mtime invalidation) | Satisfied | Cache stores both `entries` and `inverted_index` keys; single timestamp governs both |
| D-4: Cache at `tmp/topic-index-{hash}.json`, hash = index_path + project_dir | Satisfied | `_get_cache_path()` at line 192–196 |
| D-4: Mtime comparison | Satisfied | `source_mtime <= cache_timestamp` at line 279 |
| D-4: Silent cache failure | Satisfied | Try/except in both `_save_index_cache` and read path in `get_or_build_index` |
| D-4: Cache at project-local `tmp/` (never `/tmp/`) | Satisfied | `project_dir / "tmp" / f"topic-index-{hash_digest}.json"` at line 196 |

---

## Positive Observations

- Hash key uses both index path and project dir, correctly isolating cache per project+index pair
- `source_mtime <= cache_timestamp` comparison is semantically correct: cache is valid when source is NOT newer than the stored timestamp
- `Path.stat().st_mtime` used instead of `os.stat()` — consistent with codebase's `pathlib`-first style
- `_json_to_entries` correctly handles missing or malformed `keywords` field with fallback to `frozenset()` — defensive without being over-engineered
- Both serialization helpers handle the `frozenset` → `sorted(list)` → `frozenset` round-trip correctly, preserving keyword set equality
- Silent failure pattern matches existing continuation-registry cache in `userpromptsubmit-shortcuts.py` (consistent with established pattern)

## Recommendations

- Phase 3 hook integration: pass `max_entries=3` explicitly when calling `score_and_rank` to enforce the D-6 cap (noted in Phase 1 review, still applies)
