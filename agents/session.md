# Session: Plugin Migration — Phase 0 Runbook Fix

**Status:** Fixed self-referential modification bug in Phase 0 runbook. Vet skill update delegated to main repo.

## Completed This Session

- Fixed runbook-phase-0.md step 12: `find plans/` sed command included `plans/plugin-migration/` itself, would rewrite runbook during execution
- Added `-not -path 'plans/plugin-migration/*'` exclusion to prevent self-modification
- Cleaned up accidentally created `wt/runbook-self-ref-fix` worktree (not needed — fix applied to current branch)
- Delegated vet skill criterion update to background agent in `../claudeutils/agent-core` (self-referential runbook detection)

## Pending Tasks

- [ ] **Execute plugin migration** — `/orchestrate plans/plugin-migration/orchestrator-plan.md` | haiku
  - Plan: plugin-migration | Status: planned
- [ ] **Examine pending tasks for batching** — Identify parallelizable task groups for wt/ execution | sonnet
- [ ] **Handoff validation design** — Complete design, requires continuation-passing | opus
  - Plan: handoff-validation | Status: requirements
- [ ] **Orchestrate evolution design** — Absorb planning, finalize phase pattern | opus
  - Plan: orchestrate-evolution | Status: requirements
- [ ] **Evaluate requirements-skill with opus** — Dump requirements/design after conversation | opus
  - Plan: requirements-skill | Status: requirements
- [ ] **Strengthen commit Gate B coverage check** — Gate B is boolean (any report?) not coverage ratio (artifacts:reports 1:1) | sonnet
  - Commit skill Step 1 Gate B: count new/modified production artifacts, verify each has vet report
- [ ] **Review reflect skill: task output for skill/fragment fixes** — RCA should produce pending tasks for skill/fragment updates, not inline fixes, for context economy | sonnet
- [ ] **Strengthen vet-fix-agent delegation pattern** — Add execution context provision and UNFIXABLE detection | sonnet
  - Analysis: plans/reflect-rca-sequential-task-launch/rca.md
- [ ] **Update tool-batching.md for Task tool parallelization** — Add explicit Task tool guidance with examples | sonnet
- [ ] **Rewrite last-output prototype with TDD as claudeutils subcommand** — Port agent-output-cmd prototype to proper TDD implementation in claudeutils package
- [ ] **Update commit and handoff to branch after precommit** — Move git branching point from beginning to after precommit passes
- [ ] **History cleanup tooling** — Research git history rewriting, prototype reusable scripts, consider reusable agent
- [ ] **Rewrite agent-core ad-hoc scripts via TDD** — Port all ad-hoc scripts in agent-core/ to claudeutils package through TDD
- [ ] **Package wt-merge as skill** — Clean tree gate, full handoff+commit pre-merge, auto-resolve session conflicts. Blocked on continuation-passing.
  - Plan: wt-merge-skill | Status: requirements
- [ ] **Move worktrees into wt/ directory** — Solves sandbox isolation, update skills and scripts

## Worktree Tasks

- [ ] **Explore removing bash tool git prompt noise** → `wt/bash-git-prompt` — Research if suppressible via config, hooks, or shell profile
- [ ] **Continuation passing design** → `wt/continuation-passing` — Validate outline against requirements | opus | Plan: continuation-passing | Status: requirements
- [ ] **Empirical testing of memory index recall** → `wt/memory-index-recall` — Design testing methodology for memory index effectiveness | opus
- [ ] **Scope markdown test corpus work** → `wt/markdown-test-corpus` — Formatter test cases, determine approach

## Blockers / Gotchas

**Worktree sandbox exemptions needed.** `just wt-new`, `just wt-rm`, `just wt-merge` write outside project directory. Need `dangerouslyDisableSandbox: true`.

**Key dependency chain:** continuation-passing → handoff-validation → orchestrate-evolution (serial opus sessions). wt-merge-skill also blocked on continuation-passing.

**Learnings file at 187/80 lines.** Needs `/remember` consolidation urgently.

**Vet skill update in main repo.** Background agent added self-referential modification criterion to vet skill in `../claudeutils/agent-core`. Check `agents/session.md` in main repo for pending commit.

## Reference Files

- **plans/plugin-migration/runbook-phase-0.md** — Phase 0 runbook (fixed step 12 self-ref bug)
- **plans/plugin-migration/orchestrator-plan.md** — Orchestrator plan (15 steps, haiku execution)
- **plans/plugin-migration/steps/step-*.md** — 15 step files (step-0-1 through step-6-1)
- **plans/plugin-migration/design.md** — Design with Phase 0 as foundational step (D-1 naming hierarchy)
