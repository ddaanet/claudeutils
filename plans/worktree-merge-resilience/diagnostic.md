# Merge Artifact Diagnostic

## Observed: context-optimization merge (c330b7d2)

Merge base: `3bf9e28d` (pipeline-skill-updates focused session commit)

### learnings.md — two artifacts

**Artifact 1: Orphaned line at tail**
- Branch modified line 53 in-place ("When selecting reviewer" — changed "in vet-requirement.md" to "before selecting", removed "always-loaded" claim)
- Main added 8 new entries at tail (from when-recall-evaluation + pipeline-improvements merges)
- Branch added 1 new entry at tail + replaced main's 8 entries (branch diverged before those merges)
- Result: Git's 3-way merge applied the in-place edit correctly at line 53 BUT also appended the branch's version of line 53 at the tail (line 168), orphaned from its heading

**Artifact 2: Missing newline at EOF**
- Both sides modified the last line (no trailing newline). Standard git merge artifact.

**Root cause hypothesis:** The in-place edit (line 53) and tail divergence created two conflict regions that git resolved independently. The line-53 change was a clean merge (only branch modified it). The tail region had both sides adding different content — git kept main's additions AND appended the branch's modified line as if it were a new addition.

### session.md — leaked blocker note

- Branch session.md had a learnings consolidation note in a different section position
- Main session.md had a Blockers section the branch didn't have
- Merge appended branch's note into main's blockers section (line 94)

**Pattern:** Focused worktree sessions strip sections that main has. On merge, content from the branch that was positioned relative to removed sections gets placed at wrong positions.

## Prior instance: pipeline-improvements merge (cf890e39)

learnings.md merged cleanly — branch only appended entries, no in-place modifications.

## Reproduction conditions

1. Branch diverges from main
2. Main receives additional merges (adding entries to tail of append-only files)
3. Branch modifies an existing entry in-place AND adds new entries at tail
4. `_worktree merge` uses git's standard 3-way merge (ort strategy)
5. The in-place edit produces a "clean" merge at the original location, but the modified line ALSO appears in the tail conflict resolution as new content

## Affected files

Only append-only files with in-place edits during branch lifetime:
- `agents/learnings.md` — most vulnerable (append-only with occasional in-place corrections)
- `agents/session.md` — vulnerable when focused sessions strip sections

## Existing mitigations

- Blocker in session.md: "Manual post-merge check required" — catch and fix manually
- Learning: "When merging worktree with consolidated learnings" — delta-only pattern

## Potential fixes

- Custom merge driver for learnings.md (line-set union, detect duplicates)
- Post-merge validation script in `_worktree merge` (detect duplicate learnings headings, orphaned bullet lines)
- Pre-merge rebase onto main (eliminates divergence, but conflicts move to rebase)
