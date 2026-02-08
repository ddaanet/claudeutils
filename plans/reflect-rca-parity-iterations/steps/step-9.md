# Step 9

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 9: Add Mandatory Conformance Test Cycles to plan-tdd and plan-adhoc

**Objective:** Update both planning skills to mandate conformance test cycles when the design document includes an external reference (shell prototype, API spec, visual mockup).

**Design Reference:** DD-1 (design lines 64-77)

**Prerequisites:**
- **Phase 2 committed** — Gap 4 (Steps 4-5) must be committed before executing this step
- Gap 4 defined "conformance exception to prose test descriptions" in testing.md and workflow-advanced.md
- This step (Gap 1) mandates WHEN conformance tests are required — when design has external reference

**Context:**
- Gap 4 provides the precision guidance (exact expected strings)
- Gap 1 provides the trigger condition (external reference in design)
- Together they close the conformance gap identified in statusline-parity RCA

**Files:**
- `agent-core/skills/plan-tdd/SKILL.md` (existing, edit)
- `agent-core/skills/plan-adhoc/SKILL.md` (existing, edit)

**Changes Required:**

### For plan-tdd/SKILL.md:

Add conformance test cycles guidance to planner sections (likely Phase 2-3 cycle planning). Content (~15 lines):

```markdown
### Mandatory Conformance Test Cycles

**Trigger:** When design document includes external reference (shell prototype, API spec, visual mockup) in `Reference:` field or spec sections.

**Requirement:** Planner MUST include conformance test cycles that bake expected behavior from the reference into test assertions.

**Mechanism:**
- Reference is consumed at authoring time (during planning)
- Expected strings from reference become test assertions
- Tests are permanent living documentation of expected behavior (reference not preserved as runtime artifact)

**Test precision (from Gap 4):**
- Use precise prose descriptions with exact expected strings from reference
- Example: "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator"
- NOT abstracted: "Assert output contains formatted model with emoji and color"

**Rationale:** Tests that include exact expected strings eliminate translation loss between spec and implementation. This addresses statusline-parity failures where tests verified structure but not conformance.

**Related:** See testing.md "Conformance Validation for Migrations" for detailed guidance.
```

### For plan-adhoc/SKILL.md:

Add conformance validation steps guidance (adapted for non-TDD context). Content (~15 lines):

```markdown
### Mandatory Conformance Validation Steps

**Trigger:** When design document includes external reference (shell prototype, API spec, visual mockup) in `Reference:` field or spec sections.

**Requirement:** Runbook MUST include validation steps that verify implementation conforms to the reference specification.

**Mechanism:**
- Reference is consumed during planning
- Expected behavior from reference becomes validation criteria in runbook steps
- Validation can be: conformance test cycles, manual comparison steps, or automated conformance checks

**Validation precision (from Gap 4):**
- When using test-based validation: Use precise prose descriptions with exact expected strings
- Example validation criterion: "Output matches shell reference: `🥈 sonnet \033[35m…` with double-space separators"
- NOT abstracted: "Output contains formatted model with appropriate styling"

**Rationale:** Conformance validation closes the gap between specification and implementation. Exact expected strings prevent abstraction drift.

**Related:** See testing.md "Conformance Validation for Migrations" for detailed guidance.
```

**Implementation:**

1. **For plan-tdd/SKILL.md:**
   - Read file to identify planner guidance sections
   - Search for section heading containing "Phase 2" or "Phase 3" or "Cycle" or "Planning" in planner workflow
   - After identifying appropriate section (likely within Phase 2-3 cycle decomposition guidance), insert "Mandatory Conformance Test Cycles" content as a new subsection
   - Use Edit tool to add content, preserving existing structure

2. **For plan-adhoc/SKILL.md:**
   - Read file to identify planner guidance sections
   - Search for section heading containing "Point 1" or "Step Planning" or "Phase-by-Phase" in planner workflow
   - After identifying appropriate section (likely within Point 1 expansion guidance), insert "Mandatory Conformance Validation Steps" content as a new subsection
   - Use Edit tool to add content, preserving existing structure

**Expected Outcome:**
- Both skills updated with conformance requirements
- Trigger condition clear (external reference in design)
- Precision guidance references Gap 4 (exact expected strings)
- Rationale explains why (translation loss prevention)

**Validation:**
- Read both updated skills
- Verify trigger condition documented ("external reference")
- Verify precision guidance references Gap 4 or testing.md
- Verify rationale explains conformance vs structure distinction

**Success Criteria:**
- plan-tdd/SKILL.md: ~15 lines added documenting mandatory conformance test cycles
- plan-adhoc/SKILL.md: ~15 lines added documenting mandatory conformance validation steps
- Both reference DD-1 mechanism (reference consumed at authoring, tests permanent)
- Both reference Gap 4 precision guidance (exact expected strings) OR testing.md conformance section

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-9-execution.md`

---
