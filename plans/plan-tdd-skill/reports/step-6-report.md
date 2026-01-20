# Step 6: Add Cycle Breakdown Guidance - Report

**Date**: 2026-01-20
**Status**: Complete

---

## Actions Taken

### Added Comprehensive Cycle Breakdown Guidance Section

Added new section "Cycle Breakdown Guidance" to `agent-core/skills/plan-tdd/skill.md` before the Templates section.

**Section includes:**

1. **Granularity Criteria** (with examples)
   - Each cycle: 1-3 assertions
   - Clear RED failure expectation
   - Minimal GREEN implementation
   - Independent verification
   - Examples of "too granular" and "too coarse"

2. **Numbering Scheme**
   - X.Y format explained (X = phase, Y = increment)
   - Numbering rules (start at 1.1, sequential, no duplicates)
   - Example numbering across multiple phases

3. **Dependency Management**
   - Default: Sequential within phase
   - `[DEPENDS: X.Y]` for explicit dependencies
   - `[REGRESSION]` for existing behavior tests
   - Validation rules (no circular, no forward refs)

4. **Stop Conditions Generation**
   - Standard template (for all cycles)
   - Custom conditions (when to add)
   - Examples of custom conditions for complex cycles

5. **Common Patterns** (8 patterns with examples)
   - Basic CRUD operations
   - Feature flag with multiple modes
   - Authentication flow
   - Integration with external service
   - Edge cases and boundary conditions
   - Refactoring existing code
   - Multi-step feature with setup
   - Composite functionality

6. **Granularity Decision Tree**
   - Visual decision flow
   - Criteria for good vs split cycles

7. **Anti-Patterns to Avoid** (5 anti-patterns)
   - Setup-only cycles
   - God cycles
   - Unclear RED expectations
   - Missing regression verification
   - Coupled cycles

8. **Cycle Breakdown Algorithm Summary**
   - Step-by-step process
   - Validation checklist

---

## Validation

**Section exists in skill.md:**
```
✓ "Cycle Breakdown Guidance" section found
```

**Contains all 5 required subsections:**
```
✓ Granularity Criteria
✓ Numbering Scheme
✓ Dependency Management
✓ Stop Conditions Generation
✓ Common Patterns
```

**Additional subsections added:**
```
✓ Granularity Decision Tree
✓ Anti-Patterns to Avoid
✓ Cycle Breakdown Algorithm Summary
```

**Examples of common patterns:**
```
✓ 8 patterns documented with examples
✓ Each pattern has structure explanation
✓ Rationale provided for each pattern
```

**Content quality:**
```
✓ Clear, actionable guidance
✓ Examples for abstract concepts
✓ Anti-patterns with corrections
✓ Visual decision tree
```

---

## Success Criteria Met

- ✓ Clear guidance for cycle decomposition
- ✓ Common patterns documented (8 patterns)
- ✓ Dependency rules explicit
- ✓ Granularity criteria detailed
- ✓ Examples throughout section
- ✓ Anti-patterns identified with solutions

**Added value:**
- Decision tree for granularity
- Anti-patterns section
- Algorithm summary
- More patterns than required (8 vs typical 5)

---

**Step 6 complete.**
