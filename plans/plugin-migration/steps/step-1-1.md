# Step 1.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.1: Create plugin manifest

Create minimal plugin manifest at `agent-core/.claude-plugin/plugin.json`:

```bash
mkdir -p agent-core/.claude-plugin
cat > agent-core/.claude-plugin/plugin.json << 'EOF'
{
  "name": "edify",
  "version": "1.0.0",
  "description": "Workflow infrastructure for Claude Code projects"
}
EOF
```

**Validation:** File exists, JSON valid via `jq .`, contains name/version/description

---
