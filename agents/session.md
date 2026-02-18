# Session Handoff: 2026-02-18

**Status:** Attempted design-workwoods merge — tool can't handle source conflicts, wrote merge resilience requirements, RCA on escalation pattern. 3 worktrees active.

## Completed This Session

**Worktree merge resilience requirements:**
- Wrote `plans/worktree-merge-resilience/requirements.md` — 5 FRs for improving `_worktree merge` conflict handling
- FR-1: proceed through submodule conflicts, FR-2: leave parent merge in progress (don't abort), FR-3: handle untracked file collisions, FR-4: conflict context in output, FR-5: idempotent resume across all phases

**RCA on merge workaround escalation:**
- Identified "tool fails → I become the tool" pattern: manually reimplementing merge phases, losing atomicity/safety invariants
- Root cause of 82 orphaned files: `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox restriction, leaves debris
- Bounded workaround rule: pre-resolution means editing conflicting regions of EXISTING files, not creating new modules
- 2 learnings added to `agents/learnings.md`

**Agent-core submodule conflict resolved:**
- SKILL.md conflict in agent-core between runbook-skill-fixes (auto-rm with --confirm) and workwoods (no auto-rm, preserve worktree)
- Took workwoods version (newer design intent)
- agent-core HEAD at b3b6f5b (merge commit) — parent pointer not yet updated

## Pending Tasks

<!-- Priority order per plans/reports/prioritization-2026-02-16.md (rev 2) -->

- [ ] **Merge design-workwoods** — Manual merge with conflict resolution | sonnet
  - Agent-core submodule: already resolved (b3b6f5b), parent pointer needs updating (`git add agent-core && git commit`)
  - Parent repo: cli.py has 3 conflict regions (imports, `_guard_branch_removal`, `_delete_branch`)
  - `just wt-merge` recipe (line 199) also aborts on source conflicts — same limitation as Python tool
  - **Procedure:** Run `git merge --no-commit --no-ff design-workwoods` with `dangerouslyDisableSandbox: true`, resolve cli.py, complete merge
  - **CRITICAL:** Never run `git merge` without `dangerouslyDisableSandbox: true` — partial checkout + sandbox failure deposits orphaned files
  - **cli.py conflict resolution (3 regions):**
    - Imports: remove `_format_git_error` and `extract_task_blocks`, add `format_rich_ls` (from display), keep `focus_session` re-export, keep `_is_parent_dirty`/`_is_submodule_dirty`
    - `_guard_branch_removal`: take workwoods ternary style + main's `SystemExit(2)`
    - `_delete_branch`: take workwoods compact formatting + main's `SystemExit(1)`
  - **Context loss risk:** This session analyzed both versions in full. Next session must re-read both sides (`git show design-workwoods:src/claudeutils/worktree/cli.py` vs main) if conflict details unclear
  - After merge: `just precommit`, then `wt-rm design-workwoods` when ready

- [ ] **Worktree merge resilience** — `/design plans/worktree-merge-resilience/requirements.md` | opus
  - Plan: worktree-merge-resilience | Status: requirements
  - 5 FRs: submodule conflict pass-through, leave merge in progress, untracked file handling, conflict context output, idempotent resume
  - Addresses root cause of merge difficulties observed this session

- [ ] **Fix worktree rm dirty check** — Must not fail if parent repo is dirty, only if target worktree is dirty | sonnet

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents task (FR-3), augments Codebase quality sweep (FR-4)

- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Blocked on: Error handling design (needs D-3 escalation criteria, D-5 rollback semantics)
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 19 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Script commit vet gate** — Replace prose Gate B with scripted check (file classification + vet report existence) | sonnet
  - Part of commit skill optimization (FR-5 partially landed — Gate A removed, Gate B still prose)
  - Also: remove `vet-requirement.md` from CLAUDE.md `@`-references, move execution context template to memory index

- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule

- [ ] **Vet delegation routing** — Route review to artifact-appropriate agent (correct for code, skill-reviewer for skills, agent-creator for agents) | sonnet
  - General rule affecting vet-requirement.md and /runbook review delegation
  - agent-creator: Write+Read, confirmed cooperative in review mode (decisions/project-config.md:266)
  - skill-reviewer: Read/Grep/Glob only — cannot autofix, would need tool additions
  - No hook reviewer exists; no doc reviewer exists (readme skill is creation, not review)
  - Precedent: agent-creator repurposed for review via prompting (`/when agent-creator reviews agents`)

- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart

- [ ] **Remember skill update** — Resume `/design` Phase B | opus
  - Requirements: `plans/remember-skill-update/requirements.md` (7 FRs, When/How prefix mandate)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Reports: `plans/remember-skill-update/reports/outline-review.md`, `plans/remember-skill-update/reports/explore-remember-skill.md`
  - Learnings consolidation done (491→32 lines) — FR-7 migration partially addressed via consolidation
  - **New scope:** `/remember` consolidation should validate trigger names before graduating to `/when` entries

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **Memory-index auto-sync** — Sync memory-index/SKILL.md from canonical agents/memory-index.md on consolidation | sonnet
  - Deliverable review found skill drifted (3 entries missing, ordering wrong)
  - Hook into /remember consolidation flow or add precommit check

- [ ] **Agent rule injection** — process improvements batch | sonnet
  - Distill sub-agent-relevant rules (layered context model, no volatile references, no execution mechanics in steps) into agent templates
  - Source: tool prompts, review guide, memory system learnings

- [ ] **Diagnostic opus review** — Interactive post-vet RCA methodology | `/requirements` | opus
  - Extends /reflect skill with proactive invocation, two-model separation, feedback loops
  - Research: MAR, Flow-of-Action, Reflexion, Five Whys, TAMO, AgentErrorTaxonomy
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject vs index-and-recall
  - Methodology as skill referenced in design-vet-agent + outline-review-agent `skills:` frontmatter

- [ ] **Handoff insertion policy** — Change "append" to "insert at estimated priority position" in handoff skill | sonnet
  - Evidence: `p:` tasks distribute evenly (n=29), not append-biased. Agents correctly judge position.
  - Scripts: `plans/prototypes/correlate-pending-v2.py`

- [ ] **Handoff wt awareness** — Only consolidate memory in main repo or dedicated worktree | sonnet

- [ ] **Learning ages consol** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
  - Specific targets from quality-infrastructure FR-4: `_git_ok`, `_fail` helpers, 13 raw subprocess replacements, 18 SystemExit replacements, custom exception classes

- [ ] **Remember agent routing** — blocked on memory redesign | sonnet
  - When consolidating learnings actionable for sub-agents, route to agent templates (quiet-task.md, tdd-task.md) as additional target

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet

- [ ] **Behavioral design** — `/design` nuanced conversational pattern intervention | opus
  - Requires synthesis from research on conversational patterns

- [ ] **Upstream skills field** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` frontmatter | sonnet

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Existing: `bin/last-output`, `scripts/scrape-validation.py`, `plans/prototypes/*.py`
  - Requirements: `plans/prototypes/requirements.md` (multi-project scanning, directive extraction, git correlation)

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)

- [ ] **Design-to-deliverable** — Design session for tmux-like session clear/model switch/restart automation | opus | restart

- [ ] **Worktree skill adhoc mode** — Add mode for creating worktree from specific commit without task tracking | sonnet

- [ ] **Explore Anthropic plugins** — Install all 28 official plugins, explore for safety+security relevance | sonnet | restart
  - Repo: `github.com/anthropics/claude-plugins-official`

- [ ] **Ground state-machine review criteria** — Research state coverage validation in plan review | opus

- [ ] **Pre-merge untracked file fix** — `new --session` leaves session.md untracked on main | sonnet

- [ ] **Safety review expansion** — Implement pipeline changes from grounding research | opus
  - Input: `plans/reports/safety-review-grounding.md`
  - Depends on: Explore Anthropic plugins

- [ ] **Test diagnostic helper** — Replace `subprocess.run(..., check=True)` in test setup with stderr surfacing | sonnet

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design.md complete, vet in progress, planning next (design refreshed Feb 13)

- [ ] **Simplify when-resolve CLI** — Accept single argument with when/how prefix instead of two args, update skill prose | sonnet

- [ ] **Debug failed merge** — Investigate the original merge failure (exit 128 during session.md conflict resolution) | sonnet
  - Context: Merge of `remaining-workflow-items` worktree on 2026-02-16
  - Branch had 1 post-merge commit (683fc7d), conflicts on `agent-core` submodule + `agents/session.md`
  - Main at 9bb45d0, merge result at 5e024c2
  - `git add agents/session.md` returned exit 128 during `_resolve_session_md_conflict` in `_phase3_merge_parent`
  - Now that error handling is fixed, we can reproduce and see the actual git error message

- [ ] **Runbook model assignment** — apply design-decisions.md directive (opus for skill/fragment/agent edits)
  - Partially landed via remaining-workflow-items merge
- [ ] **Runbook quality gates Phase B** — TDD for validate-runbook.py (4 subcommands) | sonnet
  - Depends on Phase A merge (SKILL.md references script)
  - Graceful degradation bridges gap (NFR-2)
  - model-tags, lifecycle, test-counts, red-plausibility

- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main tree from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Workwoods impact: planstate `infer_state()` will auto-discover plans — no jobs.md write needed post-workwoods

- [ ] **Runbook evolution** — `/design plans/runbook-evolution/requirements.md` | opus
  - Plan: runbook-evolution | Status: requirements
  - 5 FRs: prose atomicity, self-modification discipline, testing diamond, deferred enforcement, test migration

- [ ] **Revert cross-tree sandbox access** — Remove `additionalDirectories` code from `_worktree new` | sonnet
  - Superseded by git show transport — sandbox access unnecessary for cross-tree operations
  - Affects: cli.py `_setup_worktree()`, justfile, `test_new_sandbox_registration`

- [ ] **Design quality gates** — `/design plans/runbook-quality-gates/` | opus | restart
  - Requirements at `plans/runbook-quality-gates/requirements.md`
  - 3 open questions: script vs agent (Q-1), insertion point (Q-2), mandatory vs opt-in (Q-3)
- [ ] **Design runbook evolution** — `/design plans/runbook-evolution/` | opus | restart
  - Requirements at `plans/runbook-evolution/requirements.md`
  - Outline exists at `plans/runbook-evolution/outline.md` — resume from Phase A.6 (outline review)
  - Scope: runbook SKILL.md generation directives only
- [x] **Fix deliverable code findings** — M-4/M-5/M-6/M-7 code + test gaps
- [ ] **Migrate test suite to diamond** — needs scoping | depends on runbook evolution design
  - Existing 1027 tests, separate design from runbook evolution
  - Different scope and execution profile

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

- [ ] **Design workwoods** → `design-workwoods` — Merge pending (see "Merge design-workwoods" task above) | opus
  - Plan: workwoods | Status: designed (runbook planned, 33 TDD + 10 general steps)

- [ ] **Runbook skill fixes** → `runbook-skill-fixes` — Batch: model assignment, design quality gates | opus
  - Runbook model assignment: apply design-decisions.md directive (opus for skill/fragment/agent edits) — partially landed
  - Design quality gates: `/design plans/runbook-quality-gates/` | restart
    - Requirements at `plans/runbook-quality-gates/requirements.md`

## Blockers / Gotchas

**Merge tool aborts on conflict (both Python and justfile):**
- `_worktree merge` AND `just wt-merge` abort and return clean tree on source conflicts
- Skill Mode C step 4 documents resolution assuming in-progress merge state — mismatch
- `just wt-merge` recipe at justfile:199, same abort behavior at line 306
- Requirements for fix: `plans/worktree-merge-resilience/requirements.md`

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files
- These orphaned files block subsequent merge attempts
- Always use `dangerouslyDisableSandbox: true` for any merge operation

**Transient git index.lock during merge:**
- `claudeutils _worktree merge` hits `index.lock` race condition during multi-step git operations
- Likely caused by file watcher (IDE/direnv) touching the index concurrently
- Workaround: retry after brief pause, or complete merge manually after partial success

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit

**`wt rm` leaves stale submodule config:**
- Removing a worktree can leave `.git/modules/agent-core/config` `core.worktree` pointing to the deleted directory
- Breaks all `git -C agent-core` operations on main until manually fixed

**Memory index `/how` operator mapping:**
- `/how X` in index → internally becomes `"how to X"` for heading matching
- Headings must include "To" (e.g., "How To Augment Agent Context")
- Index keys must NOT include "to" — validator adds it automatically

**User feedback annotations in working tree:**
- `src/claudeutils/cli.py` has 12 FIXME/TODO/antipattern comments from user code review
- `git checkout -- src/claudeutils/cli.py` to discard, or preserve as reference for quality-infrastructure design

**Agent-core submodule pointer mismatch:**
- agent-core HEAD at b3b6f5b (merge commit with SKILL.md resolution)
- Parent repo pointer still at pre-merge commit (reset reverted the pointer update)
- Next merge Phase 2 will detect this as already-resolved and skip

## Next Steps

Next: Merge design-workwoods (sonnet, manual merge with sandbox bypass). Learnings at 152/80 lines — run `/remember` urgently. 3 worktrees active (error-handling-design, design-workwoods, runbook-skill-fixes).

## Reference Files

- `plans/worktree-merge-resilience/requirements.md` — 5 FRs for merge conflict handling
- `plans/reports/prioritization-2026-02-16.md` — WSJF task prioritization (rev 2, 27 tasks)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring
- `plans/reports/code-density-grounding.md` — Grounded research on exception handling + Black formatter interaction
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/reports/safety-review-grounding.md` — Safety review grounding research
- `plans/runbook-quality-gates/design.md` — Quality gates design (6 FRs, simplification agent)
- `plans/runbook-evolution/requirements.md` — Runbook evolution (5 FRs, testing diamond, prose atomicity)
- `plans/remember-skill-update/requirements.md` — 7 FRs (When/How prefix, validation, migration)
