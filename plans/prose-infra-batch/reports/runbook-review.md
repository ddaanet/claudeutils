# Runbook Review: Prose Infrastructure Batch

**Artifact**: `plans/prose-infra-batch/runbook.md`
**Date**: 2026-03-11T00:00:00Z
**Mode**: review + fix-all
**Phase types**: Mixed (1 inline, 1 TDD)

## Summary

The runbook covers a two-phase batch: Phase 1 deletes and edits agentic prose (5 inline steps), Phase 2 builds a TDD validator (6 cycles). Phase 1 inline steps are well-specified and actionable. Phase 2 TDD cycles have correct RED/GREEN discipline overall, but Cycle 2.1 contained a visible self-correction fragment that was never cleaned up, and all 6 Verify RED lines used specific `tests/validation/` paths that (a) violate the over-specific path rule and (b) reference the wrong directory — validation tests live in `tests/` root as `test_validation_*.py`, not `tests/validation/`.

**Overall Assessment**: Ready (all issues fixed)

## Findings

### Critical Issues

1. **Wrong test directory in all Verify RED / Verify GREEN paths**
   - Location: Cycles 2.1–2.6, all `**Verify RED:**` lines
   - Problem: All six cycles reference `tests/validation/test_task_plans.py`. This path does not exist and will not be created — the project's validation test convention is `tests/test_validation_*.py` (confirmed by 21 existing `tests/test_validation_*.py` files). An executor following the runbook would write the test file to the wrong location or find the pytest path fails.
   - Fix: Changed all `pytest tests/validation/test_task_plans.py::...` to `just test tests/test_validation_task_plans.py` (project recipe, correct path, no over-specific function selector)
   - **Status**: FIXED

### Major Issues

2. **Cycle 2.1 RED phase contains unrevised self-correction prose**
   - Location: Cycle 2.1, RED Phase, lines 106–114
   - Problem: The phase opened with a first test name (`test_valid_plan_reference_passes`), then mid-paragraph concluded "Actually this passes with stub. Need a second task..." and introduced a revised test (`test_valid_plan_passes_invalid_fails`). The original test block was never removed — the phase contained both an abandoned design note and the revised spec. This is an incomplete edit that left reasoning artifacts in executor-facing content.
   - Fix: Removed the original `test_valid_plan_reference_passes` block and the "Actually this passes..." reasoning paragraph. The phase now opens directly with `test_valid_plan_passes_invalid_fails` and its assertions.
   - **Status**: FIXED

### Minor Issues

3. **Over-specific Verify RED paths (rule 3.5)**
   - Location: Cycles 2.1–2.6, all `**Verify RED:**` lines
   - Problem: Lines used `pytest tests/validation/test_task_plans.py::test_<specific_function> -v`. Specific function selectors accumulate staleness when tests are renamed or refactored. Covered by the critical fix above (wrong path), but the selector specificity itself is also a violation.
   - Fix: Resolved as part of the critical fix — all replaced with `just test tests/test_validation_task_plans.py`
   - **Status**: FIXED

### Informational

4. **Outline review report absent**
   - `plans/prose-infra-batch/reports/runbook-outline-review.md` does not exist
   - The outline itself is well-formed and requirements coverage is complete (all 5 FRs from requirements.md traced: FR-1 → Step 1.1, FR-2 → Step 1.2, FR-3 → Step 1.3, FR-4a → Step 1.4 + 1.5, FR-4b → Phase 2 cycles 2.1–2.6)
   - No action required on the runbook

## Scope Completeness Check

| Requirement | Coverage |
|-------------|----------|
| FR-1 (remove opus-design-question) | Step 1.1 — delete directory + grep all references |
| FR-2 (magic-query skill) | Step 1.2 — create skill, bin script, settings.json, sync |
| FR-3 (handoff merge-incremental) | Step 1.3 — git-dirty detection replacement |
| FR-4a (rule fragment) | Step 1.4 — execute-rule.md addition |
| FR-4a addendum (normalize bare /design) | Step 1.5 — session.md normalization |
| FR-4b (validator + tests + CLI) | Cycles 2.1–2.6 — task_plans.py + CLI wiring |

All FRs covered.

## Fixes Applied

- Cycle 2.1, RED Phase — removed abandoned `test_valid_plan_reference_passes` block and "Actually this passes with stub" reasoning paragraph; phase now opens directly with revised `test_valid_plan_passes_invalid_fails` spec
- Cycle 2.1, `**Verify RED:**` — `pytest tests/validation/test_task_plans.py::test_valid_plan_passes_invalid_fails -v` → `just test tests/test_validation_task_plans.py`
- Cycle 2.2, `**Verify RED:**` — `pytest tests/validation/test_task_plans.py::test_missing_plan_directory -v` → `just test tests/test_validation_task_plans.py`
- Cycle 2.3, `**Verify RED:**` — `pytest tests/validation/test_task_plans.py::test_empty_plan_directory -v` → `just test tests/test_validation_task_plans.py`
- Cycle 2.4, `**Verify RED:**` — `pytest tests/validation/test_task_plans.py::test_terminal_tasks_exempt -v` → `just test tests/test_validation_task_plans.py`
- Cycle 2.5, `**Verify RED:**` — `pytest tests/validation/test_task_plans.py::test_slug_only_command -v` → `just test tests/test_validation_task_plans.py`
- Cycle 2.6, `**Verify RED:**` — `pytest tests/validation/test_task_plans.py::test_cli_task_plans_command -v` → `just test tests/test_validation_task_plans.py`

## Unfixable Issues (Escalation Required)

None — all issues fixed.

---

**Ready for next step**: Yes
