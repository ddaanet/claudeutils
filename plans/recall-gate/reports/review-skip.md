# Review Skip: recall-gate

**Changed files:** 2 skill files (runbook/SKILL.md, inline/SKILL.md), learnings.md, plan artifacts

**Why review adds no value:** Three instances of the same structural rewrite — artifact-existence branching replaced with constant memory-index scan. Pattern applied identically 3 times. Change is prose rewording of gate instructions, not behavioral code. User validated the RCA analysis and directed the fix approach.

**Verification performed:**
- `grep "mandatory tool call on both paths" agent-core/skills/` → no hits (old pattern removed)
- `grep "Implementation recall" agent-core/skills/runbook/SKILL.md` → 2 hits (Tier 1, Tier 2)
- `grep "D+B anchor.*tool call required" agent-core/skills/inline/SKILL.md` → 1 hit (Phase 2.3)
- All 3 gates have identical structure: memory-index first, artifact additive, resolve always, null no-op preserved
