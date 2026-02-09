# Session: tweakcc Integration Research

## Completed This Session

### Research: tweakcc mechanics and local instances
- Analyzed tweakcc patching workflow for native binary (unpack/repack) vs npm (direct JS modification)
- Discovered Claude installed as native binary at `~/.local/share/claude/versions/2.1.37` (Mach-O arm64)
- tweakcc installed and configured at `~/.tweakcc/` with 135 system prompt files extracted
- Confirmed npm local install is the path: `@anthropic-ai/claude-code` as devDependency, direct JS patching, no binary workflow
- Per-project config via `TWEAKCC_CONFIG_DIR` env var or programmatic API (no native per-project support)
- Patches don't survive `npm install` — requires postinstall hook for reapplication

### Measured token counts for override targets
- `tool-description-bash-git-commit-and-pr-creation-instructions.md`: 1731 tokens
- `tool-description-bash-sandbox-note.md`: 513 tokens
- `system-prompt-scratchpad-directory.md`: 230 tokens
- `tool-description-bash.md` (full file): 1246 tokens
- Total removable (Phase 1): ~2624 tokens per session

### RCA: Estimation deviation
- Presented prior document estimates as fresh analysis in summary table
- Root cause: `no-estimates.md` ("report measured data only") conflicted with `token-economy.md` ("reference don't repeat") — token economy provided justification for reusing unverified numbers
- Fix: Updated `no-estimates.md` with "Reuse is not measurement" clarification

### Deliverables
- `plans/tweakcc/requirements.md` — Two-phase requirements (stopgap: remove builtins, end state: custom system + tool prompts)
- `plans/tweakcc/research.md` — tweakcc mechanics, patch survival, config structure
- `plans/tweakcc/local-instances.md` — npm local install, programmatic API, integration patterns

## Pending Tasks

- [ ] **Submit feature requests to anthropic/claude-code** — Three gh issue create commands ready in `plans/feature-requests/`
  - `gh issue create --repo anthropics/claude-code --title "[FEATURE] Allow overriding builtin tool description components" --body-file plans/feature-requests/gh-issue-tool-overrides.md`
  - `gh issue create --repo anthropics/claude-code --title "[FEATURE] Sandbox denial should stop agent, not auto-retry with bypass prompt" --body-file plans/feature-requests/gh-issue-sandbox-deny-default.md`
  - `gh issue create --repo anthropics/claude-code --title "[FEATURE] Configurable sandbox write allowlist" --body-file plans/feature-requests/gh-issue-sandbox-allowlist.md`

- [ ] **Submit CLAUDE.md PR to Piebald-AI** — File written at `/Users/david/code/claude-code-system-prompts/CLAUDE.md`
  - `cd /Users/david/code/claude-code-system-prompts && git checkout -b add-claudemd && git add CLAUDE.md && git commit -m "Add CLAUDE.md for AI agent context" && gh pr create --repo Piebald-AI/claude-code-system-prompts --title "Add CLAUDE.md for AI agent context" --body "Adds CLAUDE.md explaining origin of extracted files and guidance for AI agents."`

- [ ] **tweakcc Phase 1 implementation** — `/design plans/tweakcc/requirements.md` | Drive tweakcc from claudeutils, remove redundant builtins. Requirements written, research complete.

- [ ] **Extend pretooluse-block-tmp.sh to match Bash commands** — Match Bash tool where command contains `/tmp` path patterns. Closes gap allowing `echo > /tmp/claude/foo`.

- [ ] **PreToolUse hook for bash→specialized tool redirection** — Filter trivial one-liner Bash commands (cat, grep, find without pipes/redirects) and block with guidance to use Read/Grep/Glob.

## Blockers / Gotchas

- tweakcc research clarified: fragments MUST stay in CLAUDE.md for clean/unpatched environments — tweakcc is optimization overlay, not replacement
- Two-phase vision: stopgap (remove redundant builtins) → end state (custom system + tool prompts via tweakcc)
- `.anthropic-api-key` file in project root — do NOT commit (created for token counting, should be in .gitignore or deleted)
- Learnings at 127 lines (80 soft limit exceeded, 0 entries ≥7 days — consolidation not yet triggered)

## Reference Files

- `plans/tweakcc/` — Requirements, research, local instances analysis
- `plans/feature-requests/` — Feature request bodies and redundancy analysis
- `~/.tweakcc/system-prompts/` — 135 extracted system prompt files (override targets)
- `/Users/david/code/claude-code-system-prompts/` — Piebald's extracted system prompts
