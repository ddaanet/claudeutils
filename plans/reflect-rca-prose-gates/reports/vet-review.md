# Vet Review: Prose Gates D+B Hybrid Fix Implementation

**Scope**: Review of prose gates fix implementation across 5 files
**Date**: 2026-02-06T17:30:00Z

## Summary

Implementation merges standalone prose gates into adjacent action steps with Read/Bash anchoring to prevent execution-mode skipping. Commit skill consolidates steps 0+0b+1 into single gated Step 1. Orchestrate skill merges phase boundary detection (3.4) into post-step verification (3.3). Documentation and cross-references updated consistently.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Learnings.md stale reference to old step numbers**
   - Location: agents/learnings.md:74
   - Problem: "Fix: Added Step 0b (vet checkpoint) to commit skill" references the OLD structure (separate Step 0b) when the fix actually MERGED it into Step 1 (Gate B)
   - Fix: Update to "Fix: Merged session freshness (Gate A) and vet checkpoint (Gate B) into Step 1 with Read/Bash anchoring — commit skill D+B hybrid"

2. **Gate B git merge-base fallback may be too broad**
   - Location: agent-core/skills/commit/SKILL.md:111
   - Problem: Fallback `HEAD~5` when upstream not found is arbitrary — could miss files or check too many depending on session length
   - Suggestion: Document this limitation in the comment, or use `git log --oneline | wc -l` to determine appropriate depth dynamically
   - **Note:** Not blocking — fallback handles edge case reasonably, just lacks documentation of trade-off

### Minor Issues

1. **Implementation-notes.md entry could be more concise**
   - Location: agents/decisions/implementation-notes.md:196-222
   - Note: Entry is comprehensive (27 lines) — could trim "Why hybrid beats either alone" bullet and "Changes" section since they duplicate outline.md content. Keep Problem, Fix (D+B Hybrid), Convention, Design reference.
   - This is a style preference — no action required if current verbosity is intentional.

2. **Design comment placement inconsistency**
   - Location: Commit SKILL.md line 86 vs Orchestrate SKILL.md line 94
   - Note: Commit skill places design rule comment BEFORE Gate A heading. Orchestrate skill places it AFTER section heading "3.3" but BEFORE prose paragraph. Both work, but inconsistent.
   - Suggestion: Standardize on "comment immediately before first prose content" (orchestrate pattern) for consistency.

---

## Positive Observations

**Comprehensive cross-reference updates:**
- All learnings.md references to orchestrate step numbers correctly updated (3.4→3.3)
- Memory-index.md entry uses title-words format ("Prose Gate D+B Hybrid Fix") matching decision entry
- Implementation-notes.md documents the "Why hybrid" rationale clearly

**Control flow clarity:**
- Commit skill Gate A and Gate B use explicit "If stale: ... Return here after" and "If unvetted: STOP, delegate" branching
- Orchestrate skill 3.3 uses "IF same phase: proceed to 3.4" conditional with explicit targets

**Tool call anchoring correct:**
- Commit Gate A opens with `Read agents/session.md` providing data for freshness check
- Commit Gate B opens with `git diff --name-only` and `git status` providing data for vet check
- Orchestrate 3.3 opens with `git status --porcelain` for tree check, then `Read` next step header for phase detection

**Validation bash block preserved:**
- Commit skill Step 1 still has the original validation bash block at the end with heredoc comment requirement and precommit logic

**git merge-base scope improvement:**
- Outline.md:43 correctly identifies that `git merge-base HEAD @{u}` scopes to session branch divergence vs old approach (just last commit)
- This catches files changed throughout the session, not just the most recent edit

## Recommendations

1. Update learnings.md line 74 to reflect merged structure instead of "Added Step 0b"
2. Document the `HEAD~5` fallback limitation in Gate B bash comment (e.g., `# Fallback to 5 commits if no upstream — may miss old changes in long sessions`)
3. Consider standardizing design rule comment placement (suggest orchestrate pattern: after section heading, before prose)

## Next Steps

1. Apply the single major fix (learnings.md stale reference)
2. Optional: Add fallback documentation comment to Gate B bash block
3. Commit with message: "♻️ Fix prose gate skipping with D+B hybrid pattern"

## Requirements Validation

**No requirements context provided in task prompt.** Reviewing against design outline only.

| Design Requirement | Status | Evidence |
|-------------------|--------|----------|
| Eliminate standalone prose gates | Satisfied | Commit 0+0b+1→1, Orchestrate 3.4→3.3 |
| Anchor with Read/Bash tool call | Satisfied | Gate A: Read session.md, Gate B: git diff, 3.3: git status + Read step |
| Explicit control flow | Satisfied | "If/then" branching with explicit targets |
| Convention documentation | Satisfied | implementation-notes.md:218 + HTML comment in both skills |
| No new files/fragments | Satisfied | Only edits to existing files |
| No retroactive changes to other skills | Satisfied | Only commit and orchestrate modified |

**Gaps:** None. All outline requirements satisfied.
