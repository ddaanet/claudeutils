# Step 8

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 8: Update Documentation

**Objective**: Update tdd-workflow.md to reference /plan-tdd skill.

**Script Evaluation**: Direct execution (documentation task)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read to read tdd-workflow.md
- Use Edit to add reference
- Use Grep to find insertion point

**Implementation**:

Update `agent-core/agents/tdd-workflow.md`:

1. Find workflow entry point section (should mention /design)
2. Add reference to /plan-tdd skill after /design:
   - "After /design (TDD mode), use /plan-tdd to generate TDD runbook"
   - Include link: `agent-core/skills/plan-tdd/skill.md`
3. Add note about prepare-runbook.py step:
   - "After /plan-tdd, run prepare-runbook.py to create execution artifacts"

**Expected Outcome**: tdd-workflow.md updated with /plan-tdd reference.

**Unexpected Result Handling**:
- If tdd-workflow.md doesn't exist → STOP, report (should exist from Step 2)
- If workflow entry point unclear → STOP, ask for guidance on insertion location

**Error Conditions**:
- Read fails → STOP, report file not found
- Edit fails → STOP, report error

**Validation**:
- Grep for "/plan-tdd" in tdd-workflow.md returns match
- Reference includes link to skill.md
- prepare-runbook.py step mentioned

**Success Criteria**:
- tdd-workflow.md references /plan-tdd skill
- Workflow integration documented
- prepare-runbook.py step clear

**Report Path**: `plans/plan-tdd-skill/reports/step-8-report.md`

---
