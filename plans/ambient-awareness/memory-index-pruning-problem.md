# Problem: Memory Index Pruning Criteria

## Issue

The memory index soft limit (100 entries) lacks clear, actionable pruning criteria.

**Current guidance:**
> "When approaching this limit, review for entries where the rule has been promoted to always-loaded fragments (making the index entry redundant)."

**Problems:**
1. **Circular logic**: If a rule is important enough to promote to always-loaded, why remove the index entry? The index serves discovery across ALL fragments, not just non-@-referenced ones.
2. **No clear trigger**: "Promoted to always-loaded" is vague - promoted when? By what process? Remember skill doesn't auto-promote.
3. **Missing growth model**: What happens when we legitimately have >100 consolidated learnings? Do we just keep growing? Cap at 100 and lose knowledge?

## Context

Memory index design (Part 1) specifies:
- One line per consolidated learning
- Grouped by domain (Behavioral, Workflow, Technical, Tool)
- Soft limit 100 entries
- Maintained by `/remember` skill during consolidation

The index is always-loaded (`@`-imported in CLAUDE.md) to provide passive awareness of what knowledge exists.

## Design Question

**What should the pruning criteria actually be?**

Options:
- **A) No pruning, just growth**: Accept that the index will grow. At 100 entries × 100 chars ≈ 2500 tokens, still reasonable for always-loaded context. Soft limit becomes "consider splitting by domain into separate files."
- **B) Redundancy-based pruning**: Remove entry when the fragment it references is `@`-imported in CLAUDE.md (redundant to list it in index AND import it unconditionally).
- **C) Staleness-based pruning**: Remove entries for rules that haven't been relevant in N consolidation cycles (requires tracking metadata).
- **D) Coverage-based pruning**: When a fragment gets comprehensive enough, remove individual learning entries and replace with one "see fragment X for Y domain" entry.

## Current Workaround

Changed to: "review for entries where the rule has been promoted to always-loaded fragments"

Still doesn't solve the fundamental question: **when is it correct to remove knowledge from the index?**

## Next Steps

Need design decision on pruning model before implementation is complete.
