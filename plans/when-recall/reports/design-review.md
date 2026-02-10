# Design Review: `/when` Memory Recall System

**Design Document**: plans/when-recall/design.md
**Review Date**: 2026-02-09
**Reviewer**: design-vet-agent (opus)

## Summary

The design proposes replacing a passive memory index (0% recall across 200 sessions) with active `/when` and `/how` commands backed by a fuzzy matching engine, resolver script, and updated validator. The architecture is well-structured with clear module boundaries, solid research grounding (corpus analysis, fzf algorithm research), and a feasible migration path. The design required several fixes for accuracy, completeness, and consistency with the existing codebase.

**Overall Assessment**: Needs Minor Changes

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **Navigation module dependency ordering incorrect**
   - Problem: Migration sequencing listed Navigation (step 4) as depending on resolver, but `compute_ancestors()` and `compute_siblings()` operate on file content strings and heading data directly -- they do not call the resolver.
   - Impact: Incorrect dependency ordering would force Navigation to be built after Resolver, preventing independent TDD testing.
   - Fix Applied: Moved Navigation to step 3 (before Resolver), corrected Resolver to step 4 with dependency on navigation. Added explanatory note about the correction.

2. **Test directory structure inconsistent with project convention**
   - Problem: Design specified `tests/when/test_fuzzy.py` (nested subdirectory), but existing project uses flat directory with prefixed names: `tests/test_recall_*.py`, `tests/test_validation_*.py`.
   - Impact: Planner would create wrong directory structure, requiring rework.
   - Fix Applied: Changed to `tests/test_when_fuzzy.py` etc. with note about project convention and existing examples.

3. **Validator dual-location not documented**
   - Problem: Design referenced validator modules in `src/claudeutils/validation/` but omitted that `agent-core/bin/validate-memory-index.py` (480-line standalone script) is a parallel implementation requiring the same changes.
   - Impact: Bin script would be missed during planning, causing precommit failures after migration.
   - Fix Applied: Added bin script to Validator Changes section, Validator refactoring section, and Existing code reuse table. Documented the duplication pattern.

4. **Recall tool compatibility gap**
   - Problem: Design did not address that `src/claudeutils/recall/index_parser.py` parses the current `Key -- description` format and will break after migration. The recall tool is needed to measure NFR-3 (>10% recall within 30 sessions).
   - Impact: Measurement infrastructure would be broken post-migration, preventing success criteria validation.
   - Fix Applied: Added "Recall tool compatibility" subsection in Implementation Notes with approach (update parser or delegate to shared `when/index_parser.py`).

5. **Backward compatibility strategy missing**
   - Problem: Design specified new format for validator but did not address whether old and new formats coexist during migration or if migration is atomic.
   - Impact: Without explicit decision, planner might implement dual-format parsing (significant complexity) or miss transitional state.
   - Fix Applied: Added backward compatibility note to Validator Changes section (atomic migration chosen). Added D-8 decision documenting rationale.

### Minor Issues

1. **Entry count inconsistency (140 vs 122)**
   - Problem: FR-6 says "~140 entries" but corpus analysis counts 122 non-exempt entries. The explore-design-context.md report says 140 total lines with entries.
   - Impact: Minor confusion for planner about scope of migration.
   - Fix Applied: Added clarifying note to FR-6 explaining the count difference (140 includes exempt section entries that will be removed).

2. **Data model convention mismatch**
   - Problem: `index_parser.py` used `@dataclass` for `WhenEntry`, but project convention (per existing `recall/index_parser.py` and NFR patterns) uses Pydantic `BaseModel`.
   - Impact: Minor inconsistency; planner might use wrong pattern.
   - Fix Applied: Changed to `BaseModel` with note about project convention.

3. **Function signatures incomplete**
   - Problem: `compute_ancestors()` signature missing `file_path` parameter (needed to generate `..file.md` link). `fuzzy.py` signatures used bare annotation style instead of `def ... -> ...: ...`.
   - Impact: Planner might implement with wrong signature.
   - Fix Applied: Added `file_path` parameter to `compute_ancestors()`, fixed signature formatting.

4. **CLI registration pattern not specified**
   - Problem: Design said "Registered in main CLI as `claudeutils when <operator> <query...>`" without specifying the pattern. Main CLI uses `cli.add_command()` in `src/claudeutils/cli.py`.
   - Impact: Minor; planner would figure it out from existing code.
   - Fix Applied: Updated to reference `cli.add_command()` pattern with existing examples.

5. **Heading rename scope unclear**
   - Problem: Design said "~140 headings need renaming" but structural headings (`.` prefix) should not be renamed.
   - Impact: Planner might attempt to rename structural headings.
   - Fix Applied: Added clarification that only semantic headings get renamed (~102, not ~140), structural headings remain unchanged.

6. **Mixed heading levels not addressed in resolver**
   - Problem: Decision files use both flat H2 (workflow-core.md) and nested H2/H3 (testing.md) patterns, but resolver docs did not mention handling both.
   - Impact: Resolver might only handle one pattern.
   - Fix Applied: Added note about heading level patterns to resolver section.

7. **Structural heading handling in navigation**
   - Problem: Navigation computes ancestors by walking up heading hierarchy, but structural headings (`.` prefix) are organizational with no direct content. Design did not specify how these are handled.
   - Impact: Navigation might link to empty structural sections.
   - Fix Applied: Added structural heading handling note to navigation section.

8. **Fuzzy engine missing minimum score threshold**
   - Problem: Scoring algorithm specified boundary bonuses and gap penalties but no minimum threshold for accepting a match. Short queries could produce low-confidence spurious matches.
   - Impact: Edge case in resolver -- queries like `/when a` could match many entries with similar low scores.
   - Fix Applied: Added "Minimum score threshold to prevent spurious matches on short queries" to algorithm specification.

9. **Missing file paths in migration sequencing**
   - Problem: Migration steps listed component names but not file paths, making it harder for planner to map steps to implementation.
   - Impact: Planner would need to cross-reference Component Architecture section for each step.
   - Fix Applied: Added file paths to each migration step.

10. **Requirements traceability table missing**
    - Problem: Design had requirements and design elements but no explicit traceability mapping.
    - Impact: Reviewer and planner cannot quickly verify coverage.
    - Fix Applied: Added Requirements Traceability section with FR/NFR mapping to design elements.

## Requirements Alignment

**Requirements Source:** Inline (design.md Requirements section)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | Resolver script + skill wrappers |
| FR-2 | Yes | Fuzzy engine (fuzzy.py, D-4, D-7) |
| FR-3 | Yes | Navigation module + output format |
| FR-4 | Yes | Validator Changes section |
| FR-5 | Yes | `/remember` Skill Update section |
| FR-6 | Yes | Migration sequencing step 9 |
| FR-7 | Yes | Three resolution modes in resolver |
| NFR-1 | Yes | Fuzzy engine shared across 3 consumers (D-4) |
| NFR-2 | Yes | Testing strategy (TDD for all components) |
| NFR-3 | Yes | Success criteria defined, recall tool compatibility addressed |
| NFR-4 | Yes | Consumption header update, index stays @-loaded |

**Gaps:** None. All requirements traced to design elements.

## Positive Observations

- **Research-grounded architecture:** The design is built on concrete data (0% recall baseline from 200 sessions, corpus analysis of 122 entries, fzf algorithm research). Decisions cite specific findings rather than assumptions.

- **Clean module boundaries:** Each module in `src/claudeutils/when/` has a single responsibility with clear input/output contracts. Pure functions (fuzzy scoring, navigation computation) are separated from I/O-dependent logic (resolver file reading, CLI parsing), enabling straightforward TDD.

- **DRY fuzzy engine:** Using a single fuzzy implementation across resolver, validator, and compression tool prevents scoring divergence. Three consumers with identical behavior is a good architectural constraint.

- **Pragmatic format design:** The two-field format (`/when trigger | extras`) eliminates the description field that was redundant with decision file content. This reduces index token cost while maintaining discovery surface.

- **Explicit out-of-scope:** Dropping `/what` and `/why` operators is well-justified by the learning that LLMs don't proactively seek definitions. The corpus analysis backing (27% `/how`, 73% `/when`, 16 entries rephrased) adds confidence.

- **Migration risk mitigation:** Script-assisted heading renames + precommit validation + key compression tool form a safety net for the large-scope migration.

- **Outline-to-design fidelity:** All 9 outline components appear in the design with expanded detail. No outline elements were dropped or contradicted.

## Recommendations

1. **Fuzzy engine spike should produce a test corpus.** The spike (scoring constant tuning) should output a test fixture file with query-candidate-expected-rank triples derived from real index entries. This fixture becomes the behavioral test suite for `test_when_fuzzy.py`, bridging spike exploration and TDD.

2. **Consider adding the recall tool parser update to migration sequencing.** Currently noted as "follow-up" but NFR-3 measurement depends on it. Adding it as step 12 ensures it is not forgotten and the measurement window starts immediately post-deployment.

3. **Document the scoring threshold discovery process.** The minimum score threshold for fuzzy matching is mentioned but not specified. The spike should determine this empirically and document the chosen threshold with its rationale in the implementation.

## Next Steps

1. Design is ready for planning with `/plan-tdd`
2. All applied fixes are in the design document -- no outstanding changes needed
3. Load `plugin-dev:skill-development` before planning (skill wrappers in steps 8)
4. Fuzzy engine spike may precede formal TDD cycles (per design recommendation)
