# Session Handoff: 2026-01-31

**Status:** Hook output fix implemented and vetted. Restart required to activate hooks.

## Completed This Session

**Hook output fix implementation (Tier 2):**
- All 5 fixes from design completed: register shortcuts hook, rewrite submodule-safety.py for dual-mode (PreToolUse block + PostToolUse warn), update settings.json, delete hooks.json files, update claude-config-layout.md
- Vet review caught major issue: restore command detection allowed `cd <root> && malicious` — fixed to exact match only
- Minor fix applied: claude-config-layout.md updated from "warns" to "blocks" for accuracy
- Key changes:
  - `agent-core/hooks/submodule-safety.py`: Dual-mode script checks `hook_event_name`, PreToolUse blocks ALL commands from wrong cwd (not just dangerous ones), PostToolUse injects `additionalContext` warning, provides exact restore command
  - `.claude/settings.json`: Added PreToolUse:Bash + UserPromptSubmit hooks, kept PostToolUse:Bash
  - Deleted `.claude/hooks/hooks.json` and `agent-core/hooks/hooks.json` (invalid config location)
- Reports: `tmp/hook-fix-report.md`, `tmp/hook-fix-vet-review.md`

**Hook diagnosis and design (previous session):**
- Diagnosed three broken hooks: UserPromptSubmit shortcuts (unregistered), submodule-safety (wrong output field), hooks.json (invalid config location)
- Root causes: shortcuts hook never added to settings.json; `systemMessage` is user-only (need `hookSpecificOutput.additionalContext` for Claude visibility); `.claude/hooks/hooks.json` not read by Claude Code
- Design: `plans/hook-output-fix/design.md` — 5 fixes including upgrade from soft warning to hard cwd block

**Symlink restoration (previous session):**
- `.claude/hooks/*.py` files had become regular files (ruff reformatted them via `just dev`)
- Restored as symlinks to `agent-core/hooks/`
- Ruff errors in `agent-core/hooks/userpromptsubmit-shortcuts.py` fixed (line length, missing docstring)
- pyproject.toml updated with ruff config

**Key discovery — hook output visibility:**
- `systemMessage` → shown to user only, NOT to Claude
- `hookSpecificOutput.additionalContext` → visible to Claude
- stderr + exit 2 → visible to Claude (error/block pattern)
- The hookify plugin's "UserPromptSubmit hook success" was being mistaken for the project's shortcuts hook working

## Pending Tasks

- [ ] **Test hooks after restart** — verify shortcuts expand (`hc`), PreToolUse blocks non-root cwd, PostToolUse warns, restore works | sonnet | restart
- [ ] **Orchestrate: integrate review-tdd-process** — rename review-analysis, use custom sonnet sub-agent, runs during orchestration | sonnet
- [ ] **Refactor oneshot handoff template** — integrate into current handoff/pending/execute framework | sonnet
- [ ] **Evaluate oneshot skill** — workflow now always starts with /design, may be redundant | opus
- [ ] **Update heredoc references** — sandboxed heredoc fix landed. Remove workarounds, restore vendor default heredoc behavior for commit messages | sonnet
- [ ] **Resume workflow-controls orchestration (steps 2-7)** — `/orchestrate workflow-controls` | sonnet | restart
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Create /reflect skill** — deviation detection → RCA → fix → handoff/commit automation. Load plugin-dev skills first | opus
- [ ] **Insert skill loading in design docs** — design skill should load relevant plugin-dev skills when topic involves hooks/agents/skills | sonnet
- [ ] **Update workflow skills: pbcopy next command** — commit/handoff STATUS display copies next command to clipboard | sonnet
- [ ] **Add "go read the docs" checkpoints** — partially addressed by design-work.md rule | sonnet
- [ ] **Design runbook identifier solution** — `/design plans/runbook-identifiers/problem.md` | opus
- [ ] **Create design-vet-agent** — dedicated opus agent for design review, artifact-return pattern | opus
- [ ] **Add execution metadata to step files** — step files declare dependencies and execution mode | sonnet
- [ ] **Orchestrator scope consolidation** — delegate checkpoint phases in orchestrate skill | sonnet

## Blockers / Gotchas

**Commit-rca-fixes active:**
- Fix 3 (orchestrator stop rule) prevents dirty-state rationalization
- Fix 2 (artifact staging) ensures prepare-runbook.py artifacts are staged
- Fix 1 (submodule awareness) prevents submodule pointer drift

**Learnings file at 99/80 lines** — needs `/remember` consolidation soon.

**Hook changes require session restart** — hooks load at session start only. After commit, must restart to test new hook behavior.

**Verification procedure (after restart):**
1. Shortcuts: Type `hc` → should inject `[SHORTCUT: /handoff --commit]` in additionalContext
2. PreToolUse block: `cd agent-core` then `ls` → second command blocked with restore instruction
3. Restore: Run provided `cd` command → next command allowed
4. Subshell: `(cd agent-core && ls)` from root → allowed, cwd stays root
5. PostToolUse warn: After cwd drift, should see warning with restore command

## Next Steps

Restart session to activate hooks, then run verification procedure. All hooks should now work correctly: shortcuts expand, submodule-safety blocks/warns with correct output visibility.

---
*Handoff by Sonnet. Hook output fix implemented and vetted.*
