# Runbook Review: Session CLI Tool — Holistic Cross-Phase

**Artifact**: `plans/handoff-cli-tool/runbook-phase-{1-7}.md`
**Date**: 2026-03-07T00:00:00Z
**Mode**: review + fix-all (holistic scope)
**Phase types**: Mixed (1 general, 6 TDD)

## Summary

Complete 7-phase runbook for session CLI tool. Holistic review covers cross-phase dependency ordering, item numbering, file path validation, requirements coverage, and LLM failure modes. All per-phase reviews completed prior to this report.

**Overall Assessment**: Ready

## Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Cross-Phase Dependency Ordering

All phases sequence correctly:
- Phase 1 (general, foundation): no upstream dependencies
- Phase 2 (TDD): depends on Phase 1 package structure — correct
- Phase 3 (TDD): depends on Phase 2 SessionData — correct
- Phase 4 (TDD): depends on Phase 2 (session.md locator in Cycle 4.7) — correct
- Phase 5 (TDD): independent (commit parser + vet check) — no forward references
- Phase 6 (TDD): depends on Phase 5 (CommitInput, gate types) — correct
- Phase 7 (TDD): integration phase, depends on Phases 2-6 — correct

**Cycle 6.1 forward-reference note:** GREEN phase comments "validation level dispatch added in Cycle 6.4" and "option-gating added in Cycle 6.4". These are implementation annotations, not code dependencies. The RED/GREEN pair for 6.1 is self-contained; 6.4 extends it. No violation.

## Item Numbering

All phases use sequential numbering with no gaps or duplicates:
- Phase 1: Steps 1.1–1.3
- Phase 2: Cycles 2.1–2.2
- Phase 3: Cycles 3.1–3.4
- Phase 4: Cycles 4.1–4.7 (mid-phase checkpoint after 4.4)
- Phase 5: Cycles 5.1–5.3
- Phase 6: Cycles 6.1–6.6
- Phase 7: Cycles 7.1–7.4

## File Path Validation

All referenced source paths verified against filesystem:

| Path | Status |
|------|--------|
| `src/claudeutils/worktree/git_ops.py` | Exists ✓ |
| `src/claudeutils/cli.py` | Exists ✓ |
| `src/claudeutils/worktree/session.py` | Exists ✓ |
| `src/claudeutils/validation/task_parsing.py` | Exists ✓ |
| `src/claudeutils/exceptions.py` | Exists ✓ |
| New files (`session/`, `git.py`, `git_cli.py`, test files) | To-be-created ✓ |

**Line reference accuracy:**
- Step 1.1: `git_ops.py:9-23` → `_git()` at lines 9–23 ✓
- Step 1.1: `git_ops.py:78-112` → `_is_parent_dirty` at 78–97, `_is_submodule_dirty` at 100–112 ✓
- Step 1.2: `cli.py:145-152` → `cli.add_command(worktree)` at line 152 ✓
- Outline refs: `worktree/session.py` lines 120–150 (`find_section_bounds`), 225–245 (`_extract_plan_from_block`) ✓
- Outline refs: `validation/task_parsing.py` lines 30–42 (`ParsedTask` dataclass) ✓

**Referenced functions verified:**
- `find_section_bounds`, `extract_task_blocks`, `_extract_plan_from_block` — all present in `worktree/session.py` ✓
- `ParsedTask`, `parse_task_line`, `TASK_PATTERN` — all present in `validation/task_parsing.py` ✓

## Requirements Coverage

All 17 requirements from the outline requirements mapping are covered:

| Requirement | Phase/Cycle | Status |
|---|---|---|
| S-1: Package structure + CLI registration | Phase 1 / Step 1.2 | ✓ |
| S-2: `_git()` extraction + submodule discovery | Phase 1 / Step 1.1 | ✓ |
| S-3: Output/error conventions | Phase 1 / Step 1.1 | ✓ |
| S-4: Session.md parser | Phase 2 / Cycles 2.1–2.2 | ✓ |
| S-5: Git status/diff utility | Phase 1 / Step 1.3 | ✓ |
| H-1: Domain boundaries | Design constraint (no deliverable step) | ✓ |
| H-2: Committed detection | Phase 4 / Cycle 4.3 | ✓ |
| H-3: Diagnostics | Phase 4 / Cycle 4.6 | ✓ |
| H-4: State caching | Phase 4 / Cycle 4.4 | ✓ |
| C-1: Scripted vet check | Phase 5 / Cycle 5.3 | ✓ |
| C-2: Submodule coordination | Phase 6 / Cycle 6.2 | ✓ |
| C-3: Input validation | Phase 5 / Cycle 5.2 | ✓ |
| C-4: Validation levels | Phase 6 / Cycle 6.4 | ✓ |
| C-5: Amend semantics | Phase 6 / Cycle 6.3 | ✓ |
| ST-0: Worktree-destined tasks | Phase 3 / Cycle 3.1 | ✓ |
| ST-1: Parallel group detection | Phase 3 / Cycle 3.3 | ✓ |
| ST-2: Preconditions + degradation | Phase 2, 3 / Cycles 2.2, 3.4 | ✓ |
| Integration tests | Phase 7 / Cycles 7.1–7.4 | ✓ |

## LLM Failure Mode Analysis

**Vacuity:** No vacuous cycles detected. Each cycle adds a distinct behavioral constraint. The parametrized consolidations in Cycles 2.1 and 5.1 are per expansion guidance — identical-pattern sections merged into parametrized tests.

**Dependency ordering:** Foundation-first within all phases. Phase 7 integration cycles read existing Phase 3/4 source files as prerequisites — correct cross-phase reads of already-built artifacts.

**Density:** Cycles are appropriately sized. The consolidations (2.1 covering 5 section parsers, 5.1 covering 4 commit sections) follow outline expansion guidance and maintain behavioral isolation within each parametrized case.

**Checkpoint spacing:** No gap exceeds 7 cycles between checkpoints:
- Phase 4 has 7 cycles with a mid-phase checkpoint after Cycle 4.4
- All other phases have per-phase checkpoints
- Total phases: 7, all checkpointed

**File growth:** All files projected within bounds. `pipeline.py` in Phase 4 (~150–180 lines) and Phase 6 (~200–250 lines) are below the 350-line flag threshold.

**TDD RED/GREEN quality:** All RED phases have specific test names, file locations, expected failure messages, and behaviorally-specific assertions. No vague prose detected. GREEN phases describe behavior without prescribing implementation code.

## Fixes Applied

None — no issues found requiring fixes.

## Unfixable Issues (Escalation Required)

None — all checks pass.

---

**Ready for next step**: Yes
