# Deliverable Review: runbook-recall-expansion

**Date:** 2026-03-01
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

Deliverables identified from commit `8bbb6cbe` (parent repo) and `2ac2cc8` (agent-core submodule). Inventory script showed 0 diff (worktree branched post-merge), so deliverables identified from commit analysis.

| Type | File | Lines Added |
|------|------|-------------|
| Code | `agent-core/bin/prepare-runbook.py` | +147 |
| Agentic prose | `agent-core/agents/corrector.md` | +11 |
| Agentic prose | `agent-core/skills/runbook/SKILL.md` | +29 |
| Test | `tests/test_prepare_runbook_recall.py` | +298 |

**Total:** 4 deliverables, 485 lines added.

**Design conformance:** No design.md exists — plan executed as inline task sequence per "when implementation modifies pipeline skills" decision. Conformance baseline is `plans/runbook-recall-expansion/requirements.md`.

## Critical Findings

None.

## Major Findings

1. **No e2e test for phase-tagged recall injection into step files**
   - Location: `tests/test_prepare_runbook_recall.py` (absent test)
   - Axis: Coverage (Test)
   - Problem: `test_phase_tagged_partitioned` verifies `resolve_recall_for_runbook` returns correct data structure, but no test verifies that `## Phase Recall` content appears in generated step files. The shared path has e2e coverage (`test_shared_recall_in_agent` asserts `"Resolved Recall"` in agent content), but the phase path is tested only at the unit level. `main()` lines 1747-1751 inject phase recall into `phase_preambles`, which flows to step files via `validate_and_create` — this wiring is untested end-to-end.
   - Impact: A regression in phase recall injection (e.g., wrong dict key, preamble assembly change) would not be caught by existing tests.

## Minor Findings

1. **E2e tests replicate main() wiring instead of calling main()**
   - Location: `tests/test_prepare_runbook_recall.py:225-269`
   - Axis: Independence (Test)
   - Problem: `test_shared_recall_in_agent` manually calls `parse_frontmatter`, `extract_sections`, `detect_phase_types`, `resolve_recall_for_runbook`, then `validate_and_create` — replicating main()'s logic. If main()'s recall integration changes, the test continues passing against the old wiring. Other test files (`test_validate_runbook_integration.py`) import `_mod.main` for true integration.

2. **No subprocess exception handling in resolve_recall_entries**
   - Location: `agent-core/bin/prepare-runbook.py:135-136`
   - Axis: Robustness (Code)
   - Problem: `subprocess.run(cmd, ...)` raises `FileNotFoundError` if `claudeutils` binary absent. Non-zero exit codes return empty string gracefully, but binary-not-found crashes the script. Low practical risk (script runs in project context with claudeutils installed), but inconsistent with the function's soft-failure pattern for other error cases.

## Gap Analysis

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: prepare-runbook.py reads recall artifact | Covered | `parse_recall_artifact()` at line 61, called in `main()` at line 1734 |
| FR-2: Resolve all entry keys | Covered | `resolve_recall_entries()` calls `claudeutils _recall resolve` |
| FR-3: Inject into agent definition Common Context | Covered | `main()` lines 1741-1745, `## Resolved Recall` header |
| FR-4: Per-phase recall in phase preambles | Covered | `main()` lines 1747-1751, `## Phase Recall` header |
| FR-5: Runbook skill Common Context template format | Covered | SKILL.md template lines 424-436, `**Recall (from artifact):**` |
| FR-6: Document two orchestration patterns | Covered | SKILL.md "Recall Resolution Patterns" section lines 341-365 |
| FR-7: Corrector self-contained recall loading | Covered | corrector.md Step 1.5 lines 164-173 |
| NFR-1: Token budget | Covered | SKILL.md template specifies budget with curation guidance |
| NFR-2: No runtime resolution in step agents | Covered | SKILL.md explicitly states step agents receive pre-resolved content |
| NFR-3: Backward compatibility | Covered | `resolve_recall_for_runbook` returns `("", {})` for missing artifact; `test_no_artifact_no_recall` verifies |

**Gaps:** None — all 7 FRs and 3 NFRs are addressed.

## Summary

- Critical: 0
- Major: 1 (missing e2e test for phase recall → step files)
- Minor: 2 (test wiring replication, subprocess exception handling)

All functional requirements satisfied. Code is well-structured with clear separation (parse, resolve, partition). Agentic prose updates are accurate and consistent with code behavior. Test coverage is thorough for the shared recall path but has a gap for the phase-tagged path's end-to-end injection.
