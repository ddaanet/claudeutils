# Step 7

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 7: Create /plan-tdd skill

**Objective**: Create planning request for /plan-tdd skill implementation

**Script Evaluation**: Large/Complex - Task requires separate planning session

**Execution Model**: Sonnet (creates planning request document)

**Tool Usage**:
- Use Write tool to create planning request file
- Use Read tool to reference design document
- Never use bash file operations or heredocs

**Rationale for Separate Planning**:
- New skill creation with substantial logic
- Must adapt pytest-md reference implementation
- Complex TDD cycle planning logic
- Requires 4-point planning process for TDD runbooks
- Integration with prepare-runbook.py (depends on step 6)
- Error handling and validation
- Testing strategy needed

**Planning Requirements**:
1. Review pytest-md `/plan-design` skill as reference
2. Design 4-point planning process for TDD runbooks
3. Design cycle breakdown logic (feature → cycles)
4. Design RED/GREEN/REFACTOR phase templates
5. Design stop condition generation
6. Design dependency tracking between cycles
7. Design metadata generation for TDD runbooks
8. Create skill directory structure and frontmatter
9. Update skill documentation

**Dependencies**:
- Step 6 must be complete (prepare-runbook.py supports TDD cycles)
- pytest-md reference implementation available
- Design document TDD runbook structure specification

**Reference Material**:
- `~/code/pytest-md/.claude/skills/plan-design/` (if exists)
- `plans/tdd-integration/design.md` (TDD runbook structure section)
- `agent-core/agents/tdd-workflow.md` (created in step 2)

**Implementation**:

Create planning request document at `plans/tdd-integration/reports/step-7-planning-request.md` containing:

1. **Task Objective**: Create new `/plan-tdd` skill for TDD runbook generation

2. **Complexity Rationale**:
   - New skill creation with substantial logic
   - Must adapt pytest-md reference implementation
   - Complex TDD cycle planning logic
   - Integration with prepare-runbook.py (depends on Step 6)

3. **Planning Requirements** (from design doc):
   - Review pytest-md `/plan-design` skill as reference
   - Design 4-point planning process for TDD runbooks
   - Design cycle breakdown logic (feature → cycles)
   - Design RED/GREEN/REFACTOR phase templates
   - Design stop condition generation
   - Design dependency tracking between cycles
   - Design metadata generation for TDD runbooks
   - Create skill directory structure and frontmatter

4. **Dependencies**:
   - Step 6 must be complete (prepare-runbook.py supports TDD cycles)
   - pytest-md reference implementation available
   - Design document TDD runbook structure specification

5. **Reference Material**:
   - `~/code/pytest-md/.claude/skills/plan-design/` (if exists)
   - `plans/tdd-integration/design.md` (TDD runbook structure section)
   - `agent-core/agents/tdd-workflow.md` (created in Step 2)

6. **Next Action**: Requires separate planning session with sonnet

**Expected Outcome**:
- Planning request file created at `plans/tdd-integration/reports/step-7-planning-request.md`
- Contains all 6 sections above
- Step marked as ready for separate planning session (after Step 6 complete)

**Error Handling**:
- Write permission denied → STOP and report
- Design document not found → STOP and report

**Validation**:
- Read `plans/tdd-integration/reports/step-7-planning-request.md` successfully
- Use Grep to verify all 6 required sections present
- File size > 2000 bytes (comprehensive request)

**Success Criteria**:
- Planning request file created with all required sections
- Contains reference to pytest-md implementation
- Ready for delegation to separate planning session (after Step 6)

**Report Path**: `plans/tdd-integration/reports/step-7-report.md`

---
