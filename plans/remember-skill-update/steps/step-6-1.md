# Step 6.1

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Mechanical rename — grep-and-replace across codebase. Sonnet sufficient (no architectural judgment, purely mechanical substitution despite touching skill files). Advisory: artifact-type override rule recommends opus for skill file edits, but this phase is pure text substitution with no semantic content changes — sonnet assignment is appropriate exception.

---

## Step 6.1: Rename directory and update all references

**Objective**: Rename /remember to /codify across the codebase.

**Implementation:**
- `mv agent-core/skills/remember agent-core/skills/codify`
- Grep-and-replace across ~30 files: `grep -r "remember" agent-core/ agents/ .claude/ plans/ --include="*.md" -l`
- Key files: SKILL.md name/description, handoff skill + references, session.md, memory-index SKILL.md, agent-core docs (README.md, migration-guide.md, general-workflow.md, shortcuts.md), review skill, reflect skill, plan files
- Update skill name in SKILL.md frontmatter: `name: codify`
- Update description: "This skill should be used when..." with `/codify` trigger

**Validation:** Grep for `/remember` returns only plan files and historical references.

---
