# TDD Runbook Review: Worktree Skill Phase 1

**Artifact**: `plans/worktree-skill/runbook-phase-1.md`
**Date**: 2026-02-10T19:45:00Z
**Mode**: review + fix-all

## Summary

Phase 1 implements worktree lifecycle (`new` and `rm` subcommands) with 7 cycles. Review found 5 major issues with prescriptive implementation details in GREEN phases. All issues were fixed by rewriting GREEN phases to describe behavior and provide hints rather than prescribe exact code.

**Overall Assessment**: Ready

**Issues found**: 0 critical, 5 major, 0 minor
**Issues fixed**: 5
**Unfixable (escalation required)**: 0

## Major Issues

### Issue 1: Prescriptive implementation in Cycle 1.1 GREEN
**Location**: Cycle 1.1, lines 29-39
**Problem**: GREEN phase used bullet list prescribing exact Click decorator syntax, parameters, and implementation structure
**Fix**: Rewrote as behavior description with hints. Emphasized what the command should do (create worktree, print path, handle errors) rather than how to structure the code
**Status**: FIXED

### Issue 2: Prescriptive implementation in Cycle 1.2 GREEN
**Location**: Cycle 1.2, lines 63-68
**Problem**: GREEN phase prescribed exact validation checks with specific method calls
**Fix**: Rewrote to describe collision detection behavior (validate directory, validate branch, report specific errors) with hints about check methods
**Status**: FIXED

### Issue 3: Highly prescriptive git plumbing in Cycle 1.5 GREEN
**Location**: Cycle 1.5, lines 132-147
**Problem**: GREEN phase contained step-by-step git plumbing pseudocode with exact command sequence, essentially prescribing complete implementation
**Fix**: Rewrote to describe pre-commit behavior and critical requirements (main index unmodified, session file placement, commit message). Moved exact command sequence reference to hints pointing to design document
**Status**: FIXED

### Issue 4: Prescriptive conditional flow in Cycle 1.6 GREEN
**Location**: Cycle 1.6, lines 172-185
**Problem**: GREEN phase used nested bullet structure prescribing exact conditional logic flow
**Fix**: Rewrote to describe removal behavior, safety warnings, and approach. Moved implementation details to hints section
**Status**: FIXED

### Issue 5: Prescriptive conditional structure in Cycle 1.7 GREEN
**Location**: Cycle 1.7, lines 203-211
**Problem**: GREEN phase prescribed exact conditional flow for branch-only cleanup
**Fix**: Rewrote to describe idempotent behavior and resilience to partial cleanup states, with approach and rationale
**Status**: FIXED

## Fixes Applied

- **Cycle 1.1 GREEN**: Replaced prescriptive Click decorator details with behavior description + hints
- **Cycle 1.2 GREEN**: Replaced prescriptive validation checks with collision detection behavior + hints
- **Cycle 1.5 GREEN**: Replaced step-by-step plumbing commands with behavior/approach/hints structure, referenced design doc for sequence
- **Cycle 1.6 GREEN**: Replaced nested conditional structure with behavior description + approach + hints
- **Cycle 1.7 GREEN**: Replaced prescriptive flow with idempotent behavior description + rationale

## Critical Issues

(None)

## Minor Issues

(None)

## Unfixable Issues (Escalation Required)

None — all issues fixed.

## Requirements Coverage

Phase 1 covers requirements from outline:
- **Outline Cycle 1.1**: Basic worktree creation ✓
- **Outline Cycle 1.2**: Collision detection ✓
- **Outline Cycle 1.3**: Submodule initialization ✓
- **Outline Cycle 1.4**: Submodule branching ✓
- **Outline Cycle 1.5**: --session pre-commit ✓
- **Outline Cycle 1.6**: rm subcommand ✓
- **Outline Cycle 1.7**: Branch-only cleanup ✓

All outline cycles implemented. No gaps detected.

## Validation Notes

**File references**: All referenced files (`src/claudeutils/worktree/cli.py`, `tests/test_worktree_cli.py`) don't exist yet — expected for TDD runbook. Paths match design specification.

**Metadata accuracy**: Phase header declares 7 cycles, actual count is 7. Correct.

**RED phase prose quality**: All RED phases use behaviorally specific assertions with concrete expected values, exit codes, and error messages. No vague prose detected. No full test code found (prose descriptions only).

**Sequencing**: All cycles follow proper RED→GREEN discipline. RED phases specify failures, GREEN phases describe minimal implementations.

**Consolidation**: No trivial cycles identified. Each cycle adds distinct behavioral complexity. Cycle 1.5 is appropriately complex (git plumbing with temp index) — no split needed.

## Recommendations

1. **Cycle 1.5 complexity**: This is the most complex cycle in Phase 1. During execution, ensure test coverage for main index isolation (critical requirement).

2. **Design reference**: Cycle 1.5 GREEN now references design.md lines 92-102 for exact command sequence. Executor should read design section for git plumbing details.

3. **Test fixture strategy**: All 7 cycles use `test_worktree_cli.py`. Consider shared fixtures in `conftest.py` for base repo setup (as suggested in outline expansion guidance).

---

**Ready for next step**: Yes — Phase 1 runbook ready for execution.
