# Code Review: handoff-cli-tool (Round 3)

**Reviewer:** Opus 4.6
**Design reference:** `plans/handoff-cli-tool/outline.md`
**Scope:** 25 code files, +1585 lines. Full conformance review against design outline.

## Round 2 Fix Verification

| Finding | Fix Status |
|---------|-----------|
| C#1 `_commit_submodule check=True` | FIXED — `commit_pipeline.py:139` uses `check=True` |
| M#2 SKILL.md `claudeutils:*` | FIXED — verified in prior review report |
| M#3 `_error()` fallback | FIXED — `commit_pipeline.py:217` uses `exc.stderr or f"exit code {exc.returncode}"` |
| m-1 Dead `render_next` | FIXED — no `render_next` in `src/` (grep confirmed) |
| m-2 ▶ skips worktree-marked tasks | FIXED — `render.py:41` checks `task.worktree_marker is None` |
| m-3 `_is_dirty` raw subprocess | FIXED — `git.py:128-134` uses raw `subprocess.run` with `rstrip("\n")` |
| m-4 Dead `step_reached` field | FIXED — no `step_reached` in `src/` (grep confirmed) |
| m-5 Old section name detection | FIXED — `status/cli.py:22-28` checks before count validation |
| m-6 Weak `or` assertion | FIXED — per prior review verification |
| Corrector: `except ValueError, AttributeError` | FIXED — `aggregation.py:112,135` restored parenthesized tuples |

All 10 round 2 rework fixes verified. No regressions detected from the fix application.

## New Findings

### Critical

None.

### Major

**F-1: Parallel detection ignores Blockers/Gotchas section**

- `src/claudeutils/session/status/cli.py:98`
- Axis: Functional completeness
- Design ST-1: "Independent when: no shared plan directory, no logical dependency (Blockers/Gotchas)." The status CLI calls `detect_parallel(data.in_tree_tasks, [])` — always passing an empty blockers list. The session parser (`parse.py`) does not extract the Blockers/Gotchas section. `_build_dependency_edges` in `render.py:97-119` accepts blockers and joins their text for name-matching, but the input is always empty. Tasks linked via Blockers/Gotchas will be incorrectly classified as parallelizable.

**F-2: Stale report vet check output lacks file-level detail**

- `src/claudeutils/session/commit_gate.py:160-166`
- Axis: Conformance
- Design specifies stale-report output as:
  ```
  **Vet check:** stale report
  - Newest change: src/auth.py (2026-02-20 14:32)
  - Newest report: plans/foo/reports/vet-review.md (2026-02-20 12:15)
  ```
  Implementation returns `VetResult(stale_info=f"Source newer than reports by {delta}s")` — a time delta string, not per-file information with timestamps. The consumer at `commit_pipeline.py:176` renders this as `**Vet check:** stale report\n{vr.stale_info}`. The LLM consumer (commit skill) cannot identify which file is newest or which report to regenerate.

### Minor

**F-3: Duplicate `_fail` function in `worktree/cli.py`**

- `src/claudeutils/worktree/cli.py:66-68` vs `src/claudeutils/git.py:33-39`
- Axis: Modularity
- Design S-2 specifies extracting shared helpers to `claudeutils/git.py`. Session CLI files import `_fail` from `git.py`. The worktree CLI retains its own local `_fail` with identical behavior. Not a correctness issue — duplication adds maintenance risk (divergent fixes).

**F-4: `render_pending` ▶ line format deviates from design**

- `src/claudeutils/session/status/render.py:44`
- Axis: Conformance
- Design specifies:
  ```
  ▶ <first task> (<model>) | Restart: <yes/no>
    `<command>`
  ```
  Command on a separate indented line, model in parentheses, `Restart` capitalized. Implementation renders:
  ```
  ▶ <task> — `<cmd>` | <model> | restart: <restart>
  ```
  Command inline with the marker, model pipe-separated, lowercase `restart`. The implementation format is denser and arguably better for terminal display. Not a correctness issue but differs from design spec.

**F-5: Handoff completed parser strips blank lines between content groups**

- `src/claudeutils/session/handoff/parse.py:52`
- Axis: Functional correctness
- `parse_handoff_input` filters blank lines: `if line.strip():`. When the completed section contains multiple `### ` heading groups separated by blank lines, the parser strips the separators. `write_completed` in `pipeline.py:121` does not restore them. Result: heading groups written without blank-line separation, causing markdown rendering to merge list items across headings.

**F-6: `session_path.read_text()` called twice in status CLI**

- `src/claudeutils/session/status/cli.py:52,56`
- Axis: Robustness
- `parse_session(session_path)` reads the file at line 52, then `session_path.read_text()` reads it again at line 56 for `_check_old_section_name` and `_count_raw_tasks`. Between the two reads, the file could be modified by another process (unlikely but possible during concurrent agent sessions). The second read could see different content than what was parsed. A single read with content reuse would be safer.

**F-7: `_check_old_section_name` uses substring match**

- `src/claudeutils/session/status/cli.py:24`
- Axis: Robustness
- `if "## Pending Tasks" in content` matches the string anywhere in session.md, including prose content under other sections (e.g., "Renamed ## Pending Tasks to ## In-tree Tasks" in a completed-session entry). A line-anchored match `re.search(r"^## Pending Tasks", content, re.MULTILINE)` would be more precise.

**F-8: `_strip_hints` only removes `hint:` prefix, not continuation lines**

- `src/claudeutils/session/commit_pipeline.py:187-189`
- Axis: Functional completeness
- Design: "Strip git `hint:` and advice lines." Implementation strips lines starting with `hint:` but git hint output includes indented continuation lines (e.g., `hint:   Waiting for your editor to close the file...` followed by `hint:` on its own line). Continuation lines starting with whitespace or `advice.` lines would survive. Low impact — hint lines are rare in the commit use case, and over-filtering risks stripping legitimate output.

## Conformance Summary

| Design Section | Status |
|---------------|--------|
| S-1: Package structure | Conforms — `session/` package with cli, parse, commit, commit_gate, commit_pipeline, handoff/, status/ |
| S-2: `_git()` extraction | Conforms — extracted to `git.py`, worktree imports updated |
| S-3: Output/error conventions | Conforms — stdout only, exit codes 0/1/2, `**Header:** content` format |
| S-4: Session.md parser | Conforms — `parse.py` composes existing functions, handles both sections |
| S-5: Git changes utility | Conforms — `git_cli.py` provides `git_changes()` + `_git changes` CLI |
| H-1: Domain boundaries | Conforms — CLI writes status + completed only |
| H-2: Committed detection | Conforms — simplified to always-overwrite (documented, tested, reviewed) |
| H-3: Diagnostic output | Conforms — `git_changes()` emitted after writes |
| H-4: State caching | Conforms — `tmp/.handoff-state.json`, save before mutation, clear on success |
| C-1: Scripted vet check | Conforms — pyproject.toml patterns + agent-core patterns, report discovery |
| C-2: Submodule coordination | Conforms — partition, validate messages, commit submodule first |
| C-3: Input validation | Conforms — `validate_files` checks `git status --porcelain` + HEAD files for amend |
| C-4: Validation levels | Conforms — `just-lint`/`no-vet` options orthogonal |
| C-5: Amend semantics | Conforms — amend flag, no-edit flag, message validation |
| ST-0: Worktree-destined tasks | Conforms — ▶ skips tasks with worktree markers |
| ST-1: Parallel group detection | Partial — plan_dir check works, blocker check not wired (F-1) |
| ST-2: Preconditions and degradation | Conforms — missing session.md = exit 2, old format = exit 2 |
| Registration in `cli.py` | Conforms — `_handoff`, `_commit`, `_status`, `_git` all registered |

## Verdict

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 2 |
| Minor | 6 |

No critical issues. Two major findings: F-1 (parallel detection ignores blockers — functional completeness gap) and F-2 (stale vet output lacks file detail — conformance gap with design output format). Six minor findings covering code duplication, format deviations, edge-case robustness, and a blank-line stripping issue in handoff parsing.

The round 2 rework successfully addressed all 10 targeted findings with no regressions. The remaining issues are either conformance gaps against the detailed design output specifications or robustness improvements for edge cases.
