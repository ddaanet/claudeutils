# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## General knowledge overrides directives
- Anti-pattern: Using `ln -sf` to create symlinks in `.claude/` when `just sync-to-parent` exists
- Root cause: Script-First Evaluation says "execute simple operations directly" — but doesn't say "check for project recipes first"
- Correct pattern: Before ad-hoc commands, check `just --list` for existing recipes that handle the operation
- Fix: Created `project-tooling.md` fragment — project recipes take priority over equivalent ad-hoc commands
- Broader lesson: Loaded context directives must override general knowledge, not compete with it
## Commit RCA fixes active
- Fix 1 (submodule awareness): Commit submodule first, then stage pointer in parent
- Fix 2 (artifact staging): prepare-runbook.py stages its own artifacts via `git add`
- Fix 3 (orchestrator stop rule): Absolute "no exceptions" language, deleted contradictory scenarios
- Status: All fixes implemented and committed, active in current workflow
- Prevents: Submodule sync drift, missing artifacts in commits, dirty-state rationalization
## Precommit is read-only
- Rule: `just precommit` must not modify source files (unlike `just dev` which autoformats)
- Exemption: Volatile session state (`agents/session.md`) is exempt — `#PNDNG` token expansion runs in precommit
- Rationale: Precommit is validation, not transformation. Session state is ephemeral metadata, not source code.
## Tool batching unsolved
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)
## Efficient model analysis requires verification
- Anti-pattern: Accepting haiku/sonnet analysis for critical architectural decisions without review
- Correct pattern: Use haiku for execution tasks, delegate architectural analysis to sonnet/opus, verify results
- Example: Haiku structural header analysis was incorrect (marked semantic headers as structural), sonnet analysis was correct
- Rationale: Efficient models optimize for speed, may miss nuance in architectural distinctions
