# Cycle 3.1: Topic detector block in hook

**Status:** GREEN_VERIFIED
**Test command:** `just test tests/test_ups_topic_integration.py::test_hook_topic_injection_produces_additional_context`
**Timestamp:** 2026-03-01

## Phase Results

**RED result:** FAIL as expected
- Test setup: fixture memory-index with test entries; monkeypatch CLAUDE_PROJECT_DIR
- Expected failure: hook returns empty dict (no topic matching yet)
- Actual failure: assertion "Hook should produce output for matching keywords" failed
- Failure type: Hook integration incomplete, correct

**GREEN result:** PASS
- Added `match_topics()` entry point to `src/claudeutils/recall/topic_matcher.py`
  - Wraps pipeline: `get_or_build_index` → `get_candidates` → `score_and_rank` → `resolve_entries` → `format_output`
  - Takes prompt text, index path, project dir, threshold, max_entries
- Added import of `match_topics` to `agent-core/hooks/userpromptsubmit-shortcuts.py` (try/except for optional dependency)
- Added Tier 2.75 topic detector block to hook main()
  - Between Tier 2.5 CCG guard and Tier 3 continuation parsing
  - Reads CLAUDE_PROJECT_DIR env var
  - Checks for agents/memory-index.md
  - Calls match_topics and appends context + system_message
  - Wrapped in exception handler to prevent hook breakage
- Test now passes: hook produces context and system message with "topic" marker
- Added end-to-end test (same fixture, different prompt)

**Regression check:** 1377/1378 passed, 1 xfail (pre-existing)
- No new failures introduced
- xfail is unrelated (markdown preprocessor bug)

## Refactoring

**Lint:** PASS (after fixes)
- Formatted files: topic_matcher.py, test_ups_topic_integration.py
- Fixed docstring line length (wrapped docstring in match_topics)
- Added type annotations: Path, MonkeyPatch to all test parameters
- Fixed docstring format (D205 blank line requirement)

**Precommit:** PASS
- All checks pass after linting

## Files Modified

- `src/claudeutils/recall/topic_matcher.py` — Added `match_topics()` entry point (7 lines)
- `agent-core/hooks/userpromptsubmit-shortcuts.py` — Added import + Tier 2.75 detector block (21 lines)
- `tests/test_ups_topic_integration.py` — New integration test file with fixture and 2 tests
- `plans/userpromptsubmit-topic/reports/cycle-3.1.md` — This report

## Stop Condition

None. Cycle completed successfully.

## Decision Made

**Tier 2.75 placement:** Topic injection placed between Tier 2.5 pattern guards (skill-editing, CCG) and Tier 3 continuation parsing. Rationale: Topic matching is ambient (doesn't require exact match), like guards, but is more structured than generic continuation parsing. Positioned after guards to allow them to take priority on specific patterns.

**Exception handling:** Topic block wrapped in try/except with silent pass. Topic injection is non-essential; hook must never break due to topic matching failures. Silences exceptions to maintain hook reliability.

**Memory-index lookup:** Uses hardcoded path `agents/memory-index.md` relative to CLAUDE_PROJECT_DIR. Consistent with existing recall system conventions (memory-index as standard location).
