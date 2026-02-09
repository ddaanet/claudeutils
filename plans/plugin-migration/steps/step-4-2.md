# Step 4.2

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 4

---

## Step 4.2: Update root justfile

Add `import 'agent-core/just/portable.just'` at top, remove migrated recipes, keep project-specific recipes (test, format, check, lint, release, line-limits).

---
