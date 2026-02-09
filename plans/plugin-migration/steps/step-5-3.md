# Step 5.3

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Step 5.3: Validate all functionality

**Plugin discovery:** `claude --plugin-dir ./agent-core` → verify skills in `/help`, agents in Task tool

**Hook testing:** Restart session, trigger each event type (PreToolUse, PostToolUse, UserPromptSubmit), verify behavior matches baseline

**Agent coexistence:** Create test `test-task.md` agent, verify both plugin and local agents visible

**NFR validation:**
- NFR-1: Compare edit→restart cycle time with baseline (should match)
- NFR-2: Measure context size before/after with identical session (diff ≤ 5%)

---
