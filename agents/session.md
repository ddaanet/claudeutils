# Session Handoff: 2026-02-07

**Status:** Worktree recovery and wt-merge bug fix.

## Completed This Session

**wt-merge bug fix:**
- Root cause: `just wt-merge` uses `set -e`, `git commit` with no submodule changes exits 1, kills script before Step 2 (parent branch merge)
- Fix: Guard commit with `git diff --quiet --cached ||` (justfile line 133)
- 4 stale worktrees had been claimed merged but weren't

**Worktree recovery:**
- Merged `wt/commit-unification` — plan marked complete (a96a362)
- Merged `wt/agent-output-cmd` — session log scraping prototype (c1d0a22)
- Merged `wt/fix-wt-status` — wt status investigation (88524a7)
- Merged `wt/plan-adhoc-alignment` — plan-tdd updates ported (1b26519)
- Removed stale worktrees: release-prep-skill, update-design-skill (already merged, just needed cleanup)

## Pending Tasks

- [ ] **Continuation passing design** — Validate outline against requirements | opus
  - Plan: continuation-passing | Status: requirements
- [ ] **Add PreToolUse hook for symlink writes** — Block writes through symlink | restart
- [ ] **Handoff validation design** — Complete design, requires continuation-passing | opus
  - Plan: handoff-validation | Status: requirements
- [ ] **Orchestrate evolution design** — Absorb planning, finalize phase pattern | opus
  - Plan: orchestrate-evolution | Status: requirements
- [ ] **Evaluate requirements-skill with opus** — Dump requirements/design after conversation | opus
  - Plan: requirements-skill | Status: requirements
- [ ] **Rewrite last-output prototype with TDD as claudeutils subcommand** — Port agent-output-cmd prototype to proper TDD implementation in claudeutils package
- [ ] **Update commit and handoff to branch after precommit** — Move git branching point from beginning to after precommit passes
- [ ] **History cleanup tooling** — Research git history rewriting, prototype reusable scripts, consider reusable agent. Items: collapse runbook checkpoint commits (preserve session.md handoffs), fix history from wt-merge incident. Allow rewrite on feature branches between releases, may tighten to prevent rewrite of main.
- [ ] **Rewrite agent-core ad-hoc scripts via TDD** — Port all ad-hoc scripts in agent-core/ to claudeutils package through TDD. Add precommit check and process gating: allow quick prototyping but schedule proper rewrite.

## Worktree Tasks

- [ ] **Analyze parity test quality failures** → `wt/parity-failures` — RCA complete (plans/reflect-rca-parity-iterations/rca.md). Needs: act on 5 gaps, factor in workflow evolution
- [ ] **Evaluate plugin migration** → `wt/plugin-migration` — Symlink situation causing pain
- [ ] **Empirical testing of memory index recall** → `wt/memory-index-recall` — Design testing methodology for memory index effectiveness | opus
- [ ] **Scope markdown test corpus work** → `wt/markdown-test-corpus` — Formatter test cases, determine approach
- [ ] **Design support for domain-specific and optional project-specific validation** → `wt/domain-validation-design` — Start with plugin-dev review agents | opus

## Blockers / Gotchas

**Worktree sandbox exemptions needed.** `just wt-new`, `just wt-rm`, `just wt-merge` write outside project directory. Need `dangerouslyDisableSandbox: true`. Session.md write eliminated — pre-committed to branch via git plumbing in recipe.

**Key dependency chain:** continuation-passing → handoff-validation → orchestrate-evolution (serial opus sessions)

**orchestrate-evolution missing from jobs.md** — needs entry added.

## Reference Files

- **justfile** — `wt-new` (lines 55-87, git plumbing session pre-commit), `wt-rm`, `wt-merge`
- **agent-core/fragments/execute-rule.md** — MODE 5 (local session.md write + recipe pre-commit flow)
- **plans/workflow-skills-audit/audit.md** — Plan-adhoc alignment + design skill audit (12 items)

## Next Steps

Quick wins: plan-adhoc alignment. Use `wt` for parallel execution of independent sonnet tasks.

---
*Handoff by Sonnet. Justfile cleanup + worktree setup.*
