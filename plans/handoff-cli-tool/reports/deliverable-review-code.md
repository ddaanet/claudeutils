# Code Review: handoff-cli-tool (RC8)

**Date:** 2026-03-24
**Reviewer:** Opus 4.6 [1M]
**Files reviewed:** 25 code files (~1733 lines added)
**Methodology:** Full-scope review against outline.md design specification

## RC7 Fix Verification

RC7 had 0C/0M/0m on code. No code-specific fixes to verify (m-1, m-4, m-5, m-6 were test findings).

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

| # | File:Line | Axis | Description |
|---|-----------|------|-------------|
| m-1 | session/commit.py:38-40 | Robustness | `_parse_files` does not reject empty `## Files` section. A `## Files` section with no `- path` entries produces `files=[]`, passes `_validate` (only checks `files is None`), proceeds to pipeline where `git commit` fails with opaque "nothing to commit" error. Explicit empty-list check with clear error message would be more informative. |
| m-2 | session/handoff/cli.py:52 | Conformance | Resume path ignores `step_reached` from HandoffState. Outline H-4 defines `step_reached` values (`"write_session"`, `"diagnostics"`) implying resume should skip completed steps. Code always re-runs full pipeline. Functionally safe (writes are idempotent), but the field is vestigial — either honor it or remove it from the dataclass. |
| m-3 | session/commit_pipeline.py:334-336 | Robustness | `_git_commit(ci.message or "", ...)` passes empty string to `-m` when `ci.message is None` and `no_edit is False`. The `_validate_inputs` guard at line 262 prevents this path, but the `or ""` fallback masks a logic error if the guard is ever bypassed. An assertion or raising would be safer than silent empty-message fallback. |
| m-4 | session/handoff/pipeline.py:11 | Modularity | `_STATE_FILE = Path("tmp") / ".handoff-state.json"` is a module-level relative path. Works when cwd is project root (the normal case), but unlike other path handling in the codebase (e.g., `session_path` from env var in cli.py), this is not configurable. Consistent with outline H-4 spec (`<project-root>/tmp/`), but hardcoded assumption about cwd. |
| m-5 | session/commit_pipeline.py:193-213 | Robustness | `_strip_hints` continuation detection at line 204 has a complex nested condition: a tab or double-space after a hint line is treated as continuation. Single-space-prefixed lines that are NOT double-spaced would break continuation detection, emitting those lines. Edge case is unlikely in practice (git hint output uses consistent indentation), but the logic is fragile. |

## Carried Forward (not counted)

- `→ wt` marker not detected by `WORKTREE_MARKER_PATTERN` (pre-existing parser limitation, mitigated by section placement — worktree tasks are in Worktree Tasks section regardless of marker)

## Gap Analysis

| Design Requirement | Status |
|---|---|
| S-1: Package structure | Covered — session/ package with cli.py, parse.py, commit.py, commit_gate.py, commit_pipeline.py, handoff/, status/ |
| S-2: `_git()` extraction + submodule discovery | Covered — git.py with `_git`, `_git_ok`, `_fail`, `discover_submodules`, `_is_submodule_dirty`, `git_status`, `git_diff`, `_is_dirty` |
| S-3: Output and error conventions | Covered — all output to stdout via `click.echo`, exit 0/1/2 semantics, no stderr writes. `_fail` uses stdout. Subprocess stderr captured and surfaced through stdout channel |
| S-4: Session.md parser | Covered — parse.py composes `extract_task_blocks`, `parse_task_line`, `find_section_bounds`, `extract_blockers` |
| S-5: Git changes utility | Covered — git_cli.py with `git_changes()` function and `_git changes` CLI command. Submodule-aware, structured markdown output |
| H-1: Domain boundaries | Covered — CLI writes status + completed only. Pending tasks, learnings, blockers are agent-owned |
| H-2: Completed section write mode | Covered — uniform overwrite via `_write_completed_section`. Docstring acknowledges three modes collapse to single operation |
| H-3: Diagnostic output | Covered — unconditional git changes output at handoff/cli.py:57-58 |
| H-4: State caching | Covered — `tmp/.handoff-state.json` with save/load/clear lifecycle. `step_reached` stored but not used (m-2) |
| C-1: Scripted vet check | Covered — pyproject.toml patterns via `_load_review_patterns`, `_AGENT_CORE_PATTERNS` for agent-core, `_find_reports` discovery, mtime freshness comparison |
| C-2: Submodule coordination | Covered — `_partition_by_submodule`, message-presence validation, commit-first with pointer staging, orphaned message warning |
| C-3: Input validation | Covered — `CleanFileError` with STOP directive, amend-aware via `_head_files` union with `_dirty_files` |
| C-4: Validation levels | Covered — orthogonal just-lint/no-vet options, `_validate` dispatches to `_run_lint` or `_run_precommit` |
| C-5: Amend semantics | Covered — `amend`/`no-edit` flags propagated to `_git_commit` and `_commit_submodule`, message validation handles all four combinations |
| C-Message: EOF semantics | Covered — `in_message` flag in `_split_sections` prevents `## ` lines within message body from splitting sections |
| ST-0: Worktree-destined tasks | Covered — `worktree_marker is None` check in Next selection (render.py:45) |
| ST-1: Parallel detection | Covered — consecutive windows, dependency edges from shared plan_dir and blocker mentions, cap at `_PARALLEL_CAP = 5` |
| ST-2: Preconditions | Covered — missing session.md exit 2 (cli.py:56), old format exit 2 (cli.py:61-65), old section name exit 2 (cli.py:26-30) |
| Registration in cli.py | Covered — `_handoff`, `_commit`, `_status`, `_git` all registered (cli.py:155-158) |
| Hint stripping | Covered — `_strip_hints` in commit_pipeline.py removes `hint:` and `advice:` lines with continuation detection |
| Output formatting | Covered — `format_commit_output` with submodule labels, warning prepending, git passthrough for success |
| Error taxonomy | Covered — stop errors (CleanFileError exit 2, missing submodule message exit 1), warning+proceed (orphaned submodule message exit 0) |

## Cross-cutting Checks

- **Path consistency:** All imports between session submodules use correct relative paths. `ParsedTask` re-exported via `session/parse.py` `__all__`
- **API contract alignment:** `CommitInput` produced by `commit.py`, consumed by `commit_pipeline.py` and `commit_gate.py`. Fields match across boundaries
- **Naming conventions:** Consistent `_` prefix for internal functions, `cmd` suffix for CLI commands, `Error` suffix for exceptions
- **git.py extraction:** `_git`, `_fail`, `discover_submodules`, `_is_submodule_dirty` successfully extracted from worktree. Worktree modules import from `claudeutils.git` (verified via grep). `git_ops.py` re-exports `_is_dirty` and `_is_submodule_dirty` via `# noqa: F401` for backward compatibility

## Summary

| Severity | Count | Delta from RC7 |
|----------|-------|----------------|
| Critical | 0 | 0 (unchanged) |
| Major | 0 | 0 (unchanged) |
| Minor | 5 | +5 (new findings from full-scope review) |

Trend: RC4 2M/9m → RC5 2M/10m → RC6 1M/5m → RC7 0C/0M/0m → RC8 0C/0M/5m.

All 5 minors are robustness and modularity edge cases — no functional correctness issues. The codebase conforms to the design specification across all major requirements.
