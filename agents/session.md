# Session Handoff: 2026-02-10

**Status:** Worktree skill design complete (Phase C). Ready for TDD planning.

## Completed This Session

**Memory-index-recall worktree merge:**
- Pre-merge: worktree + submodule clean, precommit 559/559 passing
- Submodule: 1 worktree-only commit (deslop directives), ~40 dev-only — fetched from worktree path, merged cleanly
- Parent: 7 source conflicts (overlapping lint/complexity fixes on recall module) — took dev's versions (ours), precommit validates
- Non-conflicted: `plans/when-recall/` design + `cli.py` deslop fixes merged automatically
- Session context: kept ours, recovered 1 pending task ("Plan `/when` TDD runbook")
- jobs.md: when-recall plan status advanced requirements → designed
- Worktree + branch removed via `just wt-rm`

**Stale worktree cleanup:**
- bash-git-prompt: no unmerged commits, uncommitted changes — force-removed
- markdown-test-corpus: no unmerged commits, uncommitted changes — force-removed

**Worktree skill outline updated:** Added source code conflict resolution (take-ours + precommit gate), batch stale removal, submodule fetch path simplification, new test scenarios. Outline-review-agent: 4 minor fixes applied (step numbering, scope clarification, CLI naming). Branch naming reverted to "no prefix" per user requirement.

**Worktree skill design (Phase C):**
- Design document: `plans/worktree-skill/design.md` (508 lines, 10 design decisions, 8 FRs + 5 NFRs)
- Checkpoint commit: 8cb48f7
- Vet review: design-vet-agent (opus) — 0 critical, 3 major fixed, 7 minor fixed, no UNFIXABLE
- Key decisions: `wt/<slug>/` inside project root (sandbox-compatible), branch=slug (no prefix), direct git plumbing for merge commits (no /commit skill), precommit as correctness oracle
- Design clarification: submodule/merge commits use `🔀` hardcoded gitmoji, string interpolation only
- Dependency resolved: focus-session.py — skill generates inline (no script dependency)

## Pending Tasks

- [ ] **Worktree skill TDD planning** — `/plan-tdd plans/worktree-skill/design.md` | opus
  - Plan: worktree-skill | Status: designed | Load `plugin-dev:skill-development` before planning
- [ ] **Review agent-core orphaned revisions** — Check all agent-core commits reachable from parent repo history but not on current HEAD, merge if needed | sonnet
- [ ] **Execute plugin migration** — `/orchestrate plans/plugin-migration/orchestrator-plan.md` | haiku
  - Plan: plugin-migration | Status: planned
- [ ] **Examine pending tasks for batching** — Identify parallelizable task groups for wt/ execution | sonnet
- [ ] **Update design skill** — Read design artifacts referenced in context, assess plan progress | sonnet
- [ ] **Add PreToolUse hook for symlink writes** — Block writes through symlink | restart
- [ ] **Handoff validation design** — Complete design (continuation-passing now merged) | opus
  - Plan: handoff-validation | Status: requirements
- [ ] **Orchestrate evolution design** — Absorb planning, finalize phase pattern | opus
  - Plan: orchestrate-evolution | Status: requirements
- [ ] **Evaluate requirements-skill with opus** — Dump requirements/design after conversation | opus
  - Plan: requirements-skill | Status: requirements
- [ ] **Strengthen commit Gate B coverage check** — Gate B is boolean (any report?) not coverage ratio (artifacts:reports 1:1) | sonnet
- [ ] **Review reflect skill: task output for skill/fragment fixes** — RCA should produce pending tasks for skill/fragment updates, not inline fixes | sonnet
- [ ] **Update tool-batching.md for Task tool parallelization** — Add explicit Task tool guidance with examples | sonnet
- [ ] **Rewrite last-output prototype with TDD as claudeutils subcommand** — Port agent-output-cmd prototype to proper TDD implementation
- [ ] **Update commit and handoff to branch after precommit** — Move git branching point from beginning to after precommit passes
- [ ] **History cleanup tooling** — Research git history rewriting, prototype reusable scripts
- [ ] **Rewrite agent-core ad-hoc scripts via TDD** — Port all ad-hoc scripts to claudeutils package
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements | Dependency on continuation-passing now resolved
- [ ] **RCA: Planning agents leave dirty tree** — Delegation prompts lack commit instruction, fix orchestration templates | sonnet
- [ ] **RCA: User-backgrounded agents crash** — `classifyHandoffIfNeeded is not defined` on user-initiated backgrounding, code-backgrounded agents work fine | sonnet
- [ ] **Error handling framework design** — Design error handling for runbooks, task lists, and CPS skills | opus
- [ ] **Plan `/when` TDD runbook** — `/plan-tdd plans/when-recall/design.md` | blocked on plan-orchestrate workflow review
  - Plan: when-recall | Status: designed | Load `plugin-dev:skill-development` before planning

## Worktree Tasks

- [ ] **Fix preprocessor idempotency** → `wt/fix-precommit` — Route through /design or /plan-adhoc | sonnet

## Blockers / Gotchas

**Pre-existing test failure:** `tests/test_markdown_fixtures.py::test_preprocessor_idempotency[02-inline-backticks]` — not related to merge

## Reference Files

- **plans/worktree-skill/design.md** — Full design document (10 decisions, merge flow, conflict resolution, skill spec)
- **plans/worktree-skill/reports/design-review.md** — Opus vet review (all fixed, no UNFIXABLE)
- **plans/worktree-skill/outline.md** — Validated outline (binding scope)
- **plans/worktree-skill/reports/explore-integration.md** — Integration point analysis

---
*Handoff by Sonnet. Design complete, TDD planning next.*
