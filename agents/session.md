# Session Handoff: 2026-02-19

**Status:** Task consolidation complete (43 → 35 pending). 3 untouched worktrees removed, 1 active (error-handling-design). Two new worktree rm bugs discovered.

## Completed This Session

**Task consolidation (43 → 35 pending tasks):**
- Model directive pipeline: absorbed Runbook model assignment, Fix prepare-runbook.py model override, Fix plan-reviewer model adequacy gap (4 → 1)
- Remember skill update: absorbed Rename remember skill, Remember agent routing (3 → 1). Added FR-10/FR-11 to `plans/remember-skill-update/requirements.md`
- Cross-tree requirements transport: absorbed Revert cross-tree sandbox access (2 → 1)
- Worktree CLI default: absorbed Pre-merge untracked file fix, Worktree skill adhoc mode. Added Cycle 1.6 to `plans/worktree-cli-default/outline.md`
- Removed Debug failed merge (code path eliminated by worktree-cli-default)
- Quality infrastructure reform and Codebase quality sweep kept separate (pipeline work vs backlog processing)

**Worktree cleanup:**
- Removed 3 untouched worktrees: runbook-quality-gates-b (empty dir — partial creation), script-commit-vet-gate, worktree-cli-default
- Tasks moved back to Pending
- Discovered: `git worktree remove --force` returns 255 on empty dir from failed bare-slug `new`. `_git()` swallows stderr via `check=True`.
- Discovered: `rm --confirm` deletes parent branch but not agent-core submodule branch

## Pending Tasks

<!-- Priority order per plans/reports/prioritization-2026-02-18.md (rev 4) -->

- [ ] **Commit CLI tool** — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Modeled on worktree CLI pattern (mechanical ops in CLI, judgment in skill)
  - Single command: precommit → stage → commit in main + agent-core submodule

- [ ] **Script commit vet gate** — Replace prose Gate B with scripted check (file classification + vet report existence) | sonnet
  - Part of commit skill optimization (FR-5 partially landed — Gate A removed, Gate B still prose)
  - Also: remove `vet-requirement.md` from CLAUDE.md `@`-references, move execution context template to memory index

- [ ] **Design quality gates** — `/design plans/runbook-quality-gates/` | opus | restart
  - Requirements at `plans/runbook-quality-gates/requirements.md`
  - 3 open questions: script vs agent (Q-1), insertion point (Q-2), mandatory vs opt-in (Q-3)
  - Not blocked on error-handling design (quality gates are pre-execution validation, not execution-time)

- [ ] **Runbook quality gates Phase B** — TDD for validate-runbook.py (4 subcommands) | sonnet
  - Plan: runbook-quality-gates | Status: ready
  - model-tags, lifecycle, test-counts, red-plausibility
  - Graceful degradation bridges gap (NFR-2)

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **Merge learnings delta** — Reconcile learnings.md after merge when branch diverged before consolidation | sonnet
  - Plan: merge-learnings-delta | Status: requirements
  - 3 FRs: detect consolidation divergence, reconstruct correct file, handle edge cases
  - Main base + branch delta strategy (not ours, not theirs)

- [ ] **Fix worktree rm dirty check** — Must not fail if parent repo is dirty, only if target worktree is dirty | sonnet

- [ ] **Fix worktree rm on broken worktree** — `git worktree remove --force` returns 255 on empty dir from failed `new` | sonnet
  - `new` with bare slug can leave empty directory (no `.git`, no checkout). `rm` fails because git doesn't recognize it as a worktree. `_git()` swallows stderr, hiding actual error.
  - Fix: detect non-worktree directory in `rm`, fall back to `prune` + `rmdir` + branch delete

- [ ] **Fix worktree rm submodule branch cleanup** — `rm --confirm` deletes parent branch but not agent-core submodule branch | sonnet
  - Leaves stale submodule branches requiring manual `git -C agent-core branch -d <slug>`

- [ ] **Worktree CLI default** — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - `new "Task Name" --branch <slug>` form solves 29-char slug limit
  - **Scope expansion:** Eliminate Worktree Tasks section, remove `_update_session_and_amend` ceremony, co-design with session.md validator
  - Absorbs: Pre-merge untracked file fix (`new` leaves session.md untracked), Worktree skill adhoc mode (covered by `--branch`)

- [ ] **Pipeline skill updates** — `/design` | opus | restart
  - Orchestrate skill: create `/deliverable-review` pending task at exit (opus, restart)
  - Deliverable-review skill Phase 4: create one pending task for all findings → `/design`; no merge-readiness language
  - Design skill: add Phase 0 requirements-clarity gate (well-specified → triage, underspecified → `/requirements`)
  - Discussion context in runbook-skill-fixes worktree session

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 19 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring
  - Grounding: `plans/reports/code-density-grounding.md`
  - Subsumes: Rename vet agents task (FR-3), augments Codebase quality sweep (FR-4)

- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main tree from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Planstate `infer_state()` now auto-discovers plans (workwoods merged) — no jobs.md write needed
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)

- [ ] **Test diagnostic helper** — Replace `subprocess.run(..., check=True)` in test setup with stderr surfacing | sonnet

- [ ] **Memory-index auto-sync** — Sync memory-index/SKILL.md from canonical agents/memory-index.md on consolidation | sonnet
  - Deliverable review found skill drifted (3 entries missing, ordering wrong)
  - Hook into /remember consolidation flow or add precommit check

- [ ] **Session.md validator** — Scripted precommit check for session.md format (like validate-memory-index.py) | sonnet
  - Plan: session-validator | Status: requirements
  - 5 FRs: section schema, task format, reference validity, worktree marker cross-ref, status line
  - Prior handoff validation task was dropped (agent review impractical) — this is scripted/mechanical
  - FR-2/FR-4 depend on worktree-cli-default (format finalization); FR-1/FR-3/FR-5 can proceed now

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
  - Specific targets from quality-infrastructure FR-4: `_git_ok`, `_fail` helpers, 13 raw subprocess replacements, 18 SystemExit replacements, custom exception classes

- [ ] **Remember skill update** — Resume `/design` Phase B | opus
  - Requirements: `plans/remember-skill-update/requirements.md` (9 FRs + FR-10 rename, FR-11 agent routing)
  - Outline: `plans/remember-skill-update/outline.md` (reviewed, Phase B discussion next)
  - Three concerns: trigger framing enforcement, title-trigger alignment, frozen-domain recall
  - Key decisions pending: hyphen handling, agent duplication, frozen-domain priority
  - Absorbs: Rename remember skill (FR-10), Remember agent routing (FR-11, deferred until redesign)
  - **New scope:** `/remember` consolidation should validate trigger names before graduating to `/when` entries

- [ ] **Handoff wt awareness** — Only consolidate memory in main repo or dedicated worktree | sonnet

- [ ] **Agent rule injection** — process improvements batch | sonnet
  - Distill sub-agent-relevant rules (layered context model, no volatile references, no execution mechanics in steps) into agent templates
  - Source: tool prompts, review guide, memory system learnings

- [ ] **Handoff insertion policy** — Change "append" to "insert at estimated priority position" in handoff skill | sonnet
  - Evidence: `p:` tasks distribute evenly (n=29), not append-biased. Agents correctly judge position.
  - Scripts: `plans/prototypes/correlate-pending-v2.py`

- [ ] **Learning ages consol** — Verify age calculation correct when learnings consolidated/rewritten | sonnet

- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart

- [ ] **Simplify when-resolve CLI** — Accept single argument with when/how prefix instead of two args, update skill prose | sonnet

- [ ] **Explore Anthropic plugins** — Install all 28 official plugins, explore for safety+security relevance | sonnet | restart
  - Repo: `github.com/anthropics/claude-plugins-official`

- [ ] **Behavioral design** — `/design` nuanced conversational pattern intervention | opus
  - Requires synthesis from research on conversational patterns

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Existing: `bin/last-output`, `scripts/scrape-validation.py`, `plans/prototypes/*.py`
  - Requirements: `plans/prototypes/requirements.md` (multi-project scanning, directive extraction, git correlation)

- [ ] **Design-to-deliverable** — Design session for tmux-like session clear/model switch/restart automation | opus | restart

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet

- [ ] **Diagnostic opus review** — Interactive post-vet RCA methodology | `/requirements` | opus
  - Taxonomy (6 categories): completeness, consistency, feasibility, clarity, traceability, coupling
  - Two-tier context augmentation: always-inject vs index-and-recall

- [ ] **Ground state-machine review criteria** — Research state coverage validation in plan review | opus

- [ ] **Upstream skills field** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` frontmatter | sonnet

- [ ] **Workflow formal analysis** — Formal verification of agent workflow | `/requirements` then `/design` | opus
  - Candidates: TLA+ (temporal), Alloy (structural), Petri nets (visual flow)

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design.md complete, vet in progress, planning next (design refreshed Feb 13)
  - Design runbook evolution now complete — blocker lifted

- [ ] **RED pass protocol** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Blocked on: Error handling design (needs D-3 escalation criteria, D-5 rollback semantics)
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation

- [ ] **Safety review expansion** — Implement pipeline changes from grounding research | opus
  - Input: `plans/reports/safety-review-grounding.md`
  - Depends on: Explore Anthropic plugins

- [ ] **Migrate test suite to diamond** — needs scoping | depends on runbook evolution design
  - Existing 1027 tests, separate design from runbook evolution

- [ ] **Model directive pipeline** — Model guidance flows design → runbook → execution | opus
  - Touches: design skill, outline format, runbook skill, prepare-runbook.py, orchestrate skill, plan-reviewer
  - Absorbs: Runbook model assignment, Fix prepare-runbook.py model override, Fix plan-reviewer model adequacy gap

## Worktree Tasks

- [ ] **Error handling design** → `error-handling-design` — Resume `/design` Phase B (outline review) then Phase C (full design) | opus
  - Outline: `plans/error-handling/outline.md`
  - Key decisions: D-1 CPS abort-and-record, D-2 task `[!]`/`[✗]` states, D-3 escalation acceptance criteria, D-5 rollback = revert to step start

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files
- Always use `dangerouslyDisableSandbox: true` for any merge operation

**`_update_session_and_amend` exit 128 during rm:**
- `_worktree rm` calls `_update_session_and_amend` which runs `git add agents/session.md` → exit 128
- Root cause unclear — same command succeeds manually. Workaround: manual amend before `rm --confirm`

**`slug` and `--task` mutually exclusive in `_worktree new`:**
- Cannot override slug for long task names while keeping session integration
- Workaround: bare slug + manual session.md editing
- Fix: worktree-cli-default task adds `--branch` flag

**Merge ours resolution loses worktree content:**
- `just wt-merge` uses `checkout --ours` for session.md, learnings.md
- Drops worktree-side changes silently — must verify post-merge
- Learnings.md: merge brings pre-consolidation content when branch diverged before `/remember`. See `plans/merge-learnings-delta/requirements.md`

**`wt rm` blocks on dirty parent repo:**
- `claudeutils _worktree rm` exits 2 if parent has uncommitted changes
- Workaround: `git stash && wt rm && git stash pop`

**`wt rm` leaves stale submodule config:**
- `.git/modules/agent-core/config` `core.worktree` points to deleted directory
- Breaks all `git -C agent-core` operations on main until manually fixed

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit

**Memory index `/how` operator mapping:**
- `/how X` in index → internally becomes `"how to X"` for heading matching
- Index keys must NOT include "to" — validator adds it automatically
## Next Steps

1 worktree active: error-handling-design. On main: Commit CLI tool is the top unbranched task.

## Reference Files

- `plans/reports/prioritization-2026-02-18.md` — WSJF task prioritization (rev 4, 43 tasks — stale, pre-consolidation)
- `plans/merge-learnings-delta/requirements.md` — Learnings merge reconciliation (3 FRs, Q-1 consolidation marker)
- `plans/session-validator/requirements.md` — Session.md validator (5 FRs, precommit integration)
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug, Worktree Tasks elimination)
- `plans/error-handling/outline.md` — Error handling design outline (Phase A complete)
- `plans/runbook-quality-gates/design.md` — Quality gates design (6 FRs, simplification agent)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop restructuring, code density decisions, vet rename, code refactoring