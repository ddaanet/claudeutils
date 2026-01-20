# Step 3

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 3: Design Skill Process Flow

**Objective**: Design the skill's execution flow from design doc input to runbook output.

**Script Evaluation**: Prose description (design task)

**Execution Model**: Sonnet

**Implementation**:

Design skill process with these phases:

**Phase 1: Intake**
- Read design document path (from user or default location)
- Read CLAUDE.md if exists (project conventions)
- Validate design document format

**Phase 2: Analysis**
- Extract feature name and goals
- Identify design decisions and constraints
- Check for unresolved confirmations
- Determine cycle decomposition strategy

**Phase 3: Cycle Planning**
- Apply cycle breakdown algorithm (from Step 2)
- Generate cycle definitions with RED/GREEN specs
- Assign dependencies and mark regressions
- Generate stop conditions per cycle

**Phase 4: Runbook Generation**
- Create YAML frontmatter (type: tdd, model: haiku)
- Generate Weak Orchestrator Metadata section
- Generate Common Context from design decisions
- Output cycle definitions
- Write to `plans/<feature-name>/runbook.md`

**Phase 5: Validation**
- Verify runbook format
- Check prepare-runbook.py compatibility
- Report success with next action guidance

Document process flow in `plans/plan-tdd-skill/reports/step-3-process-flow.md`:
- Phase breakdown with inputs/outputs
- Error handling per phase
- User interaction points (confirmations)
- Integration with prepare-runbook.py

**Expected Outcome**: Complete skill process flow specification.

**Error Conditions**:
- Process flow has gaps → STOP, clarify design

**Validation**:
- Process flow document exists
- All 5 phases documented
- Error handling specified

**Success Criteria**:
- Clear end-to-end process from design doc to runbook
- User interaction points identified
- prepare-runbook.py integration specified

**Report Path**: `plans/plan-tdd-skill/reports/step-3-process-flow.md`

---
