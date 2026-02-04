# Vet Review: Design Workflow Enhancement Runbook

**Scope**: Runbook and step files in `plans/design-workflow-enhancement/`
**Date**: 2026-02-04T08:45:00-08:00

## Summary

Reviewed runbook for outline-first design workflow with requirements extension. The runbook covers all design requirements across 6 steps implementing both the original design (quiet-explore agent, skill restructuring) and the extension (requirements alignment validation). Structure is clear with good orchestration guidance. A few critical issues require fixing: completion gap in success criteria, missing prerequisite, inconsistent sequential dependency documentation, and structural validation gaps.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

1. **Success criteria file count mismatch**
   - Location: runbook.md:42
   - Problem: Success criteria says "All 7 files created/modified (1 agent, 3 skills, 3 vet/review agents)" but the list is ambiguous. The 7 files should be: quiet-explore (created), design skill, plan-adhoc, plan-tdd, design-vet-agent, vet-agent, vet-fix-agent (all modified). The parenthetical "(1 agent, 3 skills, 3 vet/review agents)" doesn't match this breakdown (quiet-explore is 1 agent, design-vet-agent is also an agent).
   - Fix: List all 7 files explicitly with created/modified status:
     ```markdown
     - All 7 files created/modified:
       - agent-core/agents/quiet-explore.md (created)
       - agent-core/skills/design/SKILL.md (modified)
       - agent-core/skills/plan-adhoc/SKILL.md (modified)
       - agent-core/skills/plan-tdd/SKILL.md (modified)
       - agent-core/agents/design-vet-agent.md (modified)
       - agent-core/agents/vet-agent.md (modified)
       - agent-core/agents/vet-fix-agent.md (modified)
     ```

2. **Missing design-vet-agent in prerequisites**
   - Location: runbook.md:50-57
   - Problem: Prerequisites list skill files and quiet-task.md baseline but don't include `agent-core/agents/design-vet-agent.md`. Step 5.2 modifies this file (adds section 4.5 and updates review template), so it must exist.
   - Fix: Add to prerequisites:
     ```markdown
     - Agent files exist:
       - agent-core/agents/quiet-task.md (baseline)
       - agent-core/agents/design-vet-agent.md (modified in Step 5)
       - agent-core/agents/vet-agent.md (modified in Step 6)
       - agent-core/agents/vet-fix-agent.md (modified in Step 6)
     ```

3. **Step 3 lacks structural validation directive**
   - Location: step-3.md:18
   - Problem: Says "First: Read full skill file to identify current section structure" but this is buried in the implementation for 3.1 only. Steps 3.2 and 3.3 reference specific line numbers (e.g., "line ~95") without validation that structure matches expectations. If skill file was previously edited, line numbers will be wrong.
   - Fix: Elevate structural validation to top of Step 3:
     ```markdown
     **First (all 3 skills):** Read full skill files to verify current structure matches expectations:
     - design/SKILL.md: Has Steps 0-7 with specific headings
     - plan-adhoc/SKILL.md: Has Point 0.5 at expected location
     - plan-tdd/SKILL.md: Has Phase 1 with Actions list
     Report any structural mismatches before proceeding with edits.
     ```

### Major Issues

1. **Step dependency documentation inconsistency**
   - Location: runbook.md:29-33 vs runbook.md:396-400
   - Problem: Two sections document dependencies with conflicting guidance. Line 29-33: "Steps 5-6: Independent of 1-4, can run after Step 4 or in parallel with 1-3". Line 396-400: "Steps 5-6: Can run in parallel with each other, after Step 4 (or in parallel with 1-3 if symlinks not needed)". The "if symlinks not needed" qualifier is misleading — Steps 5-6 modify skill/agent files that are validated in Step 4.
   - Suggestion: Reconcile both sections to state: "Steps 5-6: Can run in parallel with Steps 1-3 (no file dependencies), but Step 4 validation should run after all steps complete for comprehensive results."

2. **Design reference line numbers will drift**
   - Location: step-3.md:23-38 and throughout
   - Problem: Step files include exact line numbers from design.md (e.g., "lines ~40-54", "design lines 85-103", "lines ~95"). When design.md is edited (even adding a single line at top), all references become stale.
   - Suggestion: Replace line numbers with section references:
     - "lines ~40-54" → "sections 'Step 1: Understand Request' and 'Step 1.5: Memory Discovery'"
     - "design lines 85-103" → "section 'Documentation Checkpoint'"
     - "line ~95" → "section 'Point 0.5: Discover Codebase Structure'"

3. **Plugin-topic directive preservation not validated**
   - Location: step-3.md:37 and step-3.md:92
   - Problem: Preservation mapping says "Plugin-topic skill-loading directive (currently in Step 4 lines ~86-94) → Move to Phase A.5" but validation criteria don't check this was actually preserved. Step agent could delete it accidentally.
   - Suggestion: Add to Step 3 validation criteria (line 92):
     ```markdown
     - design skill Phase A.5 includes plugin-topic skill-loading directive
     - Complexity triage (Point 0) preserved before Phase A
     - Tail-call to /handoff --commit preserved in Phase C.5
     ```

4. **Vet agent conditional validation trigger unclear**
   - Location: step-6.md:86-107
   - Problem: Says "If task prompt includes requirements context" but doesn't explain how the context gets there. Planner creating the runbook will include requirements in Common Context, then vet-agent invoked during execution will have it via context reference. But this mechanism isn't stated.
   - Suggestion: Add clarification at top of 6.3 section:
     ```markdown
     **Trigger mechanism:** When runbook includes requirements in Common Context section, step files reference Common Context, loading requirements automatically. Vet-agent performs requirements validation when requirements fields are present.
     ```

### Minor Issues

1. **Step 3 preservation mapping uses line numbers**
   - Location: step-3.md:35-38
   - Note: References "currently in Step 4 lines ~86-94" and "currently Step 7 lines ~120-127". Same issue as Major Issue #2 — line numbers will drift. Use section names instead.

2. **Bash script absolute paths hardcoded**
   - Location: step-4.md:17-18 and 24
   - Note: Uses `/Users/david/code/claudeutils/` hardcoded. Works fine given orchestrator guidance, but alternative is `cd "$CLAUDE_PROJECT_DIR/agent-core"` if variable available. Not a problem, just noting.

3. **Report path naming inconsistency**
   - Location: step-5.md:148 and step-6.md:150
   - Note: Steps 1-4 use `step-N-description.md` (e.g., `step-1-agent-creation.md`, `step-3-skill-updates.md`). Steps 5-6 use `step-5-requirements-design.md` and `step-6-requirements-validation.md`. Slight format variation but both are descriptive. Not problematic.

4. **Step 5 doesn't specify verification method for nested markdown**
   - Location: step-5.md:48-68
   - Note: Shows traceability format as triple-backtick markdown block inside markdown content. Agent must understand this is example text to insert, not markdown formatting directive. Usually obvious from context but could be clearer with "Example to insert:" label.

5. **Step 6 lists "same changes as vet-agent" without detail**
   - Location: step-6.md:117-122
   - Note: Section 6.4 (vet-fix-agent) says "Apply same changes as vet-agent" and "changes mirror vet-agent exactly". For completeness, could spell out specific sections to modify rather than relying on agent to remember from 6.3.

## Positive Observations

**Strong orchestration guidance:**
- Clear parallelization opportunities documented (Step 3 can run parallel with 1-2)
- Stop conditions well-defined per step and globally
- Error escalation paths explicit (haiku → sonnet → user)
- Report locations specified for all steps

**Comprehensive validation at each step:**
- Every step includes validation criteria and success criteria sections
- Expected outcomes clearly stated
- Error conditions anticipated with handling instructions
- Unexpected result handling guidance provided

**Good separation of concerns:**
- Steps 1-2: Agent creation and review (standard vet pattern)
- Step 3: Skill updates (complex restructure + simple additions, independent from agent)
- Step 4: Integration (symlinks) and validation (just dev)
- Steps 5-6: Extension work cleanly separated from base implementation

**Design alignment traceability:**
- Step 3 includes detailed mapping from old steps (0-7) to new phases (A-C)
- Design references cited with section names and line estimates
- Preservation mapping ensures critical elements not lost

**Requirements extension well-integrated:**
- Steps 5-6 extend existing files rather than creating parallel structures
- Backward compatibility explicitly preserved ("if requirements context provided")
- Traceability format clearly specified with example

**Common Context pattern followed:**
- Runbook has Common Context section (lines 61-85)
- Step files reference "See plan file for context" (DRY principle)
- Key constraints and conventions documented once

**Design decisions section provides rationale:**
- Agent creation pattern explained (task agent + vet review)
- Model selection justified (sonnet interprets, haiku executes)
- Sequential dependency reasoning provided
- Symlink simplicity noted (2-line operation, don't over-specify)

**Realistic testing strategy:**
- Notes section acknowledges manual testing needed
- Lists specific verification steps (outline-first flow, quiet-explore file output, Context7 direct calls)
- Identifies what to test at each integration point

**Weak orchestrator metadata complete:**
- Total steps declared (6)
- Execution model per step specified
- Dependencies documented
- Error escalation paths defined
- Success criteria global and per-step

## Recommendations

1. **Consider splitting Step 3 into two steps:**
   - Step 3a: Update design skill (major restructuring, high complexity)
   - Step 3b: Update plan skills (simpler insertions)
   - Rationale: Design skill restructure (Steps 0-7 → Phases A-C) is substantial work involving content movement and new section creation. Combining with plan skill updates may overload step agent. Splitting enables better checkpointing.

2. **Add intermediate validation to Step 3:**
   - After completing 3.1 (design skill restructure), run YAML validation before proceeding to 3.2-3.3
   - Rationale: If restructure introduces syntax errors, catch them before modifying plan skills. Faster error localization.

3. **Add rollback guidance for partial completion:**
   - If Step 3 fails after completing 3.1 but before 3.2-3.3, what should orchestrator do?
   - Recommendation: Error conditions should include "Partial completion → git checkout affected files, restart step from beginning"

4. **Document testing strategy more concretely:**
   - Notes section (line 437-444) says "Manual: Run `/design` on test task with requirements.md" but doesn't specify what test task or provide example requirements.md
   - Recommendation: Add "Testing deferred to post-runbook. First real-world test will be running `/design` on continuation-passing job (which has requirements.md)."

5. **Consider adding design-vet-agent to Step 5 validation:**
   - Step 5.2 modifies design-vet-agent but validation criteria (line 138) only check "Both files modified" and "section 4.5 present"
   - Recommendation: Add "design-vet-agent review protocol includes all 4 requirement checks (completeness, consistency, scope, traceability)"

## Next Steps

1. **Fix critical issue #1:** Expand success criteria to list all 7 files explicitly with created/modified status
2. **Fix critical issue #2:** Add design-vet-agent and other agent files to prerequisites
3. **Fix critical issue #3:** Elevate structural validation to top of Step 3 for all three skills
4. **Address major issue #1:** Reconcile step dependency documentation in both sections
5. **Optional: Address major issues #2-4 and recommendations** if planner agrees they add value

## Design Alignment Analysis

### Original Design Coverage (Steps 1-4)

| Design Requirement | Runbook Step(s) | Status |
|-------------------|-----------------|--------|
| quiet-explore agent with file output | 1-2 create and review | ✓ Complete |
| Design skill three-phase workflow (A-B-C) | 3.1 restructure | ✓ Complete |
| Documentation checkpoint (Phase A.1) | 3.1 replaces Steps 1+1.5 | ✓ Complete |
| quiet-explore delegation (Phase A.2) | 3.1 updates explore section | ✓ Complete |
| Context7 direct calls (Phase A.3-4) | 3.1 updates research section | ✓ Complete |
| Outline-first (Phase A.5) | 3.1 adds outline section | ✓ Complete |
| Iterative discussion (Phase B) | 3.1 adds Phase B | ✓ Complete |
| Full design generation (Phase C.1) | 3.1 moves Step 4 content to C.1 | ✓ Complete |
| Documentation perimeter in design | 3.1 adds perimeter requirement to C.1 | ✓ Complete |
| Planner reads perimeter (plan-adhoc) | 3.2 adds Point 0.5 item 0 | ✓ Complete |
| Planner reads perimeter (plan-tdd) | 3.3 adds Phase 1 Action 0 | ✓ Complete |
| Symlink creation for agent | 4 runs just sync-to-parent | ✓ Complete |
| Validation passes | 4 runs just dev | ✓ Complete |

**Verdict:** All 13 original design requirements mapped to runbook steps. No gaps.

### Extension Design Coverage (Steps 5-6)

| Design Requirement | Runbook Step | Status |
|-------------------|--------------|--------|
| Requirements checkpoint (Phase A.0) | 5.1 adds to design skill | ✓ Complete |
| Requirements section in design | 5.1 adds C.1 guidance | ✓ Complete |
| Requirements traceability format | 5.1 provides example | ✓ Complete |
| design-vet-agent requirements checks | 5.2 adds to section 2 | ✓ Complete |
| design-vet-agent section 4.5 | 5.2 adds validation section | ✓ Complete |
| design-vet-agent report template | 5.2 adds requirements section | ✓ Complete |
| plan-adhoc requirements reading | 6.1 extends Point 0.5 item 0 | ✓ Complete |
| plan-adhoc Common Context | 6.1 adds requirements fields | ✓ Complete |
| plan-adhoc vet prompt | 6.1 updates checkpoint | ✓ Complete |
| plan-tdd requirements reading | 6.2 extends Phase 1 Action 0 | ✓ Complete |
| plan-tdd Common Context | 6.2 adds requirements fields | ✓ Complete |
| plan-tdd vet prompt | 6.2 updates checkpoint | ✓ Complete |
| vet-agent conditional validation | 6.3 adds requirements section | ✓ Complete |
| vet-agent report template | 6.3 adds requirements section | ✓ Complete |
| vet-fix-agent conditional validation | 6.4 mirrors vet-agent | ✓ Complete |

**Verdict:** All 15 extension requirements mapped to runbook steps. No gaps.

### Affected Files Cross-Check

Design "Affected Files (Extension)" section (design.md lines 369-379) lists:
- design skill ✓ (Step 5.1)
- design-vet-agent ✓ (Step 5.2)
- plan-adhoc ✓ (Step 6.1)
- plan-tdd ✓ (Step 6.2)
- vet-agent ✓ (Step 6.3)
- vet-fix-agent ✓ (Step 6.4)

Plus original design files:
- quiet-explore agent ✓ (Steps 1-2)
- design skill (also in extension) ✓ (Step 3.1 + 5.1)
- plan-adhoc (also in extension) ✓ (Step 3.2 + 6.1)
- plan-tdd (also in extension) ✓ (Step 3.3 + 6.2)

**Total:** 7 unique files (quiet-explore + design + plan-adhoc + plan-tdd + design-vet-agent + vet-agent + vet-fix-agent). Matches success criteria "7 files" count.

All affected files covered in runbook. No missing files.

### Out of Scope Verification

Design defers to future work:
- Session-log based capture → Not in runbook ✓
- Custom claude-code-guide wrapper → Not in runbook ✓
- Custom Context7 wrapper → Not in runbook ✓
- Automated perimeter validation hooks → Not in runbook ✓
- Requirements coverage metrics → Not in runbook ✓

No scope creep detected.

## Runbook Quality Analysis

### Actionability

**Strengths:**
- Each step specifies exact files to modify
- Code blocks provide insertion text verbatim (e.g., step-3.md lines 46-56, step-5.md lines 21-34)
- Insertion points specified with section headers and line estimates
- Bash commands fully spelled out (step-4.md lines 16-24)
- Agent specification complete with all YAML fields (step-1.md lines 18-36)

**Weaknesses:**
- Step 3 design skill restructure requires significant interpretation (map 8 sections → 3 phases)
- Line number estimates may be imprecise (noted with ~ prefix but no validation)
- "Read full skill file to identify structure" implies discovery work before edits

**Rating:** Strong actionability for Steps 1-2, 4-6. Moderate for Step 3 due to restructuring complexity.

### Unambiguity

**Clear:**
- Success criteria measurable (file exists, YAML parses, validation passes)
- Error conditions specify exact failure modes and escalation paths
- Stop conditions explicit (e.g., step-2.md line 34: "Report to user with specific conflicts")

**Ambiguous:**
- "Preservation mapping" in Step 3 — how to preserve while restructuring?
- "Structural changes preserve existing logic flow" — how verified?
- Conditional validation trigger in Step 6 — how does context get passed?

**Rating:** Generally clear, with a few interpretation gaps in Steps 3 and 6.

### Measurability

**All expected outcomes verifiable:**
- File existence (glob, ls)
- YAML parse (validation catches errors)
- Validation passes (just dev exit code)
- Symlink creation (ls -la)
- Git diff shows changes

**Success criteria quantifiable:**
- "All 7 files created/modified" (countable)
- "Symlinks created" (verifiable)
- "just dev passes" (exit code 0)

**Rating:** Excellent measurability throughout.

### Error Handling

**Each step includes:**
- Expected outcome
- Unexpected result handling
- Error conditions with escalation

**Escalation hierarchy clear:**
- Haiku → Sonnet: Step 4 symlink failures (line 30)
- Sonnet → User: Structural mismatches, ambiguous guidance (step-2.md line 34, step-3.md line 81)

**Stop conditions global (runbook.md lines 80-84) and per-step.**

**Rating:** Comprehensive error handling.

### Dependencies

**Sequential dependencies:**
- Step 2 depends on Step 1 (agent file must exist to review)
- Step 4 depends on Steps 1-3 (all files present for symlinks + validation)

**Parallelization opportunities:**
- Step 3 can run parallel with Steps 1-2 (no file dependency)
- Steps 5-6 can run parallel with each other

**Documentation:** Two sections cover dependencies (runbook.md lines 29-33 and 396-400), with slight inconsistency noted in Major Issue #1.

**Rating:** Dependencies well-understood, minor documentation inconsistency.

## Structural Alignment

### Weak Orchestrator Pattern

Runbook follows weak orchestrator metadata pattern:
- ✓ Total steps declared (6)
- ✓ Execution model per step
- ✓ Step dependencies documented
- ✓ Error escalation paths defined
- ✓ Report locations specified
- ✓ Success criteria global + per-step
- ✓ Common Context section

**Rating:** Full compliance.

### Step File Format

Each step file includes:
- ✓ Step header with plan reference
- ✓ Common Context reference
- ✓ Objective statement
- ✓ Execution model
- ✓ Implementation details
- ✓ Expected outcome
- ✓ Validation criteria
- ✓ Error conditions
- ✓ Report path

**Rating:** All 6 step files conform to expected structure.

### Common Context Usage

Runbook Common Context (lines 61-85) provides:
- Design location
- Key constraints
- Agent spec location
- Project conventions
- Stop conditions

Step files reference via "See plan file for context" — proper DRY pattern.

**Rating:** Correct Common Context usage.

## Completeness Check

### Prerequisites Verified

Runbook prerequisites (lines 50-57) list:
- Design document exists ✓
- Target skill files exist ✓
- Agent baseline exists (quiet-task.md) ✓
- Symlink recipe exists ✓

**Missing:** design-vet-agent, vet-agent, vet-fix-agent (Critical Issue #2)

### Dependencies Section

"Before This Runbook" and "After This Runbook" sections (lines 420-432) clearly state:
- Prerequisites (design complete, structure unchanged)
- Deliverables (skills updated, agent available, ready for testing)

**Rating:** Clear boundaries.

### Design Decisions Section

Runbook Design Decisions (lines 408-417) explain:
- Agent creation pattern
- No sequential dependency for Step 3
- Symlink step simplicity
- Model selection

**Rating:** Good rationale for key choices.

### Notes Section

Testing strategy (lines 437-444) outlines manual testing plan. Out-of-scope items deferred.

**Rating:** Adequate guidance for post-runbook work.

## Requirements Traceability Summary

**Original design:** 13 requirements, all mapped to Steps 1-4
**Extension design:** 15 requirements, all mapped to Steps 5-6
**Total coverage:** 28/28 requirements mapped to runbook steps

**No gaps detected.**
