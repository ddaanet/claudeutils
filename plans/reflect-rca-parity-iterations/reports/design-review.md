# Design Review: Parity Test Quality — Remaining Gap Fixes

**Design Document**: `plans/reflect-rca-parity-iterations/design.md`
**Review Date**: 2026-02-08
**Reviewer**: design-vet-agent (opus)

## Summary

The design document systematically addresses 4 remaining gaps and 3 Opus-identified concerns from the parity test quality RCA. It translates the validated outline's resolved decisions into 8 concrete design decisions with clear rationale, implementation locations, and tier sequencing. The architecture is appropriately scoped (guidance updates only, no pipeline changes) and the dependency analysis (Gap 4 before Gap 1) is sound.

**Overall Assessment**: Ready

## Issues Found and Fixed

### Critical Issues

None found.

### Major Issues

1. **N3 output path missing from Files Changed table and DD-8**
   - Problem: The outline (line 87) specifies `plans/reflect-rca-prose-gates/` as the output location for D+B empirical validation. The design's DD-8 said "Document evidence in a validation report" without specifying the path, and the Files Changed table omitted this entry entirely.
   - Impact: Planner would lack a concrete output target for N3, making the step underspecified.
   - Fix Applied: Updated DD-8 to specify `plans/reflect-rca-prose-gates/reports/d-b-validation.md` as the output path. Added corresponding row to Files Changed table with Tier 1 classification.

2. **RC5 coverage implicit but undocumented**
   - Problem: The RCA's RC5 ("Visual Parity Validated" claim without evidence) is mapped to Gap 4 in the outline (line 16) but the design's DD-2 (Conformance Exception to Prose Test Descriptions) did not explicitly connect to RC5. A reader tracing requirements to design elements would not find RC5 addressed.
   - Impact: Requirements traceability gap -- RC5 appears unaddressed without following the outline's mapping.
   - Fix Applied: Added explicit sentence to DD-2 rationale connecting conformance prose descriptions to RC5 detectability.

### Minor Issues

1. **testing.md line range off by one**
   - Problem: Design stated "Conformance Validation for Migrations" spans lines 128-141. Actual content ends at line 140 (13 lines including heading through Impact line).
   - Fix Applied: Corrected to "128-140".

**Note:** All fixes applied directly to design document.

## Requirements Alignment

**Requirements Source:** inline (design.md lines 17-39)

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | Yes | DD-1 (Conformance Tests as Executable Contracts), plan-tdd/plan-adhoc in Files Changed |
| FR-2 | Yes | DD-2 (Conformance Exception to Prose Test Descriptions), testing.md + workflow-advanced.md in Files Changed |
| FR-3 | Yes | DD-3 (WIP-Only Restriction), commit SKILL.md in Files Changed |
| FR-4 | Yes | DD-4 (Planning-Time File Size Awareness), plan-tdd/plan-adhoc in Files Changed |
| FR-5 | Yes | DD-5 (Vet Alignment as Standard Practice), vet-fix-agent.md in Files Changed |
| FR-6 | Yes | DD-6 (Defense-in-Depth Documentation), defense-in-depth.md in Files Changed |
| FR-7 | Yes | DD-7 (Skill Step Tool-Call-First Audit), deferred decision with clear go/no-go criteria |
| FR-8 | Yes | DD-8 (D+B Empirical Validation), validation report in Files Changed |
| NFR-1 | Yes | Architecture section explicitly states no orchestration changes; conformance triggers through existing mechanisms |
| NFR-2 | Yes | "What This Doesn't Do" section: "No retroactive fix of existing plans" |
| NFR-3 | Yes | DD-7 explicitly applies hard-limits-or-nothing principle; DD-3 uses restriction not warning |

**Gaps:** None. All requirements traced to design elements.

## Positive Observations

- **Dependency analysis is clear and well-structured.** The change topology diagram (lines 49-56) and the explicit sequencing constraint (Gap 4 before Gap 1) prevent wasted work. This is a direct response to the Opus critique's Finding 6 about interaction effects.
- **Deferred decisions are well-justified.** DD-7 (skill audit) doesn't prematurely commit to shipping a linter. The 80% threshold with exemption marker provides a clear go/no-go decision framework. This respects the "hard limits vs soft limits" learning.
- **Conformance exception to prose descriptions (DD-2) is precisely scoped.** The example contrast table (line 88-90) makes the distinction between standard and conformance prose unambiguous. Planners can apply this immediately.
- **Defense-in-depth framing (DD-6) correctly identifies the Gap 3 + Gap 5 interaction.** The critique's Finding 6 about compounding gaps is directly addressed by documenting how D+B (outer) + WIP-only restriction (inner) close the interaction.
- **File change details are concrete.** Each file has current state, planned change, location, and approximate size. The planner has enough information to write steps without re-analyzing source files.
- **The "What This Doesn't Do" section is comprehensive.** Six explicit exclusions prevent scope creep during planning. Each exclusion has a brief rationale.
- **Outline consistency is strong.** The design faithfully implements all resolved decisions (D1-D3, Q1-Q5) from the validated outline. The design improves on the outline by adding Gap 2 to plan-tdd/plan-adhoc entries (which the outline's Changes by File table omitted).

## Recommendations

- The Affected Files Detail section for plan-tdd and plan-adhoc (lines 224-231) says "exact location depends on current structure." While the Documentation Perimeter correctly lists these as required reading, the planner will need to find insertion points. This is acceptable for a design document -- the planner is expected to read the source files -- but noting specific section headings (if stable) would further reduce planning effort.
- The testing.md expansion (line 211, "Expand to ~30 lines") and the workflow-advanced.md addition (line 216, "~10 lines") are close to what Gap 4 needs, but the 400-line limit should be verified for these files before planning. If testing.md is close to 400 lines, the planner needs to know early.

## Next Steps

1. Route to `/plan-adhoc` for runbook generation
2. Planner should verify testing.md and workflow-advanced.md current line counts before expanding content
