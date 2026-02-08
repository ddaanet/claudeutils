# Session: Bash Tool Prompt Noise Research

## Completed This Session

### Research: Bash tool prompt anatomy
- Analyzed three builtin Bash tool prompt files from [claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) (Piebald AI, extracted from compiled npm JS)
- Identified ~3095 tokens of builtin content that overlaps/conflicts with project fragments
- Discovered [tweakcc](https://github.com/Piebald-AI/tweakcc) — patches individual prompt strings in local Claude Code installations
- Verified sandbox behavior: `/tmp/claude/` is in sandbox write allowlist, Bash writes succeed, `permissions.deny` only affects Write/Edit tools

### Deliverables
- `plans/feature-requests/gh-issue-tool-overrides.md` — Feature request: override builtin tool description components
- `plans/feature-requests/gh-issue-sandbox-deny-default.md` — Feature request: sandbox denial should stop agent, not auto-retry
- `plans/feature-requests/gh-issue-sandbox-allowlist.md` — Feature request: configurable sandbox write allowlist
- `plans/feature-requests/fragment-redundancy-analysis.md` — Full analysis of fragment vs builtin overlap, tweakcc integration plan
- `/Users/david/code/claude-code-system-prompts/CLAUDE.md` — PR: Add CLAUDE.md to Piebald's system-prompts repo

### RCA: Track deliverables in plans/
- Repeated violation (2026-02-06, 2026-02-08) of writing tracked artifacts to gitignored tmp/
- Root cause: Category-matching heuristic ("not a report/design/audit") defeated principle ("will this be referenced?")
- Learning updated with decision principle instead of category enumeration

## Pending Tasks

- [ ] **Submit feature requests to anthropic/claude-code** — Three gh issue create commands ready in `plans/feature-requests/`
  - `gh issue create --repo anthropics/claude-code --title "[FEATURE] Allow overriding builtin tool description components" --body-file plans/feature-requests/gh-issue-tool-overrides.md`
  - `gh issue create --repo anthropics/claude-code --title "[FEATURE] Sandbox denial should stop agent, not auto-retry with bypass prompt" --body-file plans/feature-requests/gh-issue-sandbox-deny-default.md`
  - `gh issue create --repo anthropics/claude-code --title "[FEATURE] Configurable sandbox write allowlist" --body-file plans/feature-requests/gh-issue-sandbox-allowlist.md`

- [ ] **Submit CLAUDE.md PR to Piebald-AI** — File written at `/Users/david/code/claude-code-system-prompts/CLAUDE.md`
  - `cd /Users/david/code/claude-code-system-prompts && git checkout -b add-claudemd && git add CLAUDE.md && git commit -m "Add CLAUDE.md for AI agent context" && gh pr create --repo Piebald-AI/claude-code-system-prompts --title "Add CLAUDE.md for AI agent context" --body "Adds CLAUDE.md explaining origin of extracted files and guidance for AI agents."`

- [ ] **Integrate tweakcc with Edify just wrapper** — tweakcc patches prompt strings in local Claude Code. Evaluate as Edify's tool description override mechanism. Key: Edify already runs `--system-prompt` disabled; tweakcc fills gap for tool descriptions. Research: survives npm updates? Post-install hook? Version-control patches?

- [ ] **Include custom system prompt injection in Edify just wrapper** — Override/replace builtin tool descriptions and system prompt components when wrapping `claude` CLI

- [ ] **Extend pretooluse-block-tmp.sh to match Bash commands** — Match Bash tool where command contains `/tmp` path patterns. Closes gap allowing `echo > /tmp/claude/foo`. Prerequisite for removing `tmp-directory.md` fragment.

- [ ] **Remove tmp-directory.md fragment** — Redundant with pretooluse-block-tmp.sh hook + sandbox note override. Requires: Bash hook extension (above) + tweakcc sandbox note override. See `plans/feature-requests/fragment-redundancy-analysis.md` Phase 2.

- [ ] **PreToolUse hook for bash→specialized tool redirection** — Filter trivial one-liner Bash commands (cat, grep, find without pipes/redirects) and block with guidance to use Read/Grep/Glob. Replaces prompt-level "use specialized tools" guidance with runtime enforcement.

## Blockers / Gotchas

- Feature requests #1 and #3 (tool overrides, sandbox allowlist) are prerequisites for full fragment cleanup
- tweakcc integration depends on researching its update-survival and patch format
- Bash `/tmp` hook extension needs careful regex to avoid false positives on commands that read from `/tmp` (only block writes)
- Learnings at 126 lines (80 soft limit exceeded, 0 entries ≥7 days — consolidation not yet triggered)

## Reference Files

- `plans/feature-requests/` — All feature request bodies and redundancy analysis
- `/Users/david/code/claude-code-system-prompts/` — Piebald's extracted system prompts (added as working directory)
- `.claude/hooks/pretooluse-block-tmp.sh` — Current /tmp write blocker (Write/Edit only)
- `agent-core/fragments/tmp-directory.md` — Fragment targeted for removal
- `agent-core/fragments/sandbox-exemptions.md` — Sandbox bypass patterns

## Next Steps

Submit the three feature requests and Piebald PR (manual, commands ready in Pending Tasks).
