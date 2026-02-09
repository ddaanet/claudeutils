# Outline Review: continuation-passing

**Artifact**: plans/continuation-passing/outline.md
**Date**: 2026-02-07
**Mode**: review + fix-all

## Summary

The outline is well-structured with sound technical approach grounded in existing tail-call patterns. All core requirements (FR-1 through FR-7, NFR-1 through NFR-3, C-1, C-2) are addressed. The main gaps were missing NFR-3 coverage, incomplete FR-5 translation mechanism, underspecified continuation transport format, and incomplete mapping to requirements open questions. All issues fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | Parsing Format > Prose | Complete | Delimiter syntax well-specified |
| FR-2 | Key Decisions > Cooperative skill protocol | Complete | Sequential execution via tail-call chain |
| FR-3 | Parsing Format > Prose | Complete | Peel-first-pass-remainder pattern |
| FR-4 | Parsing Format > Structured | Complete | Multi-line then:/finally: markers |
| FR-5 | Parsing Format > Prose | Complete | Added prose-to-explicit translation mechanism |
| FR-6 | Key Decisions > Sub-agent isolation | Complete | Convention + explicit prohibition |
| FR-7 | Key Decisions > Cooperative skill protocol | Complete | Light coupling, protocol-based |
| FR-8 | Scope > Out | Complete | Explicitly deferred (optional requirement) |
| NFR-1 | Key Decisions > Cooperative skill protocol | Complete | Skills understand protocol, not downstream skills |
| NFR-2 | Cooperative Skill Registry | Complete | Added detection mechanism description |
| NFR-3 | Key Decisions > Ephemeral continuation lifecycle | Complete | Added new section |
| C-1 | Key Decisions > Sub-agent isolation | Complete | Convention-based, first-party control |
| C-2 | Key Decisions > Termination invariant | Complete | Empty continuation = default tail-call |
| OQ-1 | Open Questions #1 | Addressed | Registry-based disambiguation |
| OQ-2 | Open Questions #4 | Addressed | Hook parses once, passed pre-parsed |
| OQ-3 | Open Questions #3 | Addressed | Stop on error, future configurable |
| OQ-4 | Open Questions #5 | Addressed | Hook script list, extract later if needed |

**Traceability Assessment**: All requirements covered. Open questions from requirements mapped to outline open questions with proposed approaches.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **NFR-3 (Ephemeral continuations) missing**
   - Location: Key Decisions section (no subsection existed)
   - Problem: No section addressed that continuations must not be persisted in agent memory. This is a core non-functional requirement that constrains the architecture.
   - Fix: Added "Ephemeral continuation lifecycle (NFR-3)" subsection under Key Decisions, explicitly stating continuations are not persisted and are discarded on chain completion or error.
   - **Status**: FIXED

2. **FR-5 translation mechanism incomplete**
   - Location: Parsing Format > Prose section header referenced FR-5 but lacked mechanism
   - Problem: Section mentioned FR-5 in the heading but did not describe how prose like "then plan it" gets translated to explicit `/plan-adhoc` references. Translation is a core parsing requirement.
   - Fix: Added "Prose-to-explicit translation (FR-5)" paragraph describing how hook matches connecting words to registry entries and always outputs explicit skill references.
   - **Status**: FIXED

3. **Continuation transport format unspecified**
   - Location: Continuation transport section
   - Problem: Architecture diagram showed `[CONTINUATION: /orchestrate]` but no specification of the serialization format for args. Skills need to know how to parse and re-serialize.
   - Fix: Added "Transport format" paragraph specifying the `[CONTINUATION: ...]` suffix format with comma-separated skill entries.
   - **Status**: FIXED

4. **Requirements open questions not mapped**
   - Location: Open Questions section
   - Problem: Requirements listed 4 open questions (OQ-1 through OQ-4). Outline had 3 open questions that partially overlapped but didn't explicitly address OQ-2 (metadata vs re-parsed) or OQ-4 (cooperative list location).
   - Fix: Added open questions #4 (metadata vs re-parsed, mapping to OQ-2) and #5 (cooperative list location, mapping to OQ-4). Added OQ references to existing questions.
   - **Status**: FIXED

### Minor Issues

1. **NFR-2 detection mechanism vague**
   - Location: Cooperative Skill Registry section
   - Problem: Registry listed skills but didn't explain how hook uses it for cooperation detection. "Maintains cooperative skill registry for validation" in Key Decisions was too abstract.
   - Fix: Added sentence to Cooperative Skill Registry section explaining hook checks detected skill references against registry and conditionally injects continuation metadata.
   - **Status**: FIXED

2. **Replacement behavior not explained**
   - Location: Cooperative Skill Registry, after skill list
   - Problem: Registry listed default tail-calls per skill but didn't explain what happens when continuation overrides them. Reader had to infer from Architecture diagram.
   - Fix: Added "Replacement behavior" paragraph with concrete example showing /design replacing its default /handoff --commit tail-call with /plan-adhoc.
   - **Status**: FIXED

3. **Implementation Components testing too vague**
   - Location: Implementation Components, item 4
   - Problem: "Continuation parsing unit tests, integration test for 2-skill chain" — insufficient detail for planning scope and coverage.
   - Fix: Expanded tests into 4 bullet points: parsing unit tests, registry lookup tests, consumption tests, and integration test with specific scope described.
   - **Status**: FIXED

4. **Scope section lacked justification for deferrals**
   - Location: Scope section
   - Problem: "Out" and "Deferred" items listed without context. Reader couldn't tell if these were arbitrary or aligned with requirements.
   - Fix: Added parenthetical notes explaining FR-8 is optional in requirements, cross-session is not in requirements, and mid-chain error maps to Requirements OQ-3.
   - **Status**: FIXED

## Fixes Applied

- Key Decisions: Added "Ephemeral continuation lifecycle (NFR-3)" subsection (new section after transport)
- Key Decisions > Transport: Added "Transport format" paragraph specifying `[CONTINUATION: ...]` serialization
- Parsing Format > Prose: Added "Prose-to-explicit translation (FR-5)" paragraph
- Cooperative Skill Registry: Added detection mechanism sentence explaining hook validates against registry (NFR-2)
- Cooperative Skill Registry: Added "Replacement behavior" paragraph with concrete example
- Scope: Added justification notes for Out and Deferred items
- Open Questions: Added OQ references to existing questions #1 and #3
- Open Questions: Added new question #4 (metadata vs re-parsed, OQ-2) and #5 (cooperative list location, OQ-4)
- Implementation Components: Expanded tests item with 4 specific test categories

## Positive Observations

- Core insight ("parameterize the tail-call target") is well-articulated and grounded in exploration report findings
- Architecture diagram is clear and walks through the full chain lifecycle
- Hook-based approach is well-justified with rejected alternative documented
- Sub-agent isolation rationale is honest about convention vs enforcement trade-off
- Backward compatibility explicitly guaranteed (no continuation = existing behavior)
- Risk assessment is calibrated and realistic
- Trade-offs section identifies the key tension (mid-chain state loss) with pragmatic stance

## Recommendations

- FR-5 prose translation ("plan it" resolving to `/plan-adhoc`) may be too ambitious for initial implementation. Consider limiting initial scope to explicit `/skill` references only, deferring fuzzy prose matching.
- The `[CONTINUATION: ...]` transport format should be validated during design phase. Consider whether JSON would be more robust than the comma-separated format, especially for skills with complex args.
- Sub-agent isolation by convention (FR-6, C-1) is a known medium-risk item. Design phase should specify exactly where the prohibition text goes in each skill and whether a PreToolUse hook could enforce it.

---

**Ready for user presentation**: Yes
