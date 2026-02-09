# Step 2.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 2.1: Verify agent structure

Verify `agent-core/agents/` contains 14 agent `.md` files:

```bash
agent_count=$(find agent-core/agents -maxdepth 1 -name "*.md" -type f | wc -l)
echo "Agent count: $agent_count"
[ "$agent_count" -eq 14 ] || echo "ERROR: Expected 14 agents"
```

---
