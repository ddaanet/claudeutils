# Session: Worktree — Worktree merge resilience

**Status:** Runbook reviewed and patched. Ready for orchestration with opus. Restart required.

## Completed This Session

**Prior session (committed):**
- Designed, created runbook (13 steps, 5 phases), all phases reviewed, prepare-runbook.py generated artifacts

**This session — runbook review and fixes:**
- Reviewed all 13 steps following layered context model (baseline → common context → step content)
- Found 2 major issues, 3 minor (advisory):
  - Major: step-5-1 metadata said haiku, should be sonnet (code audit); step-5-3 said haiku, should be opus (prose artifact). Root cause: prepare-runbook.py defaults all step metadata to baseline model, ignores per-step `**Execution Model:**` in phase files
  - Major: Cycle 2.1 test setup step 7 said `exit code == 3` contradicting assertions section (should be `in (0, 3)`). Holistic review fixed assertions but missed setup section — incomplete fix pattern
  - Minor/advisory: Cycles 1.2 and 1.5 may be complex for haiku (state machine routing), mitigated by TDD + opus orchestration
- Applied 3 direct fixes: step-5-1 (haiku→sonnet), step-5-3 (haiku→opus), step-2-1 (assertion alignment)
- Added Model Directives section to orchestrator-plan.md — differential review models by correctness property

**Discussion — model selection for review/refactor agents:**
- Opus orchestration = quality floor for orchestrator judgment, not blanket model upgrade
- Match review model to correctness property, not author's model: state machine routing (Phase 1) → opus vet; behavioral changes (Phases 2-4) → sonnet vet; prose artifact (Step 5.3) → opus vet
- Refactor stays sonnet — haiku code quality decisions don't need opus
- Pipeline evolution direction: model guidance should flow design → runbook → execution, with directional refinement (upgrade ok, downgrade needs justification)

## Pending Tasks

- [ ] **Orchestrate worktree merge resilience** — `/orchestrate worktree-merge-resilience` | opus | restart
  - Plan: worktree-merge-resilience | Status: planned
  - Orchestrate with opus for orchestrator judgment quality; step execution stays haiku per step metadata
  - Model Directives in orchestrator-plan.md: opus vet for Phase 1 + Step 5.3, sonnet vet for rest, sonnet refactor
  - State machine (Phase 1) is the foundation — all later phases depend on it
  - Run haiku steps in background, monitor for subagent looping (scope creep, test count inflation)
  - Validate state machine code post-Cycle 1.2 (5-branch routing dispatch, largest haiku scope)
- [ ] **Fix prepare-runbook.py model override** — Script defaults all step metadata to baseline `haiku`, ignoring per-step `**Execution Model:**` in phase file content. Parse and propagate.
- [ ] **Design model directive pipeline** — Model guidance flows design → runbook → execution. Add review/refactor model fields to runbook format, design stage outputs model recommendations per phase, runbook refines. Directional constraint: runbook can upgrade but not downgrade design recommendations without justification. | opus
  - Touches: design skill, outline format, runbook skill, prepare-runbook.py, orchestrate skill, plan-reviewer
  - Prerequisite: fix prepare-runbook.py model override (execution model propagation is foundation)
- [ ] **Fix plan-reviewer model adequacy gap** — Reviewer doesn't assess per-cycle model adequacy when no explicit model tagged. Add criterion: flag cycles where complexity exceeds default model capability. Currently only checks explicitly tagged steps. | opus

## Blockers / Gotchas

- **Never run `git merge` without sandbox bypass** — partial checkout + sandbox failure leaves orphaned files
- **Existing tests assert abort behavior** — Cycles 3.1 and 3.2 update `test_merge_conflict_surfaces_git_error` and `test_merge_aborts_cleanly_when_untracked_file_blocks` in RED phase (assert new behavior, fail with old code)
- **merge.py growth**: projected ~387 lines after Phase 4. If >350 after Phase 3 GREEN, extract `_format_conflict_report` + state detection into `merge_state.py` before Phase 4.
- **Cycle 1.5 sabotage protocol**: RED requires sabotaging `_detect_merge_state` to return `"merged"` always, confirm failure, then revert before GREEN.
- **validate-runbook.py absent** — Phase 3.5 skipped (graceful degradation per skill spec)
- **Holistic review incomplete fix pattern**: fixed Cycle 2.1 assertion (exit code) but missed matching reference in test setup section of same step. When fixing values in reviewed artifacts, grep for all references within the artifact.

## Reference Files

- `plans/worktree-merge-resilience/outline.md` — design (8 decisions)
- `plans/worktree-merge-resilience/runbook-outline.md` — reviewed outline (12 items)
- `plans/worktree-merge-resilience/orchestrator-plan.md` — orchestration plan
- `plans/worktree-merge-resilience/steps/` — 13 step/cycle files
- `plans/worktree-merge-resilience/reports/` — all review reports (phases 1-5, holistic)

## Next Steps

Restart session with opus model. Run `/orchestrate worktree-merge-resilience`.
