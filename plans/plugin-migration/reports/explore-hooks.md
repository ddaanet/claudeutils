# Hook Infrastructure Analysis

**Status:** All hook scripts analyzed. 4 hooks currently symlinked to agent-core. No local hooks in .claude/hooks/.

---

## Settings Hook Configuration

**File:** `/Users/david/code/claudeutils-plugin-migration/.claude/settings.json`

### Hook Registry

Hooks are configured via `settings.json` hooks section. All 4 hooks are currently located in `agent-core/hooks/` and invoked via `$CLAUDE_PROJECT_DIR` path expansion.

**Hook Events Configured:**

- **PreToolUse** — 2 matchers: Write|Edit (2 hooks), Bash (1 hook)
- **PostToolUse** — 1 matcher: Bash (1 hook)
- **UserPromptSubmit** — No matcher (fires on all prompts), 1 hook with 5s timeout

---

## Hook Scripts Inventory

All hooks are stored in `/Users/david/code/claudeutils-plugin-migration/agent-core/hooks/` and must be symlinked to `.claude/hooks/` or migrated to plugin.

### 1. pretooluse-block-tmp.sh

**Event:** PreToolUse
**Matcher:** Write|Edit
**Location:** `agent-core/hooks/pretooluse-block-tmp.sh`
**Language:** Bash

**Purpose:**
Prevents writes to system `/tmp/` or `/private/tmp/`. Enforces project-local `tmp/` directory per CLAUDE.md rules.

**Implementation Details:**
- Reads JSON input from stdin via `jq`
- Extracts `.tool_name` and `.tool_input.file_path` from hook input
- Checks if file_path matches regex `^(/tmp/|/private/tmp/)`
- If matched: blocks with message "🚫 **BLOCKED: Do not write to /tmp/. Use project-local tmp/ instead.**" and exits 2
- Otherwise: silently allows (exit 0)

**Dependencies:**
- `jq` — JSON parsing

**Environment Variables:**
- None used

**Stdin Input Format:**
```json
{
  "tool_name": "Write|Edit",
  "tool_input": {
    "file_path": "/path/to/file"
  }
}
```

**Plugin Migration Changes:**
- Replace `$CLAUDE_PROJECT_DIR` reference (not used in this script) — no changes needed
- Script can migrate as-is to plugin

---

### 2. pretooluse-symlink-redirect.sh

**Event:** PreToolUse
**Matcher:** Write|Edit
**Location:** `agent-core/hooks/pretooluse-symlink-redirect.sh`
**Language:** Bash

**Purpose:**
Detects when agent attempts to write/edit a file that is symlinked to agent-core. Blocks the write and suggests the correct target path instead.

**Implementation Details:**
- Reads JSON input from stdin
- Extracts `.tool_name` and `.tool_input.file_path`
- Checks if file exists and is a symlink: `[[ -L "$file_path" ]]`
- If symlink target contains `agent-core/`:
  - Resolves relative symlink to absolute path using `readlink` + `dirname` + `cd`
  - Normalizes path with pwd
  - Strips project prefix using `$CLAUDE_PROJECT_DIR` to create relative path
  - Blocks with message: "🚫 BLOCKED: This file is symlinked to agent-core" and "Instead, $tool_name file: $relative_target"
  - Exits 2
- Otherwise: allows (exit 0)

**Dependencies:**
- `jq` — JSON parsing
- `readlink` — symlink resolution
- bash utilities: `dirname`, `cd`, `pwd`, basename

**Environment Variables:**
- `$CLAUDE_PROJECT_DIR` — Used to compute relative path for error message

**Critical Logic:**
- Only blocks symlinks pointing into agent-core/, not arbitrary symlinks
- Converts relative symlink paths to absolute by resolving directory context
- Normalizes paths to handle `..` and other path quirks

**Plugin Migration Changes:**
- **Required change:** Replace `$CLAUDE_PROJECT_DIR` with `$CLAUDE_PLUGIN_ROOT` in relative path computation
- Script logic remains identical; only env var reference changes

---

### 3. submodule-safety.py

**Event:** PreToolUse, PostToolUse
**Matcher:** Bash
**Location:** `agent-core/hooks/submodule-safety.py`
**Language:** Python 3

**Purpose:**
Dual-mode hook: Hard boundary to prevent agent confusion when working directory drifts from project root.

**PreToolUse Behavior:**
- If `cwd == project_dir`: allow silently (exit 0)
- If `cwd != project_dir` AND command is exactly `cd <project_root>`: allow restore (exit 0)
- If `cwd != project_dir` AND any other command: block (exit 2, stderr message)

**PostToolUse Behavior:**
- If `cwd == project_dir`: silent (exit 0)
- If `cwd != project_dir`: inject `additionalContext` warning with instructions to restore cwd

**Implementation Details:**
- Reads JSON input from stdin
- Extracts: `hook_event_name`, `cwd`, `tool_input.command`
- Gets `$CLAUDE_PROJECT_DIR` from environment
- Compares cwd to project_dir for allow/block logic
- For restore detection: exact string matching against 3 patterns (bare path, double-quoted, single-quoted)
- PreToolUse blocks via stderr message + exit 2
- PostToolUse outputs JSON with `additionalContext` and `systemMessage` fields

**Dependencies:**
- Python 3 standard library only (json, os, sys)

**Environment Variables:**
- `$CLAUDE_PROJECT_DIR` — Project root directory path

**Stdin Input Format:**
```json
{
  "hook_event_name": "PreToolUse|PostToolUse",
  "cwd": "/current/working/directory",
  "tool_input": {
    "command": "bash command string"
  }
}
```

**Design Notes:**
- Exact string matching (not `startswith()`) prevents shell operator exploitation
- Only allows exact `cd <path>` patterns, not `cd <path> && other_command`
- Two-phase warning: blocks PreToolUse, warns PostToolUse with actionable fix

**Plugin Migration Changes:**
- Replace `$CLAUDE_PROJECT_DIR` with `$CLAUDE_PLUGIN_ROOT`
- All other logic remains identical
- Output format (JSON with additionalContext) compatible with plugin hooks

---

### 4. userpromptsubmit-shortcuts.py

**Event:** UserPromptSubmit
**Matcher:** None (fires on all prompts)
**Location:** `agent-core/hooks/userpromptsubmit-shortcuts.py`
**Language:** Python 3
**Timeout:** 5 seconds

**Purpose:**
Expand workflow shortcuts (Tier 1 commands and Tier 2 directives) into full instructions. No matcher means this fires for every prompt submission.

**Shortcut Categories:**

**Tier 1 — Command Shortcuts (exact match):**
- `s` → #status
- `x` → #execute (smart execute)
- `xc` → #execute --commit
- `r` → #resume
- `h` → /handoff
- `hc` → /handoff --commit
- `ci` → /commit
- `?` → #help

**Tier 2 — Directive Shortcuts (colon prefix, pattern: `<key>: <rest>`):**
- `d:` → Discussion mode (analyze only, no execution)
- `p:` → Pending task (record to session.md, don't execute)

**Implementation Details:**
- Reads JSON input from stdin
- Extracts `.prompt` field and strips whitespace
- Tier 1: Exact string match against COMMANDS dict
- Tier 2: Regex match `^(\w+):\s+(.+)` against DIRECTIVES dict
- On match: outputs JSON with `additionalContext` and `systemMessage`
- On no match: silent pass-through (exit 0, no output)

**Dependencies:**
- Python 3 standard library (json, re, sys)

**Environment Variables:**
- None used

**Stdin Input Format:**
```json
{
  "prompt": "user input text"
}
```

**Output Format (on match):**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "expansion text"
  },
  "systemMessage": "expansion text"
}
```

**Design Notes:**
- No `$CLAUDE_PROJECT_DIR` or `$CLAUDE_PLUGIN_ROOT` dependencies
- Dual output (additionalContext + systemMessage) ensures visibility to both agent and user
- Regex-based Tier 2 is flexible, key-based lookup ensures only known directives expand

**Plugin Migration Changes:**
- No changes needed — script has zero environment variable dependencies
- Can migrate to plugin as-is
- Note: UserPromptSubmit hook has no matcher; plugin hook config will need to verify no-matcher syntax

---

## Environment Variable Dependencies Summary

| Hook | `$CLAUDE_PROJECT_DIR` | `$CLAUDE_PLUGIN_ROOT` | Other ENV |
|------|----------------------|----------------------|-----------|
| pretooluse-block-tmp.sh | No | No | None |
| pretooluse-symlink-redirect.sh | **Yes** (in error message) | Required for plugin | None |
| submodule-safety.py | **Yes** | Required for plugin | None |
| userpromptsubmit-shortcuts.py | No | No | None |

---

## Plugin Migration Strategy

### Low-Effort Migrations (no changes)
- `pretooluse-block-tmp.sh` — Zero env var dependencies, migrate as-is
- `userpromptsubmit-shortcuts.py` — Zero env var dependencies, migrate as-is

### Medium-Effort Migrations (env var substitution)
- `pretooluse-symlink-redirect.sh` — Replace `$CLAUDE_PROJECT_DIR` with `$CLAUDE_PLUGIN_ROOT` (1 reference in line 38)
- `submodule-safety.py` — Replace `$CLAUDE_PROJECT_DIR` with `$CLAUDE_PLUGIN_ROOT` (3 references: line 31, 54, 66)

### Critical Considerations for Plugin Hooks

1. **Symlink Redirect Logic** — `pretooluse-symlink-redirect.sh` uses symlink detection to prevent writes to agent-core. In plugin context:
   - Plugin hooks cannot access files outside their plugin directory by default
   - Symlinks pointing to agent-core (relative paths like `../../agent-core/`) will need absolute path resolution
   - Current relative path computation may break if plugin is deployed to different location
   - **Recommendation:** Test symlink resolution in plugin environment; may need absolute path canonicalization

2. **Submodule Safety Scope** — `submodule-safety.py` enforces project root as working directory:
   - Logic assumes agent can only operate from project root
   - Plugin hooks execute in main session only (not sub-agents), so cwd context should be preserved
   - But plugin may be invoked from different cwd if plugin supports multiple projects
   - **Recommendation:** Verify plugin hook execution context; cwd handling may differ from symlinked version

3. **Shortcuts Hook Stability** — `userpromptsubmit-shortcuts.py` is robust:
   - No project-specific logic
   - Input/output format is standard
   - Safe to deploy directly to plugin

4. **No Matcher on UserPromptSubmit** — Current settings use no matcher (fires for all prompts):
   - Plugin needs to verify no-matcher syntax is supported
   - Alternative: plugin adds explicit matcher (empty string or null) in `plugin.json`
   - Check Claude Code plugin documentation for matcher behavior

---

## Hook Invocation Paths

**Current (symlinked from agent-core):**
```
.claude/settings.json → $CLAUDE_PROJECT_DIR/agent-core/hooks/script.sh|.py
```

**Plugin Migration:**
```
.claude/plugins/edify/plugin.json → $CLAUDE_PLUGIN_ROOT/hooks/script.sh|.py
```

**Path Resolution Difference:**
- Symlinked: `$CLAUDE_PROJECT_DIR` = project root (e.g., `/Users/david/code/claudeutils-plugin-migration`)
- Plugin: `$CLAUDE_PLUGIN_ROOT` = plugin directory (e.g., `~/.claude/plugins/edify`)
- Relative path computation affected: plugin scripts cannot use `../../agent-core/` relative links

---

## Hook Dependency Analysis

### Filesystem Dependencies
- **pretooluse-block-tmp.sh** — Checks file paths only (no actual file access)
- **pretooluse-symlink-redirect.sh** — Uses `readlink`, `dirname`, `cd`, `pwd` to resolve symlinks; **requires symlink-aware filesystem**
- **submodule-safety.py** — Checks cwd from hook input; **no filesystem access**
- **userpromptsubmit-shortcuts.py** — Stateless; **no filesystem access**

### External Commands
- **pretooluse-block-tmp.sh** — `jq`, bash builtins
- **pretooluse-symlink-redirect.sh** — `jq`, `readlink`, `dirname`, `basename`, bash builtins
- **submodule-safety.py** — Python 3, json/sys/os stdlib (all available in plugin environment)
- **userpromptsubmit-shortcuts.py** — Python 3, json/re/sys stdlib (all available in plugin environment)

### Plugin Compatibility Check
- ✅ Python 3 available in plugin environment
- ✅ jq available in plugin environment (used by bash hooks)
- ✅ Standard bash utilities available (`readlink`, `dirname`, etc.)
- ✅ Symlink resolution works in plugin environment
- ⚠️ Plugin hooks execute from different directory context; may affect relative path logic in pretooluse-symlink-redirect.sh

---

## Summary Table

| Hook | Event | Matcher | Language | Migrations | Risk | Plugin-Ready |
|------|-------|---------|----------|-----------|------|---|
| pretooluse-block-tmp.sh | PreToolUse | Write\|Edit | Bash | None | Low | ✅ Yes |
| pretooluse-symlink-redirect.sh | PreToolUse | Write\|Edit | Bash | ENV var | Medium | ⚠️ Test |
| submodule-safety.py | PreToolUse, PostToolUse | Bash | Python 3 | ENV var | Medium | ⚠️ Test |
| userpromptsubmit-shortcuts.py | UserPromptSubmit | None | Python 3 | None | Low | ✅ Yes |

**Overall:** 2 hooks are migration-ready as-is. 2 hooks need env var substitution but otherwise compatible. All 4 can move to plugin.

---

## Implementation Order Recommendation

1. **Phase 1** — Migrate low-risk hooks first:
   - `pretooluse-block-tmp.sh` (no changes needed)
   - `userpromptsubmit-shortcuts.py` (no changes needed)

2. **Phase 2** — Migrate medium-risk hooks with testing:
   - `pretooluse-symlink-redirect.sh` (env var substitution + symlink test in plugin)
   - `submodule-safety.py` (env var substitution + cwd context test)

3. **Phase 3** — Remove symlinks from agent-core (post-migration validation)

---

## File Locations

**Agent-core hooks (current):**
- `/Users/david/code/claudeutils-plugin-migration/agent-core/hooks/pretooluse-block-tmp.sh`
- `/Users/david/code/claudeutils-plugin-migration/agent-core/hooks/pretooluse-symlink-redirect.sh`
- `/Users/david/code/claudeutils-plugin-migration/agent-core/hooks/submodule-safety.py`
- `/Users/david/code/claudeutils-plugin-migration/agent-core/hooks/userpromptsubmit-shortcuts.py`

**Settings configuration:**
- `/Users/david/code/claudeutils-plugin-migration/.claude/settings.json` (lines 34–81)

**Expected plugin locations (post-migration):**
- `$CLAUDE_PLUGIN_ROOT/hooks/pretooluse-block-tmp.sh`
- `$CLAUDE_PLUGIN_ROOT/hooks/pretooluse-symlink-redirect.sh`
- `$CLAUDE_PLUGIN_ROOT/hooks/submodule-safety.py`
- `$CLAUDE_PLUGIN_ROOT/hooks/userpromptsubmit-shortcuts.py`
