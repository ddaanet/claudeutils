# Session Handoff: 2026-02-15

**Status:** Memory index actionability improvements complete. 24 key renames, 18 removals, 4 additions across 12 files.

## Completed This Session

**Memory index actionability improvements:**
- 24 index entry keys renamed from root-cause/jargon to symptom-oriented phrasing (old keys preserved as pipe synonyms)
  - Examples: `transformation table` → `choosing review gate`, `prose gates` → `prevent skill steps from being skipped`, `task names must be branch-suitable` → `naming tasks for worktrees`
- 18 entries removed: 6 meta-index (about maintaining the index itself), 5 dead/archival, 4 dead, 3 dedup merges
- 4 entries added: 2 for defense-in-depth.md (new semantic headings added), 1 deliverable-review.md expansion, dedup merges
- 24 corresponding heading renames across 8 decision files (validator requires key-heading match)
- 17 headings marked structural (`.` prefix) in 6 decision files for entries being removed
- Report: `plans/reports/memory-index-actionability-review.md`
- Precommit passes, all 855/856 tests pass (1 xfail)

**Not addressed (remaining from original task):**
- Frozen-domain passive recall mechanism — needs design, rule files unreliable per prior discussion
- Enforce behavioral trigger framing at learning staging time — folded into new design task below

## Pending Tasks

- [ ] **Design remember skill update** — `/design` based on index actionability findings | sonnet
  - Trigger framing: enforce symptom-oriented keys at learning staging time (not `/when` format but behavioral trigger framing)
  - Learning headers in learnings.md should conform to memory-index trigger constraints to prevent consolidation rephrasing
  - Frozen-domain passive recall mechanism — explore alternatives to rule files (code comments, hooks)
  - Input: this session's key renames as examples of good vs bad triggers

- [ ] **Organize plans/reports directory** — Separate persistent research from context-specific reports | sonnet
  - Currently 14 files mixing grounding research (reusable) with plan-specific reports (context-bound)
  - Define directory structure or naming convention for discoverability

- [ ] **Rename remember skill** — Test brainstorm-name agent, pick new name, update all references | sonnet | restart

- [ ] **Protocolize RED pass recovery** — Formalize orchestrator RED pass handling into orchestrate skill | sonnet
  - Scope: Classification taxonomy, blast radius procedure, defect impact evaluation
  - Reports: `plans/when-recall/reports/tdd-process-review.md`, `plans/orchestrate-evolution/reports/red-pass-blast-radius.md`

- [ ] **Precommit validation improvements** — Expand precommit checks | sonnet
  - Validate session.md references point to versioned files (reject tmp/ references) — recurring failure mode
  - Validate session.md pending tasks/worktree structure
  - Reject references to tmp/ files in all committed content
  - Autofix or fail on duplicate memory index entries (blocked on memory redesign)

- [ ] **Handoff skill memory consolidation worktree awareness** — Only consolidate in main repo or dedicated worktree | sonnet

- [ ] **Execute plugin migration** — Refresh outline then orchestrate | sonnet
  - Plan: plugin-migration | Status: planned (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite against post-worktree-update justfile, expanded phases need regeneration
  - Drift: 18 skills (was 16), 14 agents (was 12), justfile +250 lines rewritten

- [ ] **Upstream plugin-dev: document skills frontmatter** — PR/issue to official Claude Code plugin-dev plugin for missing `skills` field | sonnet

- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
  - Plan: continuation-prepend | Status: requirements

- [ ] **Codebase quality sweep** — Tests, deslop, factorization, dead code | sonnet
  - Review all tests for vacuous tests
  - Deslop entire codebase
  - Review codebase for factorization
  - Remove deprecated code — init_repo_with_commit() in conftest_git.py

- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
  - Redesign markdown preprocessor — multi-line inline markup parsing
  - Session summary extraction prototype
  - Rewrite last-output prototype with TDD as claudeutils subcommand

- [ ] **Design workwoods** — `/design plans/workwoods/requirements.md` | opus
  - Plan: workwoods | Status: requirements
  - Integrates with worktree-update (additive merge, bidirectional sync)

- [ ] **Model tier awareness hook** — Hook injecting "Response by Opus/Sonnet/Haiku" into context | sonnet | restart
  - NOT UserPromptSubmit — correct event TBD (load hook skill when executing)

- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
  - History cleanup tooling — git history rewriting, reusable scripts
  - Rewrite agent-core ad-hoc scripts via TDD to claudeutils package

## Worktree Tasks

- [ ] **Error handling framework design** → `wt/error-handling` — Resume `/design` Phase B | opus
  - Blocked on: workflow improvements
  - Outline: `plans/error-handling/outline.md`
- [ ] **Build pushback into conversation process** → `wt/pushback` — `/design plans/pushback/requirements.md` | opus
  - Plan: pushback | Status: requirements
- [ ] **Worktree fixes** → `worktree-fixes` — `/design plans/worktree-fixes/` | opus
  - Plan: worktree-fixes | Status: requirements
  - 6 FRs: task name constraints, precommit validation, migration, session merge blocks, merge commit fix, automate session edits
- [ ] **Workflow improvements** → `workflow-improvements` — Process fixes from RCA + skill/fragment/orchestration cleanup | sonnet
  - RCA blocker resolved — reports at `plans/reports/rca-*-opus.md`
  - Input: `plans/orchestrate-evolution/design.md`, `plans/process-review/rca.md`
  - Orchestrate evolution — designed, stale Feb 10, refresh after RCA
  - Fragments cleanup — remove fragments duplicating skills/workflow
  - Reflect skill output — RCA should produce pending tasks, not inline fixes
  - Tool-batching.md — add Task tool parallelization guidance with examples
  - Orchestrator delegate resume — resume delegates with incomplete work
  - Agent output optimization — remove summarize/report language from agents
  - Investigation prerequisite rule review
  - Design skill: Phase C density checkpoint (TDD non-code marking handled by per-phase typing)
  - Workflow fixes from RCA — `plans/reports/rca-*-opus.md`, normalize runbook-review axes, execution-time split, vet investigation protocol, orchestrate template
  - Commit skill optimizations — remove handoff gate, Gate B coverage ratio, branching after precommit
  - Fix skill-based agents not using skills prolog section — `skills:` frontmatter

## Blockers / Gotchas

**Two methodology documents exist:**
- `agents/decisions/review-methodology.md` — sonnet-generated, user distrusts, do NOT use
- `agents/decisions/deliverable-review.md` — ISO-grounded, use this one
- Cleanup: delete review-methodology.md (confirmed fully superseded)

**wt-merge session reconciliation incomplete:**
- merge.py has auto-resolvers for session.md, learnings.md, jobs.md
- Session merge loses continuation lines (single-line set diff) → worktree-fixes FR-4
- No-op merge skips commit → orphan branch → worktree-fixes FR-5

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes `check_orphan_entries` non-autofixable error
- Must manually remove entries from memory-index.md before running precommit
- Autofix only handles placement, ordering, and structural entry removal — not orphans

**Rule file directive adherence unreliable:**
- Agents ignore injected "load X before modifying" directives
- Same failure mode as passive index (2.9% baseline recall)
- Blocking hooks or inline code comments may be more effective than suggestion-based rules

## Reference Files

- `plans/reports/memory-index-actionability-review.md` — Opus actionability review of all index entries
- `plans/when-recall/reports/corpus-analysis.md` — Index corpus analysis (entry patterns, compatibility)
- `plans/when-recall/reports/baseline-recall-analysis.md` — 2.9% baseline recall measurement
- `plans/when-recall/design.md` — When-recall system design
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
