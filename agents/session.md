# Session Handoff: 2026-02-11

**Status:** Worktree recipes relocated to sibling directory pattern. Orchestrate evolution ready for planning after vet.

## Completed This Session

**Agent-core submodule integrity audit:**
- Exhaustive check: all 237 unique agent-core submodule pointers across parent repo history are reachable from current agent-core HEAD
- 12 worktrees had no explicit "Merge agent-core from wt/..." commit; 3 of those changed agent-core at merge time — all reachable
- Confirmed no lost work from prior `--reference` clone approach

**Worktree sibling directory relocation:**
- Worktrees moved from `wt/<slug>` (inside repo) to `../<repo>-wt/<slug>` (sibling container)
- Added `wt-path()` bash helper: detects if parent dir ends in `-wt` (already a container) vs needs `<repo>-wt/` container
- All wt-* recipes (wt-new, wt-rm, wt-merge) updated to use `wt-path()`
- Removed `main_dir` variable from all recipes — `$PWD` used directly for absolute paths
- `wt-rm` cleans up empty container directory after last worktree removed

**Worktree sandbox permission registration:**
- `add-sandbox-dir()` bash helper: adds container path to `.permissions.additionalDirectories` in settings.local.json
- Writes to both main repo and worktree repo settings.local.json
- Creates settings.local.json if absent, idempotent (no duplicates)

**Worktree setup fallback:**
- `wt-new` detects if worktree branch has `just setup` recipe
- Fallback: `direnv allow && uv sync -q && npm install`

## Pending Tasks

- [ ] **Orchestrate evolution plan** — `/plan-adhoc plans/orchestrate-evolution/design.md` | sonnet
  - Plan: orchestrate-evolution | Status: designed | Check design-review.md for UNFIXABLE before planning
- [ ] **Update worktree-skill for just setup integration** — `/plan-tdd`: integrate `just setup` in worktree creation script | sonnet
- [ ] **Redesign markdown preprocessor** — Multi-line inline markup parsing instead of line-by-line | sonnet
- [ ] **Optimize task agents and commit skill** — Examine worktree-skill for reuse, agent efficiency | sonnet
- [ ] **Review codebase for factorization** — Identify duplication, extract helpers | sonnet
- [ ] **Design review agent output optimization** — Remove summarize/report language from agents | sonnet
- [ ] **Session summary extraction prototype** — Extract session summary from session log | sonnet
- [ ] **Review all tests for vacuous tests** — Comprehensive test quality audit | sonnet
- [ ] **Deslop entire codebase** — Apply deslop principles project-wide | sonnet
- [ ] **Fragments cleanup after orchestration design** — Remove fragments duplicating skills/workflow | sonnet
- [ ] **Execute plugin migration** — `/orchestrate plans/plugin-migration/orchestrator-plan.md` | sonnet
  - Plan: plugin-migration | Status: planned
- [ ] **Update design skill** — Read design artifacts, assess plan progress | sonnet
- [ ] **Add PreToolUse hook for symlink writes** — Block writes through symlink | restart
- [ ] **Handoff validation design** — Complete design (continuation-passing merged) | opus
  - Plan: handoff-validation | Status: requirements
- [ ] **Evaluate requirements-skill with opus** — Dump requirements/design after conversation | opus
  - Plan: requirements-skill | Status: requirements
- [ ] **Strengthen commit Gate B coverage check** — Boolean to coverage ratio | sonnet
- [ ] **Review reflect skill: task output for skill/fragment fixes** — RCA → pending tasks not inline fixes | sonnet
- [ ] **Update tool-batching.md for Task tool parallelization** — Add Task tool guidance with examples | sonnet
- [ ] **Rewrite last-output prototype with TDD** — Port agent-output-cmd to claudeutils subcommand
- [ ] **Update commit and handoff to branch after precommit** — Move branching point after precommit
- [ ] **History cleanup tooling** — Research git history rewriting, prototype scripts
- [ ] **Rewrite agent-core ad-hoc scripts via TDD** — Port ad-hoc scripts to claudeutils package
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements
- [ ] **Update orchestrator workflow for delegate resume** — Resume delegates with incomplete work | sonnet
- [ ] **Error handling framework design** — Error handling for runbooks, task lists, CPS | opus
- [ ] **RCA: Planning agents leave dirty tree** — Delegation prompts lack commit instruction | sonnet
- [ ] **RCA: Planning agent delegation inefficiency** — Tier 1 misrouted to delegation | sonnet
- [ ] **Plan `/when` TDD runbook** — `/plan-tdd plans/when-recall/design.md` | blocked on orchestrate workflow review
  - Plan: when-recall | Status: designed | Load `plugin-dev:skill-development` before planning
- [ ] **Orchestrate worktree-skill execution** — Phase 2 (cycles 2.1-2.4) | sonnet
  - Plan: worktree-skill | Status: in progress (16 of 42 steps complete, 38%)
  - Worktree at `../claudeutils-wt/orchestrate` — recreate with `just wt-new orchestrate`
- [ ] **Update wt-ls and wt-task for sibling directory pattern** — Recipes still reference old `wt/` paths | sonnet

## Blockers / Gotchas

**Preprocessor idempotency test failure:** `test_preprocessor_idempotency[02-inline-backticks]` xfail (8af5677). Redesign required.

**Vet-fix-agent scope understanding:** Flags out-of-scope items as UNFIXABLE instead of "deferred."

**Design-vet-agent may still be running:** Agent af973dc was launched for design review. Check if `plans/orchestrate-evolution/reports/design-review.md` exists and grep for UNFIXABLE before proceeding to planning.

**Worktree at ../claudeutils-wt/orchestrate:** Test worktree exists from this session. Clean up with `just wt-rm orchestrate` before re-creating for actual work.

## Reference Files

- **plans/orchestrate-evolution/design.md** — Full design document (Phase C output)
- **plans/orchestrate-evolution/outline.md** — Validated outline (4 decisions, 4 resolved questions)
- **plans/orchestrate-evolution/reports/outline-review-4.md** — Latest outline review (Ready)
- **plans/parallel-orchestration/problem.md** — Deferred parallel execution requirements

---
*Handoff by Sonnet. Worktree recipes relocated to sibling directory with sandbox registration.*
