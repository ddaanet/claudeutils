# Outline Review: worktree-fixes

**Artifact**: plans/worktree-fixes/outline.md
**Date**: 2026-02-13T19:45:00Z
**Mode**: review + fix-all

## Summary

Outline provides a clear, well-structured approach to fixing 5 worktree issues across slug derivation, validation, merge handling, and session automation. The design introduces shared task-block parsing infrastructure and establishes clear phase boundaries. All requirements are traced to outline sections with complete coverage. No critical or major issues found. Minor issues related to clarity and completeness have been fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Key Decisions, Phase 0, Scope | Complete | Task name constraints with validation at creation and commit |
| FR-2 | Phase 0 | Complete | Precommit validation integrated with just precommit |
| FR-4 | Key Decisions, Phase 1, Scope | Complete | Session merge full task block extraction via shared parser |
| FR-5 | Key Decisions, Phase 1, Scope | Complete | MERGE_HEAD detection for merge commit creation |
| FR-6 | Key Decisions, Phase 2, Phase 3, Scope | Complete | Session automation moves task editing from skill to CLI |
| Q-1 | Key Decisions, Open Questions | Complete | Resolved: validation at both creation and commit |

**Traceability Assessment**: All requirements covered

## Review Findings

### Critical Issues

None identified.

### Major Issues

None identified.

### Minor Issues

1. **Missing test file in scope**
   - Location: Scope Boundaries section, line 62-70
   - Problem: `tests/test_worktree_session.py` listed as NEW but `src/claudeutils/validation/tasks.py` also NEW — missing corresponding test file for validation module
   - Fix: Added `tests/test_validation_tasks.py` to scope for validation module tests
   - **Status**: FIXED

2. **Migration requirement reference**
   - Location: Phase Boundaries table, Phase 0 rationale, line 25
   - Problem: Mentions "migration (FR-3)" but FR-3 is not defined in requirements.md
   - Fix: Removed reference to FR-3 from Phase 0 rationale, as FR-2 (precommit validation) provides sufficient rationale
   - **Status**: FIXED

3. **Phase 3 acceptance criteria vague**
   - Location: Acceptance Criteria Mapping, Phase 3 deliverables, line 56-58
   - Problem: "Remove Mode A step 4..." doesn't specify what these steps currently do or why removal is appropriate
   - Fix: Added context clarifying these are manual session.md editing steps now automated by CLI
   - **Status**: FIXED

## Fixes Applied

- Line 69: Added `tests/test_validation_tasks.py` to Scope Boundaries for validation module test coverage
- Line 25: Removed reference to undefined FR-3 from Phase 0 rationale
- Line 56: Enhanced Phase 3 deliverables description with context about what steps are being removed and why (manual session.md editing now automated)

## Positive Observations

- Shared task-block parser (`extract_task_blocks()`) is a strong design decision that reduces duplication between FR-4 and FR-6
- Defense-in-depth validation approach (creation-time + precommit) provides robust protection against invalid task names
- Phase dependencies are clearly articulated with explicit rationale for ordering
- MERGE_HEAD detection is a clean fix for FR-5 that avoids the empty-diff problem
- Scope boundaries are explicit and comprehensive, listing all affected files
- Open question Q-1 is explicitly resolved with rationale documented
- Acceptance criteria mapping provides clear traceability from requirements to deliverables

## Recommendations

- Consider adding explicit error handling patterns for edge cases in task-block parsing (e.g., malformed continuation lines, missing task name)
- Phase 2 implementation should include idempotency tests for `new --task` and `rm` operations as called out in FR-6.4
- Skill update (Phase 3) might benefit from examples showing before/after for clarity

---

**Ready for user presentation**: Yes
