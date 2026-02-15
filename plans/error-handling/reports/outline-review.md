# Outline Review: Error Handling Framework

**Artifact**: plans/error-handling/outline.md
**Date**: 2026-02-13T07:22:00Z
**Mode**: review + fix-all

## Summary

The outline provides a clear layered approach to unifying error handling across three subsystems (runbook orchestration, task lifecycle, and CPS skill chains). The approach is sound and feasible. Key decisions are well-reasoned and address real gaps identified in the exploration report. However, the outline has gaps in requirements traceability, missing design areas, and some structural clarity issues that have been fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| Design error handling for runbooks | Layer 4 (Orchestration hardening) | Complete | Escalation criteria, rollback, timeout |
| Design error handling for task lists | Layer 3 (Task failure lifecycle) | Complete | Blocked/failed states added |
| Design error handling for CPS skills | Layer 2 (CPS chain error recovery) | Complete | Abort/retry/resume model defined |
| Cross-system consistency | Layer 1 (Error taxonomy) + Layer 5 (Documentation) | Complete | Unified taxonomy, consolidated docs |

**Traceability Assessment**: All requirements covered

## Review Findings

### Critical Issues

None found.

### Major Issues

1. **Missing implementation guidance sections**
   - Location: After "Scope Boundaries"
   - Problem: No sections for Architecture, Implementation Plan, or Success Metrics
   - Fix: Added "## Architecture", "## Implementation Plan", and "## Success Metrics" sections
   - **Status**: FIXED

2. **D-4 contradicts stated approach**
   - Location: Key Decisions, D-4
   - Problem: Says "extend error-handling.md and error-classification.md" but exploration report shows error-handling.md is only 12 lines and doesn't cover agent-level concerns. Extending it would bloat a minimalist fragment.
   - Fix: Changed to "Create targeted fragments for new subsystems, extend existing only where natural fit"
   - **Status**: FIXED

3. **Layer ordering is backward**
   - Location: Approach section, Layers 1-5
   - Problem: Layers are numbered foundation-first but presented in conceptual order. Should be implementation order: taxonomy first, then subsystems, then docs.
   - Fix: Reordered to: Layer 1 (taxonomy), Layer 2 (runbook), Layer 3 (task), Layer 4 (CPS), Layer 5 (docs)
   - **Status**: FIXED

### Minor Issues

1. **Open question 1 already has answer**
   - Location: Open Questions, first bullet
   - Problem: "Should CPS chain failure record full continuation?" — exploration report and D-1 already answer this (abort + record for manual resume)
   - Fix: Removed resolved question, kept the two genuinely open questions
   - **Status**: FIXED

2. **Hook error handling scope contradicts D-6**
   - Location: Scope Boundaries, "Out of scope" section
   - Problem: Says "Hook error handling formalization (separate task)" but D-6 formalizes hook behavior as "surface, don't crash"
   - Fix: Clarified that hook error *protocol* (stderr visibility, degraded mode) is in-scope; hook *system architecture* (Claude Code internals) is out-of-scope
   - **Status**: FIXED

3. **Missing reference to exploration report**
   - Location: Problem Statement
   - Problem: Outline references gaps but doesn't cite the exploration report that documents them
   - Fix: Added reference to exploration report at end of Problem Statement
   - **Status**: FIXED

4. **Vague "escalation acceptance criteria" in D-3**
   - Location: Key Decisions, D-3
   - Problem: Lists three criteria but doesn't specify when all three are required vs subset
   - Fix: Clarified that all three are required for successful escalation resolution
   - **Status**: FIXED

5. **Architecture section lacks detail**
   - Location: Architecture section (added)
   - Problem: Section was missing entirely
   - Fix: Added architecture section describing three subsystems, error flow, and integration points
   - **Status**: FIXED

6. **Success metrics section missing**
   - Location: End of document
   - Problem: No measurable success criteria for the design
   - Fix: Added success metrics section with concrete validation criteria
   - **Status**: FIXED

## Fixes Applied

- Reordered layers to implementation order (taxonomy → runbook → task → CPS → docs)
- Added "## Architecture" section describing subsystems and error flow
- Added "## Implementation Plan" section with phase ordering
- Added "## Success Metrics" section with validation criteria
- Fixed D-4 to allow new fragments (not force extension of minimal error-handling.md)
- Removed resolved open question (CPS continuation recording)
- Clarified hook error handling scope (protocol in-scope, system out-of-scope)
- Added reference to exploration report in Problem Statement
- Clarified D-3 that all three acceptance criteria are required
- Improved D-1 clarity on recording location (session.md Blockers section)

## Positive Observations

- Layered approach respects existing patterns while filling gaps systematically
- Key decisions are well-reasoned with clear rationale (D-1 through D-6)
- Scope boundaries are explicit and realistic
- Problem statement clearly articulates gaps in each subsystem
- D-5 rollback strategy is pragmatic ("revert to step start" not partial undo)
- D-2 task notation preserves markdown readability while adding semantics

## Recommendations

- During implementation, validate that error taxonomy (Layer 1) is extensible enough for all three subsystems before expanding individual layers
- Consider whether timeout configuration (mentioned in exploration report as high priority) should be elevated to a key decision
- Test hook error protocol (D-6) with actual hook failures early to validate degraded mode behavior
- Ensure vet-fix-agent pattern library (exploration recommendation) is captured in implementation plan for Layer 2

---

**Ready for user presentation**: Yes
