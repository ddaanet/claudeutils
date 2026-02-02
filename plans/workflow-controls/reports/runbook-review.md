# Vet Review: Workflow Controls Runbook

**Scope**: plans/workflow-controls/runbook.md
**Date**: 2026-01-31-142107
**Reviewer**: Sonnet (vet skill)

## Summary

Reviewed implementation runbook for workflow controls (shortcuts, session modes, universal tail behavior). Runbook defines 7 sequential steps for creating hook script, rewriting fragment, updating 5 skill files, and registering hook in settings. Design conformity is strong. Found 2 critical file path issues, 3 major implementation gaps, and 4 minor clarity improvements needed.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

**1. Missing Hook Script File**
- Location: Step 1, line 110
- Problem: Runbook creates `agent-core/hooks/userpromptsubmit-shortcuts.py` but this file does not exist yet (expected - it's created by the runbook). However, the runbook does not create the `agent-core/hooks/` directory first if it doesn't exist.
- Fix: Add directory creation before hook script creation in Step 1: `mkdir -p agent-core/hooks`

**2. Missing Reports Directory**
- Location: Multiple steps (step-1.md through step-7.md)
- Problem: Report paths reference `plans/workflow-controls/reports/step-N.md` but the reports directory doesn't exist yet
- Fix: Add directory creation in Common Context or Step 1: `mkdir -p plans/workflow-controls/reports`

### Major Issues

**3. Step 3 Line Number Reference May Be Incorrect**
- Location: Step 3, line 286
- Problem: References "lines 185-200" for commit skill post-commit section. Current file shows Post-Commit section starts at line 185 but is only 16 lines (to ~line 200). However, the replacement content is significantly longer (35 lines). Need to verify exact old_string for Edit tool.
- Suggestion: Change edit instruction to "Replace entire section from line 185 '## Post-Commit: Display Next Task' to line 200" with exact old_string match, not line numbers. Or use section-based replacement.

**4. Step 4 Line Number Reference Vague**
- Location: Step 4, line 352
- Problem: Says "after step 6 (around line 157)" but handoff skill session size advice section is at lines 117-138, not 157. The insertion point is unclear.
- Suggestion: Specify exact insertion point: "After the last step in handoff/SKILL.md" or provide exact line/section anchor for Edit tool.

**5. Step 6 Missing Current Step Count**
- Location: Step 6, line 498
- Problem: Says "Update Process section intro (line 18) to mention 7 steps instead of 6" but doesn't verify current step count. Design skill may have different structure.
- Suggestion: Verify actual current step count before editing. Add validation instruction.

**6. UserPromptSubmit Hook Matcher Clarification**
- Location: Step 7, line 540
- Problem: The JSON example shows `"matcher": "*"` but the note below says "UserPromptSubmit always uses matcher: '*'" and design says "UserPromptSubmit does not support the matcher field." These statements conflict.
- Suggestion: Clarify whether to include matcher field or omit it entirely. Design says no matcher support; runbook shows matcher. Recommend omitting the matcher field entirely based on design statement.

### Minor Issues

**7. Hook Script Validation Missing JSON Output Check**
- Location: Step 1, validation section (line 209-216)
- Note: Validation checks file exists, is executable, and has shebang. Missing: test that hook actually produces valid JSON output when given test input.
- Suggestion: Add validation step to run hook with sample JSON and verify output structure.

**8. Step 2 Missing Validation for Behavior Matrix**
- Location: Step 2, validation section (line 262-270)
- Note: Validates presence of modes and tables but doesn't check for `x` vs `r` behavior matrix specifically mentioned in requirements.
- Suggestion: Add explicit check for behavior matrix table in validation.

**9. Step 5 Missing Example Verification**
- Location: Step 5, line 432-435
- Note: Shows examples of task metadata format but doesn't validate they match the actual format string template.
- Suggestion: Minor - examples look correct but could add validation that examples follow the documented format.

**10. Missing Hook Testing Procedure**
- Location: Notes section, line 613-621
- Note: Testing workflow mentions testing shortcuts and STATUS display but doesn't provide concrete testing procedure (e.g., create test JSON, pipe to hook script, validate output).
- Suggestion: Add detailed hook testing steps with example commands.

## Positive Observations

**Strong Design Conformity:**
- All design requirements are covered in implementation steps
- Shortcut tables match design specification exactly
- Two-tier system (hook + fragment) properly implemented
- Status display format matches design specification

**Clear Step Structure:**
- Each step has well-defined objective, implementation, validation, and success criteria
- Common Context section consolidates shared information effectively
- Report paths consistently specified

**Comprehensive Metadata:**
- Weak orchestrator metadata provides clear execution model
- Prerequisites verified
- Dependencies documented
- Design decisions section preserved from design document

**Good Error Handling:**
- Each step defines expected outcome and error conditions
- Unexpected result handling specified
- Escalation paths documented

**Graceful Degradation:**
- All STATUS display implementations handle missing session.md
- Old task format support documented
- Missing field defaults specified

## Recommendations

1. **Pre-execution validation**: Before starting Step 1, verify all target files exist and create necessary directories
2. **Edit tool preparation**: For Steps 3-6, provide exact old_string values instead of line numbers (Edit tool requires exact match)
3. **Hook testing**: Add explicit testing step after Step 1 with example JSON inputs
4. **Matcher field**: Resolve conflict between design (no matcher) and runbook example (includes matcher) - recommend following design and omitting matcher entirely

## Next Steps

### Critical Fixes (Must Address)
1. Add directory creation for `agent-core/hooks/` in Step 1
2. Add directory creation for `plans/workflow-controls/reports/` in Common Context or Step 1

### Major Fixes (Strongly Recommended)
3. Replace line number references in Steps 3-6 with exact section markers or read-then-edit pattern
4. Resolve UserPromptSubmit matcher field conflict (omit matcher based on design)
5. Verify design skill current step count before editing in Step 6

### Minor Improvements (Optional)
6. Add hook JSON output validation test to Step 1
7. Add behavior matrix validation check to Step 2
8. Add detailed hook testing procedure to Notes section

## File Path Verification

**Files that MUST exist (verified ✓ or missing ✗):**
- ✓ `agent-core/fragments/execute-rule.md`
- ✗ `agent-core/hooks/userpromptsubmit-shortcuts.py` (created by runbook)
- ✓ `.claude/settings.json`
- ✓ `agent-core/skills/commit/SKILL.md`
- ✓ `agent-core/skills/handoff/SKILL.md`
- ✓ `agent-core/skills/handoff-haiku/SKILL.md`
- ✓ `agent-core/skills/design/SKILL.md`
- ✓ `agents/session.md`
- ✗ `plans/workflow-controls/reports/` (needs creation)

**Directories that need creation:**
- `agent-core/hooks/` (may not exist)
- `plans/workflow-controls/reports/` (doesn't exist)

## Design Conformity Check

**Requirements coverage:**
- ✓ Three session continuation modes (STATUS, EXECUTE, EXECUTE+COMMIT) - covered in Step 2
- ✓ Shortcut system via UserPromptSubmit hook - covered in Step 1
- ✓ Universal tail behavior - covered in Steps 3-6
- ✓ Two-tier shortcuts (commands + directives) - covered in Steps 1-2
- ✓ Session.md task metadata convention - covered in Step 5
- ✓ STATUS display format - covered in Steps 2-4
- ✓ Fragment for vocabulary - covered in Step 2
- ✓ Hook for mechanical expansion - covered in Step 1

**Design decisions implemented:**
- ✓ Lowercase shortcuts (`xc`, `hc`)
- ✓ Colon convention for directives (`d:`, `p:`)
- ✓ Two-layer system (hook + fragment)
- ✓ STATUS as universal tail
- ✓ Keep execute-rule.md filename
- ✓ `x` smart execute vs `r` strict resume

**Non-functional requirements:**
- ✓ Fast hook (Python stdlib only, no heavy imports)
- ✓ Zero false positives (exact match for tier 1, explicit colon for tier 2)
- ✓ Fragment + hook dual approach documented

## Conclusion

The runbook is well-structured and comprehensive. It accurately translates the design specification into actionable implementation steps. The main issues are:
1. Missing directory creation steps (critical but easy fix)
2. Line number references that should be exact string matches (implementation detail)
3. Matcher field conflict (design clarification needed)

Once critical and major fixes are applied, the runbook will be ready for execution. The design conformity is excellent and all requirements are properly covered.
