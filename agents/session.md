# Session Handoff: 2026-02-15

**Status:** Memory index actionability review complete, brainstorm-name agent created.

## Completed This Session

**Memory index actionability discussion:**
- Opus agent reviewed all 150 index entries for actionability — report at `plans/reports/memory-index-actionability-review.md`
- Identified 6 systemic patterns: archival entries (~27%), root-cause-not-symptom triggers, meta-index noise, missing coverage (defense-in-depth.md), 3 redundancy clusters, frozen-domain inflation
- External research grounded in Anthropic contextual retrieval, RAG precision/recall literature
- Local research: when-recall design.md, corpus-analysis.md, baseline-recall-analysis.md (2.9% baseline)

**Discussion outcomes (not yet executed):**
- Frozen-domain entries (markdown-tooling, validation-quality, data-processing ~41 entries) need passive recall mechanism, not active index — original decision file purpose was forward compliance
- Rule files (`.claude/rules/`) considered but user reports unreliable adherence — agents ignore injected directives to load files. Inline code comments at module level may be more reliable
- Symptom-oriented trigger phrasing confirmed as intent — drift toward root-cause phrasing happened during consolidation
- Learning headers in learnings.md should conform to memory-index trigger constraints at staging time (not `/when` format, but behavioral trigger framing) to prevent consolidation rephrasing
- Pipe-delimiter synonyms (`| extra triggers`) underused — cheapest intervention for trigger surface expansion
- Meta-index entries (5-6 entries about maintaining the index) should move to rules files and/or relevant skills/agents — noise in the index itself
- Reusable research should stay in-tree and be made discoverable (cross-references in decision files)
- `defense-in-depth.md` completely unindexed, `deliverable-review.md` has only 1 entry for multi-section file

**brainstorm-name agent created:**
- `agent-core/agents/brainstorm-name.md` — opus model, magenta, Read-only tools
- Generates 8-10 name candidates across verb/metaphor/compound/terse angles
- Symlinked via `just sync-to-parent` but not discovered on first restart — needs second restart

**Dropped tasks:**
- Learning ages computation after consolidation — working fine per user observation

## Continue in Next Session

**Test brainstorm-name agent** — verify discovery after restart, then test with remember skill rename:
- Remember skill name is misleading — skill consolidates/distills learnings OUT of context, not "remembering"
- Functional description for brainstorm: takes accumulated learnings, triages (superseded/redundant/documented?), routes survivors into permanent decision files, compresses/deduplicates, prunes from active context
- Constraints: slash command (`/name`), avoid collision with existing commands, invoked rarely

## Pending Tasks

- [ ] **Memory index actionability improvements** — Apply findings from opus review | sonnet
  - Report: `plans/reports/memory-index-actionability-review.md`
  - Symptom-oriented trigger rephrasing (~15 entries)
  - Add pipe-delimiter synonyms to entries with trigger surface gaps (~10 entries)
  - Deduplicate 3 redundancy pairs
  - Index defense-in-depth.md (3 entries) and expand deliverable-review.md coverage
  - Move meta-index entries to rules/skills (5-6 entries)
  - Frozen-domain passive recall mechanism — rule files unreliable, explore alternatives (code comments, hooks)
  - Enforce behavioral trigger framing at learning staging time (remember skill or hook)

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

**All tasks with documentation must have in-tree file references.**

**Rule file directive adherence unreliable:**
- Agents ignore injected "load X before modifying" directives
- Same failure mode as passive index (2.9% baseline recall)
- Blocking hooks or inline code comments may be more effective than suggestion-based rules

## Reference Files

- `plans/reports/memory-index-actionability-review.md` — Opus actionability review of all index entries
- `plans/when-recall/reports/corpus-analysis.md` — Index corpus analysis (entry patterns, compatibility)
- `plans/when-recall/reports/baseline-recall-analysis.md` — 2.9% baseline recall measurement
- `plans/when-recall/design.md` — When-recall system design
- `plans/workwoods/requirements.md` — Workwoods requirements (6 FRs, cross-tree awareness)
- `plans/pushback/requirements.md` — Pushback requirements (3 FRs, sycophancy prevention)
- `plans/process-review/rca.md` — Process RCA (5 plans examined, root cause in planning skill)
- `plans/reports/rca-*-opus.md` — 3 RCA reports (file growth, vet over-escalation, general-step detection)
- `plans/workflow-fixes/` — Unified runbook skill, plan-reviewer, pipeline-contracts (complete)
- `plans/worktree-update/` — Runbook + reports (complete, merged)
- `plans/when-recall/design.md` — Vetted design document
- `agents/decisions/deliverable-review.md` — Post-execution review methodology
- `plans/worktree-fixes/requirements.md` — Worktree fixes requirements (6 FRs)
