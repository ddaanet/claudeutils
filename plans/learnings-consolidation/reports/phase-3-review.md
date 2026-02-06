# Vet Review: Phase 3 Runbook (remember-task + memory-refactor agents)

**Scope**: plans/learnings-consolidation/runbook-phase-3.md
**Date**: 2026-02-06T20:45:00Z

## Summary

Phase 3 runbook defines creation of two autonomous agents (remember-task and memory-refactor) with embedded protocols and quiet execution patterns. The runbook provides comprehensive specifications for both agents including frontmatter, protocol embedding, pre-check algorithms, and reporting structures. Overall quality is high with complete agent specifications and clear validation steps.

**Overall Assessment**: Needs Minor Changes

## Issues Found

### Critical Issues

None.

### Major Issues

1. **Missing report structure section count for memory-refactor**
   - Location: Step 3.2, section E "Output format"
   - Problem: Focus area specifies "6 sections for remember-task" but memory-refactor report structure isn't clearly enumerated as sections
   - Fix: While the output format is well-specified, clarify that it includes 4 components (Files created, Files modified, Content moved, Verification) to match the structural clarity of remember-task's 6-section reporting

2. **Conservative bias inconsistency**
   - Location: Step 3.1, Pre-Consolidation Checks sections 1-3
   - Problem: Each check states different conservative biases (supersession: "consolidate both", contradiction: "escalate", redundancy: "consolidate") but the overall pattern isn't explicitly summarized
   - Suggestion: Add a summary at the end of section C that states: "Conservative bias principle: When uncertain, prefer escalation (contradictions) or consolidation (supersession/redundancy) over silent data loss"

### Minor Issues

1. **Design decision reference incompleteness**
   - Location: End of step 3.2, "Design References" section
   - Note: Lists D-4, D-5, D-6 but doesn't explicitly map which decision applies to which agent step. Consider adding inline citations in step text (e.g., "Pre-Consolidation Checks (per design D-5)")
   - Already present: Step 3.1 section C has "(per design D-5)" inline, step 3.2 section C has "(per design D-6)" — inconsistency in citation density

2. **Frontmatter tools array formatting**
   - Location: Both Step 3.1 and 3.2 frontmatter examples
   - Note: Tools array shows as JSON array `["Read", "Write", ...]` in YAML frontmatter. While valid, YAML list syntax would be more idiomatic:
   ```yaml
   tools:
     - Read
     - Write
     - Edit
   ```
   - Impact: Low — both formats are valid YAML

3. **Validation bash commands missing error handling**
   - Location: Step 3.1 and 3.2 validation sections
   - Note: Validation commands use `ls -l`, `head -10`, `grep` without explicit error handling or expected output specification
   - Suggestion: Add expected output examples or success criteria for each validation command

4. **Protocol synchronization comment placement**
   - Location: Step 3.1, section D "Consolidation Protocol"
   - Note: Shows synchronization comment as `<!-- Source: agent-core/skills/remember/SKILL.md steps 1-4a -->` but doesn't specify exact placement (before protocol? after heading? inline?)
   - Impact: Low — planner will likely place appropriately, but explicit guidance prevents ambiguity

5. **Quiet execution pattern reference missing for memory-refactor**
   - Location: Step 3.2, section F "Return protocol"
   - Note: remember-task agent explicitly states "quiet execution pattern (report to file, return filepath)" in multiple places, but memory-refactor return protocol doesn't use the term "quiet execution" despite following the pattern
   - Suggestion: Add explicit reference: "Follows quiet execution pattern: return filepaths only, no report content in response"

## Requirements Validation

**Requirements context provided:** Yes, via design.md reference

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-4 (Supersession detection) | Satisfied | Step 3.1 § C.1 — keyword overlap + negation patterns with >50% threshold |
| FR-5 (Contradiction detection) | Satisfied | Step 3.1 § C.2 — semantic comparison with target file content, escalation on match |
| FR-6 (Redundancy detection) | Satisfied | Step 3.1 § C.3 — phrase overlap scoring with >70% threshold |
| FR-7 (Memory refactoring) | Satisfied | Step 3.2 § C — 6-step refactoring process with validator autofix integration |
| FR-8 (Sub-agent with skill reference) | Satisfied | Step 3.1 § D — embedded protocol from remember skill steps 1-4a with source comment |

**Gaps:** None. All Phase 3 requirements fully covered.

## Positive Observations

- **Exceptional frontmatter completeness**: Both agents include name, description (with use case context), model, color, and tools — fully addresses review focus area
- **Protocol embedding fidelity**: Step 3.1 § D faithfully extracts remember skill steps 1-4a with explicit source attribution and synchronization warnings
- **Concrete pre-check algorithms**: All three checks (supersession, contradiction, redundancy) specify thresholds (50%, 70%), methods (keyword overlap, phrase matching), and conservative bias directives
- **Comprehensive report structures**: remember-task specifies 6 distinct sections (Summary, Supersession, Redundancy, Contradictions, File Limits, Discovery, Consolidation Details) with subsection details
- **Clear refactoring process**: memory-refactor provides 6-step process with heuristics for split points, size targets (100-300 lines), and validator autofix integration
- **Validation completeness**: Both steps include bash validation commands and success criteria checklists
- **Error handling**: Both steps include "Unexpected Result Handling" and "Error Conditions" tables with specific guidance
- **Design alignment**: Explicit references to D-4 (embedded protocol), D-5 (pre-checks), D-6 (reactive refactoring) throughout

## Recommendations

1. **Enhance cross-referencing consistency**: Apply inline design decision citations uniformly across both steps (both already have some, but density varies)
2. **Add output examples**: Include sample report snippets in validation sections to demonstrate expected structure
3. **Clarify validation success criteria**: For bash validation commands, specify what output indicates success vs. failure

## Next Steps

1. Apply major issue #2: Add conservative bias summary to Step 3.1 § C
2. Optional: Address major issue #1 by clarifying memory-refactor output has 4 components (minor impact)
3. Proceed to implementation — runbook is ready for execution after minor clarification

---

**Review conducted by:** vet-agent (sonnet)
**Focus areas verified:**
- ✅ Agent frontmatter completeness (name, description, model, color, tools)
- ✅ Protocol embedding fidelity (remember skill steps 1-4a)
- ✅ Pre-check algorithms concreteness (thresholds: 50%, 70%)
- ✅ Report structure completeness (6 sections for remember-task)
- ✅ Refactoring process clarity (6 steps for memory-refactor)
- ✅ Quiet execution pattern (report to file, return filepath)
- ✅ Design decision references (D-4, D-5, D-6)
