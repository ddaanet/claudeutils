# Review: Phase 5 Checkpoint — Commit Parser + Vet Check

**Scope**: `src/claudeutils/session/commit.py`, `src/claudeutils/session/commit_gate.py`, `tests/test_session_commit.py`
**Date**: 2026-03-20T23:38:57
**Mode**: review + fix

## Summary

Phase 5 implements the commit markdown parser (Cycle 5.1), file validation gate (Cycle 5.2), and scripted vet check (Cycle 5.3). The parser is structurally sound and the gate logic is correct. Three issues found: `lstrip("- ")` corrupts filenames/options starting with `-`, the step spec requires hardcoded `agent-core` patterns that were not implemented, and the parametrized test structure creates vacuous branches where assertions are never reached.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **`lstrip("- ")` corrupts paths/options starting with `-`**
   - Location: `src/claudeutils/session/commit.py:40` (`_parse_files`), `commit.py:48` (`_parse_options`)
   - Problem: `lstrip("- ")` strips any leading combination of `-` and space characters, not just the `"- "` prefix. Input `"- -deleted.py"` produces `"deleted.py"` instead of `"-deleted.py"`. Same defect in `_parse_options` — option `"- -flag"` would strip the leading dash. `removeprefix("- ")` is the correct primitive.
   - **Status**: FIXED

2. **Missing hardcoded `agent-core` patterns in `vet_check`**
   - Location: `src/claudeutils/session/commit_gate.py:131` (`vet_check`)
   - Problem: Step 5.3 impl spec says: "Hardcode `agent-core/bin/**`, `agent-core/skills/**/*.sh` patterns (not configurable). Config model for submodule patterns deferred to separate plan." The implementation reads only `pyproject.toml` patterns. Agent-core scripts are never checked regardless of config.
   - **Status**: FIXED

### Minor Issues

1. **Parametrized test has unreachable branch structure**
   - Location: `tests/test_session_commit.py:49-75` (`test_parse_commit_input`)
   - Problem: The parametrized test calls `parse_commit_input` once per invocation and then branches on `section` parameter. Each invocation checks one section — the other `elif` branches are dead for that run. This is structurally sound but creates the false impression that all branches are tested together. The deeper issue: none of the 4 parametrize values assert `isinstance(result, CommitInput)` as a meaningful check since parsing would raise rather than return a non-`CommitInput`. The `isinstance` assert is vacuous.
   - **Status**: FIXED

2. **`_git_output` helper is defined but unused in Phase 5**
   - Location: `src/claudeutils/session/commit_gate.py:26-38`
   - Problem: `_git_output` is defined alongside `_dirty_files` and `_head_files` but only the latter two use `subprocess` directly. `_git_output` uses `subprocess.run` with `check=False` and `strip()` — consistent with the module's pattern. It is not dead code (Phase 6 pipeline will use it), but its presence with no callers in this phase is worth noting.
   - **Status**: OUT-OF-SCOPE — Phase 6 is the consumer; this is scaffolding for the next cycle, consistent with the TDD pattern used throughout this runbook.

3. **`test_vet_check_pass` relies on filesystem mtime ordering without explicit control**
   - Location: `tests/test_session_commit.py:272-289`
   - Problem: The test creates the source file after the report, relying on creation order to produce newer mtime for the report. In fast filesystems with coarse mtime resolution (1-second), the source file created immediately after the report may get the same mtime, causing the test to fail intermittently. The stale test (`test_vet_check_stale`) correctly uses `os.utime` to set an explicit old time. The pass test should also use `os.utime` to pin the report to an old mtime.
   - **Status**: FIXED

## Fixes Applied

- `src/claudeutils/session/commit.py:40` — `_parse_files`: replaced `lstrip("- ")` with `removeprefix("- ")` to avoid stripping leading dashes from filenames
- `src/claudeutils/session/commit.py:48` — `_parse_options`: replaced `lstrip("- ")` with `removeprefix("- ")` for the same reason
- `src/claudeutils/session/commit_gate.py:131` — `vet_check`: added `_AGENT_CORE_PATTERNS` constant (`agent-core/bin/**`, `agent-core/skills/**/*.sh`) merged with pyproject.toml patterns before matching
- `tests/test_session_commit.py:12` — removed now-unused `CommitInput` import (was only used in the vacuous `isinstance` assert)
- `tests/test_session_commit.py:53` — `test_parse_commit_input`: removed vacuous `isinstance` assert; each parametrize branch now asserts only its meaningful property
- `tests/test_session_commit.py:283` — `test_vet_check_pass`: added `os.utime` to pin source mtime to 10 seconds ago so report is reliably newer; eliminates timing-dependent pass/fail

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| C-1: `require-review` patterns from pyproject.toml | Satisfied | `_load_review_patterns()` reads `[tool.claudeutils.commit].require-review` |
| C-1: No patterns → check passes (opt-in) | Satisfied | `vet_check` returns `VetResult(passed=True)` when `not patterns` |
| C-1: Report discovery `plans/*/reports/` matching `*vet*` or `*review*` | Satisfied | `_find_reports()` globs correctly |
| C-1: Freshness check mtime newest source vs newest report | Satisfied | `_newest_mtime` + comparison logic |
| C-1: Hardcoded agent-core patterns | Partial → FIXED | Was missing; now added |
| C-3: Clean files → error with STOP directive | Satisfied | `CleanFileError.__init__` formats per design |
| C-5: Amend mode accepts files in HEAD commit | Satisfied | `validate_files(amend=True)` unions dirty + HEAD files |
| Section parsing: `## Message` content to EOF is body | Satisfied | `_split_sections` accumulates all lines after `## Message` heading |
| Unknown options → error (fail-fast) | Satisfied | `_parse_options` raises `CommitInputError` |
| `no-edit` without `amend` → error | Satisfied | `_validate` checks both orderings |
| `no-edit` + `## Message` → error (contradictory) | Satisfied | `_validate` detects this case |

---

## Positive Observations

- `_split_sections` correctly handles `## ` headings inside blockquote body (they're accumulated as lines, not parsed as headings) because only top-level `## ` at line start is matched.
- `_dirty_files` correctly avoids `strip()` on the raw stdout, preserving the porcelain XY format for accurate path extraction.
- `_head_files` uses `--root` with `diff-tree` which handles the initial commit case (no parent) correctly.
- Using `PurePath.full_match` (not `match`) is correct for anchor patterns like `src/**/*.py` — `match` does suffix matching and would give wrong results. The step spec suggestion of `fnmatch or PurePath.match` would have been incorrect.
- `validate_files` cleanly separates dirty-file and head-file discovery into distinct helpers, making the amend logic readable.
