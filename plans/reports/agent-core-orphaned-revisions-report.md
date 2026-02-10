# Agent-Core Orphaned Revisions Analysis

**Date:** 2026-02-10
**Analyst:** Sonnet
**Current agent-core HEAD:** fd0c120c8f2c83ebdcd8e1089703530d23126f28

## Executive Summary

**Result:** No orphaned revisions found.

All 131 unique agent-core commits referenced in the parent repository's history are reachable from the current agent-core HEAD. The submodule is fully synchronized with no missing work.

## Methodology

1. **Extracted all submodule pointers:** Scanned parent repo history (`git log --all -- agent-core`) to find all commits that touched the agent-core submodule
2. **Identified unique SHAs:** Extracted 131 unique agent-core commit SHAs from these references
3. **Checked ancestry:** Verified each SHA with `git merge-base --is-ancestor <sha> HEAD` in agent-core
4. **Validated remote branches:** Checked all remote worktree branches for unmerged commits

## Statistics

**Parent repository:**
- Total commits touching agent-core: 134
- Unique agent-core commits referenced: 131

**Agent-core submodule:**
- Current HEAD: fd0c120c8f2c83ebdcd8e1089703530d23126f28
- Total commits on main: 259
- Total branches: 6

## Branch Status

All remote worktree branches are fully merged into HEAD:

- `remotes/wt/bash-git-prompt` → Fully merged
- `remotes/wt/continuation-passing` → Fully merged
- `remotes/origin/wt/plugin-migration` → Fully merged

## Recent Merge Activity

The agent-core commit graph shows extensive recent merge activity:

```
*   fd0c120 (HEAD -> main) Merge commit 'ee60491a'
|\
| * ee60491 🤖 Add deslop directives to agent templates
*   f4f0756 Merge commit '78d1d92'
|\
| * 78d1d92 Strengthen vet delegation with execution context and UNFIXABLE protocol
```

These merges incorporate work from multiple worktree branches that were previously identified as potentially orphaned in session.md (see "Review agent-core orphaned revisions" task context).

## Historical Context

The session.md task mentioned checking for "agent-core commits reachable from parent repo history but not on current HEAD." This concern was valid during the 2026-02-08/09 timeframe when multiple worktree branches existed with uncommitted work (see learnings.md "wt-merge empty submodule failure" and "Submodule commit orphan recovery").

**Previous orphan recovery example:**
- Commit ff056c7 (focus-session.py) was orphaned when dev branch was reset to main
- Recovered via `git -C agent-core merge <orphaned-commit>`

The current analysis shows all such recoveries have been completed successfully.

## Verification

**Three-layer verification:**

1. **Ancestry check:** All 131 unique submodule SHAs pass `git merge-base --is-ancestor` test
2. **Branch check:** All remote worktree branches report "Fully merged into HEAD"
3. **Parent pointer check:** Sampled 50 recent parent commits — all submodule pointers are reachable from current HEAD

## Recommendations

**No action required.**

The agent-core submodule is in excellent shape:
- All worktree branches merged
- No orphaned commits detected
- Clean merge history
- All parent references satisfied

## Future Prevention

To prevent orphaned commits in the future:

1. **Before branch operations:** Use `git merge-base --is-ancestor <submodule-sha> HEAD` to check ancestry
2. **After worktree merge:** Verify submodule pointer with `git ls-tree HEAD -- agent-core`
3. **Regular audits:** Run this analysis periodically (monthly or when closing multiple worktrees)

The `just wt-merge` recipe now includes submodule merge logic to prevent this class of issue.

## Conclusion

The review found zero orphaned revisions. All agent-core work referenced in parent repository history is properly incorporated into the current HEAD. The task can be marked complete.
