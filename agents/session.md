# Session Handoff: 2026-01-31

**Status:** Project tooling priority fix, justfile caching system, review-tdd-process agent integration complete.

## Completed This Session

**Project tooling priority rule (diagnostic RCA):**
- Root cause: Script-First Evaluation in `delegation.md` encouraged `ln -sf` without "check for project recipes first"
- User diagnostic: Why did agent use `ln -sf` instead of `just sync-to-parent` when both loaded in context?
- Created `agent-core/fragments/project-tooling.md` — project recipes take priority over ad-hoc commands
- Updated `agent-core/fragments/delegation.md` — Script-First Evaluation now checks `just --list` first
- Added to `CLAUDE.md` and `agents/learnings.md`
- Broader lesson: Loaded directives must override general knowledge, not compete with it

**Justfile help caching system:**
- Created `agent-core/Makefile` — gmake-based cache management with dependency tracking
- Makefile hidden in `agent-core/`, entry point is `just` (default `gmake` target shows help message)
- Generated `.cache/just-help.txt` and `.cache/just-help-agent-core.txt`
- Updated `CLAUDE.md` — @file references load both cached help outputs in initial context
- Updated root `justfile`:
  - Added `cache` recipe → `gmake --no-print-directory -C agent-core all`
  - `dev` depends on `cache` (rebuilds if justfiles changed)
  - `precommit` runs `gmake check` (fails if cache stale)
- FUTURE: When justfiles factored to use agent-core includes, update Makefile dependencies

**review-tdd-process agent integration:**
- Created `agent-core/agents/review-tdd-process.md` — sonnet agent for post-execution TDD quality analysis
- Agent analyzes: plan vs execution, TDD compliance (RED/GREEN/REFACTOR), code quality, produces actionable recommendations
- Synced to `.claude/agents/` via `just sync-to-parent` (requires `dangerouslyDisableSandbox: true`)
- Updated `agent-core/skills/orchestrate/SKILL.md`:
  - Section 6: TDD completion now delegates to vet-fix-agent, then review-tdd-process
  - Integration section: Added TDD workflow stages (oneshot and TDD paths now documented)
  - TDD workflow: `/design` (TDD) → `/plan-tdd` → `/orchestrate` → [vet-fix-agent] → [review-tdd-process]

## Pending Tasks

- [ ] **Update sync-to-parent references** — document required `dangerouslyDisableSandbox: true` for the recipe | sonnet
- [ ] **Refactor oneshot handoff template** — integrate into current handoff/pending/execute framework | sonnet
- [ ] **Evaluate oneshot skill** — workflow now always starts with /design, may be redundant | opus
- [ ] **Update heredoc references** — sandboxed heredoc fix landed. Remove workarounds, restore vendor default heredoc behavior for commit messages | sonnet
- [ ] **Resume workflow-controls orchestration (steps 2-7)** — `/orchestrate workflow-controls` | sonnet | restart
- [ ] **Implement ambient awareness** — `/plan-adhoc plans/ambient-awareness/design.md` | sonnet
- [ ] **Create /reflect skill** — deviation detection → RCA → fix → handoff/commit automation. Load plugin-dev skills first | opus
- [ ] **Insert skill loading in design docs** — design skill should load relevant plugin-dev skills when topic involves hooks/agents/skills | sonnet
- [ ] **Update workflow skills: pbcopy next command** — commit/handoff STATUS display copies next command to clipboard | sonnet
- [ ] **Add "go read the docs" checkpoints** — partially addressed by design-work.md rule | sonnet
- [ ] **Design runbook identifier solution** — `/design plans/runbook-identifiers/problem.md` | opus
- [ ] **Create design-vet-agent** — dedicated opus agent for design review, artifact-return pattern | opus
- [ ] **Add execution metadata to step files** — step files declare dependencies and execution mode | sonnet
- [ ] **Orchestrator scope consolidation** — delegate checkpoint phases in orchestrate skill | sonnet

## Blockers / Gotchas

**Commit-rca-fixes active:**
- Fix 3 (orchestrator stop rule) prevents dirty-state rationalization
- Fix 2 (artifact staging) ensures prepare-runbook.py artifacts are staged
- Fix 1 (submodule awareness) prevents submodule pointer drift

**Learnings file at 131/80 lines** — needs `/remember` consolidation urgently.

**sync-to-parent requires sandbox bypass:**
- `just sync-to-parent` in agent-core/ fails with "Operation not permitted" in sandbox
- Requires `dangerouslyDisableSandbox: true` to succeed
- Should document this in CLAUDE.md sync-to-parent reference and sandbox-exemptions.md

## Reference Files

**New fragments:**
- `agent-core/fragments/project-tooling.md` — project recipe priority over ad-hoc commands

**New agent:**
- `agent-core/agents/review-tdd-process.md` — TDD process quality analysis agent

**Cache files:**
- `.cache/just-help.txt` — root justfile recipes (loaded via @file in CLAUDE.md)
- `.cache/just-help-agent-core.txt` — agent-core justfile recipes (loaded via @file in CLAUDE.md)

**Build infrastructure:**
- `agent-core/Makefile` — cache management with dependency tracking

## Next Steps

Learnings file at 131/80 lines. Run `/remember` to consolidate before next session.

---
*Handoff by Opus. Project tooling priority diagnostic complete, justfile caching system operational.*
