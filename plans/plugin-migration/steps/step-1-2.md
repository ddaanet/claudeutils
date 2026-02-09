# Step 1.2

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.2: Create fragment version marker

Create version marker at `agent-core/.version`:

```bash
printf '1.0.0' > agent-core/.version
```

**Validation:** File exists, content exactly `1.0.0` (5 bytes, no trailing newline)

---
