# Session: Plugin Migration — Runbook Ready

**Status:** Phase numbering resolved, runbook assembled. Ready to execute plugin migration.

## Completed This Session

**Design and runbook validation:**
- Validated design.md and runbook-phase-*.md files post-merge — no conflicts, content correct
- Updated Phase 0 line number references (justfile lines 19, 76) for accuracy

**prepare-runbook.py enhancements:**
- Relaxed phase numbering validation: accepts 0-based (Phase 0-6) or 1-based (Phase 1-N)
- Added general workflow detection: Step headers (not just Cycle headers for TDD)
- Validation: `start_num` detected from first phase, validates sequential from that base
- Lines 410-445: Phase detection, validation, and frontmatter generation

**Runbook assembly complete:**
- Assembled 7 phase files (Phase 0-6) into 15 step files (step-0-1 through step-6-1)
- Created `.claude/agents/plugin-migration-task.md` (quiet-task baseline)
- Created `plans/plugin-migration/orchestrator-plan.md`
- Type: general, Model: haiku
- Warnings about non-existent files expected (created during execution)

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
  - Current: reflect skill applies fixes in-session (Exit Path 1) consuming context budget
  - Better: produce tasks in session.md for separate session execution
- [ ] **Strengthen vet-fix-agent delegation pattern** — Add execution context provision and UNFIXABLE detection | sonnet
  - Sub-tasks:
    1. Add execution context to vet-fix-agent prompts (include phase dependencies, state transitions)
    2. Add UNFIXABLE detection to orchestrator (read report, grep for markers, escalate if found)
    3. Document vet-fix-agent limitations in memory-index.md (context-blind by default)
    4. Evaluate meta-review necessity (when should vet output be vetted?)
  - Analysis: plans/reflect-rca-sequential-task-launch/rca.md
- [ ] **Update tool-batching.md for Task tool parallelization** — Add explicit Task tool guidance with examples | sonnet
  - Add "Task Tool Parallelization" section to agent-core/fragments/tool-batching.md
  - Include example: vet 6 phase files in parallel (6 Task calls in single message)
  - Show anti-pattern (sequential launch) vs correct pattern (batched launch)
- [ ] **Rewrite last-output prototype with TDD as claudeutils subcommand** — Port agent-output-cmd prototype to proper TDD implementation in claudeutils package
- [ ] **Update commit and handoff to branch after precommit** — Move git branching point from beginning to after precommit passes
- [ ] **History cleanup tooling** — Research git history rewriting, prototype reusable scripts, consider reusable agent. Items: collapse runbook checkpoint commits (preserve session.md handoffs), fix history from wt-merge incident. Allow rewrite on feature branches between releases, may tighten to prevent rewrite of main.
- [ ] **Rewrite agent-core ad-hoc scripts via TDD** — Port all ad-hoc scripts in agent-core/ to claudeutils package through TDD. Add precommit check and process gating: allow quick prototyping but schedule proper rewrite.
- [ ] **Package wt-merge as skill** — Clean tree gate, full handoff+commit pre-merge, auto-resolve session conflicts, amend merge commit. Blocked on continuation-passing.
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

**wt-merge dirty tree pattern:** Session context files (session.md, jobs.md, learnings.md) are always dirty during worktree operations. Current workaround: commit before merge, retry recipe. Proper fix: wt-merge skill with clean tree gate.

**Vet-fix-agent temporal reasoning limitation:**
- Agent validates against current filesystem state, not execution-time state
- Mitigation: Provide execution context in delegation prompts (dependencies, state transitions)
- See pending task: "Strengthen vet-fix-agent delegation pattern"

**UNFIXABLE detection is manual:**
- Vet reports mark issues as UNFIXABLE but don't escalate
- Orchestrator must read report and grep for markers
- See pending task: "Strengthen vet-fix-agent delegation pattern" (sub-task 2)

## Reference Files

- **agent-core/bin/prepare-runbook.py** — Runbook assembly script (lines 410-445: phase detection, validation, frontmatter)
- **plans/plugin-migration/orchestrator-plan.md** — Orchestrator plan (15 steps, haiku execution)
- **plans/plugin-migration/steps/step-*.md** — 15 step files (step-0-1 through step-6-1)
- **.claude/agents/plugin-migration-task.md** — Plan-specific agent (quiet-task baseline)
- **plans/plugin-migration/design.md** — Design with Phase 0 as foundational step (D-1 naming hierarchy)
- **plans/plugin-migration/runbook-phase-{0-6}.md** — Source phase files (7 files, vetted)
- **plans/plugin-migration/reports/phase-{0-6}-review.md** — Vet reviews (44 issues fixed)
- **plans/wt-merge-skill/outline.md** — wt-merge skill design outline
- **plans/continuation-passing/outline.md** — Continuation passing design (in wt/continuation-passing worktree)
- **plans/reflect-rca-sequential-task-launch/rca.md** — RCA covering Task parallelization + vet context issues
- **agent-core/fragments/tool-batching.md** — Current tool batching guidance (needs Task tool section)
- **justfile** — `wt-new` (line 76), `wt-rm`, `wt-merge`
