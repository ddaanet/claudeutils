# Deliverable Review: handoff-cli-tool (RC14)

**Date:** 2026-03-26
**Methodology:** agents/decisions/deliverable-review.md
**Review type:** Full-scope (no delta-scoping per learnings)
**Layers:** L1 (3 opus agents: code, test, prose+config) + L2 (interactive cross-cutting)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1889 | -97 | +1792 |
| Test | 21 | +4158 | -111 | +4047 |
| Agentic prose | 2 | +10 | -10 | +0 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **51** | **+6059** | **-220** | **+5839** |

### RC13 Fix Verification

All 18 RC13 minors verified fixed. All 3 RC13 corrector fixes verified. 4 dismissals reconfirmed.

| RC13 Finding | Category | Status |
|-------------|----------|--------|
| m-1 blank line preservation | Code | **FIXED** — append uses `list(current.splitlines())`; autostrip uses `if not line.strip() or line.rstrip() not in committed_set` |
| m-2 `_detect_write_mode` tuple return | Code | **FIXED** — returns `tuple[str, str]`, eliminates duplicate `git show HEAD:` |
| m-3 status error accuracy | Code | **FIXED** — `{n} task lines without required metadata` replaces misleading "old-format" |
| m-5 comparison consistency | Code | **FIXED** — `.strip("\n")` on extracted sections, `.rstrip()` in set/list construction |
| m-6 empty diagnostics guard | Code | **FIXED** — `if git_output.strip()` guards diagnostic output |
| m-7 splitlines consistency | Code | **FIXED** — `splitlines(keepends=True)` + `.strip("\n")` for section extraction |
| m-8 fixture ordering | Test | **FIXED** — `SESSION_FIXTURE` defined before first usage |
| m-9 assertion specificity | Test | **FIXED** — specific strings replace generic assertion words |
| m-10 split conflated tests | Test | **FIXED** — `_init_repo_with_session` helper; three independent functions |
| m-11 removed redundant test | Test | **FIXED** — pre-H-2 test removed |
| m-13 comment rewrite | Test | **FIXED** — comments describe mode-detection rationale |
| m-14 autostrip error fallback | Test | **FIXED** — `test_detect_write_mode_overwrite_on_no_head` |
| m-15 resume from write_session | Test | **FIXED** — `test_handoff_resume_from_write_session` |
| m-17 `_detect_write_mode` unit test | Test | **FIXED** — `test_detect_write_mode_all_three_modes` |
| m-18 STOP directive alignment | Prose | **FIXED** — "STOP — wait for guidance" matches communication rule 1 |
| m-19 H-2 reference clarity | Prose | **FIXED** — descriptive behavior replaces opaque outline identifier |
| Corrector: rstrip consistency | Code | **FIXED** — autostrip `committed_set` and filter predicate both use `.rstrip()` |
| Corrector: assertion strength | Test | **FIXED** — `== "append"` replaces `!= "autostrip"` |
| Corrector: block header check | Test | **FIXED** — `"**Git status:**" not in result.output` |
| m-4 defensive guard (dismissed) | Code | **CONFIRMED** — `len > 3` is minimum valid porcelain line length |
| m-20 design/SKILL.md scope (dismissed) | Prose | **CONFIRMED** — standalone bugfix, not handoff-cli deliverable |
| m-21 settings.local.json (dismissed) | Config | **CONFIRMED** — POSIX trailing newline only |
| m-22 .gitignore broadening (dismissed) | Config | **CONFIRMED** — handles sandbox artifacts |

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Code (2)

**m-1** `commit_pipeline.py:193-215` — functional correctness — `_strip_hints` has redundant `prev_was_hint = True` in both branches of the conditional at lines 204-209. Tab/double-space branch filters the line; single-space branch keeps it. Both set `prev_was_hint = True`, making the per-branch assignment factored out. Logic obscures intent. No functional impact.

**m-2** `commit_gate.py:31-50` — modularity — `_git_output` duplicates `git.py:_git()` with minor signature differences (`cwd` param, `check=False` default). Acknowledged via TODO on line 41. Carried from prior rounds.

### Test (5)

**m-3** `test_git_cli.py:15-67` / `test_session_commit_pipeline_ext.py:22-35` / `test_session_handoff_cli.py:142-236` — conformance — Inconsistent submodule setup helpers. Three approaches: (1) git plumbing `update-index --cacheinfo 160000`, (2) shared `pytest_helpers.create_submodule_origin` + `add_submodule`, (3) manual setup with 20 subprocess calls. Carried from RC13 m-12 (expanded: third variant identified).

**m-4** `test_session_commit_pipeline_ext.py:133-136` — specificity — `test_commit_submodule_orphan_message` asserts exact warning prose including punctuation. Tight coupling to format string. Key fragments would be more resilient.

**m-5** `test_session_status.py:132` — specificity — `test_render_pending_next_task_format` asserts exact arrow-line string equality. Display format change would break assertion without functional regression.

**m-6** `test_session_handoff.py:217-232` — vacuity — `test_write_completed_with_accumulated_content` does not commit session.md before calling `write_completed`, so `_detect_write_mode` returns `"overwrite"`. Exercises same path as basic overwrite test.

**m-7** `test_session_handoff_cli.py:371-391` — coverage — `test_handoff_resume_from_write_session` does not assert state file cleared after resume. Coverage exists in adjacent tests. Carried from corrector deferred item.

### Prose+Config (3 carried dismissals)

**m-8** `agent-core/skills/design/SKILL.md:135-139` — scope — Standalone bugfix (competing-execution-paths learning). Not a handoff-cli deliverable. Dismissed.

**m-9** `.claude/settings.local.json` — vacuity — POSIX trailing newline change only. Dismissed.

**m-10** `.gitignore:17` — scope — `/.vscode/` to `/.vscode` broadening. Handles sandbox artifacts. Dismissed.

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | `session/` with `handoff/` and `status/` sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | `git.py`; all worktree modules import from `claudeutils.git` |
| S-3: Output and error conventions | Covered | stdout-only, exit 0/1/2, `**Error:**` format, STOP directives |
| S-4: Session.md parser | Covered | `session/parse.py` composes existing functions |
| S-5: Git changes utility | Covered | `git_cli.py` with submodule iteration |
| H-1: Domain boundaries | Covered | CLI writes status + completed; agent owns other sections |
| H-2: Committed detection | Covered | Three modes with correct normalization |
| H-3: Diagnostic output | Covered | `git_changes()` after writes, empty-output guard |
| H-4: State caching + step_reached | Covered | HandoffState + resume logic |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + report freshness |
| C-2: Submodule coordination | Covered | 4-state matrix, pointer staging |
| C-3: Input validation + STOP | Covered | CleanFileError with STOP directive |
| C-4: Validation levels | Covered | Orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered | diff-tree, directional propagation |
| ST-0: Worktree-destined tasks | Covered | Marker check skips for Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5 |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2 |
| Registration in cli.py | Covered | `_handoff`, `_commit`, `_status`, `_git` |
| Coupled skill update | Covered | Handoff SKILL.md Step 7 precommit gate |

## Cross-Cutting Analysis (Layer 2)

- **Path consistency:** `CLAUDEUTILS_SESSION_FILE` env var consistent between handoff (`handoff/cli.py:38`) and status (`status/cli.py:51`) ✓
- **API contract alignment:** All exception types (`CommitInputError`, `CleanFileError`, `HandoffInputError`) caught at CLI boundaries with S-3 compliant exit codes ✓
- **Naming uniformity:** Error classes (`*Error`), data classes (`*Input`, `*Result`, `*Data`, `*State`), private functions (`_*`) — consistent patterns ✓
- **`_fail()` consolidation:** Single definition in `git.py:38`, imported by `session/cli.py`, `handoff/cli.py`, `status/cli.py` ✓
- **Import chain (S-2):** All worktree modules (`merge.py`, `merge_state.py`, `remerge.py`, `resolve.py`, `git_ops.py`, `cli.py`) import from `claudeutils.git`. No remaining `worktree.utils` imports ✓
- **Fragment convention:** Skill changes follow established patterns ✓
- **State file coverage:** `tmp/.handoff-state.json` covered by existing gitignore ✓
- **Coupled skill update:** Precommit gate delivered (SKILL.md Step 7). CLI composition deferred to skill-cli-integration plan ✓

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 10 (7 active + 3 dismissed) |

**RC13 closure:** All 18 addressed minors verified fixed. All 3 corrector fixes verified. All 4 dismissals reconfirmed. No regressions from the fix cycle.

**New findings:** 6 new minors (1 code clarity, 2 test specificity, 1 test vacuity, 1 test coverage note, 1 submodule helper expansion). All style/resilience — no functional impact.

**Carried:** m-2 (`_git_output` duplication, TODO'd), m-3 (submodule helpers, expanded from m-12), m-7 (resume state clearing, deferred). Three dismissed scope/config notes.

**Trend:** RC9 0C/2M/13m → RC10 0C/2M/13m → RC11 0C/2M/15m → RC12 1C/0M/22m → RC13 0C/0M/22m → RC14 0C/0M/10m. Minors reduced from 22 to 10. Both original majors resolved (RC12). Critical regression introduced and closed (RC12→RC13). RC13 fix cycle resolved 18 of 22 minors cleanly.
