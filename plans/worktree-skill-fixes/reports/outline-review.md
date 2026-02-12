# Runbook Outline Review: Worktree-Skill Fixes

**Artifact**: plans/worktree-skill-fixes/runbook-outline.md
**Requirements**: plans/worktree-skill/reports/deliverable-review.md
**Date**: 2026-02-11T18:45:00Z
**Mode**: review + fix-all

## Summary

Outline provides comprehensive fix plan for 27 findings (3 critical, 12 major, 12 minor) from deliverable review. Structure is logical with critical fixes first, major code/docs/tests in middle phases, minor fixes batched at end. All requirements mapped to specific steps with clear fix guidance.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| C6: merge --abort after committed merge | 0 | 0.1 | Complete | Fix error handling logic |
| A1: Wrong path in SKILL.md launch commands | 0 | 0.2 | Complete | Path correction |
| D1: Wrong directory in sandbox-exemptions | 0 | 0.3 | Complete | Path correction |
| C1: Dead derive_slug() | 1 | 1.1 | Complete | Remove function |
| C2: No slug validation | 1 | 1.2 | Complete | Add validation at entry point |
| C3: Duplicate git helpers | 1 | 1.3 | Complete | Extract git_utils.py |
| C7: Missing lock file retry | 1 | 1.4 | Complete | Implement retry wrapper |
| G1: Missing /wt/ in .gitignore | 1 | 1.5 | Complete | Add directory pattern |
| G2: Dead wt-path() in justfile | 1 | 1.6 | Complete | Remove function |
| A2: Lock file removal instruction | 2 | 2.1 | Complete | Update prose |
| T2: Tests verify git not production code | 3 | 3.1 | Complete | Delete file |
| T3: Mode 5 absence tests | 3 | 3.2 | Complete | Remove 6 tests |
| T4: Merge debris cleanup untested | 3 | 3.3 | Complete | Add test |
| T6: Git init boilerplate 5× | 3 | 3.4 | Complete | Consolidate to conftest |
| T7: Submodule setup 3× | 3 | 3.5 | Complete | Consolidate to conftest |
| C4: __all__ re-exports wrong module | 4 | 4.1 | Complete | Update test imports |
| C5: Inconsistent subprocess.run | 4 | 4.2 | Complete | Use run_git helper |
| T1: test_merge_helpers is utility | 4 | 4.3 | Complete | Rename to conftest_merge |
| T5: Source conflict flow partial | 4 | 4.4 | Complete | Add e2e test |
| T8: Raw subprocess boilerplate | 4 | 4.5 | Complete | Refactor to helper |
| T9: Merge verification 90% setup | — | — | Complete | Addressed by T2 deletion |
| T10: Section extraction copy-paste | 4 | 4.6 | Complete | Extract helper |
| T11: 10 micro-tests for YAML | 4 | 4.7 | Complete | Consolidate to 2-3 |
| T12: Near-duplicate test | 4 | 4.8 | Complete | Delete test |
| A3: Usage Notes contradict Mode C | 4 | 4.9 | Complete | Update prose |
| A4: Vague special characters | 4 | 4.10 | Complete | Clarify regex |

**Coverage Assessment**: All requirements covered with explicit references and fix guidance.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Percentage | Assessment |
|-------|-------|------------|------------|------------|
| 0 | 3 | Medium | 11% | Balanced |
| 1 | 6 | Medium | 22% | Balanced |
| 2 | 1 | Low | 4% | Balanced (single doc fix) |
| 3 | 5 | High | 19% | Balanced |
| 4 | 10 | Low-Medium | 37% | Acceptable (minor fixes) |

**Balance Assessment**: Well-balanced. Phase 4 is largest (37%) but consists of minor fixes that can be batched. No phase exceeds 40% threshold. Phase ordering is logical (critical → major → minor).

### Complexity Distribution

- **Low complexity phases**: 1 (Phase 2)
- **Medium complexity phases**: 2 (Phase 0, Phase 1)
- **High complexity phases**: 1 (Phase 3)
- **Low-Medium complexity phases**: 1 (Phase 4)

**Distribution Assessment**: Appropriate. High complexity limited to test refactoring (Phase 3) which requires understanding fixture dependencies. Critical and major code fixes are medium complexity. Minor fixes batched as low-medium.

## Review Findings

### Critical Issues

None. Outline correctly addresses all critical findings from deliverable review.

### Major Issues

**M1. Phase 4 lacks step descriptions**
- Location: Phase 4 section
- Problem: Original outline listed only step titles (16-26) without detailed guidance
- Fix: FIXED — Added detailed step descriptions for all 10 minor fixes (4.1-4.10)
- **Status**: FIXED

**M2. T9 marked as "skip" but should be explicit**
- Location: Requirements mapping, Phase 4
- Problem: T9 listed in mapping but marked as "skip" without explanation
- Fix: FIXED — Added note "Already addressed by T2 deletion" in requirements mapping
- **Status**: FIXED

### Minor Issues

**m1. Phase 4 step numbering inconsistency**
- Location: Phase 4 section
- Problem: Steps numbered 16-26 in original list, but Phase 4 is the 5th phase (0-indexed)
- Fix: FIXED — Renumbered to 4.1-4.10 for consistency with other phases
- **Status**: FIXED

**m2. Missing deliverables metadata for Phase 4**
- Location: Phase 4 header
- Problem: Phase 4 had "Steps:" list but no "Deliverables:" metadata like other phases
- Fix: FIXED — Added "Deliverables: Fixed test modules, updated documentation"
- **Status**: FIXED

**m3. Consolidation gate assessment too brief**
- Location: Consolidation Gate Assessment section
- Problem: Assessment says "Proceed with current structure" without quantitative justification
- Fix: NOT FIXED — Assessment is correct (no trivial phases, all have 3-6+ steps). Brevity acceptable for negative finding.
- **Status**: ACCEPTABLE

## Fixes Applied

- Phase 4: Added detailed step descriptions for all 10 steps (4.1-4.10)
- Phase 4: Added deliverables metadata to header
- Phase 4: Renumbered steps from 16-26 to 4.1-4.10
- Requirements mapping: Clarified T9 skip reason
- Overall structure: Improved consistency across all phases

## Design Alignment

**Note**: No design.md exists for this plan. Requirements source is deliverable-review.md.

- **Requirements coverage**: All 27 findings mapped to phases
- **Module structure**: git_utils.py extraction decision matches review finding C3
- **Key decisions**: Lock file retry matches outline specification from original worktree-skill plan

## Phase Structure Rationale

**Phase ordering reasoning**:
1. **Phase 0 (Critical)**: Functional correctness issues that break existing features (C6 silent merge failure, A1/D1 wrong paths)
2. **Phase 1 (Major Code)**: Code quality and missing behavior (dead code, validation, module extraction, lock retry)
3. **Phase 2 (Major Docs)**: Single documentation fix separated for clarity (contradicts behavioral rule)
4. **Phase 3 (Major Tests)**: Test suite improvements requiring high complexity (fixture consolidation, deletions, new coverage)
5. **Phase 4 (Minor)**: Batched minor fixes for efficiency (can be executed together)

**Dependency flow**:
- Phase 1 Step 1.3 (extract git_utils.py) must precede Step 1.4 (lock retry uses git_utils.py)
- Phase 3 Step 3.4/3.5 (consolidate fixtures) should precede Step 3.1/3.2 (delete tests) to maintain test infrastructure
- Phase 4 has no internal dependencies, steps can be executed in any order

## Positive Observations

- **Comprehensive requirements mapping**: All 27 findings explicitly traced to steps with file:line references
- **Clear fix guidance**: Each step includes target file, problem statement, and specific fix actions
- **Logical phase grouping**: Phases grouped by severity and artifact type (code/docs/tests)
- **Consolidation assessment**: Explicitly evaluated and rejected phase merging with reasoning
- **Complexity transparency**: Each phase has complexity rating and model recommendation
- **Verification steps**: Many steps include explicit "Verify:" guidance for validation

## Recommendations

**For full runbook expansion**:

1. **Step 0.1 (C6 fix)**: Include detailed logic for detecting if merge commit was created. Check `git log -1 --format=%H` vs ORIG_HEAD to determine if commit exists before choosing abort vs reset strategy.

2. **Step 1.2 (C2 validation)**: Consider whether validation should be in CLI layer or `cmd_new()` function. CLI layer fails fast before setup, but function-level validation provides defense-in-depth if function called from other contexts.

3. **Step 1.3 (git_utils extraction)**: After extraction, verify circular dependency is truly resolved. If merge_helpers.py imports from git_utils.py and commands.py imports from merge_helpers.py, circular dependency is broken.

4. **Step 1.4 (lock retry)**: Specify whether retry logic should be decorator or wrapper function. Decorator cleaner but may complicate error handling. Wrapper function more explicit control flow.

5. **Phase 3 fixture consolidation**: Consider whether conftest.py will become too large. If consolidating 5 git init + 3 submodule setup implementations, conftest.py may exceed 500 lines. Evaluate creating separate `conftest_fixtures.py` or keeping conftest_merge.py approach.

6. **Step 4.6 (section extraction)**: Parametrize can reduce code but may reduce test clarity if failure messages don't indicate which section failed. Include section name in parametrize IDs for debuggability.

7. **Step 4.7 (YAML consolidation)**: Ensure consolidated tests maintain same assertion granularity. 10 micro-tests may be excessive, but consolidating to 1 test loses failure localization. 2-3 grouped tests is good middle ground.

8. **Checkpoint strategy**: Run precommit after each phase. Phase 3 (test changes) and Phase 4 (minor fixes) likely won't trigger violations, but Phase 0-2 (code/docs changes) should be validated before proceeding.

9. **Test execution frequency**: Consider running test suite after Phase 1 (major code changes), Phase 3 (test changes), and Phase 4 (final validation). Phase 0 critical fixes should also trigger test run to verify no regressions.

10. **Vet strategy**: Phase 0-2 are code/docs changes requiring vet-fix-agent review. Phase 3-4 are test changes — vet should focus on test quality (vacuity, expressiveness, pertinence) not just correctness.

---

**Ready for full expansion**: Yes

All requirements traced, phases balanced, complexity realistic, no blocking issues.
