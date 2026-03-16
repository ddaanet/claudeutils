# Outline: Remove Fuzzy Matching from Recall Resolve

## Approach

Remove all fuzzy matching from `resolver.py` and validator modules. Replace with exact case-insensitive matching. Fix data mismatches surfaced by exact validation.

## Scope

**IN:**
- `src/claudeutils/when/resolver.py` — 3 fuzzy paths
- `src/claudeutils/validation/memory_index_checks.py` — 1 fuzzy path
- `src/claudeutils/validation/memory_index.py` — 1 fuzzy path
- `tests/test_when_resolver.py` — 3 tests assume fuzzy trigger/heading matching
- `tests/test_when_resolver_errors.py` — 3 tests assert "Did you mean:" suggestions
- `src/claudeutils/recall_cli/cli.py` — differentiated error wrapping per D3 (artifact-form vs keyword-form)
- `tests/test_validation_memory_index_formats.py` — 2 tests assert fuzzy matching behavior
- `agents/memory-index.md` — fix any trigger/heading mismatches surfaced by exact validation
- `agents/decisions/*.md` — fix any heading discrepancies

**OUT:**
- `src/claudeutils/when/fuzzy.py` — retained: `compress.py` uses `fuzzy.rank_matches()` for compression suggestions (separate concern from recall resolve)
- `src/claudeutils/when/cli.py` — no changes needed (query parsing, operator stripping unchanged)
- `src/claudeutils/validation/memory_index_helpers.py` — no fuzzy usage
- `tests/test_when_fuzzy.py` — retained (tests fuzzy module used by compress)
- `tests/test_when_resolver_hyphenated.py` — uses `_heading_matches()` (already exact, case-insensitive), no change

## Key Decisions

**D1: Trigger matching becomes exact.** `_resolve_trigger()` replaces `fuzzy.rank_matches(query, trigger_candidates)` with exact case-insensitive lookup: `query.lower() == trigger.lower()`. Cross-operator matching still works — triggers stored without operator prefix.

**D2: Heading matching uses `_heading_matches()` only.** Remove fuzzy fallback from `_find_heading()`. The existing `_heading_matches()` function (case-insensitive, whitespace-normalized) is the sole matching mechanism. Mismatches between `_build_heading()` output and file headings → hard error.

**D3: Error messages differentiated by call context.** Two failure modes per brief:
- **Keyword-form** (`_recall resolve "when <trigger>"`): `"No memory entry for '<trigger>'. Read agents/memory-index.md to find valid entries."` Facts + recovery guidance (per "when cli error messages are llm-consumed"). No suggestions.
- **Artifact-form** (`_recall resolve plans/<job>/recall-artifact.md`): `"No memory entry for '<trigger>'. STOP: stale key in recall artifact — downstream work will miss critical context."` STOP with rationale: the entry was judged relevant by a planning skill; if it can't resolve, that context is definitively missing. Rationale improves agent adherence to the halt. The recall artifact is produced upstream (/design A.1, /requirements, /runbook Phase 0.5) — consumers at execution time cannot fix stale keys.

**D4: `check_collisions()` simplified to exact-only.** With exact matching, two entries can collide only if they have identical keys — already caught by `check_duplicate_entries()`. Simplify `check_collisions()` to exact-only lookup (not deleted — still validates entry-to-heading resolution). `_resolve_entry_heading()` becomes a dict lookup.

**D5: `_check_orphan_headers()` uses exact lookup.** Replace fuzzy scoring loop with `title in entries`. Removes `from claudeutils.when.fuzzy import score_match` from both validator modules.

**D6: Pre-flight data check.** Before committing code changes, run validator with exact matching against live `agents/memory-index.md` and `agents/decisions/`. Fix any trigger-heading mismatches in data. The recall entry "when writing memory-index trigger phrases" documents this: articles must be present if heading contains them.

## Affected Functions

### resolver.py

| Function | Current | After | Lines |
|----------|---------|-------|-------|
| `_get_suggestions()` | Sequential char matching, returns top 3 | **Delete** | 125-146 |
| `_handle_no_match()` | Formats "Did you mean:" with fuzzy suggestions | **Delete** | 149-165 |
| `_resolve_trigger()` | `fuzzy.rank_matches()` for matching | Exact lookup, context-differentiated error per D3 | 177-236 |
| `_find_heading()` | Exact match + fuzzy fallback | Exact match only, return None on miss | 259-294 |
| import | `from claudeutils.when import fuzzy` | **Remove** (no remaining usage) | 5 |

### validation/memory_index_checks.py

| Function | Current | After | Lines |
|----------|---------|-------|-------|
| `_resolve_entry_heading()` | Exact + fuzzy `score_match` fallback | Dict lookup only | 191-209 |
| `check_collisions()` | Uses `_resolve_entry_heading` with fuzzy | Exact key comparison | 212-242 |
| import | `from claudeutils.when.fuzzy import score_match` | **Remove** | 9 |

### validation/memory_index.py

| Function | Current | After | Lines |
|----------|---------|-------|-------|
| `_check_orphan_headers()` | Fuzzy scoring loop with threshold 50.0 | `title in entries` dict lookup | 112-149 |
| import | `from claudeutils.when.fuzzy import score_match` | **Remove** | 18 |

### recall_cli/cli.py

D3 error differentiation lives here, not in `resolver.py`. `cli.py` knows the call context (keyword-form vs artifact-form) from argument parsing — it determines whether the user passed a trigger string or a file path. When `resolver.py` raises `ResolveError`, `cli.py` catches and wraps with the appropriate error message per D3:

| Function | Current | After |
|----------|---------|-------|
| Resolve dispatch (keyword path) | Surfaces `ResolveError` message as-is | Wrap with keyword-form message: `"No memory entry for '<trigger>'. Read agents/memory-index.md to find valid entries."` |
| Resolve dispatch (artifact path) | Surfaces `ResolveError` message as-is | Wrap with artifact-form message: `"No memory entry for '<trigger>'. STOP: stale key in recall artifact — downstream work will miss critical context."` |

**Rationale for cli.py not resolver.py:** `resolver.py` processes entries without knowledge of invocation form. Call-context awareness belongs in the CLI layer that parsed the arguments.

## Test Changes

### test_when_resolver.py

| Test | Change |
|------|--------|
| `test_trigger_mode_resolves` | Remove `"mock test"` fuzzy assertion (line 110-111). Keep exact `"writing mock tests"` assertion. |
| `test_trigger_fuzzy_heading_match` | **Rewrite:** trigger with missing article ("to enumerated system" vs "to an enumerated system") → expect `ResolveError`. Or fix trigger to include article and test exact success. |
| `test_trigger_fuzzy_heading_match_how_operator` | **Rewrite:** similar — trigger "configure script entry points" vs heading "Configure the Script Entry Points" has extra "the". Expect error or fix data. |

### test_when_resolver_errors.py

| Test | Change |
|------|--------|
| `test_trigger_not_found_suggests_matches` | **Rewrite:** assert error contains `"No memory entry for"` and `"Read agents/memory-index.md"`. No "Did you mean:" assertion. |
| `test_trigger_suggestions_limited_to_three` | **Delete** — no suggestions to count. |
| `test_how_operator_error_suggestions` | **Delete** — no operator-specific suggestions. |

Tests for `recall_cli/cli.py` error differentiation (new tests or additions to existing CLI test file):

| Test | Purpose |
|------|---------|
| `test_keyword_form_error_message` | Keyword resolve with bad trigger → error contains `"No memory entry for"` and `"Read agents/memory-index.md"`. No STOP directive. |
| `test_artifact_form_error_message` | Artifact resolve with stale key → error contains `"STOP:"` and `"stale key in recall artifact"`. No index-read guidance. |

### test_validation_memory_index_formats.py

| Test | Change |
|------|--------|
| `test_fuzzy_bidirectional_integrity` | **Rewrite:** exact matching behavior. Entry key must exactly match heading key. |
| `test_collision_detection` | **Rewrite:** collision requires identical keys after exact matching. Adjust fixture entries. |

## Sequencing

1. **Pre-flight:** Run current validator, then prototype exact validator against live data. Enumerate mismatches.
2. **Data fixes:** Fix trigger/heading mismatches in `agents/memory-index.md` and `agents/decisions/*.md`.
3. **Validator changes:** Make validator exact (`memory_index_checks.py`, `memory_index.py`). Update validator tests. Verify precommit passes.
4. **Resolver changes:** Remove fuzzy from resolver. Update resolver tests. Verify precommit passes.

Validator before resolver: validator must catch mismatches before resolver starts rejecting them.
