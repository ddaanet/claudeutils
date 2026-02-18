# Runbook Review: Phase 5 — Exit code threading + skill update + stdout unification

**Artifact**: `plans/worktree-merge-resilience/runbook-phase-5.md`
**Date**: 2026-02-18T00:00:00Z
**Mode**: review + fix-all
**Phase types**: General (3 steps)

## Summary

Phase 5 is a clean, well-structured documentation/threading phase covering three independent concerns: exit code reclassification, stderr-to-stdout migration, and SKILL.md Mode C update. File references all valid. Step ordering correct (implementation before documentation). Four issues found and fixed: duplicated grep verification instruction, ambiguous scope boundary for cli.py, vacuous "verify Usage Notes" implementation bullet, and a scope/instruction conflict in Step 5.2 implementation that would cause an executor to over-apply `err=True` removal.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

1. **Step 5.2 implementation conflicts with scope boundary**
   - Location: Step 5.2, Implementation steps 1-2
   - Problem: Steps 1-2 said "run grep on both files" then "for each match: remove `err=True`" — no filter between the scan and the edit. The scope boundary note appeared between steps 2 and 3, not before step 2. An executor reading mechanically would remove `err=True` from ALL matches across both files, including `new`, `rm`, `ls`, and other non-merge functions in cli.py.
   - Fix: Moved scope boundary before implementation steps. Split step 2 into explicit file-specific instructions (merge.py: all matches; cli.py: merge command only). Updated validation to match — old validation said "zero matches in both files" which was incorrect since non-merge cli.py `err=True` calls should be preserved.
   - **Status**: FIXED

### Minor Issues

1. **Step 5.1 duplicated grep instruction**
   - Location: Step 5.1, Implementation step 5 and Validation
   - Problem: `grep -n "SystemExit" src/claudeutils/worktree/merge.py` appeared as both implementation step 5 and the first validation bullet — identical instruction in both sections. No behavioral difference, just churn.
   - Fix: Removed from implementation (step 5 deleted), kept in Validation where it belongs.
   - **Status**: FIXED

2. **Step 5.3 exit 3 implementation said "write fresh prose" — move intent not explicit**
   - Location: Step 5.3, implementation bullet 1
   - Problem: The new exit 3 step description read as an original specification, implying the executor should write new conflict-handling prose from scratch. The existing exit 1 conflict workflow (Edit → git add → Re-run) should be preserved and moved, not discarded and rewritten. Writing fresh prose risks losing the specific substep structure that agents depend on.
   - Fix: Added explicit move instruction: "This moves the 'If conflicts detected' workflow from the current exit 1 section into the new exit 3 step. Preserve the existing 4-substep conflict workflow — adapt, don't rewrite from scratch."
   - **Status**: FIXED

3. **Step 5.3 vacuous "verify Usage Notes" bullet**
   - Location: Step 5.3, implementation bullet 4
   - Problem: "Verify it references the updated state machine" is a check-only item with no planned action — it adds no implementation content and duplicates what the validation section already covers. Vacuous implementation bullet.
   - Fix: Removed implementation bullet 4. The validation section ("Read SKILL.md Mode C after edit — verify...") already covers post-edit correctness checking.
   - **Status**: FIXED

## Fixes Applied

- Step 5.1, implementation — removed step 5 (duplicated grep already in Validation)
- Step 5.2, scope boundary — moved before implementation steps (was between steps 2 and 3)
- Step 5.2, implementation — split step 2 into file-specific instructions with explicit merge-only filter for cli.py; added step 4 with scoped verification
- Step 5.2, validation — corrected "zero matches" assertion to file-split assertions (merge.py: zero; cli.py: non-merge only)
- Step 5.3, implementation bullet 1 — added move/adapt instruction to preserve existing conflict workflow substeps
- Step 5.3, implementation bullet 4 — removed vacuous "verify Usage Notes" bullet (covered by Validation)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
