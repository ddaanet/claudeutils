# Session Handoff: 2026-01-31

**Status:** Hooks fixed and working; all pending tasks postponed

## Completed This Session

**Hook fixes (committed in 7083806):**
- Fixed pretooluse-block-tmp.sh: Output plain text to stderr + exit 2 (not JSON)
- Moved submodule-safety.py from PreToolUse to PostToolUse (cwd checks need to run after commands execute)
- Updated .claude/settings.json with correct hook configuration (PreToolUse for Write, PostToolUse for Bash)
- Removed Bash PreToolUse hook for submodule-safety (was checking cwd before command changed it)

**Hook testing and debugging:**
- Ran partial test-hooks.md procedure (Tests 1-10)
- Discovered hooks need to be in .claude/settings.json (not separate .claude/hooks/hooks.json)
- Found official example showing deny hooks must: output to stderr + exit 2
- Confirmed PostToolUse hooks work for cwd warnings (now showing properly)
- Confirmed PreToolUse hooks work for /tmp blocking (clean error message)

**Previous session work (committed earlier):**
- Hook fixes and vet requirement (daa2281, 8c36c0b, 02788f7)
- Feedback-fixes execution
- Recovery runbook generation (43 TDD cycles across 4 phases)

## Pending Tasks

**All tasks postponed by user**

## Blockers / Gotchas

**Hook output format for deny decisions:**
- Must output to stderr (`>&2`) and exit with code 2
- Plain text message works (no JSON wrapper needed)
- JSON output creates noise: `PreToolUse:Write hook error: [path]: {json}`
- Plain text is cleaner: `PreToolUse:Write hook error: [path]: message`
- The `permissionDecision` field is NOT required - exit code 2 is sufficient to deny

**Hook configuration location:**
- Hooks MUST be in `.claude/settings.json` under `"hooks": {...}`
- Separate `.claude/hooks/hooks.json` file is NOT loaded
- Plugin hooks use `{"description": "...", "hooks": {...}}` wrapper format
- Settings/project-local hooks use direct `{event: [...]}` format

**PreToolUse vs PostToolUse timing:**
- PreToolUse runs BEFORE command executes (cwd unchanged)
- PostToolUse runs AFTER command executes (cwd may have changed)
- cwd checks must be PostToolUse (to detect cwd changes after cd commands)
- Path validation can be PreToolUse (checking command arguments before execution)

**Hooks require session restart:**
- Hook changes only take effect after restarting Claude Code
- Test hooks after commit by restarting session

**Symlinks in git:**
- .claude/ symlinks now tracked (refactor agent, opus-design-question skill, hooks)
- Point to agent-core/ source files
- Run `just sync-to-parent` in agent-core to recreate if broken

**Python 3.14 Incompatibility:**
- litellm dependency uvloop doesn't support Python 3.14 yet
- Solution: `uv tool install --python 3.13 'litellm[proxy]'`

**Mock Patching Pattern:**
- Patch at usage location, not definition location
- Example: `patch("claudeutils.account.state.subprocess.run")`

**Bash cwd behavior:**
- Main interactive agent: cwd persists between Bash calls
- Sub-agents (Task tool): cwd does NOT persist
- CLAUDE.md absolute path guidance targets sub-agents

**prepare-runbook.py requires sandbox bypass:**
- Writing to `.claude/agents/` triggers sandbox permission error
- Workaround: Added to excludedCommands in settings.json

## Reference Files

- `agent-core/agents/test-hooks.md` — Hook testing procedure (10 tests)
- `agent-core/hooks/pretooluse-block-tmp.sh` — /tmp write blocking hook (fixed)
- `agent-core/hooks/submodule-safety.py` — PostToolUse cwd warning hook
- `.claude/settings.json` — Hook configuration (PreToolUse + PostToolUse)
- `/Users/david/.claude/plugins/cache/claude-plugins-official/plugin-dev/*/skills/hook-development/examples/validate-write.sh` — Official hook example showing stderr + exit 2 pattern

**Previous work:**
- `plans/claude-tools-recovery/design.md` — Recovery design (4 phases R0-R4)
- `plans/claude-tools-recovery/runbook.md` — Generated TDD runbook (43 cycles)
- `agent-core/fragments/vet-requirement.md` — Production artifact vet directive
- `agent-core/agents/refactor.md` — Refactor agent (symlinked)
- `agent-core/skills/opus-design-question/` — Opus design consultation skill (symlinked)

## Next Steps

**No active work** - all tasks postponed by user.

**When resuming:**
1. Review postponed tasks from previous session handoff
2. Determine next priority
3. Execute appropriate workflow

---
*Handoff by Sonnet. Hook fixes committed; all tasks postponed.*
