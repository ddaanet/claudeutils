# Step 5.1 Self-Review: General-Step Reference Material

**Step**: 5.1 — Create general-step reference material
**FR**: FR-4
**Reviewer**: Self-review (skill-reviewer delegation skipped per modified validation)

## Files Changed

- `agent-core/skills/runbook/references/general-patterns.md` — Created (127 lines)
- `agent-core/skills/runbook/references/anti-patterns.md` — Updated (added General Step Anti-Patterns section)
- `agent-core/skills/runbook/references/examples.md` — Updated (added General Step Examples section)

## Checklist

### general-patterns.md
- [x] Granularity criteria: atomic (<100 lines, single file), composable (2-5 files, shared purpose), complex (>100 lines, split required)
- [x] When to split vs merge heuristics with concrete criteria
- [x] Prerequisite validation patterns: creation (2+ reads), transformation (target read), investigation gates
- [x] Each pattern type has: pattern template, rationale ("Why"), heuristic for identification
- [x] Step structure template with all required fields

### anti-patterns.md
- [x] General Step Anti-Patterns section added as table matching TDD section format
- [x] 6 anti-patterns with Bad Example and Correct Pattern columns
- [x] Each anti-pattern has concrete correction (not just "fix it")
- [x] Downstream-reference-in-bootstrapping anti-pattern included (from learnings)
- [x] File title updated from "TDD" scope to general scope, TDD section labeled

### examples.md
- [x] Creation step example with 2 prerequisite reads (investigation pattern)
- [x] Transformation step example with single target read (self-contained)
- [x] Both examples include all required fields: Objective, Prerequisites, Implementation, Expected Outcome, Error Conditions, Validation
- [x] Expected Outcomes are concrete and verifiable (not vague)
- [x] Error Conditions map specific failures to recovery actions
- [x] Key Observations section explains creation vs transformation differences
- [x] File title updated from "TDD" scope to general scope, TDD section labeled

## Observations

**FR-4 acceptance criteria discrepancy:** FR-4 says "each of patterns.md, anti-patterns.md, examples.md has a general-step section." The step file specifies creating a separate `general-patterns.md` rather than adding a section to `patterns.md`. I followed the step file's instruction. The separate file avoids inflating `patterns.md` (already 151 lines of TDD-specific content) and maintains clean separation between TDD patterns and general patterns.

**No issues found.** All deliverables created per step specification with concrete content.

## Status

PASS — all expected outcomes met.
