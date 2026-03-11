# Simplification Report

**Outline:** plans/handoff-cli-tool/runbook-outline.md
**Date:** 2026-03-07

## Summary

- Items before: 38
- Items after: 29
- Consolidated: 9 items across 4 patterns

## Consolidations Applied

### 1. Git module helpers (Phase 1, Steps 1.1 + 1.2)
- **Type:** same-module
- **Items merged:** Step 1.1 (extract `_git()`, `_is_submodule_dirty()`, add `discover_submodules()`) + Step 1.2 (add `_git_ok()`, `_fail()`)
- **Result:** Step 1.1 — all `claudeutils/git.py` functions in single step
- **Rationale:** Both create independent functions in `claudeutils/git.py`. No inter-dependency. Combined step still has manageable scope (5 functions, import updates, unit tests).

### 2. Session.md section parsers (Phase 2, Cycles 2.1-2.4)
- **Type:** identical-pattern + sequential-addition
- **Items merged:** Cycle 2.1 (status line), 2.2 (completed section), 2.3 (pending tasks), 2.4 (worktree tasks)
- **Result:** Cycle 2.1 — parametrized section parser with 4 section types
- **Rationale:** Each cycle parses one section of session.md into a field of SessionData. Same pattern: locate section bounds, extract content, parse into typed field. Outline itself flags 2.3/2.4 as "likely parametrizable." All four share the same test structure (fixture session.md -> parsed section). Combined: 4 parametrized test cases (one per section type) plus edge cases (missing section, old format).

### 3. Status render sections (Phase 3, Cycles 3.2-3.4)
- **Type:** identical-pattern
- **Items merged:** Cycle 3.2 (Pending section), 3.3 (Worktree section), 3.4 (Unscheduled Plans section)
- **Result:** Cycle 3.2 — render all list sections with parametrized tests
- **Rationale:** Each renders a section from SessionData into STATUS markdown. Same pattern: iterate items, format with metadata, join. Three parametrized test cases cover all sections. Combined step stays under 8 assertions (3 sections x 2 assertions each: content correctness + empty-section omission).

### 4. Commit stdin section parsers (Phase 5, Cycles 5.1-5.4)
- **Type:** identical-pattern
- **Items merged:** Cycle 5.1 (Files), 5.2 (Options), 5.3 (Submodule), 5.4 (Message)
- **Result:** Cycle 5.1 — commit markdown parser with parametrized section tests
- **Rationale:** Each cycle parses one `## Section` from the same stdin markdown format. Same test pattern: input markdown -> parsed section data. Four parametrized test cases plus edge cases (unknown options -> exit 2, blockquote handling). Outline's commit parser is a single `parse.py` module — splitting into 4 cycles inflates expansion without design benefit.

## Patterns Not Consolidated

- **Cycles 3.5 (parallel detection) + 3.6 (CLI wiring):** Outline flags 3.6 as potential inline with 3.5, but 3.6 has explicit dependency annotation ("Depends on: Phase 2, Phase 1") and is integration glue with different test characteristics (CliRunner vs unit). Left separate.
- **Cycles 4.1-4.7 (handoff pipeline):** Sequential pipeline steps with genuine inter-dependencies (4.4 state caching depends on 4.2-4.3 mutations; 4.5 precommit depends on 4.3 writes). Different dependency chains prevent consolidation.
- **Cycles 6.1-6.6 (commit pipeline):** Sequential pipeline with inter-dependencies (6.2 submodule depends on 6.1 parent-only; 6.3 amend depends on both). Different dependency chains.
- **Cycles 7.1-7.4 (integration tests):** Each tests a different subcommand with different fixtures. Could batch 7.1-7.3 as independent, but each requires distinct git repo setup and the phase has only 4 items.

## Requirements Mapping

Updated mappings for consolidated items:

| Requirement | Phase | Steps/Cycles | Notes |
|---|---|---|---|
| S-1: Package structure + CLI registration | 1 | 1.2 | `_session` group + `_git` group in main cli.py |
| S-2: `_git()` extraction + submodule discovery | 1 | 1.1 | Move from worktree/git_ops.py, add discover_submodules() |
| S-3: Output/error conventions | 1, all | 1.1 | `_fail()` + `_git_ok()` — conventions applied cross-cutting |
| S-4: Session.md parser | 2 | 2.1-2.2 | Extends existing worktree/session.py + validation/task_parsing.py |
| S-5: Git status/diff utility | 1 | 1.3 | `_git` CLI group with status/diff subcommands |
| H-1: Domain boundaries | 4 | -- | Design constraint, not a deliverable step |
| H-2: Committed detection | 4 | 4.3 | Diff-based three-mode write |
| H-3: Diagnostics | 4 | 4.6 | Conditional: precommit, git status/diff, learnings age |
| H-4: State caching | 4 | 4.4 | tmp/.handoff-state.json with step_reached resume |
| C-1: Scripted vet check | 5 | 5.3 | pyproject.toml patterns, report freshness |
| C-2: Submodule coordination | 6 | 6.2 | Per-submodule partition + commit + stage pointer |
| C-3: Input validation | 5 | 5.2 | Clean-files check with STOP directive |
| C-4: Validation levels | 6 | 6.4 | Orthogonal: just-lint, no-vet, amend |
| C-5: Amend semantics | 6 | 6.3 | HEAD file check + submodule amend propagation |
| ST-0: Worktree-destined tasks | 3 | 3.1 | Skip markers in Next selection |
| ST-1: Parallel group detection | 3 | 3.3 | Largest independent group only |
| ST-2: Preconditions + degradation | 2, 3 | 2.2, 3.4 | Missing session.md -> exit 2; old format -> defaults |
| Integration tests | 7 | 7.1-7.4 | E2E with real git repos via tmp_path |
