# Step 2.6

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 2.6: Update /commit Skill

**Execution Model:** Sonnet

**File:** `agent-core/skills/commit/SKILL.md`

**Implementation:**

### 1. Add frontmatter `continuation:` block

```yaml
continuation:
  cooperative: true
  default-exit: []
```

**Note:** `/commit` is terminal — empty `default-exit` list.

### 2. No other changes needed

`/commit` already terminal (displays STATUS and stops). No hardcoded tail-call to remove, no protocol section needed (empty continuation = no tail-call).

**Expected Outcome:**
/commit skill has frontmatter with empty `default-exit`. No behavioral changes.

---
