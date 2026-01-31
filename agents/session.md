# Session Handoff: 2026-01-31

**Status:** Heredoc sandbox fix found and factorized into agent-core. Ready for commit.

## Completed This Session

**Heredoc sandbox fix — TMPPREFIX discovery:**
- Root cause: zsh uses `TMPPREFIX` (default `/tmp/zsh`) for heredoc temp files, NOT `TMPDIR`. Sandbox sets `TMPDIR=/tmp/claude` (in allowlist) but doesn't set `TMPPREFIX`, so heredocs fail with "operation not permitted"
- Fix: `export TMPPREFIX="${TMPDIR:-/tmp}/zsh"` — derives from TMPDIR, works in all environments
- Verified: heredocs and git commit heredoc pattern both work with fix applied

**Factorized Claude env setup into agent-core:**
- Created `agent-core/configs/claude-env.sh` — shared env setup sourced by .envrc
  - CLAUDE_CODE_TMPDIR (project-local tmp)
  - claude-env and claude-model-overrides direnv loading (managed by claudeutils)
  - TMPPREFIX fix for zsh heredocs
- Simplified `agent-core/templates/dotenvrc` to source shared file
- Symlinked `.envrc` in claudeutils and pytest-md to `agent-core/templates/dotenvrc`

**Changes across repos (uncommitted):**
- `agent-core/configs/claude-env.sh` — new file
- `agent-core/templates/dotenvrc` — simplified to source claude-env.sh
- `claudeutils/.envrc` — symlink to agent-core/templates/dotenvrc
- `pytest-md/.envrc` — symlink to agent-core/templates/dotenvrc

## Pending Tasks

- [ ] **Design solution for ambient awareness of consolidated learnings**
- [ ] **Add specific "go read the docs" checkpoints in design and plan skills**
- [ ] **Design runbook identifier solution** — /design plans/runbook-identifiers/problem.md (semantic IDs vs relaxed validation vs auto-numbering)
- [ ] **Create design-vet-agent** — Opus agent for design document review (deferred to opus session)
- [ ] **Add execution metadata to step files** — Step files declare dependencies and execution mode
- [ ] **Orchestrator scope consolidation** — Update orchestrate skill to delegate checkpoint phases (Fix + Vet + Functional) instead of manual invocation

## Blockers / Gotchas

**Vet minor item deferred — OPTIONAL:**
- Mock assertion in test_account_keychain.py:143 could be more specific (assert_called_once_with vs assert_called_once)
- Fix opportunistically when touching that test file

**Tail-call pattern is untested in live workflow:**
- Pattern is documented but hasn't been exercised end-to-end (plan-* → handoff --commit → commit → next)
- Watch for: skill termination timing, session.md state after handoff, clipboard content

**pytest-md has other uncommitted changes:**
- README.md, dev/architecture.md, session.md, tests/test_output_expectations.py also modified
- Only .envrc symlink change is from this session

## Next Steps

Commit agent-core submodule first (new file + template change), then claudeutils (.envrc symlink + agent-core ref). pytest-md .envrc commit separately in that repo.

---
*Handoff by Opus. TMPPREFIX fix for zsh heredocs in sandbox. Factorized Claude env setup into agent-core/configs/claude-env.sh.*
