## 2026-03-02: Merge→rm lifecycle audit

### Context

5 worktree merges in one session exposed 3 distinct bugs at phase boundaries. All fixed individually, but the pattern indicates the merge→rm lifecycle needs systematic audit, not more point fixes.

### Bugs found this session

1. **Lifecycle.md dirty-state** (wt-rm-dirty, delivered): `_append_lifecycle_delivered` ran after merge commit, left lifecycle.md unstaged. Fix: moved into phase 4 before commit, return `list[Path]` for staging.

2. **Submodule conflict ordering** (merge-submodule-ordering, brief): Submodule MERGE_HEAD check runs after parent merge commit. On re-run, creates 1-parent fixup commit instead of amending the merge. Fix: move check before commit.

3. **Amend regression** (task-classification): `_update_session_and_amend` replaced with `_update_session` by task-classification design (D-4 conflated move semantics with post-merge hygiene). Fix: restored amend logic.

### Approach

1. Map the actual state machine: merge phases (validate → submodule → parent merge → commit → precommit → submodule check) and rm phases (dirty check → session update → amend → remove → prune → branch delete). Document assumptions each phase makes about prior phase output.

2. Enumerate integration seams — every phase boundary is a potential bug site.

3. Write integration tests for full merge→rm lifecycle sequences: merge-with-submodule-conflict→resolve→resume→rm, merge-with-lifecycle→rm→amend, merge-with-session-conflicts→rm.

4. Fix phase ordering issues found during audit.

### Absorbs

- merge-submodule-ordering (brief) — subsumed by lifecycle audit
- Related: wt-rm-task-cleanup (brief) — rm removing completed task entries. Separate concern but touches the same rm code path.

### Key files

- `src/claudeutils/worktree/merge.py` — merge phases, `_phase4_merge_commit_and_precommit`
- `src/claudeutils/worktree/cli.py` — `_update_session_and_amend`, `rm()`
- `src/claudeutils/worktree/remerge.py` — session.md/learnings.md structural merge
- `tests/test_worktree_rm_after_merge.py` — existing integration tests (from wt-rm-dirty)
