# Deliverable Review: handoff-cli-tool (RC15)

**Date:** 2026-03-26
**Methodology:** agents/decisions/deliverable-review.md
**Review type:** Full-scope (no delta-scoping per learnings)
**Layers:** L1 (2 opus agents: code, test) + L2 (interactive cross-cutting + prose/config)

## Inventory

| Type | Files | + | - | Net |
|------|-------|---|---|-----|
| Code | 26 | +1870 | -97 | +1773 |
| Test | 21 | +4099 | -111 | +3988 |
| Agentic prose | 2 | +10 | -10 | +0 |
| Configuration | 2 | +2 | -2 | +0 |
| **Total** | **51** | **+5981** | **-220** | **+5761** |

### RC14 Fix Verification

All 7 RC14 active minors verified fixed. All 3 RC14 dismissed items reconfirmed. No regressions from the fix cycle.

| RC14 Finding | Status | Evidence |
|-------------|--------|----------|
| m-1 `_strip_hints` clarity | **FIXED** | `commit_pipeline.py:193-213` — redundant `prev_was_hint = True` removed; named `is_continuation` boolean; single conditional append |
| m-2 `_git_output` consolidation | **FIXED** | `commit_gate.py` no longer defines `_git_output`; `_head_files` uses `_git(check=False, cwd=cwd)` |
| m-3 submodule helper standardization | **FIXED** | `test_git_cli.py` and `test_session_handoff_cli.py` use canonical `create_submodule_origin` + `add_submodule`; plumbing approach eliminated |
| m-4 orphan-message assertion loosening | **FIXED** | Key fragments (`"no changes found"`, `"agent-core"`) replace exact prose |
| m-5 arrow-line assertion loosening | **FIXED** | Four fragment checks replace exact string equality |
| m-6 vacuous test fix | **FIXED** | `test_write_completed_with_accumulated_content` commits baseline, exercises autostrip path |
| m-7 resume state clearing | **FIXED** | `assert not (tmp_path / "tmp" / ".handoff-state.json").exists()` added |
| m-8 design/SKILL.md scope (dismissed) | **CONFIRMED** — standalone bugfix, not handoff-cli deliverable |
| m-9 settings.local.json (dismissed) | **CONFIRMED** — POSIX trailing newline only |
| m-10 .gitignore broadening (dismissed) | **CONFIRMED** — sandbox artifact handling |

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

### Code (5 active + 2 dismissed)

**m-1** `git.py:34-37` — excess — `_git_ok()` has no production callers (no import in `src/`). Tests exist (`test_git_helpers.py:22-33`) but no production code uses it. Extracted alongside `_git()` but not referenced by any session/worktree module.

**m-2** `handoff/pipeline.py:12` — robustness — `_STATE_FILE = Path("tmp") / ".handoff-state.json"` is relative to cwd. The `session_path` uses `CLAUDEUTILS_SESSION_FILE` env var but state file has no equivalent anchor. Low practical risk (CLI runs from project root), but inconsistent with session_path's resolution pattern.

**m-3** `commit_pipeline.py:203-211` — functional correctness — `_strip_hints`: when a non-continuation indented line is kept after a hint, `prev_was_hint` stays True. Subsequent indented lines are still evaluated against hint context. Correct for known git output (single-space prefix for file stats, tab/double-space for continuations), but the assumption about git output format is implicit.

**m-4** `status/render.py:44-48` — conformance — `▶` line always shows `({model})` including default `sonnet`. Non-▶ items suppress default: `f" ({model})" if model != "sonnet" else ""`. Inconsistent display between first-task and remaining-task formatting.

**m-5** `git.py:65-70` — functional correctness — `discover_submodules` calls `line.strip()` before `split()`, discarding the leading status character (`+`/`-`/`U`/space) that distinguishes submodule states. No functional impact for path extraction. Status character not needed by any current caller.

**m-6** `status/render.py:164-169` — robustness — `detect_parallel` uses O(n² × cap) consecutive window search. With cap=5 and typical n<20, negligible. **Dismissed** — algorithm is simple and readable; optimization would add complexity without measurable benefit.

**m-7** `status/render.py:120-128` — functional correctness — `_build_dependency_edges` uses substring matching on concatenated blocker text. Common-word task names create false dependencies. **Dismissed** — conservative direction documented in code comment (line 120): "may create false dependency edges... never enables unsafe parallelism."

### Test (3 active)

**m-8** `test_session_status.py:77-83` — specificity — `test_render_section` (worktree parametrization) creates task with `worktree_marker="wt"` but only asserts `"Future work" in result`. Does not assert `"→ wt" in result`. Assertion passes even if `render_worktree` drops the `→ wt` suffix.

**m-9** `test_session_status.py:20-38,56` — independence — `_task()` helper omits `plan_dir` from construction; tests set it post-construction (`t1.plan_dir = "parser"`). Couples to dataclass mutability. Low risk — standard dataclass behavior.

**m-10** `test_session_integration.py:17-80` — coverage — Single integration test covers handoff→status happy path. No error-recovery integration scenario (e.g., handoff failure → subsequent status consistency). Adequate for Phase 7 TDD scope but below "end-to-end across subcommands" aspiration.

### Prose+Config (3 carried dismissals)

**m-11** `agent-core/skills/design/SKILL.md:135-139` — scope — Standalone bugfix (competing-execution-paths learning). Not a handoff-cli deliverable. **Dismissed.**

**m-12** `.claude/settings.local.json` — vacuity — POSIX trailing newline change only. **Dismissed.**

**m-13** `.gitignore:17` — scope — `/.vscode/` to `/.vscode` broadening. Handles sandbox artifacts. **Dismissed.**

## Gap Analysis

| Design Requirement | Status | Reference |
|-------------------|--------|-----------|
| S-1: Package structure | Covered | `session/` with `handoff/` and `status/` sub-packages |
| S-2: `_git()` extraction + submodule discovery | Covered | `git.py` with `cwd` param; all worktree modules import from `claudeutils.git` |
| S-3: Output and error conventions | Covered | stdout-only, exit 0/1/2, `**Error:**` format, STOP directives |
| S-4: Session.md parser | Covered | `session/parse.py` composes existing `extract_task_blocks` + `parse_task_line` |
| S-5: Git changes utility | Covered | `git_cli.py` — `changes_cmd` with submodule iteration |
| H-1: Domain boundaries | Covered | CLI writes status + completed; agent owns other sections |
| H-2: Committed detection | Covered | Three modes (overwrite/append/autostrip) with normalization |
| H-3: Diagnostic output | Covered | `git_changes()` after writes, guarded empty-output check |
| H-4: State caching + step_reached | Covered | HandoffState dataclass + resume logic + state file cleanup |
| C-1: Scripted vet check | Covered | pyproject.toml patterns + `PurePath.full_match()` + report freshness |
| C-2: Submodule coordination | Covered | 4-cell matrix, pointer staging, multi-submodule ordering |
| C-3: Input validation + STOP | Covered | CleanFileError with STOP directive; exit 2 |
| C-4: Validation levels | Covered | Orthogonal just-lint/no-vet options |
| C-5: Amend semantics | Covered | diff-tree + --root, directional propagation, no-edit validation |
| ST-0: Worktree-destined tasks | Covered | Marker check skips for Next selection |
| ST-1: Parallel detection | Covered | Consecutive windows, cap 5, dependency edges |
| ST-2: Preconditions | Covered | Missing file/old format → exit 2; metadata mismatch → exit 2 |
| Registration in cli.py | Covered | `_handoff`, `_commit`, `_status`, `_git` group |
| Coupled skill update | Covered | Handoff SKILL.md has `claudeutils:*` in allowed-tools |

## Cross-Cutting Analysis (Layer 2)

- **Path consistency:** `CLAUDEUTILS_SESSION_FILE` env var consistent between handoff (`handoff/cli.py:38`) and status (`status/cli.py:51`) ✓
- **API contract alignment:** All exception types (`CommitInputError`, `CleanFileError`, `HandoffInputError`, `SessionFileError`) caught at CLI boundaries with S-3 compliant exit codes ✓
- **Import chain (S-2):** All worktree modules (`merge.py`, `merge_state.py`, `remerge.py`, `resolve.py`, `git_ops.py`, `cli.py`) import from `claudeutils.git`. No remaining `worktree.utils` imports ✓
- **`_fail()` consolidation:** Single definition in `git.py:40`, imported by `session/cli.py`, `handoff/cli.py`, `status/cli.py`, `recall_cli/cli.py`, `worktree/cli.py` ✓
- **Naming uniformity:** Error classes (`*Error`), data classes (`*Input`, `*Result`, `*Data`, `*State`), private functions (`_*`) — consistent patterns ✓
- **Porcelain safety:** `_dirty_files` uses raw `result.stdout.splitlines()` (line 45); `_git()` docstring warns against porcelain use (line 19); `git_status()` uses `rstrip("\n")` preserving XY format ✓
- **PurePath.full_match:** `commit_gate.py:135` uses `full_match()` per Python 3.13+ requirement (learning verified) ✓
- **PEP 758 syntax:** `worktree/cli.py:103,176` uses unparenthesized except per Python 3.14+ convention ✓
- **State file coverage:** `tmp/.handoff-state.json` covered by existing gitignore (`tmp/` entry) ✓

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 13 (8 active + 5 dismissed) |

**RC14 closure:** All 7 active minors verified fixed. All 3 dismissed items reconfirmed. No regressions.

**New findings:** 8 active minors — 5 code (1 dead code, 1 robustness, 2 correctness notes, 1 display inconsistency), 3 test (1 specificity, 1 independence, 1 coverage). All style/robustness-class — no functional defects.

**Dismissed:** 5 — 2 new (documented conservative design, algorithm within bounds), 3 carried (out-of-scope changes).

**Trend:** RC9 0C/2M/13m → RC10 0C/2M/13m → RC11 0C/2M/15m → RC12 1C/0M/22m → RC13 0C/0M/22m → RC14 0C/0M/10m → RC15 0C/0M/13m (8 active). New minors are uniformly lower-severity than RC14's (no carried findings from prior rounds). Both original majors resolved (RC12). All design requirements covered.
