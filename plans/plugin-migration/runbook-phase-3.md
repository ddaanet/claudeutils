# Phase 3: Hook Migration

**Purpose:** Create plugin hook configuration, version check hook script, and delete obsolete symlink-redirect hook.

**Dependencies:** Phase 1 (plugin manifest exists)

**Model:** Haiku (configuration and script files)

---

## Step 3.1: Create hooks.json

**Objective:** Create `agent-core/hooks/hooks.json` with plugin hook configuration using wrapper format.

**Execution Model:** Haiku (inline execution)

**Implementation:**

Create `agent-core/hooks/hooks.json`:

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

**Design References:**
- D-4: `hooks.json` separate file, not inline in `plugin.json`
- Design Component 2: Hook migration with wrapper format
- Design Component 2 table: Hook script changes (all scripts stay unchanged except symlink-redirect deletion)

**Path resolution:**
- `$CLAUDE_PLUGIN_ROOT` resolves to plugin directory at runtime
- Dev mode (`--plugin-dir ./agent-core`): resolves to `agent-core/`
- Consumer mode (marketplace): resolves to cached plugin directory

**Validation:**
- File exists at `agent-core/hooks/hooks.json`
- JSON is well-formed: `jq . agent-core/hooks/hooks.json`
- Contains `hooks` field at root level
- All hook events present: PreToolUse, PostToolUse, UserPromptSubmit
- All scripts referenced exist (check in Step 3.2 after deletion)

**Expected Outcome:** Plugin hook configuration file created with wrapper format.

**Error Conditions:**
- JSON syntax error → Fix JSON structure
- `jq` not installed → Install with `brew install jq`
- Missing wrapper structure → Verify `hooks` field wraps events

**Success Criteria:**
- File exists at `agent-core/hooks/hooks.json`
- JSON validates with `jq`
- Plugin hooks.json format (root `hooks` field, no description wrapper)
- All referenced scripts exist (verified after Step 3.2)

---

## Step 3.2: Delete obsolete hook script

**Objective:** Delete `agent-core/hooks/pretooluse-symlink-redirect.sh` (purpose eliminated by plugin auto-discovery).

**Execution Model:** Haiku (inline execution)

**Implementation:**

Remove symlink-redirect hook:

```bash
rm agent-core/hooks/pretooluse-symlink-redirect.sh
```

**Design Reference:**
- Design Component 2 table: "pretooluse-symlink-redirect.sh: Delete — Purpose eliminated — no symlinks to protect"
- Design "Affected Files (Delete)" section: Lists this file for deletion

**Rationale:**
This hook prevented editing agent-core files via symlinks. With plugin auto-discovery, skills/agents/hooks load directly from agent-core (no symlinks), so the hook's purpose is eliminated.

**Validation:**
- File no longer exists: `[ ! -f agent-core/hooks/pretooluse-symlink-redirect.sh ]`
- Remaining hooks present: `pretooluse-block-tmp.sh`, `submodule-safety.py`, `userpromptsubmit-shortcuts.py`, `userpromptsubmit-version-check.py`

**Expected Outcome:** Symlink-redirect hook script deleted.

**Error Conditions:**
- File doesn't exist (already deleted) → Success (idempotent)
- Permission denied → Check write permissions on `agent-core/hooks/`

**Success Criteria:**
- `pretooluse-symlink-redirect.sh` no longer exists
- Other hook scripts remain intact

---

## Step 3.3: Create version check hook

**Objective:** Create `agent-core/hooks/userpromptsubmit-version-check.py` with once-per-session version mismatch detection.

**Execution Model:** Haiku (inline execution)

**Implementation:**

Create version check hook script:

```bash
cat > agent-core/hooks/userpromptsubmit-version-check.py << 'EOF'
#!/usr/bin/env python3
"""
UserPromptSubmit hook: Check if project's .edify-version matches plugin .version.
Fires once per session (uses temp file gate). Warns via additionalContext if mismatch.
"""
import json
import os
import sys
from pathlib import Path


def main():
    # Read hook input from stdin
    hook_input = json.load(sys.stdin)

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    plugin_root = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", "agent-core"))

    # Temp file for once-per-session gating
    temp_file = project_dir / "tmp" / ".edify-version-checked"

    # If already checked this session, exit silently
    if temp_file.exists():
        sys.exit(0)

    # Read version files
    project_version_file = project_dir / ".edify-version"
    plugin_version_file = plugin_root / ".version"

    # If project has no .edify-version, skip check (may not use managed fragments)
    if not project_version_file.exists():
        sys.exit(0)

    # Read versions
    project_version = project_version_file.read_text().strip()
    plugin_version = plugin_version_file.read_text().strip() if plugin_version_file.exists() else "unknown"

    # If versions match, mark as checked and exit silently
    if project_version == plugin_version:
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.touch()
        sys.exit(0)

    # Version mismatch: warn via additionalContext
    warning = f"⚠️ Fragments outdated (project: {project_version}, plugin: {plugin_version}). Run /edify:update."

    output = {
        "hookSpecificOutput": {
            "additionalContext": warning
        },
        "systemMessage": f"Fragment version mismatch detected. {warning}"
    }

    # Mark as checked (only warn once per session)
    temp_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file.touch()

    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
EOF

chmod +x agent-core/hooks/userpromptsubmit-version-check.py
```

**Design References:**
- Design Component 7: Post-upgrade version check behavior
- Once-per-session gating: temp file `tmp/.edify-version-checked`
- Rationale: No PostUpgrade hook exists; UserPromptSubmit is earliest reliable hook point

**Script behavior:**
1. Check if already fired this session (temp file exists) → exit silently
2. Read `.edify-version` (project) and `.version` (plugin)
3. If project has no `.edify-version` → exit silently (not using managed fragments)
4. If versions match → create temp file, exit silently
5. If versions differ → inject warning via `additionalContext`, create temp file, exit

**Temp file path:** `$CLAUDE_PROJECT_DIR/tmp/.edify-version-checked` (follows project tmp/ convention per CLAUDE.md, not system `/tmp/`; also avoids conflict with pretooluse-block-tmp.sh hook which blocks /tmp writes)

**Validation:**
- File exists at `agent-core/hooks/userpromptsubmit-version-check.py`
- File is executable: `[ -x agent-core/hooks/userpromptsubmit-version-check.py ]`
- Python syntax valid: `python3 -m py_compile agent-core/hooks/userpromptsubmit-version-check.py`
- Script uses project `tmp/` directory (not system `/tmp/`)

**Expected Outcome:** Version check hook script created and executable.

**Error Conditions:**
- Python syntax error → Fix script
- Permission denied → Check write permissions
- Incorrect temp file path (system `/tmp/`) → Must use `$CLAUDE_PROJECT_DIR/tmp/`

**Success Criteria:**
- Script exists and is executable
- Python syntax is valid
- Uses project `tmp/` directory for temp file
- Follows once-per-session gating pattern

---

## Phase 3 Checkpoint

**Verification:**

Run these commands to verify Phase 3 completion:

```bash
# Verify hooks.json exists and is valid
test -f agent-core/hooks/hooks.json && jq . agent-core/hooks/hooks.json > /dev/null && echo "✓ hooks.json valid" || echo "✗ hooks.json invalid"

# Verify symlink-redirect deleted
[ ! -f agent-core/hooks/pretooluse-symlink-redirect.sh ] && echo "✓ Obsolete hook deleted" || echo "✗ Symlink-redirect still exists"

# Verify version check hook exists and is executable
test -x agent-core/hooks/userpromptsubmit-version-check.py && echo "✓ Version check hook created" || echo "✗ Version check hook missing or not executable"

# Verify all referenced scripts exist
for script in pretooluse-block-tmp.sh submodule-safety.py userpromptsubmit-shortcuts.py userpromptsubmit-version-check.py; do
  test -f "agent-core/hooks/$script" && echo "✓ $script exists" || echo "✗ $script missing"
done

# Verify Python syntax for all Python hooks
for script in submodule-safety.py userpromptsubmit-shortcuts.py userpromptsubmit-version-check.py; do
  python3 -m py_compile "agent-core/hooks/$script" && echo "✓ $script syntax valid" || echo "✗ $script syntax error"
done
```

**Manual test (requires restart):**
1. Exit current Claude Code session
2. Restart: `claude --plugin-dir ./agent-core`
3. Verify hooks load without errors (check startup output)
4. Test each hook event:
   - **PreToolUse (Write/Edit):** Try `echo "test" > tmp/test.txt` → pretooluse-block-tmp.sh should block `/tmp/` writes
   - **PreToolUse (Bash):** Try `cd subdir && ls` (if cwd ≠ project root) → submodule-safety should warn or block
   - **PostToolUse (Bash):** Verify submodule-safety runs after Bash commands
   - **UserPromptSubmit:** Submit any prompt → shortcuts hook processes (no visible output unless shortcut matched)
   - **Version check:** Create `.edify-version` with old version, restart, verify warning on first prompt

**Success:** All verification commands pass, hooks functional after restart

**On failure:** Review error messages, check hook scripts exist, verify JSON syntax, restart to reload hooks

**Next:** Proceed to Phase 4 (Justfile Modularization)
