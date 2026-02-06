# Runbook Outline Review: Learnings Consolidation

**Artifact**: plans/learnings-consolidation/runbook-outline.md
**Design**: plans/learnings-consolidation/design.md
**Date**: 2026-02-06T18:45:00Z
**Mode**: review + fix-all

## Summary

Outline provides solid phase structure with appropriate complexity distribution and complete requirements coverage. All 12 requirements (FR-1–9, NFR-1–3) are traced to specific phases and steps. Phase boundaries are logical: script foundation → skill updates → agent definitions → testing. Cross-phase dependencies are clearly identified with opportunities for parallel work in Phase 3.

Issues identified were primarily in requirements mapping clarity, step elaboration depth, and dependency documentation. All issues have been fixed directly in the outline.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps | Coverage | Notes |
|-------------|-------|-------|----------|-------|
| FR-1 | 2 | 2.1 | Complete | Handoff step 4c with trigger evaluation |
| FR-2 | 1 | 1.1 | Complete | Script calculates git-active-day age |
| FR-3 | 2 | 2.1 | Complete | Trigger thresholds: 150 lines OR 14 days, 7 days freshness |
| FR-4 | 3 | 3.1 | Complete | Remember-task agent pre-check — supersession detection |
| FR-5 | 3 | 3.1 | Complete | Remember-task agent pre-check — contradiction detection |
| FR-6 | 3 | 3.1 | Complete | Remember-task agent pre-check — redundancy detection |
| FR-7 | 2 | 2.1 | Complete | Handoff refactor flow (detect → spawn → retry) |
| FR-8 | 3 | 3.1 | Complete | Remember-task agent embeds /remember protocol per D-4 |
| FR-9 | 2 | 2.2 | Complete | Remember skill quality criteria and staging retention |
| NFR-1 | 2 | 2.1 | Complete | Try/catch wrapper in handoff, log and continue on error |
| NFR-2 | 3 | 3.1, 3.2 | Complete | Both agents use model: sonnet in frontmatter |
| NFR-3 | 3 | 3.1 | Complete | Remember-task writes to tmp/consolidation-report.md |

**Coverage Assessment**: All requirements covered with explicit phase/step mappings and implementation notes.

## Phase Structure Analysis

### Phase Balance

| Phase | Steps | Complexity | Lines | Percentage | Assessment |
|-------|-------|------------|-------|------------|------------|
| 1 | 1 | Moderate | ~150 | 25% | Balanced — single focused script |
| 2 | 2 | Low-Moderate | ~50 | 8% | Balanced — surgical skill updates |
| 3 | 2 | Moderate-High | ~200 | 33% | Balanced — two agents with coordination |
| 4 | 2 | Moderate | ~200 | 33% | Balanced — testing matches implementation |

**Balance Assessment**: Well-balanced. Phases 3 and 4 are larger but appropriately scoped (two agents with pre-checks, comprehensive test coverage). Phase 2 is smallest but most delicate (skill modification requires precision). No phase exceeds 40% threshold.

### Complexity Distribution

- **Low complexity phases**: 0
- **Low-Moderate complexity phases**: 1 (Phase 2)
- **Moderate complexity phases**: 2 (Phases 1, 4)
- **Moderate-High complexity phases**: 1 (Phase 3)

**Distribution Assessment**: Appropriate escalation from script foundation → skill updates → agent definitions → testing. Complexity peaks in Phase 3 (protocol embedding, pre-checks) and Phase 4 (git mocking, integration validation), which aligns with architectural risk areas identified in design.

## Review Findings

### Critical Issues

None identified.

### Major Issues

**1. Requirements Mapping Table Incomplete**
- Location: Requirements Mapping section
- Problem: Original table lacked "Notes" column and used verbose descriptions instead of concise implementation references
- Fix: Restructured table to standard format (Requirement | Phase | Steps | Notes), added implementation details for each requirement, standardized FR-1–9 notation
- **Status**: FIXED

**2. Step 1.1 Lacked Implementation Detail**
- Location: Phase 1, Step 1.1
- Problem: Step listed tasks as bullets without design decision references, staleness algorithm unclear, error handling not specified
- Fix: Expanded step to include script location, shebang requirement, git blame flags (`-C -C` for renames/merges), active-day calculation algorithm, staleness detection via `git log -p`, fallback behavior, output format reference (D-2), error exit codes
- **Status**: FIXED

**3. Step 2.1 Missing Refactor Flow Detail**
- Location: Phase 2, Step 2.1
- Problem: "Handle file-limit escalations (refactor flow)" was one bullet, but design § D-6 describes multi-step process (detect → spawn memory-refactor → retry)
- Fix: Expanded step to include full refactor flow sub-steps: detect limit in report, spawn memory-refactor agent, re-invoke remember-task with only skipped entries
- **Status**: FIXED

**4. Phase 3 Steps Missing Agent Body Structure**
- Location: Phase 3, Steps 3.1 and 3.2
- Problem: Steps listed components but didn't structure agent body content (protocol extraction, pre-checks, reporting)
- Fix: Restructured both steps with clear body content structure: role statement, input spec, process/protocol, constraints, output/return protocol, design references (D-4, D-5, D-6)
- **Status**: FIXED

**5. Cross-Phase Dependencies Underspecified**
- Location: Cross-Phase Dependencies section
- Problem: Original stated "No parallelization opportunities" but Phase 3 steps 3.1 and 3.2 are actually independent (remember-task and memory-refactor agents)
- Fix: Added detailed dependency graph (Phase 2 → Phase 1, Phase 3 → Phase 2, etc.), identified parallelization opportunities (Phase 3 steps, Phase 4 early start), documented critical path
- **Status**: FIXED

### Minor Issues

**1. Step 2.2 Lacked Content Specificity**
- Location: Phase 2, Step 2.2
- Problem: "Add sections per design" without listing section content (principle-level, incident-specific, meta-learnings, etc.)
- Fix: Expanded step to list all section content: Learnings Quality Criteria (principle/incident/meta examples), Staging Retention Guidance (keep/consolidate/drop criteria)
- **Status**: FIXED

**2. Phase 4 Test Categories Not Enumerated**
- Location: Phase 4, Step 4.1
- Problem: "Mock git operations, test active-day calculation" was too high-level for test design
- Fix: Enumerated all test categories from design § Implementation Component 6: parsing, age calculation, staleness, trigger logic, freshness filter, error handling, with edge cases and boundary conditions
- **Status**: FIXED

**3. Success Criteria Too Generic**
- Location: Phase 1, Phase 2, Phase 3 success criteria
- Problem: Criteria like "script runs without errors" don't specify what constitutes success (format correctness, edge case handling)
- Fix: Added specific criteria: Phase 1 (format matches D-2 exactly, handles merge commits, edge cases), Phase 2 (thresholds match design values, existing behavior unchanged), Phase 3 (protocol embedding faithful, source comment present, quiet execution pattern)
- **Status**: FIXED

**4. Manual Testing Procedure Unspecified**
- Location: Phase 4, Step 4.2
- Problem: "Manually test handoff trigger" without procedure specification
- Fix: Added manual test options (Option A: >150 lines, Option B: >14 days staleness), verification checklist (filtered entry list, failure handling), agent validation checklist (protocol embedding, source comment, tools/model/color)
- **Status**: FIXED

**5. Missing Expansion Guidance Section**
- Location: End of outline
- Problem: No guidance for full runbook expansion phase (Phase 1.6 in plan-adhoc workflow)
- Fix: Added comprehensive Expansion Guidance section covering: required file loading, per-phase cycle guidance, checkpoint validation, consolidation candidates, reference inclusion
- **Status**: FIXED

## Fixes Applied

**Requirements Mapping section:**
- Restructured table to standard format (Requirement | Phase | Steps | Notes)
- Added implementation details for all 12 requirements
- Standardized requirement notation (FR-1–9, NFR-1–3)

**Phase 1 (Step 1.1):**
- Added script location and shebang requirement
- Specified git blame flags (`-C -C`) and why
- Detailed active-day calculation algorithm
- Detailed staleness detection via `git log -p` with fallback
- Added output format reference (D-2) and error exit codes
- Expanded success criteria with edge cases

**Phase 2 (Steps 2.1, 2.2):**
- Step 2.1: Expanded refactor flow to multi-step process (detect → spawn → retry)
- Step 2.1: Added try/catch wrapper detail with error handling
- Step 2.1: Specified allowed-tools update (Task, learning-ages.py)
- Step 2.2: Listed all section content for quality criteria and staging retention
- Expanded success criteria with threshold values and preservation requirements

**Phase 3 (Steps 3.1, 3.2):**
- Step 3.1: Structured agent body content (role, input, pre-checks, protocol, report, return)
- Step 3.1: Detailed pre-check algorithms (supersession, contradiction, redundancy)
- Step 3.1: Specified report format with all sections
- Step 3.2: Structured agent body content (role, input, process, constraints, output)
- Both steps: Added design decision references (D-4, D-5, D-6)

**Phase 4 (Steps 4.1, 4.2):**
- Step 4.1: Enumerated all test categories from design § Implementation Component 6
- Step 4.1: Added edge cases and boundary conditions for each category
- Step 4.2: Added manual test procedure options with verification checklists
- Step 4.2: Added agent definition validation checklist

**Cross-Phase Dependencies section:**
- Added detailed dependency graph with step-level references
- Identified parallelization opportunities (Phase 3 steps, Phase 4 early start)
- Documented critical path

**New section: Expansion Guidance:**
- Required file loading (skills and reference docs)
- Per-phase cycle guidance (4 phases)
- Checkpoint validation guidance (4 checkpoints)
- Consolidation candidates evaluation
- Reference inclusion reminders

## Design Alignment

**Architecture alignment:**
- Phase structure follows component dependencies: script → skill updates → agents → tests
- Data flow correctly sequenced: learning-ages.py provides data → handoff evaluates → agents execute
- Quiet execution pattern preserved (agents report to files, return filepaths)

**Design decision alignment:**
- D-1 (Step 4c insertion): Phase 2 Step 2.1 specifies insertion between 4b and 5
- D-2 (Markdown output): Phase 1 Step 1.1 references D-2 format
- D-3 (Trigger evaluation): Phase 2 Step 2.1 includes threshold values (150 lines, 14 days, 7 days, 3 minimum)
- D-4 (Embedded protocol): Phase 3 Step 3.1 specifies protocol embedding with source comment
- D-5 (Pre-consolidation checks): Phase 3 Step 3.1 details all three checks (supersession, contradiction, redundancy)
- D-6 (Reactive refactoring): Phase 2 Step 2.1 includes refactor flow (detect → spawn → retry)
- D-7 (Graceful failure): Phase 2 Step 2.1 specifies try/catch wrapper

**Implementation component alignment:**
- Component 1 (learning-ages.py): Phase 1 Step 1.1
- Component 2 (remember-task agent): Phase 3 Step 3.1
- Component 3 (memory-refactor agent): Phase 3 Step 3.2
- Component 4 (handoff skill): Phase 2 Step 2.1
- Component 5 (remember skill): Phase 2 Step 2.2
- Component 6 (tests): Phase 4 Steps 4.1, 4.2

All six implementation components mapped to phases/steps.

## Positive Observations

**Clear phase boundaries:**
- Phase 1 produces working script (testable independently)
- Phase 2 wires script into handoff (integrates foundation)
- Phase 3 creates agents (completes automation)
- Phase 4 validates (comprehensive coverage)

**Realistic complexity assessment:**
- Phase 1 "Moderate" reflects git operations complexity (staleness heuristic non-trivial)
- Phase 3 "Moderate-High" reflects protocol embedding + pre-checks + two agents
- Phase 4 "Moderate" reflects git mocking complexity balanced against test design clarity

**Good dependency documentation:**
- Critical path identified: Phase 1 → Phase 2.2 → Phase 3.1 → Phase 4.2
- Parallelization opportunities noted (Phase 3 steps, Phase 4 early start)
- No hidden dependencies or circular references

**Risk areas identified:**
- Protocol embedding drift (remember skill changes → agent out of sync)
- Staleness detection edge cases (no prior consolidation, file renames)
- Handoff skill insertion (preserve existing behavior)
- Mitigation strategies included for each

**Success metrics well-defined:**
- Per-phase completion criteria (testable, measurable)
- Overall success criteria (end-to-end workflow validation)

## Recommendations

**During Phase 1 expansion:**
- Consider extracting staleness detection to separate function (complexity warrants isolation)
- Include diagnostic logging for git operations (aid debugging in production)

**During Phase 2 expansion:**
- Document handoff step numbering preservation explicitly (4c insertion between 4b and 5)
- Include example error messages for consolidation failures (user-facing diagnostics)

**During Phase 3 expansion:**
- Cross-reference remember skill sections when embedding protocol (ensure fidelity)
- Include report format examples with sample content (clarity for future maintenance)

**During Phase 4 expansion:**
- Prioritize staleness detection tests (highest complexity, most edge cases)
- Consider adding smoke test for full workflow (basic happy path validation)

**Post-implementation:**
- Monitor protocol embedding drift (remember skill changes → agent synchronization)
- Add documentation cross-references (CLAUDE.md or memory-index.md entry for new workflow)

---

**Ready for full expansion**: Yes

All requirements traced, phases balanced, dependencies clear, complexity appropriately distributed. Outline provides sufficient detail for phase-by-phase expansion with comprehensive expansion guidance section.
