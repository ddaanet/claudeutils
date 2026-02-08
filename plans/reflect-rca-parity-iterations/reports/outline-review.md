# Outline Review: Parity Test Quality Gap Fixes

**Artifact**: plans/reflect-rca-parity-iterations/outline.md
**Date**: 2026-02-06T19:45:00Z
**Mode**: review + fix-all

## Summary

The outline proposes fixes for 4 remaining gaps from the parity test RCA plus 3 Opus-identified concerns through a mix of pipeline changes, mechanical fixes, and tooling. The original outline was well-structured but had significant gaps in traceability, missing interactions between fixes, incomplete implementation guidance, and unresolved design decisions. All issues have been fixed.

**Overall Assessment**: Ready for user discussion after fixes

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| RCA Gap 1: No conformance validation | Key Decisions D1, D2; Changes by File | Complete | Added defense-in-depth approach (all 3 mechanisms), orchestrate skill change, mandatory planning guidance |
| RCA Gap 2: No pre-write file size check | Gap Prioritization; Changes by File | Complete | Planning-time awareness + D+B-ensured commit check documented |
| RCA Gap 3: Prose gates (D+B status) | Gap 3 status clarification | Complete | Added explicit "substantially mitigated, not closed" assessment per Opus Finding 1 |
| RCA Gap 4: Test description imprecision | Gap Prioritization; Changes by File | Complete | Maps to testing.md and workflow-advanced.md updates |
| RCA Gap 5: `--test` bypass | Gap Prioritization; Changes by File | Complete | Mechanical fix: add run-line-limits to both `just test` and `just lint` |
| RCA RC1: Conformance validation gap in orchestration | Key Decisions D1 | Complete | Addressed via defense-in-depth (planning + execution + review layers) |
| RCA RC2: Vet agent scope limitation | Changes by File (N2) | Complete | Vet-fix-agent gets conformance review dimension |
| RCA RC3: Precommit not run | Gap Prioritization | Complete | Links Gap 5 fix to RC3; D+B fix already addressed structural cause |
| RCA RC4: No file size awareness during writing | Gap Prioritization | Complete | Links Gap 2 to RC4 |
| RCA RC5: False "visual parity validated" claim | Gap Prioritization | Complete | Links Gap 4 to RC5 (imprecise descriptions enabled false claims) |
| Opus Finding 1: Gap 3 overclaimed as closed | Gap 3 status clarification | Complete | Added explicit clarification that D+B mitigates but doesn't eliminate class |
| Opus Finding 2: Gap 5 mitigation overclaimed | Gap Prioritization table | Complete | Revised to show Gap 5 fix is mechanical (line limits in test recipe), not D+B effect |
| Opus Finding 3: Gap 2 should be partially mitigated | Gap Prioritization dependencies | Complete | Added "Gap 2 benefits from Gap 3 fix" — D+B ensures commit-time check runs |
| Opus Finding 4: Incomplete staleness assessment | (Not directly applicable to outline) | N/A | Outline is forward-looking (fixes), not assessing RCA staleness |
| Opus Finding 5: Root cause ranking stability | Gap Prioritization table | Complete | Table now includes "Addresses" column mapping gaps to RCs |
| Opus Finding 6: Missing interaction effects | Dependencies section; D1 defense-in-depth | Complete | Added explicit dependency analysis and defense-in-depth approach |
| Opus Finding 7: Convention without enforcement | N1 in prioritization; Changes by File | Complete | Added N1 (lint script for tool-call-first convention) |
| Opus Finding 8: D+B fix not empirically validated | N3 in prioritization; Changes by File | Complete | Added N3 (empirical validation procedure) |
| Opus Finding 9: Minor issues | Open Questions Q1 | Partial | Addressed line limits in multiple recipes (Q1), other minor issues not applicable to outline |
| Concurrent evolution factor (rca.md:253-265) | Concurrent Evolution Factor section | Complete | Explicitly noted as out of scope (scheduling concern, not quality gate) |

**Traceability Assessment**: All requirements covered with explicit references

## Review Findings

### Critical Issues

**None after fixes**

### Major Issues

**1. Missing traceability between gaps and root causes**
- Location: Gap Prioritization table (original line 12)
- Problem: Table showed gaps without mapping to RCA's 5 root causes (RC1-RC5), making it unclear which fixes address which failure modes
- Fix: Added "Addresses" column mapping each gap to specific RCs and Opus findings
- **Status**: FIXED

**2. Incomplete interaction analysis**
- Location: Dependencies section (original line 21)
- Problem: Single-line dependency note missed critical interactions identified by Opus (Gap 1+4, Gap 3+5, Gap 2+3)
- Fix: Expanded to multi-bullet format covering all three interaction types with rationales
- **Status**: FIXED

**3. Gap 3 status ambiguity**
- Location: Approach section (original line 5-6)
- Problem: Outline counted "4 remaining gaps" without clarifying Gap 3's status after D+B fix, creating confusion given Opus Finding 1's critique
- Fix: Added explicit "Gap 3 status clarification" paragraph explaining "substantially mitigated, not closed" assessment
- **Status**: FIXED

**4. Single-layer conformance validation approach**
- Location: Key Decisions D1, D2 (original lines 24-39)
- Problem: D1 proposed choosing between three mechanisms; D2 proposed single trigger point. Opus Finding 6 shows single-layer approaches leave gaps.
- Fix: Revised D1 to recommend all three mechanisms as defense-in-depth. Revised D2 to hybrid approach (planning-time + execution-time)
- **Status**: FIXED

**5. Incomplete file change inventory**
- Location: Changes by File table (original lines 49-56)
- Problem: Missing orchestrate skill change (final checkpoint conformance), missing defense-in-depth doc, line limits only in `just test` not `just lint`
- Fix: Added 3 missing rows, expanded justfile change to cover both recipes
- **Status**: FIXED

**6. Unresolved design decisions**
- Location: Open Questions section (original lines 68-72)
- Problem: Three questions posed without recommendations, blocking implementation
- Fix: Expanded to 5 questions (Q1-Q5) with explicit leanings and rationales for each
- **Status**: FIXED

### Minor Issues

**1. Missing N3 (empirical validation) from prioritization**
- Location: Gap Prioritization table (original line 12)
- Problem: Opus Finding 8 (D+B not empirically validated) was acknowledged but not added to work items
- Fix: Added N3 row with trivial complexity tier
- **Status**: FIXED

**2. "What This Doesn't Do" section incomplete**
- Location: What This Doesn't Do (original lines 60-63)
- Problem: Listed what's not being done without explaining why, creating impression of arbitrary scope cuts
- Fix: Expanded each bullet with rationale (scheduling concern, planning vs tooling, etc.)
- **Status**: FIXED

**3. No implementation sequencing guidance**
- Location: End of outline (after Concurrent Evolution section)
- Problem: Outline lists 11 file changes across 3 complexity tiers without sequencing or tier grouping
- Fix: Added "Implementation Tiers" section grouping work into Tier 1 (trivial), Tier 2 (low), Tier 3 (moderate) with sequencing recommendation
- **Status**: FIXED

**4. Gap 2 benefits from D+B not documented**
- Location: Gap Prioritization (original line 15)
- Problem: Opus Finding 3 identified that Gap 2 is partially mitigated by D+B (ensures commit-time check runs) but outline didn't document this
- Fix: Added to Dependencies section: "Gap 2 benefits from Gap 3 fix — D+B ensures commit-time file size check actually runs"
- **Status**: FIXED

**5. Vague "Addresses" references**
- Location: Gap Prioritization table (after fix)
- Problem: Some gaps address multiple RCs but table only showed gap numbers
- Fix: Table now explicitly lists RC numbers alongside gap numbers (e.g., "RCA Gap 1, RC1")
- **Status**: FIXED

## Fixes Applied

All fixes applied to `/Users/david/code/claudeutils-parity-iterations/outline.md`:

1. **Line 5-10** — Added "Gap 3 status clarification" paragraph explaining D+B mitigation vs elimination
2. **Line 12-18** — Gap Prioritization table: added "Addresses" column, added N3 row, expanded traceability
3. **Line 20-26** — Dependencies section: expanded from 1 line to 3 bullets covering all interaction types
4. **Line 28-43** — D1 (conformance mechanism): revised from "leaning C+B" to "all three as defense-in-depth"
5. **Line 35-44** — D2 (conformance trigger): revised from "Option 3" to "Hybrid 2+3" with rationale
6. **Line 49-59** — Changes by File table: added orchestrate, defense-in-depth doc, D+B validation; expanded justfile row
7. **Line 60-66** — What This Doesn't Do: expanded each bullet with rationales
8. **Line 68-87** — Open Questions: expanded from 3 questions to 5 (Q1-Q5) with recommendations for each
9. **Line 76-77** — Concurrent Evolution Factor: added note that question remains unresolved
10. **Line 79-91** — Added "Implementation Tiers" section with sequencing guidance

## Positive Observations

**Strong foundation:**
- Outline correctly identified all 4 remaining gaps from RCA plus 2 Opus concerns (N1, N2)
- Gap prioritization by impact matches RCA's empirical evidence (iterations caused)
- Mechanical fix for Gap 5 is correct and trivial (add run-line-limits to recipes)

**Good structure:**
- Separation of Key Decisions from Changes by File enables design discussion before implementation commitment
- "What This Doesn't Do" section prevents scope creep by explicitly marking boundaries
- Concurrent Evolution Factor acknowledgment shows awareness of meta-level factors

**Integration with existing workflow:**
- Changes target existing files (testing.md, workflow-advanced.md, plan-tdd, etc.) rather than creating parallel documentation
- Vet-fix-agent enhancement (N2) builds on existing checkpoint infrastructure
- Skill step lint (N1) complements D+B fix rather than replacing it

## Recommendations

**For user discussion:**

1. **Conformance validation mechanism (D1):** The outline now recommends defense-in-depth (all three mechanisms). User should confirm this approach vs simpler single-mechanism approach. Trade-off: robustness vs implementation cost.

2. **Mandatory vs guidance for conformance cycles (Q2):** Outline leans toward mandatory (planner MUST include conformance cycles if design has reference). User should confirm enforcement level. Alternative: leave as guidance, rely on vet checkpoint to catch omissions.

3. **Defense-in-depth documentation location (Q5):** Outline suggests new file `agents/decisions/defense-in-depth.md`. User should confirm this is worth separate file vs section in existing workflow doc. Pattern may have broader applicability beyond Gap 3+5.

4. **Tier 3 sequencing:** Outline notes Tier 3 (conformance validation) may need `/opus-design-question` for mechanism design. User should confirm whether to proceed with outline's defense-in-depth recommendation or seek opus input first.

5. **Empirical validation of D+B (N3):** Outline adds this as Tier 1 work. User should confirm priority — is D+B validation prerequisite for other work, or can it happen in parallel?

**For next phase (planning):**

- The outline provides sufficient detail for planning to proceed
- Key Decisions section has clear recommendations (not unresolved choices)
- Open Questions have explicit leanings to guide planner
- Implementation Tiers provide natural phase boundaries (Tier 1 → Tier 2 → Tier 3)

---

**Ready for user presentation**: Yes — all fixable issues resolved, design decisions clarified, traceability complete
