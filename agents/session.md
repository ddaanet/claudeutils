# Session: Plugin Migration — Merge Complete

**Status:** tools-rewrite merged. Plugin migration blocked on prepare-runbook.py phase numbering validation.

## Completed This Session

**Merge operations:**
- Merged `tools-rewrite` branch into `wt/plugin-migration`
- Resolved session.md conflicts, combined infrastructure and plugin migration contexts
- agent-core submodule already up-to-date with main

**Prior work from tools-rewrite:**
- Merged `infrastructure-improvements` branch (df9f903) — 4 workflow infrastructure tasks
- Merged `wt/complexity-fixes` — precommit fixes complete (complexity + line limits, 509 tests passing)
- Merged `wt/domain-validation-design` (966c580) — plugin-dev-validation skill, plan updates
- Merged `wt/parity-failures` (1be1171) — parity gap fixes (11 steps, 3 phases)
- Merged `wt/agent-core-links` (ee19369) — fixed sync-to-parent agent symlinks

**Plugin migration status:**
- All 7 phase files generated and vetted (Phase 0-6, 44 issues fixed across all phases)
- `prepare-runbook.py` expects 1-based phase numbering (phases 1-N)
- Plugin migration uses 0-based numbering (Phase 0-6)
- Design intentionally uses Phase 0 for directory rename (foundational step before Phase 1)

## Pending Tasks

- [ ] **Resolve prepare-runbook.py phase numbering** — Fix validation to support 0-based or 1-based phase numbering | sonnet
  - Current: Script enforces 1-based (phases 1-N), fails on plugin migration's 0-based (Phase 0-6)
  - Options: (1) Renumber phases 0-6 → 1-7, (2) Fix script to accept 0-based, (3) Make validation flexible
  - File: `agent-core/bin/prepare-runbook.py` lines 403-414
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

**Prepare-runbook.py phase numbering mismatch:**
- Script validation at lines 410-414 expects `range(1, N+1)` (1-based)
- Plugin migration design uses Phase 0 (directory rename) as foundational step
- All phase files exist: `runbook-phase-0.md` through `runbook-phase-6.md`
- Error message: "Phase numbering gaps detected. Missing phases: []" (misleading — no gaps, just wrong base)
- Cannot proceed with runbook assembly until validation fixed

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

- **agent-core/bin/prepare-runbook.py** — Runbook assembly script (lines 403-414: phase numbering validation)
- **plans/plugin-migration/runbook-phase-{0-6}.md** — All phase files (vetted, ready for assembly)
- **plans/plugin-migration/reports/phase-{0-6}-review.md** — Vet reviews (44 issues fixed)
- **plans/plugin-migration/design.md** — Design with Phase 0 as foundational step (D-1 naming hierarchy)
- **plans/wt-merge-skill/outline.md** — wt-merge skill design outline
- **plans/continuation-passing/outline.md** — Continuation passing design (in wt/continuation-passing worktree)
- **plans/reflect-rca-sequential-task-launch/rca.md** — RCA covering Task parallelization + vet context issues
- **agent-core/fragments/tool-batching.md** — Current tool batching guidance (needs Task tool section)
- **justfile** — `wt-new` (lines 55-87), `wt-rm`, `wt-merge`
