# Deliverable Review: runbook-quality-gates

**Date:** 2026-02-18
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

**Phase B deliverables (this branch):**

| Type | File | Lines |
|------|------|-------|
| Code | `agent-core/bin/validate-runbook.py` | 352 |
| Test | `tests/test_validate_runbook.py` | 377 |
| Test | `tests/test_validate_runbook_integration.py` | 145 |
| Test (fixture) | `tests/fixtures/validate_runbook_fixtures.py` | 342 |
| **Total** | | **1216** |

**Phase A deliverables (merged to main prior to this branch):**

| Type | File | Status |
|------|------|--------|
| Agentic prose | `agent-core/agents/runbook-simplification-agent.md` | Verified present |
| Agentic prose | `agent-core/skills/runbook/SKILL.md` (Phase 0.86 + 3.5) | Verified present |
| Agentic prose | `agent-core/skills/review-plan/SKILL.md` (Section 12) | Verified present |
| Agentic prose | `agent-core/agents/plan-reviewer.md` (model assignment) | Verified present |
| Human docs | `agents/decisions/pipeline-contracts.md` (T2.5, T4.5) | Verified present |
| Human docs | `agents/memory-index.md` (2 entries) | Verified present |

**Execution artifacts (not reviewed):** 19 reports in `plans/runbook-quality-gates/reports/`

**Unspecified file on branch:** `plans/runbook-evolution/requirements.md` — unrelated plan, not part of this design.

## Gap Analysis

| Design Requirement | Status | Reference |
|----|--------|-----------|
| FR-1: Outline consolidation | Covered (Phase A) | `runbook-simplification-agent.md`, SKILL.md Phase 0.86 |
| FR-2 mechanical: model-tags | Covered | `validate-runbook.py check_model_tags` |
| FR-2 semantic: model review | Covered (Phase A) | `review-plan/SKILL.md` Section 12, `plan-reviewer.md` |
| FR-3: File lifecycle | **Partial** | modify-before-create + duplicate create implemented; future-phase reads + missing creation descoped |
| FR-4 structural: RED plausibility | Covered | `validate-runbook.py check_red_plausibility` |
| FR-5: Test count reconciliation | Covered (with caveat) | `validate-runbook.py check_test_counts` — see Major #2 |
| FR-6: Scaling | Covered (Phase A) | Mandatory-for-all design, no size-dependent paths |
| NFR-1: Workflow integration | Covered | SKILL.md phases, pipeline-contracts T2.5/T4.5 |
| NFR-2: Incremental adoption | Covered | `--skip-*` flags, graceful degradation in SKILL.md |

## Critical Findings

None.

## Major Findings

### 1. FR-3 lifecycle: two of four specified checks not implemented

Design specifies four lifecycle flags: modify-before-create, duplicate creation, future-phase reads, missing creation (existing-file without prior create). Only the first two are implemented.

- **File:** `agent-core/bin/validate-runbook.py:119-174`
- **Design:** FR-3 in design.md lines 293-302
- **Impact:** Future-phase reads and missing-creation violations pass undetected. These are real runbook defect patterns — a step reading content from a file that won't exist until a later phase creates it, or a step modifying a file marked "Existing" that isn't on disk and has no prior creation.
- **Mitigation:** The vet review explicitly documents this as OUT-OF-SCOPE (line 60). The two implemented checks cover the most common lifecycle violations. The gap is known and tracked.

### 2. check_test_counts compares against global count, not cumulative-to-checkpoint

Each `"All N tests pass"` checkpoint is compared against the total unique test count across the entire document. For runbooks with interim checkpoints (common in multi-phase runbooks), this produces false positives.

- **File:** `agent-core/bin/validate-runbook.py:192-214`
- **Design:** "Count unique test function names per phase (cumulative across phases)" — implies position-aware accumulation
- **Example:** Phase 1 with 2 tests + checkpoint "All 2 tests pass", Phase 2 with 3 more tests + checkpoint "All 5 tests pass". Current code compares both checkpoints against 5, flagging the Phase 1 checkpoint as wrong.
- **Mitigation:** Vet review noted this in Recommendations (line 76). All current test fixtures use end-of-document checkpoints only, so tests pass. Production runbooks routinely have interim checkpoints.

## Minor Findings

### Unused imports (dead code)
- **File:** `agent-core/bin/validate-runbook.py:14,16,18`
- Three module-level assignments from prepare-runbook.py never used: `parse_frontmatter`, `extract_sections`, `extract_file_references`. Only `extract_cycles`, `extract_step_metadata`, and `assemble_phase_files` are used.
- Not caught by lint because importlib dynamic loading bypasses unused-import detection.

### No test coverage for `agents/decisions/workflow-*.md` artifact pattern
- **File:** `agent-core/bin/validate-runbook.py:31`
- The `_is_artifact_path` regex branch (`agents/decisions/workflow-[^/]+\.md$`) has no dedicated test fixture exercising it. The three `ARTIFACT_PREFIXES` are indirectly tested via the `VIOLATION_MODEL_TAGS` fixture (uses `agent-core/skills/`), but the regex path is untested.

### Report format simplified from design
- Design specifies structured violation subsections (Location/File/Expected/Found per violation). Implementation uses flat `- {description}` list items with inline formatting. Functional but less machine-parseable.

### Fixture format deviation
- Design specified `tests/fixtures/runbooks/*.md` files. Implementation uses Python string constants in `tests/fixtures/validate_runbook_fixtures.py`. Reasonable deviation — string constants are more portable and self-contained for TDD. Consistent with project testing conventions.

## Cross-Cutting Consistency

| Check | Status |
|-------|--------|
| SKILL.md Phase 3.5 invocation matches script CLI | Pass — directory input, subcommand names, exit codes all match |
| pipeline-contracts T4.5 matches implementation | Pass — "validate-runbook.py (script)" with correct check descriptions |
| memory-index entries present | Pass — both `/when` entries under pipeline-contracts.md |
| plan-reviewer model assignment reference | Pass — single line referencing review-plan skill |
| review-plan Section 12 artifact-type paths | Pass — matches `ARTIFACT_PREFIXES` + regex in code |
| Naming: subcommand names consistent across all artifacts | Pass — `model-tags`, `lifecycle`, `test-counts`, `red-plausibility` everywhere |
| Test suite passing | Pass — 17/17 tests pass, precommit clean |

## Summary

- **Critical:** 0
- **Major:** 2 (partial FR-3, test-counts accumulation)
- **Minor:** 4 (unused imports, untested regex path, simplified report format, fixture format deviation)

The Phase B deliverable (`validate-runbook.py`) satisfies its core requirements: four subcommands with correct exit codes, directory input, skip flags, and importlib reuse. Both Major findings are known and documented — the vet review explicitly notes both. The partial FR-3 is an intentional descoping; the test-counts accumulation is a correctness limitation for multi-phase runbooks with interim checkpoints. Neither blocks merge — both should be addressed in follow-up work.

Phase A deliverables (verified present on main) are complete and consistent with Phase B. No cross-cutting inconsistencies detected.
