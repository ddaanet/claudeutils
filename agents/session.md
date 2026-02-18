# Session: Worktree — Worktree merge resilience

**Status:** All 4 Majors fixed. 71/71 tests pass. Ready for `wt merge`.

## Completed This Session

**Execute fix plan (4 Majors) — diamond TDD:**
- Fix #4 (resolve.py): removed `err=True` from two `click.echo` calls in `resolve_session_md` fallback — diagnostics now go to stdout
- Fix #2 (merge.py): precommit stdout forwarded before stderr echo (was silently dropped at line 313)
- Fix #1 (merge.py): `_auto_resolve_known_conflicts` helper extracted from `_phase3_merge_parent`; `parent_conflicts` branch now calls it; all-auto-resolved case falls through to Phase 4 instead of always exiting 3
- Fix #3 (merge.py): after Phase 4 commit + precommit pass, detects orphaned `agent-core` MERGE_HEAD → exits 3 with message
- 5 RED tests (incl. edge case for Fix #1 all-auto-resolved path) → all GREEN after fixes
- Existing `in (0, 3)` assertions tightened to `== 3` across routing + submodule tests
- Test files split to stay under 400-line limit: `test_worktree_merge_parent_conflicts.py`, `test_worktree_merge_submodule_lifecycle.py`
- Vet: no UNFIXABLE — `plans/worktree-merge-resilience/reports/vet-fix-majors.md`

**Prior sessions (committed):**
- Fix plan design, deliverable review, vet invariant scope design, orchestration (23 commits, b69ff220..3c063383)

## Pending Tasks

- [ ] **Merge worktree** — `wt merge` to merge worktree-merge-resilience back to main
  - Also import `plans/vet-invariant-scope/design.md` to main after merge
- [ ] **Fix prepare-runbook.py model override** — Script defaults all step metadata to baseline `haiku`, ignoring per-step `**Execution Model:**` in phase file content. Parse and propagate.
- [ ] **Design model directive pipeline** — Model guidance flows design → runbook → execution. Add review/refactor model fields to runbook format, design stage outputs model recommendations per phase, runbook refines. Directional constraint: runbook can upgrade but not downgrade design recommendations without justification. | opus
  - Touches: design skill, outline format, runbook skill, prepare-runbook.py, orchestrate skill, plan-reviewer
  - Prerequisite: fix prepare-runbook.py model override (execution model propagation is foundation)
- [ ] **Fix plan-reviewer model adequacy gap** — Reviewer doesn't assess per-cycle model adequacy when no explicit model tagged. Add criterion: flag cycles where complexity exceeds default model capability. Currently only checks explicitly tagged steps. | opus

## Blockers / Gotchas

- **Never run `git merge` without sandbox bypass** — partial checkout + sandbox failure leaves orphaned files
- **Learnings at 199 lines** — well over 80-line soft limit, but no entries old enough (≥7 active days) for consolidation batch. Will resolve as entries age.

## Reference Files

- `plans/worktree-merge-resilience/fix-plan.md` — diamond TDD fix plan (4 Majors batched)
- `plans/worktree-merge-resilience/reports/vet-fix-majors.md` — vet report for this session's fixes
- `plans/worktree-merge-resilience/reports/deliverable-review.md` — original review (4 Major, 12 Minor)
- `plans/vet-invariant-scope/design.md` — process improvement design (for import to main)
- `src/claudeutils/worktree/merge.py` — main merge logic (fixes #1, #2, #3)
- `src/claudeutils/worktree/resolve.py` — conflict resolution (fix #4)

## Next Steps

`wt merge` to merge worktree-merge-resilience into main, then import `plans/vet-invariant-scope/design.md`.
