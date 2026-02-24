# Session Handoff: 2026-02-24

**Status:** Validated merge integrity, 4 worktrees created, task-lifecycle designed and executed (planstate-derived commands + STATUS continuation).

## Completed This Session

- Prioritization report — 37 tasks scored via WSJF, report at `plans/reports/prioritization-2026-02-24.md`
  - Top 5: orchestrate evolution (5.3), session CLI tool (4.0, blocked), planstate delivered (3.8), session.md validator (2.6), WT merge session loss dx (2.6)
- Discussion: test sentinel versioning (rejected — local cache, not versionable)
- Merged `orchestrate-evolution` (×2) — 1st: recall skill tweak. 2nd: runbook planning (11 commits, design amendments + 4-phase runbook + execution artifacts)
- Merged `sentinel-copy` — `_worktree new` copies `tmp/.test-sentinel` to new worktrees
- Merged `planstate-delivered` — lifecycle implementation (TDD), deliverable review (0 Critical, 2 Major fixed), new bug tasks spawned
  - New tasks: execute orchestrate-evolution, fix prepare-runbook.py bugs, fix validate-runbook.py false positives, deliverable review auto-commit, fix when-resolve.py heading lookup
- Created `wt-merge-dirty-tree` worktree — bug: merge blocks on dirty worktree (should only check main)
- Post-merge validation: 4 merges checked, artifacts cleaned each time. Autostrategy still unreliable for session.md
- Designed recall tool anchoring (`plans/recall-tool-anchoring/`)
  - Gate inventory: 31 gates across 13 files, 61% prose-only (report: `plans/recall-tool-anchoring/reports/recall-gate-inventory.md`)
  - Outline through 3 discussion rounds: D+B hybrid application, reference manifest format, throwaway prototype
  - Key decisions: reference manifest forces tool-anchoring structurally (format requires resolution call); `_recall diff` anchors write-side gates; `_recall generate` deferred (entry selection is cognitive)
  - Recall artifact written with 11 entries from 6 decision files
- Merged `wt-merge-dirty-tree` — dirty-tree guard fix on main, worktree removed
- Designed task-classification (`plans/task-classification/`)
  - Feature 1: `/prime` skill — loads plan artifacts + chain-calls `/recall` for ad-hoc plan work outside workflow skills
  - Feature 2: Two-section task list — "In-tree Tasks" + "Worktree Tasks" (static planning signal, no move semantics)
  - Design evolution: @ref preload → SessionStart hook → scripted gate → all dropped → explicit `/prime` skill invocation
  - Key insight: @ref expansion and Read calls are cumulative (not deduplicated) — drove decision away from implicit injection
  - Outline reviewed by corrector: 0 critical, 3 major fixed, 3 minor fixed
- Validated merge integrity — wt-merge-dirty-tree (`50e37ede`) and planstate-delivered (`8a97fb71`), no session detail or learning loss
  - planstate-delivered merge: 5 `[from:]` artifacts appended to Blockers (cleaned in subsequent handoff `b571df3c`)
- Created 4 worktrees: recall-tool-anchoring, wt-merge-session-loss, when-resolve-fix, prepare-runbook-fixes
- Designed and executed task-lifecycle (`plans/task-lifecycle/`)
  - D: stale task commands in session.md after `/design` and `/runbook` advance plan
  - D: STATUS missing session-level continuation after direct skill execution
  - Three changes: (1) STATUS derives commands from planstate via CLI, (2) handoff carry-forward derives commands from `_NEXT_ACTION_TEMPLATES` mapping, (3) STATUS shows session continuation when tree dirty
  - Files: `execute-rule.md`, `handoff/SKILL.md`
  - Skill-reviewer caught 2 bugs: `designed` → wrong file (`outline.md` not `design.md`), `planned` → missing `agent-core/bin/` prefix. Fixed.

## Pending Tasks

- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring
- [ ] **Deslop remaining skills** — Prose quality pass on skills not yet optimized | sonnet

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
  - Blocked on: recall-tool-anchoring prototype
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

## Worktree Tasks


- [ ] **Recall tool anchoring** → `recall-tool-anchoring` — `/design plans/recall-tool-anchoring/outline.md` | sonnet
  - Plan: recall-tool-anchoring | Status: designed (outline reviewed, ready for prototype)
  - Throwaway prototype: 3 shell scripts (check, resolve, diff) + D+B restructure of 8 skills/agents + PreToolUse hook
  - Reference manifest format: thin trigger list replaces content dump in recall-artifact.md

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**Merge resolution produces orphaned lines in append-only files:**
- When branch modifies existing entry in-place AND both sides add at tail, git appends modified line as duplicate.
- Manual post-merge check required until worktree-merge-resilience automated

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping:**
- `/how X` → internally `"how to X"` — index keys must NOT include "to"

**Learnings consolidated — 28 lines, 5 entries:**
- Next consolidation when entries age past 7 active days or file approaches 80-line soft limit.

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

## Next Steps

4 worktrees active (recall-tool-anchoring, wt-merge-session-loss, when-resolve-fix, prepare-runbook-fixes). Next: execute in worktrees, or task-classification runbook, or execute orchestrate-evolution on main.

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