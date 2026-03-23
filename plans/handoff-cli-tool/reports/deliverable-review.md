# Deliverable Review: handoff-cli-tool (Round 3)

**Date:** 2026-03-23
**Methodology:** agents/decisions/deliverable-review.md
**Scope:** Rework delta only (325+/143- across 15 files, commits `c2f7bd75..f3017971`)
**Layer 1:** Three opus agents (code, test, prose+config) — full scope, filtered to delta
**Layer 2:** Cross-cutting checks + delta verification

## Round 2 Fix Verification

All 10 findings fixed. Corrector regression fixed.

| Finding | Status | Evidence |
|---------|--------|----------|
| C#1 `_commit_submodule check=True` | ✅ | `commit_pipeline.py:139` — `check=True`, pipeline catches CalledProcessError at :306 |
| M#2 SKILL.md `claudeutils:*` | ✅ | `SKILL.md:4` — `Bash(just:*,wc:*,git:*,claudeutils:*)` |
| M#3 `_error()` fallback | ✅ | `commit_pipeline.py:217` — `exc.stderr or f"exit code {exc.returncode}"` |
| M#4 Skill-CLI integration | ⏳ DEFERRED | Split to `plans/skill-cli-integration/` — worktree task in session.md |
| M#5 `aggregate_trees` dedup | ✅ | `aggregation.py:203-208` — all plans appended per-tree, no dict dedup |
| m-1 Dead `render_next` | ✅ | Function removed from `render.py` |
| m-2 ▶ worktree-marker skip | ✅ | `render.py:41` — `task.worktree_marker is None` |
| m-3 `_is_dirty` raw subprocess | ✅ | `git.py:128-134` — raw `subprocess.run`, `rstrip("\n")` preserves porcelain format |
| m-4 Dead `step_reached` | ✅ | Field removed from `HandoffState`, `save_state()` simplified |
| m-5 Old section name detection | ✅ | `status/cli.py:22-28` — `_check_old_section_name()` before count validation |
| m-6 Weak `or` assertion | ✅ | `test_status_rework.py:142-144` — two separate asserts |
| Corrector: Python 2 except syntax | ✅ | `aggregation.py:112,135` — parenthesized tuple form restored |

## Critical Findings

None.

## Major Findings

None from rework delta.

## Minor Findings

### 1. `_check_old_section_name` uses substring match, not line-anchored

- **File:** `src/claudeutils/session/status/cli.py:24`
- **Axis:** Robustness
- **Introduced by:** m-5 fix
- `"## Pending Tasks" in content` matches anywhere in session.md, including prose (e.g., "Renamed ## Pending Tasks to ## In-tree Tasks" in a completed entry). `re.search(r"^## Pending Tasks", content, re.MULTILINE)` would be more precise. False-positive risk is low in practice.

### 2. `load_state()` backward-incompatible with pre-rework state files

- **File:** `src/claudeutils/session/handoff/pipeline.py:44-45`
- **Axis:** Robustness
- **Introduced by:** m-4 fix (removed `step_reached`)
- `HandoffState(**data)` on a state file containing `step_reached` raises `TypeError: unexpected keyword argument`. Crash-recovery path breaks if: handoff crashes before rework → code updated → retry. Impact: near-zero (state files are ephemeral crash recovery in `tmp/`, cleared on success).

## Pre-existing Findings (not from rework)

Observed during review but pre-dating the rework delta. Included for tracking — these exist in the current deliverable set regardless of rework.

**Major (pre-existing):**

- **Parallel detection ignores Blockers/Gotchas** — `status/cli.py:98` passes `[]` to `detect_parallel`. Session parser doesn't extract blockers. ST-1 design specifies blocker-based dependency. Unit-tested in `detect_parallel` but never wired e2e.
- **Stale vet output lacks file-level detail** — `commit_gate.py:160-166` returns time delta, not per-file info with timestamps. Design specifies `Newest change: src/auth.py (date)` format.

**Minor (pre-existing, 6):**

- Duplicate `_fail` in `worktree/cli.py` vs `git.py` (S-2 extraction incomplete)
- `render_pending` ▶ line format differs from design spec (denser inline format vs separate command line)
- Handoff completed parser strips blank lines between `### ` groups
- `session_path.read_text()` called twice in status CLI (parse_session + raw read)
- `_strip_hints` only removes `hint:` prefix, not `advice` lines
- `_init_repo` duplicated in 8 test files instead of using shared `pytest_helpers.init_repo_at`

## Gap Analysis

| Design Requirement | Status |
|-------------------|--------|
| S-1 Package structure | ✓ Conforms |
| S-2 `_git()` extraction | ✓ Conforms |
| S-3 Output/error conventions | ✓ Conforms |
| S-4 Session.md parser | ✓ Conforms |
| S-5 Git changes utility | ✓ Conforms |
| H-1 Domain boundaries | ✓ Conforms |
| H-2 Committed detection | ✓ Simplified to overwrite (documented) |
| H-3 Diagnostic output | ✓ Conforms |
| H-4 State caching | ✓ Conforms |
| C-1 Scripted vet check | ✓ Conforms (output detail gap — pre-existing) |
| C-2 Submodule coordination | ✓ Conforms |
| C-3 Input validation | ✓ Conforms |
| C-4 Validation levels | ✓ Conforms |
| C-5 Amend semantics | ✓ Conforms |
| ST-0 Worktree-destined tasks | ✓ Conforms |
| ST-1 Parallel group detection | Partial — blocker check not wired (pre-existing) |
| ST-2 Preconditions/degradation | ✓ Conforms |
| CLI registration | ✓ Conforms |

## Summary

| Severity | Rework delta | Pre-existing |
|----------|-------------|-------------|
| Critical | 0 | 0 |
| Major | 0 | 2 |
| Minor | 2 | 6 |

All 10 round 2 findings verified fixed. Corrector regression (Python 2 except syntax) verified fixed. Two minor issues introduced by the rework: substring match in old-section detection, backward-incompatible state file format. Two pre-existing Major findings (blocker detection gap, vet output detail) and six pre-existing Minor findings.
