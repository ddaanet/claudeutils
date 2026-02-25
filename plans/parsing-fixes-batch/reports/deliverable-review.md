# Deliverable Review: parsing-fixes-batch

**Date:** 2026-02-25
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

Changes span parent repo and `agent-core` submodule (commit `d47722a`).

| Type | File | + | - |
|------|------|---|---|
| Code | `agent-core/bin/validate-runbook.py` | 43 | 25 |
| Code | `agent-core/bin/prepare-runbook.py` | 0 | 1 |
| Code | `src/claudeutils/validation/memory_index_checks.py` | 0 | 1 |
| Test | `tests/fixtures/validate_runbook_fixtures.py` | 46 | 0 |
| Test | `tests/test_validate_runbook.py` | 335 | 353 |
| Test | `tests/test_prepare_runbook_phase_context.py` | 278 | 353 |

**Design conformance:** All 7 plan items covered. No missing deliverables. Unspecified changes (test helper extraction, formatting cleanup) are justified refactoring.

## Critical Findings

None.

## Major Findings

1. **CLI `--known-file` argument path untested** — `test_validate_runbook.py`
   - Plan specifies: "Update `cmd_lifecycle()` to accept `--known-file` repeated option"
   - Implementation exists (lines 354-360: argparse `action="append"`) and wired through `cmd_lifecycle` (line 192)
   - Tests exercise `check_lifecycle(known_files=...)` directly but never invoke the CLI with `--known-file`
   - The argparse path (`getattr(args, "known_file", None) or []` → `set()`) is untested
   - Axis: functional completeness
   - Note: plan's RED phase targeted the function contract, not CLI — consistent with TDD spec, but the CLI plumbing has zero coverage

2. **`test_model_tags_non_markdown_artifact_not_flagged` bypasses `_run_validate` helper** — `test_validate_runbook.py:234-254`
   - All other tests were refactored to use `_run_validate` helper (the stated goal of "test file compaction")
   - This test manually does `monkeypatch.setattr(sys, "argv", ...)` + `try/main()/except SystemExit` + manual report read
   - Could use `_run_validate(monkeypatch, tmp_path, "model-tags", "script-runbook", NON_MARKDOWN_ARTIFACT)`
   - Axis: functional correctness (consistency of test infrastructure)

## Minor Findings

**Style:**
- `from datetime import UTC` imported at module level (line 6) while `from datetime import datetime` remains lazy inside `write_report()` — inconsistent import pattern. Pre-existing lazy import, but this batch added the top-level UTC.
- Incidental formatting changes in validate-runbook.py (single→double quotes on regex strings, ternary expression for `report_dir`, `re.compile` string normalization) — unspecified by plan, harmless.

## Gap Analysis

| Plan Item | Status | Reference |
|-----------|--------|-----------|
| #1: model-tags extension filter | Covered | `validate-runbook.py:29`, test + fixture |
| #2: lifecycle known_files | Covered (function), partial (CLI) | `validate-runbook.py:116-179`, tests unit-only |
| #3: C1 model propagation verify | Covered | `TestModelPropagation.test_phase_model_overrides_frontmatter` |
| #4: C2 phase numbering verify | Covered | `TestModelPropagation.test_gapped_phase_numbering_preserved` |
| #5: C3 phase context verify | Covered | `TestPhaseContextCompleteness.test_post_cycle_content_not_in_preamble` |
| #6: Dead code prepare-runbook | Covered | `prepare-runbook.py:450` line removed |
| #7: Dead code memory_index_checks | Covered | `memory_index_checks.py:44` line removed |

**Additional deliverables (unspecified):**
- `_run_validate` helper extracted in test_validate_runbook.py — reduces boilerplate
- `_run_prepare` helper extracted in test_prepare_runbook_phase_context.py — reduces boilerplate
- Both test files under 400-line limit (254 and 283 lines)

## Summary

- Critical: 0
- Major: 2
- Minor: 2

All 7 plan items implemented and verified. 21/21 tests pass. Major findings are test coverage gaps (CLI arg path, helper consistency) — neither affects runtime correctness.
