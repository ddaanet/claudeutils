# Runbook Outline: Worktree Merge Resilience

## Requirements Mapping

| Requirement | Phase | Key Decision |
|---|---|---|
| FR-1: Submodule conflict pass-through | Phase 2 | D-6 |
| FR-2: Parent merge preservation | Phase 3 | D-3 |
| FR-3: Untracked file collision | Phase 3 | D-4 |
| FR-4: Conflict context output | Phase 4 | D-8 |
| FR-5: Idempotent resume | Phase 1 | D-5 |
| NFR-1: Backward-compatible exit codes | Phase 5 | D-1 |
| NFR-2: No data loss | Phase 3 | D-7 |
| C-1: Skill contract | Phase 5 | — |
| C-2: Non-interactive compatibility | Phase 5 | — |

## Phase Structure

### Phase 1: State detection + idempotent resume (type: tdd)

**Scope:** Add `_detect_merge_state(slug)` function to `merge.py`. Rewrite `merge()` entry point to detect state and route to appropriate phase. States: `merged`, `parent_resolved`, `parent_conflicts`, `submodule_conflicts`, `clean`.

- Cycle 1.1: `_detect_merge_state` + routing — `merged` state: slug is ancestor of HEAD → Phase 4 only (integration: real git repo in tmp_path, verify pre-merge phase skipped)
- Cycle 1.2: `_detect_merge_state` + routing — `parent_resolved` state: MERGE_HEAD exists, no unresolved conflicts → Phase 4 (integration: manually put repo in mid-merge-resolved state, verify re-run completes)
- Cycle 1.3: `_detect_merge_state` + routing — `parent_conflicts` state: MERGE_HEAD exists with unresolved conflicts → exit 3, no destructive ops (integration: put repo in mid-merge-conflicted state, verify exit 3 + MERGE_HEAD preserved)
- Cycle 1.4: `_detect_merge_state` + routing — `submodule_conflicts` state: agent-core MERGE_HEAD exists → check conflict status, continue to Phase 3 (integration: manually put agent-core in mid-merge state, verify Phase 3 entry)

**Dependencies:** None (foundation phase).
**Affected files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_merge_head.py` (new or existing)
**Complexity:** High — state machine with 5 branches, each requires distinct git state setup.

### Phase 2: Submodule conflict pass-through (type: tdd)

**Scope:** Change `_phase2_resolve_submodule` to use `check=False` on `_git("-C", "agent-core", "merge", ...)`. On non-zero return: leave agent-core MERGE_HEAD, continue to Phase 3 (do not raise). Re-running Phase 2 when submodule already merged is a no-op (existing skip logic).

Depends on: Phase 1 (state machine must handle `submodule_conflicts` before Phase 2 can be tested via re-run).

- Cycle 2.1: Submodule merge conflict — agent-core MERGE_HEAD preserved, pipeline continues to Phase 3 (integration: set up diverged submodule on both sides, verify `_phase2` doesn't abort, verify agent-core MERGE_HEAD exists)
- Cycle 2.2: Resume after manual submodule resolution — Phase 2 skip (already merged), pipeline proceeds to Phase 3 (integration: resolve agent-core conflict manually + stage, re-run `_worktree merge`, verify Phase 2 skipped via commit history)

**Depends on:** Cycle 1.4.
**Affected files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_submodule.py`
**Complexity:** Medium — behavioral change to submodule merge path, error handling.

### Phase 3: Parent merge preservation + untracked handling (type: tdd)

**Scope:** Three changes to `_phase3_merge_parent`:
1. Remove `_git("merge", "--abort")` + `_git("clean", "-fd")` (lines 170-175) — replace with report + `raise SystemExit(3)` (D-3, NFR-2)
2. Add untracked-file-collision detection: parse `git merge` stderr for "Your local changes to the following files would be overwritten", `git add` each file, retry merge (D-4)
3. Update two existing tests in `test_worktree_merge_errors.py` that assert abort behavior

Updates existing tests:
- `test_merge_aborts_cleanly_when_untracked_file_blocks`: setup has file untracked on main with different content than branch → conflict markers + exit 3 (not generic error)
- `test_merge_conflict_surfaces_git_error`: source file conflict → exit 3, MERGE_HEAD preserved, no "aborted" message

- Cycle 3.1: Source conflict → MERGE_HEAD preserved, no abort, exit 3 (FR-2, NFR-2) — updates `test_merge_conflict_surfaces_git_error` (integration: real conflict in non-session file, assert exit 3, assert MERGE_HEAD still present, assert no --abort)
  - Depends on: Cycle 1.3 (state machine must handle parent_conflicts before this path is exercised via re-run)
- Cycle 3.2: Untracked file same-content as incoming → `git add` + retry → merge proceeds to Phase 4 (FR-3, D-4) — updates `test_merge_aborts_cleanly_when_untracked_file_blocks` to cover same-content case (integration: untracked file on main with identical content to branch, assert exit 0, assert file tracked post-merge)
- Cycle 3.3: Untracked file different-content → conflict markers in file + exit 3 (FR-3, D-4) — new test (integration: untracked file on main with different content from branch, assert exit 3, assert conflict markers in file, assert MERGE_HEAD present)

**Depends on:** Cycles 1.3, 2.1 (Phase 3 behavior tested after Phase 1 routing is correct).
**Affected files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_errors.py`
**Complexity:** High — core behavioral change, untracked file detection, stderr parsing.

### Phase 4: Conflict context output (type: tdd)

**Scope:** Add `_format_conflict_report(conflicts, slug)` function to `merge.py`. Called from Phase 3 before `raise SystemExit(3)` and from state machine `parent_conflicts` path. Output contract (FR-4): conflicted file list with conflict type (`git diff --name-only --diff-filter=U` + conflict type via `git status --short`), per-file diff stats (`git diff MERGE_HEAD -- <file>` stat), branch divergence summary (`git rev-list --count HEAD..slug` and `slug..HEAD`), hint line.

- Cycle 4.1: Conflict output includes file list with conflict type and per-file diff stat (integration: trigger conflict, capture exit-3 output, assert file path + conflict type label + diff stat lines present)
- Cycle 4.2: Conflict output includes branch divergence summary and hint text (integration: trigger conflict, assert commit count lines present on each side, assert hint contains "Resolve conflicts" and `claudeutils _worktree merge <slug>`)

**Depends on:** Cycle 3.1 (exit 3 path must exist before output format matters).
**Affected files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_conflicts.py` or new `tests/test_worktree_merge_resilience.py`
**Complexity:** Medium — output formatting, multiple git queries for context.

### Phase 5: Exit code threading + skill update + stdout unification (type: general)

**Scope:** Three independent changes. Must not be split — each is complete in one step per prose atomicity and D-8 unification.

- Step 5.1: Audit all `raise SystemExit(1)` in `merge.py` — update conflict-pause paths (unresolved conflicts, MERGE_HEAD present) to `raise SystemExit(3)`. Keep `SystemExit(1)` for error paths (precommit failure, git command failure). Verify no paths remain that abort merge state silently. (NFR-1)
  - Affected: `src/claudeutils/worktree/merge.py`
  - Execution model: Sonnet (code audit + judgment on error vs conflict classification)
- Step 5.2: Migrate all `click.echo(..., err=True)` → `click.echo()` in `merge.py` (D-8, C-2). All output to stdout. Exit code is the semantic signal. (Single step covers all occurrences — prose atomicity)
  - Affected: `src/claudeutils/worktree/merge.py`
  - Execution model: Haiku (mechanical substitution, ~8 call sites)
- Step 5.3: Update `agent-core/skills/worktree/SKILL.md` Mode C — add exit code 3 handling: "Parse merge exit code 3 (conflicts, merge paused). Read stdout for conflict report. For each conflicted file listed: edit to resolve conflicts, `git add <file>`. Re-run `claudeutils _worktree merge <slug>` to resume." Update existing exit-1 handling to distinguish precommit failure (still exit 1) from conflict-pause (now exit 3). All SKILL.md changes in this step. (C-1, prose atomicity)
  - Affected: `agent-core/skills/worktree/SKILL.md`
  - Execution model: Opus (prose artifact, LLM-consumed)

**Depends on:** Phases 1–4 (all exit code semantics must be stable before documenting).
**Affected files:** `src/claudeutils/worktree/merge.py`, `agent-core/skills/worktree/SKILL.md`
**Complexity:** Low — mechanical audit + mechanical substitution + prose update.

## Key Decisions Reference

- **D-1:** Exit 3 = "merge paused, conflicts need resolution". Exit 1 = error. Exit 2 = fatal.
- **D-3:** Remove abort lines 170-175. Remaining conflicts → report + exit 3. No path discards staged auto-resolutions.
- **D-4:** Parse untracked-file stderr, `git add` each file, retry merge. One code path for same/different content.
- **D-5:** State machine entry detects: `merged` | `parent_resolved` | `parent_conflicts` | `submodule_conflicts` | `clean`.
- **D-6:** `_git("-C", "agent-core", "merge", ...)` → `check=False`, handle returncode explicitly.
- **D-7:** Audit every error/conflict handler. No `--abort`, no `clean -fd`, no discard of staged content.
- **D-8:** All output via `click.echo()` (stdout). Migrate all `err=True` call sites.

## Expansion Guidance

- Testing diamond: integration tests (real git repos, tmp_path) are primary for all TDD phases. No subprocess mocks for git operations. Unit tests only if combinatorial coverage needed.
- Prose atomicity: all SKILL.md edits in Step 5.3 only. Do not split across steps.
- Self-modification ordering: Phase 5 (SKILL.md + exit code threading) is last — implementation complete before documentation.
- D-7 audit: Step 5.1 must enumerate every `raise SystemExit` in merge.py and classify each as error (1) / fatal (2) / conflict-pause (3). Do not update D-3 paths until Phase 3 GREEN is complete.
- Phase 3 note: `_git("merge", "--abort")` removal is the primary data-loss fix. Verify no other code path calls `--abort` or `clean -fd` (grep merge.py).
- Cycle 3.1 prerequisite: Read `merge.py:137-175` before implementing to understand exact abort location and what follows it.
- Cycle 4.1 prerequisite: Read `merge.py` Phase 3 and state-machine entry after Phase 1 implementation to understand call sites for `_format_conflict_report`.
- Existing test updates: Cycles 3.1 and 3.2 each update one existing test in `test_worktree_merge_errors.py`. These updates are RED-phase changes (update test to assert new behavior; implementation still old → test fails). GREEN implements fix.
