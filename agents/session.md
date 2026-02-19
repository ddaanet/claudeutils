# Session Handoff: 2026-02-19

**Status:** Reorganized — archived 6 completed plans, batched overlapping tasks, top 10 prioritized, 30+ tasks moved to backlog.

## Completed This Session

**Plan archival:** Deleted 6 plan directories (completed or superseded):
- when-recall, worktree-merge-resilience, worktree-update, workwoods (fully executed)
- error-handling (inline execution superseded runbook)
- claude (empty placeholder)

**Task reorganization:**
- Batched 3 worktree rm fixes into single task
- Absorbed: Script commit vet gate → Commit CLI, Codebase quality sweep → Quality infrastructure, vet-invariant-scope + inline-phase-type → Pipeline skill updates, worktree-rm-safety → Worktree CLI default
- Dropped stale tasks: Design quality gates + Runbook quality gates Phase B (both fully executed — validate-runbook.py implemented with 17/17 tests)
- Moved 30+ tasks to `agents/backlog.md`

## Pending Tasks





- [ ] **PostToolUse auto-format hook** — PostToolUse hook on Write/Edit running formatter on changed file | sonnet | restart

- [ ] **Worktree CLI default** — Positional = task name, `--branch` = bare slug | `/runbook plans/worktree-cli-default/outline.md` | sonnet
  - Plan: worktree-cli-default | Status: designed
  - Absorbs: worktree-rm-safety (safety gates), Worktree Tasks section elimination

- [ ] **SessionStart status hook** — Bundled hook: dirty tree warning, learnings limit, stale worktree detection, model tier display, tip rotation | sonnet | restart


- [ ] **Pipeline skill updates** — `/design` | opus | restart
  - Orchestrate: `/deliverable-review` pending task at exit
  - Design skill: Phase 0 requirements-clarity gate
  - Absorbs: vet-invariant-scope, inline-phase-type

- [ ] **Quality infrastructure reform** — `/design plans/quality-infrastructure/requirements.md` | opus
  - Plan: quality-infrastructure | Status: requirements
  - 4 FRs: deslop restructuring, code density, vet rename, code refactoring
  - Absorbs: Codebase quality sweep, integration-first-tests

## Worktree Tasks

- [ ] **Precommit test sentinel** → `precommit-test-sentinel` — Sentinel file caches passing test suite; rerun only when python version, pyproject.toml, conftest.py, or src/ change | sonnet

- [ ] **Worktree rm fixes** → `worktree-rm-fixes` — Batch: (1) dirty check fails on parent instead of target worktree, (2) broken worktree from failed `new` (empty dir, exit 255), (3) `rm --confirm` skips submodule branch cleanup | sonnet

- [ ] **Handoff CLI tool** → `handoff-cli-tool` — Mechanical handoff+commit pipeline in CLI | `/design` | sonnet
  - Same pattern as worktree CLI: mechanical ops in CLI, judgment stays in agent
  - Inputs: status line, completed text, optional files, optional commit message with gitmoji
  - Outputs (conditional): learnings age status, precommit result, git status+diff, worktree ls
  - Cache on failure: inputs to state file, rerun without re-entering skill
  - Gitmoji: embeddings + cosine similarity over 78 pre-computed vectors

- [ ] **Commit CLI tool** → `commit-cli-tool` — CLI for precommit/stage/commit across both modules | `/design` | sonnet
  - Absorbs: Script commit vet gate (Gate B → scripted check)
  - Single command: precommit → gate → stage → commit in main + agent-core submodule

- [ ] **Orchestrate evolution** → `orchestrate-evolution` — `/runbook plans/orchestrate-evolution/design.md` | sonnet
  - Design complete, ready for runbook planning

## Blockers / Gotchas

**Never run `git merge` without sandbox bypass:**
- `git merge` without `dangerouslyDisableSandbox: true` partially checks out files, hits sandbox, leaves 80+ orphaned untracked files

**`_update_session_and_amend` exit 128 during rm:**
- `_worktree rm` calls `_update_session_and_amend` → exit 128. Workaround: manual amend before `rm --confirm`

**`slug` and `--task` mutually exclusive in `_worktree new`:**
- Fix: worktree-cli-default adds `--branch` flag

**Merge ours resolution loses worktree content:**
- `just wt-merge` uses `checkout --ours` for session.md, learnings.md — verify post-merge

**`wt rm` blocks on dirty parent repo:**
- Workaround: `git stash && wt rm && git stash pop`

**`wt rm` leaves stale submodule config:**
- `.git/modules/agent-core/config` `core.worktree` points to deleted directory

**Validator orphan entries not autofixable:**
- Marking headings structural (`.` prefix) causes non-autofixable error in `check_orphan_entries`

**Memory index `/how` operator mapping:**
- `/how X` → internally `"how to X"` — index keys must NOT include "to"

## Next Steps

Precommit test sentinel is next. Error-handling-design worktree ready to remove (`wt-rm error-handling-design`).

## Reference Files

- `agents/backlog.md` — 30+ deferred tasks with plan associations and groupings
- `plans/worktree-cli-default/outline.md` — CLI change design (positional=task, --branch=slug)
- `plans/quality-infrastructure/requirements.md` — 4 FRs: deslop, code density, vet rename, refactoring
- `plans/orchestrate-evolution/design.md` — Orchestration evolution design (ready for runbook)
