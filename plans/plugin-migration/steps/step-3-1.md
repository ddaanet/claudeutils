# Step 3.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 3.1: Create hooks.json

**Objective:** Create `edify-plugin/hooks/hooks.json` with plugin hook configuration using direct format (per D-4).

**Execution Model:** Haiku (inline execution)

**Implementation:**

Create `edify-plugin/hooks/hooks.json`:

```bash
cat > edify-plugin/hooks/hooks.json << 'EOF'
{
  "PreToolUse": [
    {
      "matcher": "Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "bash $CLAUDE_PLUGIN_ROOT/hooks/pretooluse-block-tmp.sh",
          "timeout": 5
        }
      ]
    },
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py",
          "timeout": 10
        }
      ]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Bash",
      "hooks": [
        {
          "type": "command",
          "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py",
          "timeout": 10
        }
      ]
    }
  ],
  "UserPromptSubmit": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/userpromptsubmit-shortcuts.py",
          "timeout": 5
        },
        {
          "type": "command",
          "command": "python3 $CLAUDE_PLUGIN_ROOT/hooks/userpromptsubmit-version-check.py",
          "timeout": 5
        }
      ]
    }
  ]
}
EOF
```

**Design References:**
- D-4: `hooks.json` separate file with DIRECT format `{"PreToolUse": [...]}` (not wrapper format)
- Design Component 2: Hook migration with `$CLAUDE_PLUGIN_ROOT` paths
- Design Component 2 table: Hook script changes (all scripts stay unchanged except symlink-redirect deletion)

**Format note:**
- Direct format: hook events at root level (correct for `hooks/hooks.json` file)
- Wrapper format (`{"hooks": {...}}`) only used for inline hooks in `plugin.json`
- This file uses direct format per D-4 decision

**Path resolution:**
- `$CLAUDE_PLUGIN_ROOT` resolves to plugin directory at runtime
- Dev mode (`--plugin-dir ./edify-plugin`): resolves to `edify-plugin/`
- Consumer mode (marketplace): resolves to cached plugin directory

**Validation:**
- File exists at `edify-plugin/hooks/hooks.json`
- JSON is well-formed: `jq . edify-plugin/hooks/hooks.json`
- Root level contains hook event keys (PreToolUse, PostToolUse, UserPromptSubmit) - NO wrapper `hooks` field
- All scripts referenced exist (check in Step 3.2 after deletion)

**Expected Outcome:** Plugin hook configuration file created with direct format.

**Error Conditions:**
- JSON syntax error → Fix JSON structure
- `jq` not installed → Install with `brew install jq`
- Wrapper format used → Must be direct format per D-4

**Success Criteria:**
- File exists at `edify-plugin/hooks/hooks.json`
- JSON validates with `jq`
- Direct format (hook events at root, no wrapper `hooks` field)
- All referenced scripts exist (verified after Step 3.2)

---
