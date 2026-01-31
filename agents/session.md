# Session Handoff: 2026-01-31

**Status:** Hook output fix design complete. Ready for planning/implementation.

## Completed This Session

**Hook diagnosis and design:**
- Diagnosed three broken hooks: UserPromptSubmit shortcuts (unregistered), submodule-safety (wrong output field), hooks.json (invalid config location)
- Root causes: shortcuts hook never added to settings.json; `systemMessage` is user-only (need `hookSpecificOutput.additionalContext` for Claude visibility); `.claude/hooks/hooks.json` not read by Claude Code
- Design: `plans/hook-output-fix/design.md` — 5 fixes including upgrade from soft warning to hard cwd block

**Symlink restoration:**
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

- [ ] **Implement hook-output-fix** — `/plan-adhoc plans/hook-output-fix/design.md` | sonnet
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

**Commit-rca-fixes active (from previous session):**
- Fix 3 (orchestrator stop rule) prevents dirty-state rationalization
- Fix 2 (artifact staging) ensures prepare-runbook.py artifacts are staged
- Fix 1 (submodule awareness) prevents submodule pointer drift

**Learnings file at 99/80 lines** — needs `/remember` consolidation soon.

**Hook changes require session restart** — after implementing hook-output-fix, must restart to test.

## Next Steps

Implement hook-output-fix design (5 fixes: register shortcuts, fix output format, upgrade to hard cwd block, delete stale hooks.json, update docs). Then test all hooks after restart.

---
*Handoff by Opus. Hook output fix designed.*
