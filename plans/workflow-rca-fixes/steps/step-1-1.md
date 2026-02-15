# Step 1.1

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.1: Create error-handling skill

**Objective**: Wrap error-handling.md fragment as a skill for injection into bash-heavy agents.

**Prerequisites**:
- Read `agent-core/skills/project-conventions/SKILL.md` (early bootstrap reference)
- Read `agent-core/fragments/error-handling.md` (content to wrap)
- plugin-dev:skill-development loaded

**Implementation**:

Create `agent-core/skills/error-handling/SKILL.md` following project-conventions pattern:

1. YAML frontmatter:
   - name: error-handling
   - description: "This skill should be used when bash-heavy agents need error suppression guidance. Provides error handling rules for agents that execute bash commands frequently."
   - user-invocable: false

2. Skill prolog (brief purpose statement)

3. Include full content of `agent-core/fragments/error-handling.md`

**Expected Outcome**: Skill file created at `agent-core/skills/error-handling/SKILL.md` following fragment-wrapping pattern.

**Error Conditions**:
- If skill structure invalid → review frontmatter format
- If content duplicates → ensure single source of truth (fragment content only)

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer (plugin-dev): "Review error-handling skill for structure, frontmatter quality, and progressive disclosure"
3. Read review report
4. If UNFIXABLE: STOP, escalate to user
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-1.1-skill-review.md

---
