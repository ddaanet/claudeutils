# Simplification Report

**Outline:** plans/hook-batch/runbook-outline.md
**Date:** 2026-02-21

## Summary

- Items before: 19 (8 cycles Phase 1 + 3 cycles Phase 2 + 2 steps Phase 3 + 3 steps Phase 4 + 4 steps Phase 5)
- Items after: 14 (5 cycles Phase 1 + 2 cycles Phase 2 + 2 steps Phase 3 + 3 steps Phase 4 + 4 steps Phase 5)
- Consolidated: 5 items across 4 patterns

## Consolidations Applied

### 1. COMMANDS dict string updates (r + xc + hc)
- **Type:** identical-pattern
- **Items merged:** Cycle 1.2 (r expansion), Cycle 1.3 (xc/hc compression)
- **Result:** Cycle 1.2 — parametrized table with 3 COMMANDS keys
- **Rationale:** Same edit pattern (replace string value in COMMANDS dict), no branching logic, no inter-dependency. Review explicitly flagged these as consolidation candidates.

### 2. New directives with dual output (p:, b:, q:, learn:)
- **Type:** independent same-module functions
- **Items merged:** Cycle 1.5 (p: dual output), Cycle 1.6 (b:, q:, learn: dual output)
- **Result:** Cycle 1.4 — parametrized table with 4 directives, 7 aliases
- **Rationale:** All add expansion constants + DIRECTIVES dict entries using identical dual-output pattern (systemMessage + additionalContext). No inter-dependency beyond shared Cycle 1.3 prerequisite. 8 assertions at limit, not exceeding.

### 3. Pattern guards (skill-editing + CCG)
- **Type:** independent same-module functions
- **Items merged:** Cycle 1.7 (skill-editing guard), Cycle 1.8 (CCG integration)
- **Result:** Cycle 1.5 — parametrized table with 3 regex patterns
- **Rationale:** Both add regex patterns + detection blocks at Tier 2.5 with additionalContext-only injection. Same mechanism, same location in main(), no inter-dependency. Old 1.8 "depended on 1.7" only for the collector pattern, which actually comes from old 1.4 (now 1.3).

### 4. Redirect patterns (ln + git worktree + git merge)
- **Type:** identical-pattern
- **Items merged:** Cycle 2.2 (ln redirect), Cycle 2.3 (git worktree + git merge redirects)
- **Result:** Cycle 2.2 — parametrized table with 3 command prefixes
- **Rationale:** Same edit pattern (add command prefix match + additionalContext injection), same file, same mechanism. All depend only on Cycle 2.1 (script structure).

## Patterns Not Consolidated

- **Cycle 1.1 (line-based matching) + Cycle 1.3 (additive scanning):** Different complexity tiers. 1.1 modifies existing match logic; 1.3 refactors function signature, return type, and main() control flow. Different dependency chains.
- **Phase 3 Steps 3.1 + 3.2:** Only 2 items, create+validate pattern. No reduction value.
- **Phase 4 Steps 4.2 + 4.3:** Sequential dependency (flag file coordination between scripts). Different target files with shared state protocol.
- **Phase 5 Steps 5.1-5.4:** Sequential dependency chain (5.1 creates config, 5.2 creates merger, 5.3 integrates into recipe, 5.4 verifies).

## Requirements Mapping

No changes -- all 17 FR mappings preserved. Merged items map to the consolidated cycle numbers:
- FR-2, FR-3 -> Cycle 1.2
- FR-5, FR-6 -> Cycle 1.4
- FR-7, FR-8 -> Cycle 1.5
- FR-9 -> Cycles 2.1-2.2
