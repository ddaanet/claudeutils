# Step 5.1

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: opus
**Phase**: 5

---

## Step 5.1: Create general-step reference material

**Objective**: Create general-patterns.md reference file and update anti-patterns.md and examples.md with general-step content.

**Prerequisites**:
- Read `agent-core/skills/runbook/references/` directory structure
- Read existing references/anti-patterns.md and references/examples.md (pattern understanding)
- plugin-dev:skill-development loaded (progressive disclosure guidance)

**Implementation**:

**Part A: Create general-patterns.md**

Create `agent-core/skills/runbook/references/general-patterns.md`:

1. **Granularity criteria**:
   - Atomic steps (single file, single concern, <100 lines changed)
   - Composable steps (multiple files, related changes, shared validation)
   - Complex steps (>100 lines, needs separate planning)

2. **Prerequisite validation patterns**:
   - Creation steps: must include "**Prerequisite:** Read [file:lines] — understand [behavior/flow]"
   - Transformation steps: self-contained recipe sufficient
   - Investigation gates: when to require codebase exploration before implementation

3. **Composable vs atomic guidelines**:
   - When to split: unrelated files, different validation criteria
   - When to merge: same file, sequential operations, shared success criteria

**Part B: Update anti-patterns.md**

Update `agent-core/skills/runbook/references/anti-patterns.md`:

1. **Add general-step anti-patterns section**:
   - Missing investigation prerequisites for creation steps
   - Vague success criteria ("analysis complete" vs "analysis has 6 sections with line numbers")
   - Success criteria checking structure when step should verify content/behavior
   - Steps without concrete Expected Outcome
   - Ambiguous Error Conditions
   - Referencing downstream consumers instead of upstream source (e.g., referencing an agent that applies criteria instead of the decision document that defines them — in bootstrapping pipelines, downstream consumers may not be updated yet)

**Part C: Update examples.md**

Update `agent-core/skills/runbook/references/examples.md`:

1. **Add complete general-step example**:
   - Show all fields: Objective, Prerequisite, Implementation, Expected Outcome, Error Conditions, Validation
   - Include both creation step (with prerequisite) and transformation step (self-contained)
   - Demonstrate concrete success criteria

**Expected Outcome**:
- general-patterns.md created with granularity criteria and prerequisite patterns
- anti-patterns.md has general-step anti-patterns section
- examples.md has complete general-step examples (creation + transformation)

**Error Conditions**:
- If patterns too abstract → add concrete heuristics and thresholds
- If anti-patterns lack corrections → add "correct pattern" for each anti-pattern
- If examples incomplete → verify all required fields present and filled

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review runbook references additions. Verify general-patterns.md has concrete granularity criteria and prerequisite patterns, anti-patterns.md general section has corrections, and examples.md has complete general-step examples with all required fields."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-5.1-skill-review.md

---
