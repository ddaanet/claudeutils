# Remove UPS Topic Injection

## Requirements

### Functional Requirements

**FR-1: Remove Tier 2.75 topic injection from UPS hook**
Delete the topic injection block (import of `match_topics`, Tier 2.75 code block at lines 1033–1047) from `agent-core/hooks/userpromptsubmit-shortcuts.py`. The hook must continue to function for all other tiers (1, 2, 2.5, 3). Acceptance: hook passes existing non-topic tests; no `match_topics` import; no `topic` references in hook output for any prompt.

**FR-2: Delete dead `topic_matcher.py` module**
Remove `src/claudeutils/recall/topic_matcher.py` — no production callers remain after FR-1. Acceptance: module deleted; no import references in non-test code.

**FR-3: Delete orphaned test files**
Remove test files that exclusively test topic injection:
- `tests/test_ups_topic_integration.py` (UPS hook topic integration tests)
- `tests/test_recall_topic_matcher.py` (topic_matcher unit tests)
- `tests/test_recall_topic_cache.py` (topic index cache tests)
Acceptance: no test files importing from `topic_matcher`; remaining test suite passes.

**FR-4: Clean cross-references**
Audit and remove references to topic injection in:
- Plan archive entries mentioning the feature
- Any `__init__.py` exports of `topic_matcher`
Acceptance: `grep -r topic_matcher` returns zero non-report hits; `grep -r "topic.inject"` returns only historical reports (plans/reports/).

### Out of Scope

- Removing the recall subsystem (`index_parser`, `relevance`, `cli`, `recall.py`) — these serve `/when`, `/how`, `/recall` skills
- Removing `topics.py` — extracts session keywords, unrelated to hook injection
- Replacing topic injection with an alternative mechanism — explicit recall skills are sufficient
- Modifying `when/resolver.py` — the `_capitalize_heading` comment noting duplication with topic_matcher becomes stale but is harmless; removing it is optional cleanup

### Dependencies

- `just precommit` must pass after all changes — validates no broken imports or test failures
