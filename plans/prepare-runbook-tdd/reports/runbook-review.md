# Runbook Review: prepare-runbook-tdd

**Date:** 2026-01-20
**Reviewer:** Sonnet orchestrator
**Runbook:** `plans/prepare-runbook-tdd/runbook.md`

---

## Overall Assessment: READY

The runbook is well-structured and executable by weak agents with minor improvements recommended. The design is sound, steps are clear, and validation criteria are measurable.

---

## Critical Issues

**None.** The runbook meets all hard requirements for execution.

---

## Major Issues

### 1. Missing Tool Usage Reminders in Steps

**Location:** Steps 3-8 (implementation steps)

**Issue:** While Common Context includes tool usage reminders, individual implementation steps don't explicitly remind agents to use specialized tools instead of Bash one-liners.

**Impact:** Risk of agents falling back to bash commands (grep, cat, etc.) instead of using Read, Edit, Grep tools.

**Recommendation:** Add tool reminder to each implementation step's Implementation section:

```markdown
**Tool Reminder**: Use Read (not cat), Edit (not sed), Write (not echo >), Grep (not grep/rg)
```

**Severity:** Major - Could cause sandbox errors or execution failures

---

### 2. Report Path Inconsistency

**Location:** Step 1 vs other steps

**Issue:** Step 1 uses `step-1-analysis.md` while Step 2 uses `step-2-design.md` (no "-report" suffix). Steps 3-9 use `-report.md` suffix consistently.

**Current pattern:**
- Step 1: `step-1-analysis.md` ✗
- Step 2: `step-2-design.md` ✗
- Steps 3-9: `step-N-report.md` ✓

**Recommendation:** Standardize to one pattern (prefer `-report.md` for consistency):
- Step 1: `step-1-report.md` (or keep as-is if semantic names preferred)
- Step 2: `step-2-report.md`

**Severity:** Major - Affects orchestrator file tracking and report discovery

---

### 3. Step 9 Inline Script vs Delegation Pattern

**Location:** Step 9

**Issue:** Script evaluation says "Small script (≤25 lines)" which correctly suggests inline execution, but the runbook includes a full 88-line bash script in the step content. This creates ambiguity about whether the orchestrator should:
1. Execute the inline script directly
2. Delegate to an agent with the script
3. Have an agent write and execute the script

**Current state:**
```markdown
**Script Evaluation**: Small script (≤25 lines)
**Execution Model**: Sonnet

**Implementation**:
```bash
#!/usr/bin/env bash
[88 lines of script]
```
```

**Recommendation:** Clarify execution approach:

**Option A - Direct execution (if script is stable):**
```markdown
**Script Evaluation**: Integration test (88 lines) - execute directly
**Execution Model**: Orchestrator (direct bash execution)

**Implementation**:
Run the following integration test script:
[script content]
```

**Option B - Agent writes script (if script needs adaptation):**
```markdown
**Script Evaluation**: Integration test (88 lines) - agent writes and executes
**Execution Model**: Sonnet

**Implementation**:
Create and execute integration test script with the following requirements:
1. Test TDD runbook processing
2. Verify agent baseline selection
3. Verify cycle file creation (not step files)
4. Verify orchestrator plan creation
5. Exit with clear pass/fail status

[Keep script as reference example]
```

**Severity:** Major - Could cause confusion about delegation vs direct execution

---

## Minor Issues

### 1. Missing Rollback Strategy

**Location:** Overall metadata

**Issue:** No documented rollback plan if integration test fails or implementation breaks existing functionality.

**Recommendation:** Add to metadata or notes:
```markdown
**Rollback Strategy**:
- All changes isolated to `prepare-runbook.py`
- Existing general runbook processing unchanged
- If critical failures, revert to git commit before Step 3
- Test general runbook processing after each implementation step
```

**Severity:** Minor - Good practice for risk management

---

### 2. No Interim Validation Points

**Location:** Steps 3-8

**Issue:** No intermediate validation checkpoints. If Step 7 fails, unclear which earlier step introduced the bug.

**Recommendation:** Add validation suggestion:
```markdown
**Interim Validation**: After Steps 4, 6, and 8, run:
`python3 agent-core/bin/prepare-runbook.py plans/tdd-integration/runbook.md --dry-run`
(if dry-run flag exists) or verify syntax with `python3 -m py_compile`
```

**Severity:** Minor - Improves debugging but not essential

---

### 3. Success Criteria Could Be More Specific

**Location:** Steps 3-8

**Issue:** Some success criteria are vague (e.g., "Function tested with sample data (documented in report)").

**Examples:**
- Step 3: "Function tested with sample data" - What specific test cases?
- Step 5: "Changes tested (documented in report)" - What constitutes a test?

**Recommendation:** Add specific test requirements:

**Step 3:**
```markdown
**Success Criteria**:
- `extract_cycles()` function implemented
- Validation logic implemented
- At least 3 error conditions handled
- Function tested with:
  * Valid input: "## Cycle 1.1: Title"
  * Invalid input: "## Cycle X.Y: Title" (non-numeric)
  * Edge case: Non-sequential numbers
- Test results documented in report
```

**Severity:** Minor - Steps are still executable without this detail

---

### 4. Missing Expected Line Counts

**Location:** Steps 3-8

**Issue:** "Prose description (50-80 line modification)" provides estimates but no validation of whether implementation matches complexity assessment.

**Recommendation:** Add to success criteria:
```markdown
**Complexity Check**: If implementation significantly exceeds estimated line count (>2x), document why in report and consider refactoring.
```

**Severity:** Minor - Good practice but not blocking

---

### 5. No Performance Considerations

**Location:** Overall design

**Issue:** No mention of performance implications (e.g., regex efficiency, file I/O patterns).

**Recommendation:** Add to notes:
```markdown
**Performance**: All changes follow existing patterns which handle runbooks up to ~1000 lines efficiently. Cycle extraction uses same regex approach as step extraction (O(n) where n = lines).
```

**Severity:** Minor - Performance likely adequate given existing patterns

---

## Detailed Criteria Assessment

### 1. Completeness ✅

**Design decisions documented:** Yes (5 decisions, clear rationale)

**Missing choices:** None critical. All major design points covered:
- File location strategy
- Baseline selection approach
- Validation timing
- Numbering format
- Error handling philosophy

**Dependencies clear:** Yes - Prerequisites and "After This Runbook" sections complete

**Verdict:** Complete

---

### 2. Executability ✅

**Can weak agents execute:** Yes, with tool reminder additions (see Major Issue #1)

**Ambiguous instructions:** Only Step 9 script execution pattern (see Major Issue #3)

**Clear acceptance criteria:** Mostly yes (see Minor Issue #3 for improvements)

**Error escalation:** Yes, clear STOP conditions in each step

**Verdict:** Executable with minor clarifications

---

### 3. Script vs Direct Assessment ✅

**Complexity assessments:**
- Steps 1-2: Prose (analysis/design) ✓
- Steps 3-8: Prose (30-80 line modifications) ✓
- Step 9: Claims ≤25 lines but shows 88-line script ✗ (see Major Issue #3)

**Appropriateness:** Generally correct. Only Step 9 needs clarification.

**Verdict:** Appropriate with Step 9 clarification needed

---

### 4. Validation ✅

**Measurable criteria:** Yes
- Step 3: "At least 3 error conditions handled"
- Step 9: "All 3 verification checks pass"
- Overall: "Integration test passes on `plans/tdd-integration/runbook.md`"

**Specific enough:** Mostly (see Minor Issue #3)

**Testable:** Yes, Step 9 provides concrete integration test

**Verdict:** Validation criteria are measurable and specific

---

### 5. Error Handling ✅

**Escalation triggers clear:** Yes
- "If structure differs significantly... → STOP and report"
- "If cycle structure in test runbook doesn't match pattern → report and STOP"
- "If any check fails → report which check failed, expected vs actual, and STOP"

**Actionable:** Yes, all escalation points specify what to report

**Consistent:** Yes, follows pattern: "If X → report Y and STOP"

**Verdict:** Error handling is clear and actionable

---

### 6. Tool Usage Reminders ⚠️

**Present in Common Context:** Yes ✓

**Present in individual steps:** No ✗ (see Major Issue #1)

**Verdict:** Need to add reminders to implementation steps

---

### 7. Report Paths ⚠️

**Absolute paths:** Yes, all use `plans/prepare-runbook-tdd/reports/`

**Consistent:** Mostly (see Major Issue #2)

**Verdict:** Need to standardize naming convention

---

### 8. Step Objectives ✅

**Clear and focused:** Yes
- Step 1: "Understand current implementation"
- Step 3: "Modify `extract_sections()` or create `extract_cycles()`"
- Step 6: "Create `generate_cycle_file()` function"

**Single responsibility:** Yes, each step has one primary goal

**Verdict:** Objectives are clear and focused

---

### 9. Expected Outcomes ✅

**Specific enough:** Yes
- Step 3: "Function that extracts cycles from TDD runbooks with validation"
- Step 6: "Cycle files generated for TDD runbooks instead of step files"

**Testable:** Yes, outcomes map to validation criteria

**Verdict:** Expected outcomes are specific and testable

---

### 10. Implementation Guidance ⚠️

**Ambiguity:** Minimal, except:
- Step 9 script execution pattern (Major Issue #3)
- Tool usage not repeated in steps (Major Issue #1)

**Detail level:** Appropriate for sonnet-level agents

**Code examples:** Good - Step 6 includes cycle file template, Step 8 includes help text

**Verdict:** Good guidance with clarifications needed

---

## Recommendations Summary

### Must Fix (Critical)
None

### Strongly Recommend (Major)
1. Add tool usage reminders to Steps 3-8 implementation sections
2. Standardize report path naming (step-N-report.md vs step-N-[name].md)
3. Clarify Step 9 execution pattern (orchestrator direct vs agent delegation)

### Consider (Minor)
4. Add rollback strategy to metadata
5. Add interim validation checkpoints
6. Make success criteria more specific with concrete test cases
7. Add complexity check reminder to success criteria
8. Document performance considerations in notes

---

## Conclusion

The runbook is **READY FOR EXECUTION** with the understanding that:

1. **Critical path is clear:** Steps 1-9 form a logical progression from analysis to integration test
2. **Success criteria are measurable:** Integration test provides concrete pass/fail validation
3. **Error handling is robust:** STOP conditions at appropriate points with clear escalation
4. **Design is sound:** 5 documented decisions with clear rationale
5. **Major issues are addressable:** 3 major issues are documentation/clarity improvements, not fundamental design flaws

**Estimated time to address major issues:** 15-30 minutes

**Risk level:** Low - All issues are documentation improvements, no fundamental design flaws

**Recommendation:** Address Major Issues #1-3, then proceed with execution.
