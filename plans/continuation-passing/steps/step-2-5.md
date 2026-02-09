# Step 2.5

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 2.5: Update /handoff Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/handoff/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: ["/commit"]
```

**Note:** `/handoff` default exit is `["/commit"]` only when `--commit` flag present. Hook handles this conditional logic (design "Handoff --commit Special Case" line 249-252).

### 2. Replace hardcoded tail-call section

**Current location:** "Tail-Call: --commit Flag" section (line ~213: "If `--commit` flag was provided: As the **final action** of this skill, invoke `/commit` using the Skill tool.")

**Replacement:** Continuation protocol template (from Common Phase Context).

**Expected Outcome:**
/handoff skill has frontmatter and continuation protocol. Conditional default exit handled by hook, not skill logic.

---
