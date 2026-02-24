# Session Handoff: 2026-02-24

**Status:** Recall pass delivered. 3 worktrees merged. Merge context loss diagnosed — worktree merge diagnosis pending.

## Completed This Session

- Merged `worktree-rm-error-ux` — clean merge, precommit passed, rm succeeded
- Recall pass discussion — 4-pass model with reference forwarding, convergence via forwarding not repetition
  - Named "recall pass" — explicit step in pipeline where project memory is read, entries selected by name, results forwarded downstream
  - 4 passes: design recall (deep, whole decision files) → runbook recall (+impl +testing) → task agent injection (filtered) → review recall (+failure modes)
- Created `plans/recall-pass/brief.md` capturing discussion conclusions
- Grounded recall pass methodology — Moderate grounding quality
  - CE framework (Write/Select/Compress/Isolate) maps well; failure modes (distraction, clash, confusion, poisoning) independently confirmed
  - Agentic RAG paradigm deliberately inverted: prescriptive retrieval at fixed points, not adaptive agent-decided retrieval (justified by 2.9% measured adaptive recall)
  - Key project-specific insight: multiplicative token cost (artifact × agent count), mechanical filterability for haiku orchestrators, format-per-consumer-tier
  - Reports: `plans/reports/recall-pass-grounding.md`, `plans/reports/recall-pass-internal-brainstorm.md`
- Merged `update-grounding-skill` — scout-based diverge-converge pattern replacing general-purpose agents
- Merged `recall-pass-requirements` — requirements captured via Tier 2 delegation, recall skill added, 4 new learnings
  - New task: Consolidate recall tooling (rename when-resolve, phase out /when + /how)
  - Read tool context optimization test: no dedup confirmed (T1 protocol)
  - Sync-to-parent sandbox documentation updated
- Validated merge context — diagnosed 2 merges for session.md loss:
  - Merge 1 (`update-grounding-skill`, `f525d705`): Worktree Tasks entry dropped by autostrategy (focused session lacks main's WT section)
  - Merge 2 (`recall-pass-requirements`, `c91c7628`): orphaned Worktree Tasks entry, malformed blocker, completed tasks not in Completed section
  - Pre-merge state with both WT entries: `0c91d969`. Fixed all artifacts manually
  - Root cause: session.md autostrategy doesn't preserve main-only sections when branch has diverged focused session
- Recall pass marked delivered (full pipeline: brief → grounding → requirements → execution in worktree)

## Pending Tasks

- [ ] **Codebase sweep** — `/design plans/codebase-sweep/requirements.md` | sonnet
  - Plan: codebase-sweep | Status: requirements
  - _git_ok, _fail, exception cleanup — mechanical refactoring


- [ ] **Planstate delivered status** — `/runbook plans/planstate-delivered/outline.md` | sonnet
  - Plan: planstate-delivered | Status: designed
  - Grounded lifecycle: `requirements → designed → planned → ready → review-pending → [rework ↔ review-pending] → reviewed → delivered`
  - Single `lifecycle.md` per plan (append-only, last entry = status) replaces 4 marker files
  - 3 phases: core inference (TDD), merge integration (TDD), skill/prose updates (general)

- [ ] **Orchestrate evolution** — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete with Phase 1 (foundation) + Phase 2 (ping-pong TDD), ready for runbook planning
  - Insights input: ping-pong TDD agent pattern — alternating tester/implementer agents with mechanical RED/GREEN gates between handoffs. Tester holds spec context (can't mirror code structure), implementer holds codebase context (can't over-implement beyond test demands). Resume-based context preservation avoids startup cost per cycle
  - Absorbs: Task agent guardrails — tool-call limits, regression detection, model escalation (haiku→sonnet→opus on capability mismatch) all additive. Design covers agent→user escalation and context-size heuristic but not inter-tier promotion or tool-call budgets
  - Absorbs: RED pass protocol — classification taxonomy, blast radius procedure, defect impact evaluation. Design has remediation + escalation patterns but not formal classification or blast radius assessment

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


- [x] **Recall pass** — delivered (brief → grounding → requirements → design → runbook → execution → review)
  - Plan: recall-pass

- [ ] **Consolidate recall tooling** — rename `when-resolve.py` → `claudeutils _recall`, remove `..file` syntax; phase out `/when` and `/how` as separate skills, ensure `/recall` covers reactive single-entry lookups; memory-index entry format changes from `/when`+`/how` prefixes → new format; update `src/claudeutils/validation/memory_index_checks.py` and `when` module accordingly | sonnet

- [ ] **Worktree merge session loss diagnosis** — RCA why `_worktree merge` autostrategy drops session.md context | sonnet
  - Root cause: focused session.md in branch lacks main's Worktree Tasks, autostrategy favors branch version
  - Observed: Merge 1 (`f525d705`) dropped WT entry, Merge 2 (`c91c7628`) left orphan + malformed blocker. Pre-merge: `0c91d969`
  - Fix target: `src/claudeutils/worktree/merge.py` session autostrategy
  - Related: planstate-delivered (plan: planstate-delivered) would prevent "completed but no record" class
## Worktree Tasks


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

Worktree merge session loss diagnosis, then planstate-delivered or codebase sweep.

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