# Code Review: handoff-cli-tool (RC12)

**Date:** 2026-03-25
**Methodology:** Full-scope review of all 26 code files against outline.md
**Review type:** RC11 fix verification + new finding scan

## RC11 Fix Verification

### Majors

**M-1 (H-2 committed detection): FIXED**
`pipeline.py:143-233` — `_detect_write_mode()` implements three-way classification:
- `committed == current` → "overwrite" (line 170)
- `committed_lines.issubset(current_lines)` → "autostrip" (line 180)
- else → "append" (line 183)

`write_completed()` dispatches on mode (lines 198-233): overwrite calls `_write_completed_section` directly; append extracts current non-blank lines, concatenates with new_lines; autostrip computes committed set, filters current to uncommitted lines, concatenates.

Corrector fix verified: `except ValueError, subprocess.CalledProcessError:` guard at line 217 handles both error paths in autostrip mode.

**M-2 (H-4 step_reached): FIXED**
`pipeline.py:16-22` — `HandoffState` has `step_reached: str = "write_session"` field.
`save_state()` accepts `step_reached` parameter (line 24).
`cli.py:47` — Fresh path saves with `step_reached="write_session"`.
`cli.py:59` — Resume path: `if state is None or state.step_reached != "diagnostics":` skips writes when already at diagnostics.
`cli.py:66` — After writes succeed, updates to `step_reached="diagnostics"`.
Backward compat: `load_state()` filters to known fields (line 49-50), defaulting `step_reached` to `"write_session"`.

### Code Minors

**m-1 (WORKTREE_MARKER_PATTERN documentation): FIXED**
`task_parsing.py:21-23` — Comment documents that bare `→ wt` (ST-0) won't match and those tasks belong in Worktree Tasks section.

**m-2/m-3 (submodule missing-message exit code): FIXED**
`commit_pipeline.py:275-278` — Missing submodule message now raises `CommitInputError`. `cli.py:26-27` catches `CommitInputError` with `code=2`. Redundant check at old location removed.

**m-4 (_strip_hints single-space continuation): FIXED**
`commit_pipeline.py:207-208` — Comment clarified: "Single-space indent: not a hint continuation, but keep hint context active (next line may be a continuation)."

**m-5 (_dirty_files -u flag): NOT FIXED (documented)**
`commit_gate.py:56` — Comment explains `-u` purpose. No code change, as expected.

**m-6 (git_changes() unconditional): NOT FIXED**
No comment added at `cli.py:69`. Session notes claim "comment added" but the call is uncommented. Trivial — git_changes() is fast and tree is almost certainly dirty after writes.

**m-7 (_build_dependency_edges substring matching): FIXED**
`render.py:118-120` — Comment documents conservative behavior.

**m-8 (list_plans relative path): FIXED**
`status/cli.py:67-68` — Comment documents cwd assumption.

**m-9 (testability comment): FIXED**
`commit_pipeline.py:25,43` — Both functions now have "Module-level for ``monkeypatch.setattr`` in tests."

**m-10 (TODO consolidate): FIXED**
`commit_gate.py:41` — TODO comment added for `_git_output` duplication.

**m-11 (SESSION_FIXTURE ordering): NOT FIXED**
`test_session_status.py:280` — `SESSION_FIXTURE` still defined at line 280, first used at line 253. Session notes claim "moved SESSION_FIXTURE before first usage" but it remains after. Python forward-references work at module level, so no functional impact.

**m-12 (assertion strings): CARRIED**
`test_session_commit_pipeline.py:108-153` — Assertion strings contextual with inline test data. Low risk.

### Corrector Fixes

**Unguarded CalledProcessError in autostrip: FIXED**
`pipeline.py:217` — `except ValueError, subprocess.CalledProcessError:` catches both error paths, falls back to plain overwrite on failure.

**Dead mock in step_reached test: FIXED**
No dead mocks observed in test_session_handoff.py or test_session_handoff_cli.py.

## New Findings

**1.** `session/handoff/pipeline.py:203,228` — functional correctness, Minor
Append and autostrip modes strip blank lines from current section content (`if line.strip()`) before combining with `new_lines`. If the current section has markdown structure (blank lines separating `###` sub-groups), that structure is lost. Both modes produce collapsed output missing inter-group spacing. Design H-2 doesn't specify blank-line preservation, but the handoff input format uses `###` headings which conventionally have blank-line separation.

**2.** `session/handoff/pipeline.py:206-219` — modularity, Minor
Autostrip mode duplicates the `_find_repo_root` + `git show HEAD:` sequence already executed inside `_detect_write_mode` (lines 149-164). The committed content is computed once during detection, discarded, then recomputed in `write_completed`. Could pass committed content from detection to avoid the extra `git show`. Performance impact negligible (one extra subprocess call).

**3.** `session/status/cli.py:60-65` — robustness, Minor
Old-format detection compares `_count_raw_tasks(content)` (lines matching `- [`) against `len(data.in_tree_tasks)` (successfully parsed tasks). If a task line matches `- [` but fails to parse (e.g., missing `**name**` bold markers), counts diverge and the CLI exits with misleading "Old-format tasks missing metadata" error. The actual issue would be malformed task lines, not old-format ones.

**4.** `session/commit_gate.py:66` — functional correctness, Minor
`_dirty_files()` checks `len(line) > 3` before extracting `line[3:]`. Porcelain format has a 3-character prefix (`XY `) followed by the path. The guard `> 3` skips lines with exactly 3 characters (status code + space, empty path). Git status never produces empty paths in practice, but the guard should be `>= 3` for correctness against the format specification.

**5.** `session/handoff/pipeline.py:173-178` — robustness, Minor
`_detect_write_mode` compares stripped lines between committed and current content to determine mode, but the stripping is one-way: `line.strip()` removes leading/trailing whitespace for set membership. If committed content has a line like `"  - indented item"` and current has `"- indented item"`, they would match after `.strip()`, causing mode detection to classify as "overwrite" when content actually differs. Edge case — session.md completed content is typically unindented.

**6.** `session/handoff/cli.py:70` — excess, Minor
Diagnostics output wraps `git_changes()` in a markdown fenced code block (```` ``` ````). When the tree is clean, `git_changes()` returns an empty string and the output becomes `` **Git status:**\n\n```\n\n``` `` — an empty code block. The `git_cli.py:68` `changes_cmd` handles this with "Tree is clean." but the handoff CLI calls `git_changes()` directly (the Python function, not the Click command), missing that fallback.

**7.** `session/handoff/pipeline.py:115-140` — robustness, Minor
`_extract_completed_section` uses `splitlines(keepends=True)` and `"".join()` to preserve line endings, but the two call sites handle the result differently: `_detect_write_mode` compares raw text with `==` (line 170, newline-sensitive) and `write_completed` splits with `.splitlines()` (line 228, newline-insensitive). A trailing newline difference between committed and current completed sections would cause `_detect_write_mode` to see a diff (not overwrite) while the content is semantically identical, potentially triggering append mode when overwrite was intended.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 7 |

**RC11 fix verification:** Both majors (M-1, M-2) confirmed fixed. 8 of 10 code minors fixed. 2 not addressed as expected (m-5 documented, m-6 no comment visible). 1 claimed fix not applied (m-11 SESSION_FIXTURE ordering). Corrector fixes verified.

**Trend:** RC9 0C/2M/13m → RC10 0C/2M/13m → RC11 0C/2M/15m → RC12 0C/0M/7m. Both long-standing majors resolved. All 7 new minors are from fresh full-scope review of the H-2/H-4 implementations — new code surface area that didn't exist in prior rounds.
