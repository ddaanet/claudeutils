# Runbook Outline Review: Worktree Skill

**Artifact**: plans/worktree-skill/runbook-outline.md
**Design**: plans/worktree-skill/design.md
**Date**: 2026-02-10T18:45:00Z
**Mode**: review + fix-all

## Summary

The runbook outline provides comprehensive TDD cycle structure for the worktree skill implementation. Coverage is complete across all 8 functional requirements and 5 non-functional requirements. Phase structure is well-balanced with logical grouping and appropriate complexity ratings. The outline demonstrates strong TDD discipline with clear RED/GREEN sequencing.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1 | 0-2 | 0.2, 1.1, 1.6, 2.1, 2.6 | Complete | All 6 subcommands mapped (fixed cycle references) |
| FR-2 | 4 | 4.1-4.5 | Complete | Submodule merge resolution with ancestry checks |
| FR-3 | 3 | 3.1-3.2 | Complete | Session conflict with task extraction |
| FR-4 | 5 | 5.1-5.3 | Complete | Source conflicts with precommit gate |
| FR-5 | 6 | 6.1-6.4 | Complete | SKILL.md three modes |
| FR-6 | 7 | 7.2 | Complete | execute-rule.md Mode 5 update (fixed) |
| FR-7 | 7 | 7.4 | Complete | Justfile recipe deletion (fixed) |
| FR-8 | All | Throughout | Complete | E2E test strategy integrated |
| NFR-1 | 4 | 4.9 | Complete | Idempotent merge (fixed cycle ref) |
| NFR-2 | 3 | 3.1-3.4 | Complete | Deterministic session resolution |
| NFR-3 | 2, 4 | 2.5, 4.1-4.5 | Complete | Direct git plumbing |
| NFR-4 | 4, 5 | 4.8, 5.2 | Complete | Mandatory precommit gate |
| NFR-5 | 0 | 0.1-0.3 | Complete | CLI follows claudeutils patterns |

**Coverage Assessment**: All requirements covered with explicit cycle mappings.

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles | Complexity | Percentage | Assessment |
|-------|--------|------------|------------|------------|
| 0 | 3 | Low | 7% | Appropriate foundation |
| 1 | 6 | Low-Medium | 14% | Balanced |
| 2 | 7 | Medium | 16% | Balanced |
| 3 | 4 | Medium | 9% | Balanced |
| 4 | 10 | High | 23% | Appropriate for merge complexity |
| 5 | 3 | Medium | 7% | Balanced |
| 6 | 5 | Medium-High | 12% | Balanced |
| 7 | 4 | Low | 9% | Balanced |

**Total cycles**: 42

**Balance Assessment**: Well-balanced. Phase 4 (merge orchestration) is largest at 23% but justified by high complexity of 3-phase merge flow with idempotency requirements. No phase exceeds 40% threshold.

### Complexity Distribution

- **Low complexity phases**: 2 (Phases 0, 7)
- **Medium complexity phases**: 4 (Phases 1, 2, 3, 5)
- **High complexity phases**: 1 (Phase 4)
- **Medium-High complexity phases**: 1 (Phase 6)

**Distribution Assessment**: Appropriate. High complexity concentrated in Phase 4 (merge orchestration) which has detailed checkpoint requirements. SKILL.md authoring (Phase 6) correctly rated Medium-High for opus workflow artifact.

## Review Findings

### Critical Issues

None found. All critical requirements have explicit mappings and appropriate cycle structure.

### Major Issues

1. **Requirements mapping table had incorrect cycle references**
   - Location: Requirements Mapping table, lines 7-19
   - Problem: FR-1 said "0.1-2.6" but add-commit is cycle 1.6 (not in Phase 2); FR-6 said 7.1 but should be 7.2; FR-7 said 7.2 but should be 7.4; NFR-1 said "4.6-4.7" but is cycle 4.9
   - Fix: Updated FR-1 to list specific subcommand cycles (0.2, 1.1, 1.6, 2.1, 2.6), FR-6 → 7.2, FR-7 → 7.4, NFR-1 → 4.9
   - **Status**: FIXED

2. **Parallel group annotations misleading**
   - Location: Phase metadata (Phases 0-2 marked "Parallel group: A")
   - Problem: Phases 0-2 are sequential within CLI implementation (foundation → subcommands → lifecycle), not parallel to each other
   - Fix: Removed "Parallel group: A" annotations from Phases 0-2, updated Phase 3 to "Parallel: Can run parallel to Phases 0-2", clarified parallel execution notes
   - **Status**: FIXED

### Minor Issues

1. **Cycle 0.1 RED phase lacked specificity**
   - Location: Phase 0, Cycle 0.1
   - Problem: "Test that import succeeds" doesn't specify what to assert before package exists
   - Fix: Changed to "Test import raises ImportError (package doesn't exist). GREEN: Create __init__.py (empty) and empty cli.py"
   - **Status**: FIXED

2. **Cycle 4.8 RED phase lacked failure behavior**
   - Location: Phase 4, Cycle 4.8
   - Problem: "Test merge runs precommit" doesn't specify expected behavior on failure
   - Fix: Added "and exits 1 on precommit failure without rolling back merge" to RED phase
   - **Status**: FIXED

3. **Consolidation analysis lacked detail**
   - Location: Consolidation Opportunities section, line 321
   - Problem: Listed patterns but didn't explain why no consolidation recommended
   - Fix: Added clarifications: Phase 1.3-1.5 tests distinct cases, Phase 2.1-2.4 is sequential build-up, Phase 3 functions are independent
   - **Status**: FIXED

4. **Parallel execution notes used outdated "Groups A and B" terminology**
   - Location: Parallel Execution Notes section
   - Problem: Referred to "Parallel group A" and "Parallel group B" after removing those annotations
   - Fix: Reworded to "Phase 3 can run parallel to Phases 0-2" with clarification that 0-2 are sequential within their group
   - **Status**: FIXED

## Fixes Applied

- **Requirements Mapping table** — corrected cycle references for FR-1, FR-6, FR-7, NFR-1
- **Phase 0 metadata** — removed "Parallel group: A" annotation
- **Phase 1 metadata** — removed "Parallel group: A" annotation
- **Phase 2 metadata** — removed "Parallel group: A" annotation
- **Phase 3 metadata** — changed "Parallel group: B" to descriptive parallel note
- **Cycle 0.1 RED phase** — added ImportError assertion before package creation
- **Cycle 4.8 RED phase** — specified exit 1 on precommit failure without rollback
- **Consolidation analysis** — added rationale for why pattern cycles don't need consolidation
- **Parallel Execution Notes** — clarified sequential vs parallel phase relationships
- **Expansion Guidance section** — appended comprehensive guidance for runbook expansion (consolidation, cycle details, checkpoints, test fixtures, git plumbing, critical assertions)

## Design Alignment

The outline follows design decisions and architecture specifications:

- **Architecture**: Package structure (worktree/__init__.py, cli.py, merge.py, conflicts.py) matches design exactly
- **Module structure**: 7 phases align with functional grouping in design (foundation → subcommands → lifecycle → conflicts → merge → skill → integration)
- **Key decisions**:
  - D-1 (wt/<slug>/ directory): Referenced in Phase 2
  - D-3 (--no-commit --no-ff): Phase 4 cycles 4.6-4.7
  - D-4 (precommit oracle): Phase 4 cycle 4.8, Phase 5 cycle 5.2
  - D-5 (CLI vs skill boundary): Phases 0-5 (CLI), Phase 6 (skill)
  - D-6 (extract before resolve): Phase 3 cycle 3.1
  - D-7 (submodule before parent): Phase 4 structure
  - D-8 (idempotent merge): Phase 4 cycle 4.9
  - D-10 (add-commit idempotent): Phase 1 cycle 1.6

## Positive Observations

**Strong TDD discipline:**
- All cycles have explicit RED/GREEN sequencing
- RED phases specify behavioral assertions (not just "write a test")
- GREEN phases describe approach/behavior (not prescriptive code)

**Excellent cycle scoping:**
- Each cycle has clear, bounded objective
- Complexity increases incrementally within phases
- Critical scenarios from design (12 scenarios, line 443) all mapped to specific cycles

**Comprehensive expansion guidance:**
- Gotchas section covers 6 critical implementation challenges
- Phase-specific notes provide actionable context
- Test fixture strategy clearly specified
- Git plumbing patterns documented with references

**Well-structured checkpoints:**
- Phase 4 (merge) correctly marked "full checkpoint" for high complexity
- Phase 6 (SKILL.md) correctly specifies design-vet-agent for opus workflow artifact
- Light checkpoints appropriate for other phases

**File size awareness:**
- Expected sizes documented (cli.py ~300-400 lines, merge.py ~250-350 lines)
- Split triggers defined (>400 lines)
- No files expected to exceed limits

## Recommendations

**For full runbook expansion:**

1. **Phase 2 cycle 2.5 (--session pre-commit)**: This is the most complex single cycle. Ensure runbook expansion includes detailed git plumbing steps with temp index pattern verification.

2. **Phase 4 checkpoint**: After completing Phase 4, run full checkpoint with vet-fix-agent. Include execution context specifying 3-phase merge flow and idempotency requirements.

3. **Phase 6 model assignment**: SKILL.md authoring requires opus (workflow artifact). Ensure orchestration routes this phase to opus execution.

4. **Test fixture creation**: Build shared fixtures (`base_repo`, `base_submodule`, `repo_with_submodule`) early in Phase 0 or 1. All subsequent phases depend on this test infrastructure.

5. **Integration test priority**: The 12 critical scenarios (design line 443) should be implemented first within each phase. Edge cases can follow after critical paths validated.

6. **Expansion guidance integration**: The appended Expansion Guidance section should be referenced during Phase 1.6 (runbook expansion step) to ensure recommendations are incorporated.

---

**Ready for full expansion**: Yes

All requirements traced, phases balanced, complexity distribution appropriate, TDD discipline strong, and all issues fixed. The outline provides clear structure for full runbook expansion.
