# Deliverable Review: when-resolve-fix

**Date:** 2026-02-27
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

Deliverables from commit `e6806939`:

| Type | File | + | - |
|------|------|---|---|
| Code | `src/claudeutils/when/cli.py` | +49 | -16 |
| Code | `src/claudeutils/when/resolver.py` | +6 | -13 |
| Code | `src/claudeutils/when/navigation.py` | 0 | -191 |
| Test | `tests/test_when_cli.py` | +115 | -1 |
| Test | `tests/test_when_resolver.py` | +4 | -4 |
| Test | `tests/test_when_navigation.py` | 0 | -277 |

**Total:** 6 files, +174 / -502 (net -328)

Design conformance: brief.md specifies Phase 2 — dedup, stdin, navigation simplification. All three delivered. Prior corrector review: 0C/0M/1m (stale docstring, fixed).

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Style/Clarity

1. **`_resolve_queries` parameter name `arg`** — `cli.py:43`: loop variable `for arg in queries` reads as CLI argument, not query. **FIXED:** renamed to `query`.

2. **`_collect_queries` type annotation** — `cli.py:22`: accepts `tuple[str, ...]` (Click's type) but converts to `list` immediately. Kept as-is: documents the actual Click call site, and `Sequence` import adds churn for no behavioral change.

### Robustness

3. **Stdin ordering undocumented** — `cli.py:26`: args come first, then stdin lines. **FIXED:** added docstring noting ordering.

### Test

4. **No test for dedup + error interaction** — Tests covered dedup-only and error-only batches. **FIXED:** added `test_dedup_with_error`.

## Gap Analysis

| Design requirement | Status | Reference |
|---|---|---|
| Deduplicate fuzzy matches | Covered | `_resolve_queries` seen-set, tests `test_dedup_identical_results` / `test_dedup_preserves_distinct` |
| Accept queries on stdin | Covered | `_collect_queries` stdin reader, 5 stdin tests |
| Remove sibling/related navigation | Covered | `navigation.py` deleted, no remaining imports |
| Replace broader links with `Source:` path | Covered | `resolver.py:233` builds source_path, `test_resolve_output_format` asserts |
| `click.UsageError` for no-queries | Covered | `cli.py:72`, `test_no_queries_error` + `test_dot_prefix_preserved` assertion |

**Cross-cutting checks:**
- Path consistency: `source_path` format (`agents/decisions/{file}`) matches project convention ✓
- API contract: `_collect_queries` → `_resolve_queries` → `click.echo` chain correct ✓
- Navigation removal complete: no `navigation` imports in source or test tree ✓
- Click pattern: `required=False` + manual guard is correct for stdin support (recall: Click `required=True` rejects stdin-only invocations) ✓
- Error signaling: `click.UsageError` follows recall decision (consolidated display+exit) ✓
- `# noqa: TRY003` justified: Click framework exception, not custom class target ✓

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 4 (3 fixed, 1 kept as-is) |

All design requirements covered. Navigation removal clean — no orphaned references. 28/28 tests pass after fixes.
