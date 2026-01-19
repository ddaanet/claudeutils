# Step 2

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 2: Create TDD workflow documentation

**Objective**: Write new `agent-core/agents/tdd-workflow.md` documenting TDD workflow

**Script Evaluation**: Prose description (requires semantic content creation)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Write tool to create new file
- Use Read tool to reference design document
- Use Grep tool for content validation
- Never use bash file operations or heredocs

**Implementation**:

Create new file `agent-core/agents/tdd-workflow.md` with the following structure and content based on design document:

**Required Sections:**

1. **Overview**
   - TDD workflow purpose and when to use
   - Integration with oneshot workflow
   - Methodology detection signals

2. **Workflow Stages**
   - `/design` (TDD mode) → design document with spike test section
   - `/plan-tdd` → TDD runbook with cycles
   - `/orchestrate` → cycle execution via tdd-task agent
   - `/vet` → review uncommitted changes
   - Apply fixes if needed
   - `/review-analysis` → TDD process review

3. **TDD Cycle Structure**
   - RED phase protocol
   - GREEN phase protocol
   - REFACTOR phase protocol (mandatory per cycle)
   - Stop conditions and escalation

4. **Refactoring Tiers**
   - Tier 1: Script-based (mechanical transformations)
   - Tier 2: Simple runbook (2-5 steps, minor judgment)
   - Tier 3: Full runbook (5+ steps, design decisions)

5. **Commit Strategy**
   - WIP commit as rollback point
   - Post-refactoring amend
   - Safety checks before amend
   - Only precommit-validated states in history

6. **Command Reference**
   - `just test` - Run test suite
   - `just lint` - Lint + reformat
   - `just precommit` - Check + test (no reformat)

7. **Integration Points**
   - How TDD workflow differs from oneshot
   - When to use each workflow
   - Transition between workflows

**Content Source**: Extract from `plans/tdd-integration/design.md` sections:
- Unified Workflow Entry Point
- TDD Runbook Structure
- TDD Task Agent (protocol sections)
- Post-TDD Execution Flow
- Command Reference

**Expected Outcome**:
- File `agent-core/agents/tdd-workflow.md` created
- Contains all 7 required sections
- Follows markdown format consistent with oneshot-workflow.md
- File size 5000-8000 bytes (substantial documentation)

**Unexpected Result Handling**:
- If agent-core/agents directory missing: STOP - verify submodule
- If file size < 3000 bytes: Review content completeness before proceeding

**Error Conditions**:
- Directory not found → STOP and report to user
- Write permission denied → STOP and report to user

**Validation**:
- Read `agent-core/agents/tdd-workflow.md` successfully (confirms file exists)
- Use Grep to verify all required sections present (Overview, Workflow Stages, etc.)
- File size typically 5000-8000 bytes (may vary with detail level)
- Content accurately reflects design document

**Success Criteria**:
- File created with all 7 required sections
- Content accurately reflects design document
- File size indicates substantial documentation (5000-8000 bytes)
- Markdown syntax valid

**Report Path**: `plans/tdd-integration/reports/step-2-report.md`

---
