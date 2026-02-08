# Vet Review: Phase 2 Runbook

**Scope**: Phase 2 runbook file (Tier 2 fixes, 6 steps)
**Date**: 2026-02-08T21:00:00Z

## Summary

Phase 2 runbook covers 6 low-complexity steps addressing Gaps 2, 3, 4, 5 and concerns Q5, N1. The runbook is well-structured with clear objectives, design references, and executable guidance. All steps include proper structure (objective, implementation, validation, success criteria). Parallelization guidance is clear. Step 8 correctly handles conditional output paths.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Step 3: Line count mismatch in content structure vs success criteria**
   - Location: Lines 27-59 (content structure) vs line 78 (success criteria)
   - Problem: Content structure template shows ~50-60 lines of markdown, success criteria says "Between 60-80 lines total"
   - Suggestion: Verify expected line count — template suggests lower bound, criteria suggests higher

2. **Step 4: Current state line reference may drift**
   - Location: Line 94 "Section 'Conformance Validation for Migrations' at lines 128-140"
   - Problem: Hard-coded line numbers may become stale if testing.md is edited before this step executes
   - Suggestion: Consider "around line 128" or section heading search instead of exact range

3. **Step 5: Similar line reference brittleness**
   - Location: Lines 157-158, 182, 195
   - Problem: Multiple references to "line 199" which may shift
   - Suggestion: Use "after 'Impact' line" without hard-coded number (already used in line 163)

4. **Step 8: Tool call pattern unclear for multi-step process**
   - Location: Lines 329-362 (audit process)
   - Note: Step describes 5-part process but doesn't specify which parts use what tools (Bash for find, Read for each skill, Write for report)
   - Suggestion: Make tool usage explicit in each process step for haiku/sonnet clarity

## Requirements Validation

**Design references verified:**

| Design Decision | Coverage | Evidence |
|-----------------|----------|----------|
| DD-2 (lines 79-93) | Complete | Steps 4-5 implement conformance exception with exact table (lines 118-122, 173-176) |
| DD-4 (lines 108-119) | Complete | Steps 6-7 implement file size awareness with 350-line threshold (lines 220-237, 279-296) |
| DD-6 (lines 137-146) | Complete | Step 3 implements defense-in-depth doc with layer enumeration (lines 27-59) |
| DD-7 (lines 148-158) | Complete | Step 8 implements manual audit with 80% threshold decision (lines 350-361) |

**Gap coverage verified:**

| Gap | Steps | Status |
|-----|-------|--------|
| Gap 2 (file size) | 6, 7 | Satisfied — planning-time awareness in both plan-tdd and plan-adhoc |
| Gap 4 (test precision) | 4, 5 | Satisfied — conformance exception in testing.md and workflow-advanced.md |
| Q5 (defense-in-depth) | 3 | Satisfied — new decision document with layered pattern |
| N1 (skill audit) | 8 | Satisfied — manual audit with conditional lint decision |

**Gap 3 + Gap 5 interaction:** Step 3 content structure (lines 42-45) correctly documents the D+B hybrid (outer defense) + WIP-only restriction (inner defense) relationship per DD-6.

**Gaps:** None. All stated design decisions are covered.

## Positive Observations

**Strong structure compliance:**
- All 6 steps follow consistent format: Objective → Design Reference → File → Implementation → Expected Outcome → Validation → Success Criteria → Report Path
- Report paths consistently use `plans/reflect-rca-parity-iterations/reports/step-N-execution.md` pattern
- Step 8 correctly uses `n1-audit.md` as both execution report and review report

**Accurate design alignment:**
- Step 4 example contrast table (lines 118-122) matches design DD-2 lines 86-91 exactly
- Step 5 example table (lines 173-176) matches same design reference
- Step 6 threshold (350 lines) and rationale match DD-4 lines 114-118
- Step 8 decision threshold (≥80% = ship) matches DD-7 line 154

**Clear parallelization guidance:**
- Header (lines 7-10) explicitly identifies independent steps (3, 6, 7, 8) and prerequisite relationship (4-5 → Phase 3 Step 9)
- Checkpoint section (lines 394-396) reinforces Gap 4 prerequisite for Phase 3

**Conditional logic well-specified:**
- Step 8 lines 359-361 provide clear decision threshold
- Lines 359-362 enumerate both output paths (A: ship lint, B: don't ship)
- Success criteria (line 376) allows either conditional output

**Model selection justified:**
- Header specifies haiku for steps 3-7 (mechanical edits, file creation)
- Step 8 explicitly states sonnet requirement with rationale (line 326: "requires semantic judgment")

**File size estimates reasonable:**
- Step 3: ~60-80 lines for decision doc (line 66)
- Step 4: expand from ~13 to ~30-35 lines (line 125, 139)
- Step 5: add ~10-12 lines (line 163)
- Steps 6-7: add ~15 lines each (lines 238, 253)
- Total additions: ~140-175 lines across 6 files — matches "~200 lines total" in header

**Success criteria measurable:**
- All steps include quantifiable outcomes (file exists, line count ranges, content elements present)
- Step 8 has clear numeric threshold (≥80% compliance)

## Recommendations

1. **Harmonize line count expectations for Step 3**: Content structure suggests 50-60 lines of markdown, success criteria says 60-80 total. Verify which is intended or adjust one to match.

2. **Consider section-based navigation over line numbers**: Steps 4 and 5 use hard-coded line numbers that may drift. Using section headings as anchors is more resilient (e.g., "locate section 'Conformance Validation for Migrations'" instead of "at lines 128-140").

3. **Make tool usage explicit in Step 8 process**: The 5-part audit process (lines 329-362) implies Bash for find, Read for auditing, Write for report, but doesn't state this. Spelling it out aids execution agents.

4. **Validate Step 3 template line count empirically**: The markdown template (lines 27-59) is 33 lines in the runbook. If expanded with full sentences in bracketed sections, verify it reaches 60-80 lines total as success criteria requires.

## Next Steps

1. **Optional refinements** (defer to author judgment):
   - Adjust Step 3 line count expectation (minor issue #1)
   - Replace hard-coded line numbers with section-based navigation (minor issues #2, #3)
   - Add explicit tool usage to Step 8 process steps (minor issue #4)

2. **Execution readiness**: Runbook is executable as-written. Minor issues are navigational conveniences, not blockers.

3. **Checkpoint preparation**: Ensure Gap 4 changes (Steps 4-5) are committed before Phase 3 execution begins, per prerequisite documented in lines 394-396.
