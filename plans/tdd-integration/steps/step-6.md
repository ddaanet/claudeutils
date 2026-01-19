# Step 6

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 6: Update prepare-runbook.py for TDD cycles

**Objective**: Create planning request for prepare-runbook.py TDD cycle support

**Script Evaluation**: Large/Complex - Task requires separate planning session

**Execution Model**: Sonnet (creates planning request document)

**Tool Usage**:
- Use Write tool to create planning request file
- Use Read tool to reference design document
- Never use bash file operations or heredocs

**Rationale for Separate Planning**:
- Script modifications exceed 100 lines
- Complex parsing logic for cycle detection
- Multiple code paths (TDD vs general runbook)
- Requires careful handling of baseline selection (tdd-task.md vs quiet-task.md)
- Error handling for malformed cycle definitions
- Testing strategy needed

**Planning Requirements**:
1. Analyze current prepare-runbook.py structure
2. Design cycle detection logic (regex patterns for "## Cycle X.Y:")
3. Design TDD metadata detection (frontmatter: `type: tdd`)
4. Design baseline selection logic (tdd-task.md vs quiet-task.md)
5. Design cycle file generation (different from step files)
6. Design validation for cycle format
7. Update help text and error messages
8. Add unit tests or validation scripts

**Dependencies**:
- Step 3 must be complete (tdd-task.md baseline must exist)
- Understanding of current prepare-runbook.py implementation
- Design document cycle format specification

**Implementation**:

Create planning request document at `plans/tdd-integration/reports/step-6-planning-request.md` containing:

1. **Task Objective**: Add TDD cycle format support to prepare-runbook.py

2. **Complexity Rationale**:
   - Script modifications exceed 100 lines
   - Complex parsing logic for cycle detection
   - Multiple code paths (TDD vs general runbook)
   - Baseline selection logic (tdd-task.md vs quiet-task.md)

3. **Planning Requirements** (from design doc):
   - Analyze current prepare-runbook.py structure
   - Design cycle detection logic (regex for "## Cycle X.Y:")
   - Design TDD metadata detection (frontmatter: `type: tdd`)
   - Design baseline selection logic
   - Design cycle file generation
   - Design validation for cycle format
   - Update help text and error messages

4. **Dependencies**:
   - Step 3 must be complete (tdd-task.md baseline exists)
   - Current prepare-runbook.py implementation understood

5. **Reference Material**:
   - `plans/tdd-integration/design.md` (TDD runbook structure section)
   - `agent-core/bin/prepare-runbook.py` (current implementation)
   - `agent-core/agents/tdd-task.md` (baseline template created in Step 3)

6. **Next Action**: Requires separate planning session with sonnet or opus

**Expected Outcome**:
- Planning request file created at `plans/tdd-integration/reports/step-6-planning-request.md`
- Contains all 6 sections above
- Step marked as ready for separate planning session

**Error Handling**:
- Write permission denied → STOP and report
- Design document not found → STOP and report

**Validation**:
- Read `plans/tdd-integration/reports/step-6-planning-request.md` successfully
- Use Grep to verify all 6 required sections present
- File size > 2000 bytes (comprehensive request)

**Success Criteria**:
- Planning request file created with all required sections
- Contains all planning requirements from design doc
- Ready for delegation to separate planning session

**Report Path**: `plans/tdd-integration/reports/step-6-report.md`

---
