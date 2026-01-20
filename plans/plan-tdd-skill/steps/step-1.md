# Step 1

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 1: Review pytest-md Reference Implementation

**Objective**: Understand pytest-md /plan-tdd skill structure and extract reusable patterns.

**Script Evaluation**: Direct execution (research task)

**Execution Model**: Sonnet

**Implementation**:

Read and analyze:
1. `/Users/david/code/pytest-md/.backup/skills/plan-tdd/SKILL.md`
2. `/Users/david/code/pytest-md/.backup/skills/plan-design/SKILL.md`

Extract:
- Cycle structure and numbering (X.Y format)
- Dependency markers (`[DEPENDS: X.Y]`, `[REGRESSION]`)
- RED/GREEN specification format
- Stop condition templates
- Extraction compatibility requirements

Document findings in `plans/plan-tdd-skill/reports/step-1-analysis.md`:
- Reusable patterns for agent-core
- Differences between pytest-md standalone vs agent-core orchestration
- Adaptation requirements

**Expected Outcome**: Analysis report documenting reusable patterns and adaptation needs.

**Error Conditions**:
- Reference files missing → STOP, report to user

**Validation**:
- Report exists at specified path
- Report contains sections: Reusable Patterns, Differences, Adaptation Requirements
- Report size > 1000 bytes

**Success Criteria**:
- Clear understanding of pytest-md cycle structure
- Identified patterns applicable to agent-core
- Documented differences requiring adaptation

**Report Path**: `plans/plan-tdd-skill/reports/step-1-analysis.md`

---
