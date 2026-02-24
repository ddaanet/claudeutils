# Runbook Review: Phase 4 — Skill and prose updates

**Artifact**: `plans/orchestrate-evolution/runbook-phase-4.md`
**Date**: 2026-02-24T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (2 steps, model: opus)

## Summary

Phase 4 is a well-structured general phase covering the SKILL.md rewrite (Step 4.1) and refactor.md/delegation.md updates (Step 4.2). Design decision coverage (D-1 through D-6) is explicit with a checklist, model assignment is correct (opus mandatory for all architectural artifacts), and the D+B hybrid constraint is documented. Four issues found: one major (redundant duplicate instruction that would cause executor failure), and three minor (missing script paths in validation, D+B hybrid check absent from validation checklist, minor resume pattern placement awkwardness). All issues are fixable and have been fixed.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **Redundant duplicate instruction in delegation.md modifications (modification #4)**
   - Location: Step 4.2, `delegation.md` modifications list
   - Problem: Modification #1 already removes the Haiku bullet as part of "Replace Model Selection list (lines 9-17)". Modification #4 then separately instructs "Delete 'Haiku: Execution...' from Model Selection" — the same operation on the same content. An executor following both instructions sequentially would attempt to delete a line that modification #1 already removed, causing the second deletion to fail or apply to wrong content.
   - Fix: Removed modification #4 entirely. The haiku removal is fully covered by modification #1's list replacement instruction.
   - **Status**: FIXED

### Minor Issues

1. **Validation for Step 4.1 specifies "correct paths" for verify scripts without naming them**
   - Location: Step 4.1, Validation checklist
   - Problem: "verify-step.sh and verify-red.sh referenced by correct paths" leaves ambiguity — an executor could reference wrong paths and the validation check would provide no guidance. The design specifies exact locations.
   - Fix: Replaced vague "correct paths" with explicit paths: `agent-core/skills/orchestrate/scripts/verify-step.sh` and `agent-core/skills/orchestrate/scripts/verify-red.sh`.
   - **Status**: FIXED

2. **D+B hybrid compliance check missing from Validation checklist**
   - Location: Step 4.1, Validation section
   - Problem: The D+B hybrid pattern requirement ("every section must open with a tool call") is documented in Key Constraints and mentioned in Error Conditions, but is absent from the Validation checklist. Executors use the Validation checklist as the completion gate — a missing criterion here means the check is skipped.
   - Fix: Added explicit D+B validation bullet to Validation checklist: "D+B hybrid compliance: every numbered step in the skill opens with a tool call (Read/Bash/Glob) — no prose-only step sections."
   - **Status**: FIXED

3. **Resume pattern insertion point (refactor.md line 183) has minor placement awkwardness**
   - Location: Step 4.2, refactor.md modification #3
   - Problem: "Add to Return Protocol section (after line 183)" places the resume pattern between `**Failure:** \`error: [brief reason]\`` and `Do not provide summary...`. The resume pattern is behavioral guidance, not a return value — inserting it mid-Return-Protocol between the failure line and the closing note creates a slight flow discontinuity. Better placement would be before the return value options (before `**Success:**`) or after "Do not provide summary" line.
   - Assessment: The design intent is clear and an executor will produce correct content; the placement is readable even if slightly awkward. No fix applied — fixing would require changing line references, and the design describes the placement as "after line 183" which is unambiguous. Documenting for awareness.
   - **Status**: Advisory only (no fix needed — executor intent unambiguous)

## Fixes Applied

- Step 4.1, Validation — replaced "verify-step.sh and verify-red.sh referenced by correct paths" with explicit script paths from design.md
- Step 4.1, Validation — added D+B hybrid compliance check as explicit validation bullet
- Step 4.2, delegation.md modifications — removed modification #4 (duplicate haiku removal instruction; already covered by modification #1)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
