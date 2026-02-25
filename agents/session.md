# Session Handoff: 2026-02-25

**Status:** Skills quality pass complete: 28 skills edited, 3 agents fixed, 15 reference files created, ~2,600 lines compressed. 7 convergence review majors fixed and committed.

## Completed This Session

- **Skills quality pass execution** — lightweight orchestration from outline, 4 parallel opus agents
  - Phase 1: 3 agent D+B gates (corrector gate 10, design-corrector gate 11, runbook-outline-corrector gate 9) + restart
  - Phases 2-5: 4 background opus agents dispatched in parallel (disjoint file sets)
  - Phase 2 (Agent A): commit, handoff, codify — 5 D+B gates added, FR-1/2/8/9 applied, 21 control flow paths verified
  - Phase 3 (Agent B): design, runbook, token-efficient-bash, orchestrate, review — 1,499 lines removed (50%), 15 reference files created, 4 D+B gates in design skill
  - Phase 4 (Agent C): review-plan, reflect, plugin-dev-validation, shelve, requirements — 572 lines removed, 5 reference files, gate 6 added to requirements
  - Phase 5 (Agent D): 15 light-touch skills — FR-1/2/6/8/9 per variation table, error-handling reduced to redirect stub
  - Pre-resolved recall dump (`plans/skills-quality-pass/reports/resolved-recall.md`) — shared file eliminated redundant when-resolve.py calls across agents
- **Convergence review** — 5 parallel opus agents (4 skill reviewers + 1 behavior invariance)
  - R1 (Phase 2): 0 critical, 2 major — handoff Gate 5 Bash anchor missing, orphaned consolidation-flow.md
  - R2 (Phase 3): 0 critical, 2 major — orchestrate and review description NFR-6 violations
  - R3 (Phase 4): 0 critical, 1 major — reflect 2 references lack in-body load points
  - R4 (Phase 5): 0 critical, 2 major — how/when retained preambles (design scope gap), prioritize list_plans()
  - BI (behavior invariance): 0 broken paths across 50 paths in 6 conditional-branch skills
- Codify learnings worktree spawned → `codify-learnings`
- **Skills quality pass convergence fixes** — 7 majors from review reports applied
  - handoff: Gate 5 Bash anchor (`claudeutils _worktree ls`), orphaned `consolidation-flow.md` deleted
  - orchestrate/review: description rewritten to NFR-6 format
  - reflect: in-body load points added for `rca-design-decisions.md` and `rca-examples.md`
  - how/when: "When to Use"/"When NOT to Use" preambles folded into description
  - prioritize: `list_plans()` replaced with CLI wrapper

## Pending Tasks

- [x] **Fix when-resolve double-to and cross-operator** — 4 bugs fixed via TDD | sonnet
- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring
- [x] **Skills quality pass fixes** — 7 major fixes applied from convergence review | sonnet
  - Plan: skills-quality-pass | Status: designed
  - Reports: `plans/skills-quality-pass/reports/review-r{1-4}-phase{2-5}.md`, `behavior-invariance-review.md`

- [ ] **Diagnose compression detail loss** — RCA against commit `0418cedb` | sonnet
- [ ] **Precommit python3 redirect** — `/design plans/precommit-python3-redirect/brief.md` | sonnet
  - PreToolUse hook: intercept python3/uv-run/ln patterns, redirect to correct invocations

- [ ] **Worktree merge from main** — `/design plans/worktree-merge-from-main/` | sonnet
- [ ] **Cross-tree requirements transport** — `/requirements` skill writes to main from worktree | sonnet
  - Transport solved: `git show <branch>:<path>` from main (no sandbox needed)
  - Remaining: requirements skill path flag/auto-detection, optional CLI subcommand (`_worktree import`)
  - Absorbs: Revert cross-tree sandbox access (remove `additionalDirectories` from `_worktree new`)
- [ ] **Handoff wt awareness** — Only consolidate memory in main repo | sonnet
- [ ] **Parallel orchestration** — Parallel dispatch via worktree isolation | sonnet
  - Plan: parallel-orchestration | Blocked on: orchestrate-evolution
- [ ] **Model directive pipeline** — Model guidance design → runbook → execution | opus
- [ ] **Merge learnings delta** — Reconcile learnings.md after diverged merge | sonnet
  - Plan: merge-learnings-delta | Strategy: main base + branch delta
- [ ] **Continuation prepend** — `/design plans/continuation-prepend/problem.md` | sonnet
- [ ] **Execute plugin migration** — Refresh outline then orchestrate | opus
  - Plan: plugin-migration | Status: ready (stale — Feb 9)
  - Recovery: design.md architecture valid, outline Phases 0-3/5-6 recoverable, Phase 4 needs rewrite
- [ ] **Migrate test suite to diamond** — Needs scoping | depends on runbook evolution (delivered)
- [ ] **Test diagnostic helper** — Replace subprocess.run check=True with stderr surfacing | sonnet
- [ ] **Session.md validator** — Scripted precommit check | sonnet
  - Plan: session-validator | worktree-cli-default merged; all FRs can proceed
- [ ] **Agent rule injection** — Distill sub-agent rules into agent templates | sonnet
- [ ] **Handoff insertion policy** — Insert at priority position instead of append | sonnet
- [ ] **Behavioral design** — Nuanced conversational pattern intervention | opus
- [ ] **Diagnostic opus review** — Post-vet RCA methodology | opus
- [ ] **Safety review expansion** — Pipeline changes from grounding research | opus
  - Depends on: Explore Anthropic plugins
- [ ] **Ground state-machine review criteria** — State coverage validation research | opus
- [ ] **Workflow formal analysis** — Formal verification of agent workflow | opus
- [ ] **Design-to-deliverable** — tmux-like session automation | opus | restart
- [ ] **Feature prototypes** — Markdown preprocessor, session extraction, last-output | sonnet
- [ ] **Cache expiration prototype** — Debug log token metrics, measure TTL | sonnet
- [ ] **Explore Anthropic plugins** — Install all 28 official plugins | sonnet | restart
- [ ] **Tweakcc** — Remove redundant builtin prompts, inject custom | sonnet
  - Plan: tweakcc
- [ ] **TDD cycle test optimization** — Selective test rerun via dependency analysis | sonnet
- [ ] **Fix task-context.sh task list bloat** — Filter/trim output | sonnet
- [ ] **Upstream skills field** — PR/issue for missing skills frontmatter | sonnet
- [ ] **Infrastructure scripts** — History tooling + agent-core script rewrites | sonnet
- [!] **Session CLI tool** — `/runbook plans/handoff-cli-tool/outline.md` | sonnet
  - Plan: handoff-cli-tool | Status: designed (outline reviewed 6 rounds, ready for runbook)
  - `_session` group (handoff, status, commit)
  - Discussion conclusions baked into outline: amend, git passthrough, deviation-only output, submodule labeling
- [ ] **UserPromptSubmit topic detection hook** — Phase 7 analysis recommends this as highest-impact recall improvement | sonnet
  - Seed keyword table from 200+ memory-index triggers
  - Inject matching decision content via additionalContext on prompt submit
  - Complementary to recall pass (cheap first layer vs deep pipeline integration)
- [ ] **Prioritize script assistance** — Automate mechanical parts of prioritization scoring | sonnet

- [ ] **Task classification** — `/runbook plans/task-classification/outline.md` | sonnet
  - Plan: task-classification | Status: designed (outline reviewed, ready for runbook)
  - `/prime` skill (ad-hoc plan context) + two-section task list (In-tree / Worktree Tasks)
  - Scope: `session.py`, `resolve.py`, `aggregation.py`, `session_structure.py`, handoff skill, execute-rule.md
- [ ] **Recall CLI integration** — Production `claudeutils _recall` CLI (check/resolve/diff), Click, TDD | sonnet
  - Prototype delivered via recall-tool-anchoring worktree
- [ ] **Prose gate anchoring terminology** — Find proper name for D+B pattern, ground, update docs | opus

- [ ] **Consolidate recall tooling** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet

- [ ] **Execute orchestrate-evolution** — `/orchestrate orchestrate-evolution` | sonnet | restart
  - 14 steps: 12 TDD cycles (sonnet) + 2 general steps (opus)
  - Phase 1: agent caching model (4 cycles)
  - Phase 2: orchestrator plan format + verify-step.sh (4 cycles)
  - Phase 3: TDD agent generation + verify-red.sh (4 cycles)
  - Phase 4: SKILL.md rewrite + refactor.md/delegation.md updates (2 steps, opus)
  - Checkpoints: light at phase boundaries, full at Phase 4 (final)
- [ ] **Fix validate-runbook.py false positives** — sonnet
  - model-tags: bash scripts under `agent-core/skills/` falsely flagged as prose artifacts
  - lifecycle: pre-existing files flagged as "modified before creation"

- [ ] **Deliverable review auto-commit** — after fixing all issues in deliverable-review, auto handoff and commit | sonnet
- [ ] **Worktree new fuzzy matching** — `_worktree new` accepts approximate task names instead of exact match | sonnet

- [ ] **Design skill stale recall artifact format** — diagnose /design producing old-style recall artifact instead of memory key list | sonnet

- [ ] **Skill progressive disclosure** — `/design plans/skill-progressive-disclosure/brief.md` | opus
  - Plan: skill-progressive-disclosure | Status: requirements
  - Segment loading at gate boundaries: initial load → write-outline → write-design (/design); tier assessment → tier3-planning → expansion (/runbook)
  - Complementary with skills-quality-pass FR-3 extractions

- [ ] **Runbook outline review loop** — update runbook skill: user review gate after outline correction, iterative fix cycle until approved | sonnet
- [ ] **Runbook recall expansion** — `/design plans/runbook-recall-expansion/requirements.md` | sonnet
  - Plan: runbook-recall-expansion | Status: requirements
  - prepare-runbook.py recall injection, corrector.md self-loading, two-pattern docs (7 FRs)
- [ ] **Recall pipeline improvements** — `d:` when-resolve.py stdin/recall-artifact support, session log dedup | opus
  - Accept recall keys on stdin (ignore post-"|" memory-index format), change recall-artifact format (dash separator unsafe)
  - Session log scraping to auto-eliminate already-recalled entries
- [ ] **Recall learnings integration** — `d:` whether learnings.md entries should be resolvable via when-resolve.py | opus
  - Implies memory-index format changes (new source type), resolver changes — genuine design uncertainty

- [x] **Codify learnings** — `/codify` | opus
  - Consolidated 14 entries (89→32 lines) into 9 decision files
  - Split workflow-optimization.md → workflow-execution.md (exceeded 400-line limit)
  - 14 memory-index entries added, all resolve correctly
  - 5 entries kept in staging (0-day)
- [ ] **Generate memory index from decisions** — `/design` | opus
  - Each decision/learning declares keywords for index. Index generated from declarations. Diff displayed after update for agent review. Supersedes manual append workflow in `/codify` step 4a.

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**Merge resolution produces orphaned lines in append-only files:**
- When branch modifies existing entry in-place AND both sides add at tail, git appends modified line as duplicate.
- Manual post-merge check required until worktree-merge-resilience automated

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping (resolved):**
- Operator prefix no longer used in matching — bare trigger matching handles both `/when` and `/how` entries
- `removeprefix("to ")` in resolver strips leftover "to" from "how to X" invocations

**Learnings consolidated — 40 lines, 7 entries:**
- `/codify` completed. 14 entries consolidated into decision files. 5 recent entries retained.

**SessionStart hook #10373 still open:**
- Output discarded for new interactive sessions. Stop hook fallback deployed (Phase 4).

**`_worktree new` requires sandbox bypass:**
- Writes `.claude/settings.local.json` which is in sandbox deny list. Must use `dangerouslyDisableSandbox: true`.

**Custom agents not discoverable as subagent_types:**
- `.claude/agents/*.md` files with proper frontmatter weren't available via Task tool. Built-in types work. May need platform investigation.

**`_worktree rm --force` doesn't restore task to Pending:**
- `rm --force` removes worktree but leaves task in Worktree Tasks section. Manual session.md edit needed to move back to Pending.

**`_worktree rm` fails on merge commits:**
- `_update_session_and_amend` calls `git commit --amend` which fails on merge commits (exit 128). Then `--force` can fail on submodule removal. Manual `rm -rf` of directory needed after.

**Orphaned remember-skill-update directory:**
- `/Users/david/code/claudeutils-wt/remember-skill-update` — git deregistered but directory remains. Needs manual removal.

**Worktree merge drops session.md Worktree Tasks entries:**
- Focused session in branch lacks main's full Worktree Tasks section. Autostrategy resolves in favor of branch, dropping main-only entries. Manual post-merge validation required until merge.py fixed.

**`just sync-to-parent` requires sandbox bypass:**
- Recipe removes and recreates symlinks in `.claude/` — sandbox blocks `rm` on those paths

**Possible Claude Code skill caching:**
- On-disk skills current, but `/design` and `/reflect` invocations received older content. No structural fix — awareness only.

## Next Steps

Skills quality pass delivered. Codify learnings in parallel worktree (88/80 lines).

## Reference Files

- `plans/recall-pass/brief.md` — 4-pass model, reference forwarding, discussion conclusions
- `plans/reports/recall-pass-grounding.md` — Moderate grounding (CE + Agentic RAG synthesis)
- `plans/reports/recall-pass-internal-brainstorm.md` — 27 dimensions, project-specific constraints
- `plans/planstate-delivered/outline.md` — Plan lifecycle design (7 decisions, 3 phases)
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
- `plans/handoff-cli-tool/outline.md` — Session CLI combined outline (reviewed 6 rounds)
- `plans/worktree-merge-resilience/diagnostic.md` — Merge artifact reproduction conditions
- `plans/codebase-sweep/requirements.md` — mechanical refactoring (_git_ok, _fail, exceptions)
- `agents/decisions/cli.md` — LLM-native output decision (from session-cli-tool)
- `plans/reports/prioritization-2026-02-24.md` — WSJF scoring, 37 tasks ranked
- `plans/recall-tool-anchoring/outline.md` — Recall gate tool-anchoring design (D+B + reference manifest)
- `plans/recall-tool-anchoring/recall-artifact.md` — 11 entries, reference manifest format
- `plans/recall-tool-anchoring/reports/recall-gate-inventory.md` — 31 gates inventoried across 13 files
- `plans/task-classification/outline.md` — `/prime` skill + two-section task list design (8 rounds, reviewed)
- `plans/task-classification/reports/outline-review.md` — Corrector review (0 critical, 3 major fixed)
- `plans/task-lifecycle/outline.md` — Planstate-derived commands + STATUS continuation design
- `plans/when-resolve-fix/diagnostic-double-to.md` — Double-to + cross-operator bugs, TDD plan, code paths
- `plans/when-resolve-fix/reports/corrector-review.md` — Corrector review of 4-bug fix (0 critical, 0 major)
- `plans/skills-quality-pass/design.md` — Skills quality pass design (3 workstreams, 10 FRs, 7 NFRs)
- `plans/skills-quality-pass/recall-artifact.md` — 10 resolution keys (corrected from inline summaries)
- `plans/skills-quality-pass/runbook-outline.md` — 5 phases, 16 steps, parallel 4-agent execution model
- `plans/skills-quality-pass/reports/runbook-outline-review.md` — Corrector review (0 critical, 3 major fixed)
- `plans/runbook-recall-expansion/requirements.md` — Step agent + corrector recall during full orchestration (7 FRs)
- `plans/skills-quality-pass/reports/skill-inventory.md` — Sonnet scout v2: 30 skills, content segmentation, compression opportunities
- `plans/skills-quality-pass/reports/full-gate-audit.md` — Sonnet scout: 12 prose-only gates, fix directions
- `plans/reports/skill-optimization-grounding.md` — Segment→Attribute→Compress framework (LLMLingua/ProCut)
- `plans/skill-progressive-disclosure/brief.md` — Segment loading at gate boundaries (/design and /runbook)
- `plans/skills-quality-pass/reports/phase-{2-5}-report.md` — Execution agent reports (changes, NFR verification, line counts)
- `plans/skills-quality-pass/reports/review-r{1-4}-phase{2-5}.md` — Convergence skill reviews (4 reviewers)
- `plans/skills-quality-pass/reports/behavior-invariance-review.md` — 50-path independent verification (0 issues)
- `plans/skills-quality-pass/reports/resolved-recall.md` — Pre-resolved recall dump for shared agent consumption