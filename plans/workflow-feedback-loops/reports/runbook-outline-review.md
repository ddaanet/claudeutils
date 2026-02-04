# Runbook Outline Review: workflow-feedback-loops

**Scope**: plans/workflow-feedback-loops/runbook-outline.md
**Date**: 2026-02-04T18:45:00Z
**Mode**: review + fix

## Summary

Reviewed runbook outline for workflow-feedback-loops implementation. The outline provides good phase structure with balanced complexity distribution across 4 phases (11 files affected). Found issues with requirements mapping accuracy, missing file path specificity, and phase complexity assessment. All issues have been fixed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **FR-2 requirements mapping incorrect**
   - Location: runbook-outline.md:11
   - Problem: FR-2 (feedback after implementation phase) mapped to Phase 4, step 4.3, but Phase 4 is infrastructure (prepare-runbook.py, workflows.md). The /orchestrate skill enhancement that implements FR-2 is in Phase 3, step 3.4.
   - Fix: Corrected mapping from "Phase 4, step 4.3" to "Phase 3, step 3.4"
   - **Status**: FIXED

2. **Missing file paths in Phase 1 steps**
   - Location: runbook-outline.md:25-26
   - Problem: Steps 1.1 and 1.2 don't specify file paths for new agents, making it unclear where files will be created
   - Fix: Added explicit file paths (agent-core/agents/outline-review-agent.md and agent-core/agents/runbook-outline-review-agent.md)
   - **Status**: FIXED

3. **Missing file paths in Phase 2 steps**
   - Location: runbook-outline.md:32-35
   - Problem: Steps 2.1-2.4 don't specify which files are being enhanced
   - Fix: Added explicit file paths for all four agent files in agent-core/agents/
   - **Status**: FIXED

4. **Missing file paths in Phase 3 steps**
   - Location: runbook-outline.md:41-44
   - Problem: Steps 3.1-3.4 don't specify which files are being updated
   - Fix: Added explicit file paths for all four skill files
   - **Status**: FIXED

5. **Missing file paths in Phase 4 steps**
   - Location: runbook-outline.md:50-51
   - Problem: Steps 4.1-4.2 don't specify which files are being updated
   - Fix: Added explicit file paths (agent-core/bin/prepare-runbook.py and agents/decisions/workflows.md)
   - **Status**: FIXED

### Minor Issues

1. **Phase 4 complexity underassessed**
   - Location: runbook-outline.md:48
   - Problem: Phase 4 marked as "Low" complexity but touches critical infrastructure (prepare-runbook.py generates metadata consumed by skills, workflows.md is authoritative documentation)
   - Fix: Changed complexity from "Low" to "Medium"
   - **Status**: FIXED

2. **Step 3.4 description incomplete**
   - Location: runbook-outline.md:44
   - Problem: Description only mentions "phase boundary enhancement" but doesn't mention requirements context passing (a key design decision from lines 485-488 of design.md)
   - Fix: Extended description to "(phase boundary checkpoint, requirements context)"
   - **Status**: FIXED

3. **Step 4.1 description lacks specificity**
   - Location: runbook-outline.md:50
   - Problem: Description "Phase metadata in step files" doesn't specify where metadata goes
   - Fix: Changed to "add Phase metadata to step file frontmatter" (matches design line 540)
   - **Status**: FIXED

## Fixes Applied

All fixes applied to runbook-outline.md:

- Line 11: Corrected FR-2 mapping from "4 | 4.3" to "3 | 3.4"
- Lines 25-26: Added file paths to Phase 1 steps (agent-core/agents/*.md)
- Lines 32-35: Added file paths to Phase 2 steps with clarifications (fix-all vs review-only)
- Lines 41-44: Added file paths to Phase 3 steps with enhanced descriptions
- Line 48: Changed Phase 4 complexity from "Low" to "Medium"
- Lines 50-51: Added file paths to Phase 4 steps with more specific descriptions

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 | Satisfied | Phase 1-4, all agent/skill changes implement feedback checkpoints |
| FR-2 | Satisfied | Phase 3 step 3.4 (corrected from 4.3) |
| FR-3 | Satisfied | Phase 1 steps 1.1-1.2, Phase 2 steps 2.1-2.2 |
| FR-4 | Satisfied | Phase 1 steps 1.1-1.2, Phase 2 steps 2.1-2.2 |
| FR-5 | Satisfied | Phase 1 steps 1.1-1.2, Phase 2 steps 2.1-2.2 |
| FR-6 | Satisfied | Phase 1 steps 1.1-1.2, Phase 2 step 2.1 |
| FR-7 | Satisfied | Phase 3 steps 3.2-3.3 |
| FR-8 | Satisfied | Phase 1-2 all steps |

**Gaps:** None. All requirements mapped to implementation steps.

---

## Positive Observations

**Phase structure is well-balanced:**
- Phase 1-2: Agent work (2 new + 4 enhanced = 6 files)
- Phase 3: Skill work (4 files)
- Phase 4: Infrastructure (1 script + 1 doc)
- No single phase is disproportionately large

**Dependency ordering is correct:**
- New agents (Phase 1) before enhanced agents (Phase 2)
- Agent work (Phase 1-2) before skills that invoke them (Phase 3)
- Skill changes (Phase 3) before infrastructure that supports them (Phase 4)

**Requirements mapping table is comprehensive:**
- Every FR-* from design is accounted for
- Phase and step references are specific
- Notes column provides context

**Complexity assessment is reasonable:**
- Medium for agent work (6 files, protocol changes)
- High for skill work (4 files, behavioral changes)
- Medium for infrastructure (2 files, critical path)

**Key decisions reference section:**
- Captures the four most important design constraints
- Provides quick lookup for implementers
- Matches design Section 4 (Architecture) decisions

## Recommendations

**For phase expansion:**
- Phase 3 (skills) will likely need sub-phases due to "High" complexity
- Consider reviewing /design and /plan-adhoc changes separately from /plan-tdd and /orchestrate
- Each skill file is ~200-400 lines; phase-by-phase review will catch integration issues early

**For implementation:**
- Start with Phase 1 (new agents) to establish fix-all pattern
- Use Phase 1 agents as templates for Phase 2 enhancements
- Test agent enhancements (Phase 2) before skill integration (Phase 3)
- Validate prepare-runbook.py changes (Phase 4.1) with test runbooks before updating documentation (Phase 4.2)

**File coverage verification:**
- All 11 files from design Section "Implementation Notes" are covered
- New artifact types (outline.md, runbook-outline.md, runbook-phase-N.md) are documented in outline
- No files from design are missing from outline
