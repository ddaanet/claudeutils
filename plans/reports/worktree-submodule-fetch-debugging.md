# Worktree Submodule Fetch Debugging Report

**Date:** 2026-02-10
**Issue:** wt-merge failed to fetch from worktree submodule
**Status:** Fixed

## Problem

When merging worktree `rca-cycle-metadata`, the `wt-merge` recipe failed at the submodule fetch step:

```
fatal: 'wt/rca-cycle-metadata/agent-core' does not appear to be a git repository
```

**Root cause:** The recipe attempted to fetch from the worktree's agent-core using its path:
```bash
git fetch "$wt_dir/agent-core" HEAD
```

This failed because the worktree's agent-core is itself a git worktree, not a regular repository. Its `.git` file is just a pointer (70 bytes):
```
gitdir: ../../../.git/worktrees/rca-cycle-metadata/modules/agent-core
```

## Investigation

1. **Checked if commit exists in main agent-core:** No - commit c113d31 was created in the worktree and doesn't exist in main
2. **Attempted direct fetch from worktree path:** Failed - git can't fetch from worktree directories
3. **Solution:** Fetch from the git directory path instead of the worktree path

## Fix

Updated `justfile` line 212 to fetch from the worktree's git directory:

```bash
# Before
(cd agent-core && visible git fetch "$wt_dir/agent-core" HEAD)

# After
(cd agent-core && visible git fetch "../.git/worktrees/$slug/modules/agent-core" HEAD)
```

**Why this works:** Git worktrees for submodules store their objects in `.git/worktrees/$slug/modules/$submodule_name`. Fetching from this path accesses the actual git repository data.

## Related Learning

Existing learning "Git worktree submodule gotchas" mentions `--reference <local-checkout>` for worktree creation, but didn't cover fetching FROM worktree submodules during merge.

## Testing

After fix:
- ✅ Submodule fetch succeeded
- ✅ Submodule merge completed (fast-forward)
- ✅ Parent merge succeeded (session.md conflict resolved)
- ✅ Precommit validation passed

## Worktree-Skill Revision Notes

The worktree-skill design/runbook should include:

1. **Submodule worktree structure:** Document that submodule worktrees use `.git` file pointers to `.git/worktrees/$slug/modules/$submodule_name`
2. **Fetch path pattern:** Use git directory path, not worktree path
3. **Merge conflict handling:** Session.md conflicts expected when both sides have pending tasks - extraction logic needed
4. **Precommit cache:** Cache staleness after merge is expected (justfile changes)

## Commits

- e5d31a2: Initial worktree cleanup fixes
- 1197f75: Fix worktree submodule fetch to use git directory path
- 0cc3d59: Merge agent-core from rca-cycle-metadata (submodule)
- 4baee09: Merge rca-cycle-metadata (parent)
