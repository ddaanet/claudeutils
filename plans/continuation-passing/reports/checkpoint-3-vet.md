# Vet Review: Continuation Passing Documentation

**Scope**: Documentation artifacts from continuation passing project (fragment, workflow decisions, design.md updates, memory index)
**Date**: 2026-02-09
**Mode**: review + fix

## Summary

Reviewed 4 documentation files after architecture change (single-skill pass-through, skills own default-exit). Found minor terminology inconsistencies and clarity issues. All fixable issues have been addressed.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None found.

### Major Issues

1. **Design.md contradicts architecture in D-3**
   - Location: plans/continuation-passing/design.md:115-116
   - Problem: States "Hook does NOT append default-exit entries" but earlier text suggests hook reads default-exit
   - Fix: Clarify that hook never reads or appends default-exit — skills manage at runtime
   - **Status**: FIXED

2. **Fragment uses outdated terminology**
   - Location: agent-core/fragments/continuation-passing.md:42
   - Problem: Says "If no continuation: use default-exit from frontmatter" suggesting runtime lookup
   - Fix: Clarify skills implement their own default-exit behavior (may reference frontmatter)
   - **Status**: FIXED

### Minor Issues

1. **Fragment table inconsistent with design**
   - Location: agent-core/fragments/continuation-passing.md:67-75
   - Problem: Table header says "Default Exit" but design.md D-3 clarifies skills own default-exit at runtime, not as metadata the hook uses
   - Fix: Add note to table clarifying this is documentation of skill behavior
   - **Status**: FIXED

1. **Workflow decisions missing "correct pattern" emphasis**
   - Location: agents/decisions/workflow-optimization.md:300
   - Problem: "Correct pattern" describes reading continuation but doesn't emphasize skills own default-exit
   - Fix: Add explicit statement about skills managing default-exit at runtime
   - **Status**: FIXED

3. **Design.md D-3 verbose on backward compatibility**
   - Location: plans/continuation-passing/design.md:125-126
   - Problem: "Backward compatibility" section repeats concept already stated in "Mechanism"
   - Fix: Consolidate to single clear statement
   - **Status**: FIXED

2. **Fragment missing clarification on cooperative skills**
   - Location: agent-core/fragments/continuation-passing.md:19
   - Problem: Frontmatter schema shown but no explanation of what makes a skill "cooperative"
   - Fix: Add brief note that cooperative means skill implements consumption protocol
   - **Status**: FIXED

## Fixes Applied

- agent-core/fragments/continuation-passing.md:20 — Added clarification that "cooperative" means implementing consumption protocol
- agent-core/fragments/continuation-passing.md:42-43 — Clarified skills implement default-exit behavior (not lookup from frontmatter)
- agent-core/fragments/continuation-passing.md:76 — Added table note explaining Default Exit column is documentation not enforcement
- agents/decisions/workflow-optimization.md:300 — Added explicit statement that skills manage their own standalone exit logic
- plans/continuation-passing/design.md:115-126 — Clarified hook never reads default-exit, consolidated mechanism and backward compatibility

## Positive Observations

- **Architecture consistency**: Design.md D-1 through D-7 tell a coherent story about the architecture change
- **Implementation alignment**: Fragment protocol matches actual parser implementation in userpromptsubmit-shortcuts.py
- **Empirical validation**: Design.md accurately documents 0% FP rate achievement and validation methodology
- **Clear scope**: Fragment is appropriately concise (protocol reference, not tutorial)
- **Memory index structure**: Entries follow existing keyword-rich format
- **Test coverage**: Parser tests comprehensively validate single-skill pass-through behavior

## Recommendations

- Consider adding a "Migration" section to the fragment for existing cooperative skills (how to update from old hardcoded tail-calls)
- Design.md D-6 could benefit from a concrete example showing single-skill vs multi-skill parsing outcomes
- Workflow-optimization decisions might include a "Related decisions" pointer to workflow-core.md handoff tail-call pattern
