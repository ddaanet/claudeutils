# Vet Review: Phase 1 Runbook (Tier 1 Fixes)

**Scope**: Phase 1 runbook file (`plans/reflect-rca-parity-iterations/runbook-phase-1.md`)
**Date**: 2026-02-08T12:00:00Z

## Summary

Phase 1 runbook defines 2 steps (WIP-only restriction + D+B validation) with clear structure and actionable instructions. Step 1 is well-formed with precise implementation guidance. Step 2 has critical structural issues: contradictory instructions, ambiguous escalation conditions, and semantic mismatch between title and execution.

**Overall Assessment**: Needs Significant Changes

## Issues Found

### Critical Issues

1. **Step 2: Contradictory commit instructions**
   - Location: runbook-phase-1.md:86-88, 128
   - Problem: Step 2 instructs to "Invoke `/commit` skill" (line 86) but later states "This step consumes the Step 1 changes by committing them" (line 128). However, Step 2's objective is empirical validation of D+B gates, not committing Step 1 changes. The step conflates two distinct concerns: validating gate execution vs. creating a commit.
   - Fix: Clarify whether Step 2 should: (a) commit Step 1 changes as the vehicle for validation, OR (b) validate gates using a mock/trivial change without committing Step 1 changes. Design DD-8 (lines 160-172) says "Execute `/commit` on a trivial change" — this implies Step 1 changes ARE the trivial change, supporting interpretation (a). If so, Step 2 should explicitly state: "Use Step 1 changes as the commit vehicle for D+B validation" upfront, not as an afterthought in the Note section.

2. **Step 2: Ambiguous escalation condition**
   - Location: runbook-phase-1.md:114
   - Problem: "If session.md not found: Document error, proceed with validation (session.md read is conditional)" contradicts the gate validation objective. If Gate A (Read session.md) does NOT execute because the file doesn't exist, this is a validation failure (gate did not fire), not a conditional pass. The instruction says "proceed with validation" — does this mean "proceed with remaining gates" or "mark Gate A as failed but continue"?
   - Fix: Clarify: "If session.md not found: Mark Gate A as 'File not found — gate did not execute' in report, continue validation of Gate B and precommit." Or if session.md absence should halt validation, make that explicit with STOP directive.

3. **Step 2: Title-implementation mismatch**
   - Location: runbook-phase-1.md:63 (title) vs. 86-104 (implementation)
   - Problem: Title says "D+B Empirical Validation" but implementation section (lines 86-104) executes a full commit workflow. The title suggests observational validation (watch gates fire), but the implementation is active execution (commit Step 1 changes). This semantic mismatch creates confusion: is this step about validating D+B behavior or about committing Phase 1 work?
   - Fix: Retitle to "D+B Validation via Step 1 Commit" or clarify in Objective: "Execute `/commit` on Step 1 changes to validate D+B gate execution empirically."

### Major Issues

1. **Step 1: Line number references may drift**
   - Location: runbook-phase-1.md:23-31
   - Problem: Implementation section references exact line numbers (19-40, 24-27, 38-40) from commit/SKILL.md. If the file structure changes between planning and execution, these references will be incorrect.
   - Suggestion: Use section headings as anchors ("Flags section", "TDD workflow pattern") with approximate line numbers in parentheses for guidance, not as exact edit targets. Or instruct executor to search for section headings first, then locate lines within that section.

2. **Step 2: Evidence snippet ambiguity**
   - Location: runbook-phase-1.md:100-102
   - Problem: "Gate A: Did Read session.md execute? (yes/no, evidence snippet)" — what qualifies as evidence? The executor might interpret this as "session.md content appeared somewhere in output" vs. "Read tool call explicitly shown in transcript." DD-8 says "Verify Gate A (Read session.md) executes" but doesn't define verification criteria.
   - Suggestion: Specify evidence type: "Evidence = Read tool call visible in transcript with session.md path, OR session.md content snippet in context." Give executor clear criteria for yes/no judgment.

3. **Step 2: Unexpected result handling incomplete**
   - Location: runbook-phase-1.md:111-114
   - Problem: Covers three specific failure modes but omits general failure case. What if commit fails for an unexpected reason (network error, disk full, permission denied)? Current instructions only handle: gate not executing, precommit fails, session.md missing.
   - Suggestion: Add catch-all: "If commit fails for any other reason: Document error message, escalate to sonnet without proceeding to Phase 2."

### Minor Issues

1. **Step 1: Validation references "DD-3 intent" without quoting it**
   - Location: runbook-phase-1.md:47
   - Note: "Verify changes match DD-3 intent" assumes executor has DD-3 loaded in context. Better to quote the key constraint from DD-3 here: "WIP commits only, final commits require full precommit."

2. **Step 2: Prerequisites assume sequential execution**
   - Location: runbook-phase-1.md:74-76
   - Note: "Step 1 complete" prerequisite is valid for sequential execution but could be made explicit: "Must execute Step 1 before Step 2 — Step 1 changes provide the trivial change needed for D+B validation."

3. **Phase Checkpoint: Missing evidence reference**
   - Location: runbook-phase-1.md:133-139
   - Note: Completion criteria lists Step 2 report created but doesn't specify where to check for it. Add: "Evidence: `plans/reflect-rca-parity-iterations/reports/d-b-validation.md` exists and contains all three gate results."

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| DD-3 (WIP-only restriction) | Satisfied | Step 1 implementation (lines 21-43) covers flag scope restriction, TDD workflow clarification |
| DD-8 (D+B empirical validation) | Partial | Step 2 execution covers validation mechanics, but contradictory instructions and ambiguous escalation undermine reliability |

**Gaps:** Step 2 semantic confusion (validation vs. commit) creates execution risk. If executor interprets Step 2 as "validate gates without committing" they will deviate from design intent.

---

## Positive Observations

- Step 1 is exceptionally clear: implementation section provides exact edits with before/after examples
- Report path specification consistent across both steps (absolute and relative paths given)
- Success criteria are concrete and testable for Step 1
- Design reference callouts (DD-3, DD-8) make traceability explicit

## Recommendations

1. **Resolve Step 2 commit semantics:** Decide if Step 2 is "validate gates by committing Step 1" or "validate gates with mock commit." Design DD-8 implies the former. Make this explicit in Step 2 Objective and Prerequisites.

2. **Strengthen escalation conditions:** Replace "proceed with validation" language with explicit failure marking ("Gate A: FAILED — file not found, gate did not execute").

3. **Evidence criteria precision:** Define what "evidence" means for each gate (tool call visibility, output snippet, etc.) to eliminate executor interpretation variance.

4. **Add general failure handler:** Cover unexpected commit failures with catch-all escalation rule.

## Next Steps

1. Clarify Step 2 commit semantics (validation vehicle vs. validation only)
2. Resolve session.md absence handling (fail vs. conditional pass)
3. Specify evidence criteria for Gate A/B/validation
4. Add catch-all failure escalation
5. Retitle Step 2 or update Objective to align title with implementation

