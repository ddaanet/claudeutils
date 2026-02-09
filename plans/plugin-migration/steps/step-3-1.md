# Step 3.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 3.1: Create hooks.json

Create `agent-core/hooks/hooks.json` with plugin hook configuration:

```bash
cat > agent-core/hooks/hooks.json << 'EOF'
{
  "hooks": {
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
}
EOF
```

**Validation:** File exists, JSON valid, contains `hooks` field at root level

---
