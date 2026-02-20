# Session Handoff: 2026-02-20

**Status:** Context optimization analysis complete, hook batch scoped, briefs written. Communication rule updated.

## Completed This Session

**Context optimization analysis:**
- Analyzed 25.5k tokens of always-loaded fragments for demotion candidates
- Identified ~6.6k demotable tokens (26%): sandbox-exemptions, claude-config-layout, project-tooling, bash-strict-mode, vet-requirement, workflows-terminology (partial), error-handling (partial)
- Key finding: vet-requirement (2.4k) is passive — commit skill gate is the actual enforcement
- Key finding: "frequently useful" ≠ "always needed" — behavioral rules vs procedural reference
- Deferred: learnings consolidation (entries need aging), memory-index restructuring (needs usage data)
- Brief: `plans/context-optimization/brief.md`

**Hook batch scoping:**
- Consolidated PostToolUse auto-format + SessionStart status hook + new patterns into single task
- SessionStart scoped to 3 features (not 5): dirty tree, learning-ages --summary, stale worktrees. Model tier blocked (no API). Tip rotation deferred (no content source).
- UserPromptSubmit improvements plan: line-based shortcuts, directive refinements (scope clarification, p: dual output, q:/learn: implementation), skill-editing guard, ccg integration
- Skill activation research: 20% baseline (pure LLM reasoning), forced-eval hook reaches 84% (Scott Spence)
- Brief: `plans/hook-batch/brief.md`, plan: `plans/hook-batch/userpromptsubmit-plan.md`

**RCA: Skill trigger failure:**
- "drop a brief" should have triggered `/brief` skill, agent started manual execution
- Root cause: execution routing preempts skill scanning (attention-dependent gate vs pattern-reinforced behavior)
- Platform limitation: ~20% baseline skill activation, not project-specific
- Fix direction: UserPromptSubmit hook with targeted patterns (skill-editing guard, ccg)

**Communication rule change:**
- Removed AskUserQuestion directive from `agent-core/fragments/communication.md` (rule 5)

**Sandbox denylist specification:**
- Block from bypass: `git merge`, `git worktree`, `ln`
- NOT blocking `git commit` (commit skill uses it internally, deferred until Session CLI)
- Manual user configuration, not automated

## Pending Tasks

- [ ] **When recall evaluation** — sonnet
- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet

- [ ] **Hook batch** — `/design plans/hook-batch/brief.md` | sonnet | restart
  - Absorbs: PostToolUse auto-format hook, SessionStart status hook
  - Scope: SessionStart health (3 features), PreToolUse recipe-redirect, UserPromptSubmit improvements (7 changes), PostToolUse auto-format
  - Plan: hook-batch | Status: designed (UserPromptSubmit plan written, other hooks need design)
  - b: directive semantics TBD (fourth member of b/d/p/q mirror-letter set)

- [ ] **Context optimization** — Fragment demotion from CLAUDE.md | sonnet
  - Plan: context-optimization | Status: designed
  - Depends on: Hook batch (denylist + PreToolUse hook replace project-tooling.md)
  - ~6.6k tokens demotable (26%), injection points in worktree/design/orchestrate/hook-dev/plugin-dev/token-efficient-bash skills

- [ ] **Worktree CLI default** — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `--branch` creates worktree from existing branch (no session.md handling)
  - Scope expansion: Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: pre-merge untracked file fix (`new` leaves session.md untracked), worktree skill adhoc mode (covered by `--branch`), `--slug` override for `--task` mode (25-char slug limit vs prose task names)
  - `rm --confirm` gate: replace with merge-status check (is branch ancestor of HEAD?). Current gate provides no safety, gives wrong error message ("use wt merge" when user already merged), agent retries immediately with `--confirm`

- [ ] **SessionStart status hook** — Absorbed into Hook batch
- [ ] **PostToolUse auto-format hook** — Absorbed into Hook batch

- [ ] **Pipeline skill updates** — `/design` | opus | restart
  - Orchestrate: `/deliverable-review` pending task at exit
  - Design skill: Phase 0 requirements-clarity gate
  - Absorbs: vet-invariant-scope, inline-phase-type
  - Insights input: Diamond TDD definition needed at `/design` (direct execution path), `/runbook` (step generation), `tdd-task` agent (cycle execution)
  - Discussion context in runbook-skill-fixes worktree session

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents (FR-3), Codebase quality sweep (FR-4)
  - Absorbs: integration-first-tests

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete with Phase 1 (foundation) + Phase 2 (ping-pong TDD), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle

- [ ] **Audit rules for design-history noise** — Scan fragments/skills for design history embedded in directives (rejected alternatives). Distinguish from functional motivation (why the rule exists) which stays. | opus
- [ ] **Design skill review gate fix** — Apply transition-gated wording to Phase B step 4 in design/SKILL.md. Include motivation (review validates cross-cutting consistency that individual approvals don't check). | sonnet
- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized (handoff and commit done) | sonnet
- [ ] **Pending task capture wording** — Fix agent tendency to capture pending tasks verbatim instead of rewording with context from the discussion | opus
- [ ] **Session CLI tool** — `_session` group (handoff, status, commit) | sonnet
  - Plan: handoff-cli-tool | Status: designed
  - Combined outline at `plans/handoff-cli-tool/outline.md` (355 lines, 7 phases)
  - Blocked on: Pipeline skill updates (fix pipeline leaks before running 7-phase runbook)
  - After pipeline fixes: outline review → sufficiency gate → `/runbook`
  - New requirement: commit subcommand must output shortened commit IDs (session scraping)

## Worktree Tasks

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`_update_session_and_amend` exit 128 during rm:**
- `_worktree rm` calls `_update_session_and_amend` → exit 128. Workaround: manual amend before `rm --confirm`

**`slug` and `--task` mutually exclusive in `_worktree new`:**
- Fix: worktree-cli-default adds `--branch` flag

**Merge resolution silently corrupts learnings and blockers:**
- Learnings: line-set-difference reintroduces pre-consolidation entries when branch diverged before `/remember`. Blockers: focused sessions have no blockers section, so resolved blockers aren't detected
- **Manual post-merge check required:** After `wt merge`, verify learnings.md for pre-consolidation duplicates (diff against ancestor) and blockers for items fixed by the branch's work

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping:**
- `/how X` → internally `"how to X"` — index keys must NOT include "to"

**Learnings at 157 lines — consolidation deferred:**
- Past 150-line trigger but 0 entries ≥7 active days. Aging required before graduation.

**Skill activation ~20% baseline:**
- Platform limitation — skill matching is pure LLM reasoning with no algorithmic routing. UserPromptSubmit hook with targeted patterns is the structural fix.

## Next Steps

Hook batch is the critical path — unblocks context optimization and provides mechanical enforcement for skill activation, recipe priority, and session health checks.

## Reference Files

- `plans/context-optimization/brief.md` — Fragment demotion analysis (demotable/stays/blocked)
- `plans/hook-batch/brief.md` — Consolidated hook task scope and research findings
- `plans/hook-batch/userpromptsubmit-plan.md` — UserPromptSubmit improvements (7 changes)
- `plans/handoff-cli-tool/brief.md` — Session CLI briefs (status subcommand + commit ID requirement)
- `agents/backlog.md` — 30+ deferred tasks with plan associations and groupings
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop, code density, vet rename, refactoring
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Combined session CLI outline (handoff + commit + status)
