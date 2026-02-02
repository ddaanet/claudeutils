# Design: Hook Output Fix

## Problem

Three hooks are broken or misconfigured:

1. **UserPromptSubmit shortcuts hook** — file exists at `.claude/hooks/userpromptsubmit-shortcuts.py` but is **not registered** in any valid hook configuration. The "UserPromptSubmit hook success: Success" system reminder comes from the hookify plugin's generic `userpromptsubmit.py`, not the project's shortcut expander.

2. **PostToolUse submodule-safety hook** — registered and executes, but uses `systemMessage` for output. Per docs, `systemMessage` is user-facing only and NOT visible to Claude. Must use `hookSpecificOutput.additionalContext` instead.

3. **`.claude/hooks/hooks.json`** — not a valid configuration location. Claude Code does NOT read hook config from this file. Contains stale/contradictory entries.

## Root Cause

| Hook | Issue | Evidence |
|------|-------|----------|
| shortcuts | Not in settings.json `hooks` section | Grep: no UserPromptSubmit in any settings file |
| submodule-safety | Wrong output field | `systemMessage` → user only; `additionalContext` → Claude visible |
| hooks.json | Invalid config location | Claude Code docs: hooks configured in settings files only |

## Additional Findings

**PreToolUse vs PostToolUse for submodule-safety:**
- settings.json registers it as PostToolUse:Bash
- hooks.json (stale) registered it as PreToolUse:Bash
- Hook docstring says "PreToolUse hook"
- **Decision:** Use BOTH events with different enforcement levels (see Fix 2).

**Symlinks already restored:** `.claude/hooks/*.py` files were converted from copies to symlinks earlier this session. Edits to `agent-core/hooks/` now propagate correctly.

## Fixes

### Fix 1: Register UserPromptSubmit hook in settings.json

Add to `.claude/settings.json` → `hooks`:

```json
"UserPromptSubmit": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/userpromptsubmit-shortcuts.py"
      }
    ]
  }
]
```

No matcher — UserPromptSubmit doesn't support matchers (fires on every prompt, filtering is script-internal).

### Fix 2: Upgrade submodule-safety from warning to hard block

Replace the current soft-warning approach with two-hook hard enforcement:

**PreToolUse:Bash — block execution when cwd != project root:**
- If cwd == project root → allow silently
- If cwd != project root AND command restores cwd (matches `cd <project_root>`) → allow
- If cwd != project root AND any other command → **BLOCK** (exit 2) with error message containing the exact `cd` command to run

**PostToolUse:Bash — detect cwd drift after execution:**
- If cwd == project root → silent
- If cwd != project root → inject `additionalContext` warning: "Bash is blocked until cwd is restored. Run: `cd <project_root>`"

**How they interact:**

| Step | Event | cwd | Command | Result |
|------|-------|-----|---------|--------|
| 1 | PreToolUse | root ✅ | `cd agent-core` | Allow |
| 2 | PostToolUse | agent-core ❌ | — | Warn: run `cd /path/to/root` |
| 3 | PreToolUse | agent-core ❌ | `ls` | **BLOCK** |
| 4 | PreToolUse | agent-core ❌ | `cd /path/to/root` | Allow |
| 5 | PostToolUse | root ✅ | — | Silent |

**Design decisions:**
- Block ALL commands from wrong cwd, not just "dangerous" ones. Read-only commands (`ls`, `git status`) from wrong cwd actively mislead the agent. Soft boundaries don't work — this project's experience with warnings confirms this.
- The subshell pattern `(cd subdir && command)` doesn't change persistent cwd, so it's unaffected.
- Provide exact restore command in error message — agent copies verbatim, no guesswork.

**Implementation:** Rewrite `agent-core/hooks/submodule-safety.py` to handle both events. Register as both PreToolUse:Bash and PostToolUse:Bash in settings.json. The script checks `hook_event_name` from input to determine behavior (block vs warn).

### Fix 3: Delete `.claude/hooks/hooks.json`

Remove the invalid config file. All hook configuration lives in `.claude/settings.json`. Also delete `agent-core/hooks/hooks.json` if it exists (source of the symlink).

### Fix 4: Update claude-config-layout.md

Update the settings-level hooks example to match actual settings.json structure (nested `matcher` + `hooks` array pattern, not the flat `name`/`command` pattern currently shown). The "NOT read from hooks.json" statement is correct and stays.

### Fix 5: Update settings.json hook structure

Final settings.json `hooks` section:

```json
"hooks": {
  "PreToolUse": [
    {
      "matcher": "Write",
      "hooks": [{"type": "command", "command": "bash $CLAUDE_PROJECT_DIR/.claude/hooks/pretooluse-block-tmp.sh"}]
    },
    {
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/submodule-safety.py"}]
    }
  ],
  "PostToolUse": [
    {
      "matcher": "Bash",
      "hooks": [{"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/submodule-safety.py"}]
    }
  ],
  "UserPromptSubmit": [
    {
      "hooks": [
        {"type": "command", "command": "python3 $CLAUDE_PROJECT_DIR/.claude/hooks/userpromptsubmit-shortcuts.py"}
      ]
    }
  ]
}
```

## Verification

After all fixes + session restart:

- **Shortcuts:** Type `hc` → agent should see `[SHORTCUT: /handoff --commit]` in additional context
- **Submodule-safety block:** `cd agent-core` then `ls` → second command blocked with restore instruction
- **Submodule-safety restore:** Run the provided `cd` command → next command allowed
- **Subshell pattern:** `(cd agent-core && ls)` from root → allowed, cwd stays at root
- **hooks.json:** File should not exist

## Scope

**In scope:** The five fixes above.
**Out of scope:** Adding new hooks beyond cwd enforcement, changing shortcut hook behavior.
