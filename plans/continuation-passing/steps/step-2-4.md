# Step 2.4

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 2.4: Update /orchestrate Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/orchestrate/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/handoff --commit", "/commit"]
```

### 2. Add `Skill` to `allowed-tools`

Current `allowed-tools: Task, Read, Bash, Grep, Glob`
Updated: `allowed-tools: Task, Read, Bash, Grep, Glob, Skill`

### 3. Add continuation protocol section

**Note:** Design states "/orchestrate has no hardcoded Skill tail-call to remove — suggests next actions in prose". Add continuation protocol alongside existing completion handling (Section 6 "Completion").

Insert protocol at end of skill, after completion section:

```markdown
