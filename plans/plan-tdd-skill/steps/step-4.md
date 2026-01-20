# Step 4

**Plan**: `plans/plan-tdd-skill/runbook.md`
**Common Context**: See plan file for context

---

## Step 4: Create Skill Directory and Frontmatter

**Objective**: Create skill directory structure with metadata frontmatter.

**Script Evaluation**: Small script

**Execution Model**: Sonnet

**Tool Usage**:
- Use Bash for mkdir
- Use Write for file creation
- Never use heredocs

**Implementation**:

```bash
mkdir -p agent-core/skills/plan-tdd
```

Create `agent-core/skills/plan-tdd/skill.md` with frontmatter:

```yaml
---
name: plan-tdd
description: Create TDD runbook with RED/GREEN/REFACTOR cycles from design document
model: sonnet
requires:
  - Design document from /design (TDD mode)
  - CLAUDE.md for project conventions (if exists)
outputs:
  - TDD runbook at plans/<feature-name>/runbook.md
  - Ready for prepare-runbook.py processing
---
```

**Expected Outcome**: Skill directory created with frontmatter-only file.

**Error Conditions**:
- Directory creation fails → STOP, report permissions issue
- Write fails → STOP, report error

**Validation**:
- Directory exists: `agent-core/skills/plan-tdd/`
- File exists: `agent-core/skills/plan-tdd/skill.md`
- File contains valid YAML frontmatter

**Success Criteria**:
- Skill directory structure ready
- Frontmatter metadata correct

**Report Path**: `plans/plan-tdd-skill/reports/step-4-report.md`

---
