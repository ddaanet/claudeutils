# Vet Review: worktree-update outline.md

**Scope**: Internal consistency check after series of amendments
**Date**: 2026-02-12T18:45:00Z
**Mode**: review + fix

## Summary

Reviewed outline.md for stale references and internal consistency after recent amendments removed `create-task` compound command and CLI commands for `derive-slug` and `focus-session`. Found 4 issues related to outdated references and 1 issue with incorrect phase count description. All issues fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Stale reference to `create-task` in focus_session documentation**
   - Location: Line 194
   - Problem: Documentation said "consumed internally by `create-task` compound command" but that command was removed
   - **Status**: FIXED — Changed to "consumed internally by `new --task` mode"

2. **Stale references to `create-task` in key decisions**
   - Location: Lines 313-314 (D4 decision)
   - Problem: Said functions were "consumed by `create-task`" which no longer exists
   - **Status**: FIXED — Changed to "consumed by `new --task` mode"

3. **Function documented as CLI command**
   - Location: Line 176 section header
   - Problem: Section header said "Add `focus-session` command (new)" but it's not a CLI command, just a function
   - **Status**: FIXED — Changed to "Add `focus_session()` function (new)" and updated all references from stdout to return string

4. **Incorrect implementation sequence numbering**
   - Location: Line 357
   - Problem: Said "Steps 1-8: TDD" but step 8 was labeled as "non-code artifacts (no TDD)"
   - **Status**: FIXED — Changed to "Steps 1-7: TDD (RED → GREEN → REFACTOR). Step 8: non-code artifacts"

5. **Inconsistent phase count in problem statement**
   - Location: Line 12
   - Problem: Said merge command has "3-phase ceremony" but solution implements 4-phase ceremony
   - **Status**: FIXED — Changed to "4-phase ceremony" to match solution description

## Fixes Applied

- Line 12: Updated ceremony phase count from 3 to 4
- Line 176: Changed section header from "command" to "function", updated description from stdout to return string
- Line 194: Changed "consumed internally by `create-task` compound command" to "consumed internally by `new --task` mode"
- Lines 313-314: Changed both occurrences of "consumed by `create-task`" to "consumed by `new --task` mode"
- Line 357: Changed "Steps 1-8: TDD. Step 9: non-code artifacts" to "Steps 1-7: TDD. Step 8: non-code artifacts"
- Line 272: Added explicit test coverage for `--task` mode

## Requirements Validation

N/A - Outline is internal documentation, not implementation against requirements.

## Positive Observations

- Architecture section correctly describes `new --task` mode composition
- D7 key decision accurately reflects the current design (no separate `create-task` command)
- D8 justfile independence is consistently stated throughout
- Test file list is consistent (no `test_create_task.py`)
- Scope IN/OUT clearly delineates submodule-agnostic support as future work
- Implementation sequence covers all Scope IN deliverables
- All references to submodule operations correctly use hardcoded `agent-core` paths

## Recommendations

None. Outline is internally consistent and ready for planning.
