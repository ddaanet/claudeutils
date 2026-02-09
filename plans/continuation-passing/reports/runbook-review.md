# Runbook Review: Continuation Passing Implementation

**Scope**: plans/continuation-passing/runbook.md
**Date**: 2026-02-09

## Summary

Reviewed assembled runbook for continuation passing implementation. The runbook provides comprehensive, well-structured execution guidance across 3 phases (hook implementation, skill modifications, testing/validation/documentation). Overall structure is sound with clear phase boundaries, parallelization opportunities identified, and consistent step numbering.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Frontmatter vs YAML Terminology Inconsistency**
   - Location: Steps 2.1-2.6, Common Phase Context
   - Problem: Design document uses "frontmatter" throughout; runbook mixes "frontmatter" and "YAML frontmatter" inconsistently
   - Suggestion: Use "frontmatter" consistently (as design does), omit redundant "YAML" qualifier since frontmatter is always YAML in SKILL.md files

2. **Handoff Flag Detection Logic Ambiguity**
   - Location: Step 1.2 (lines 249-252), Step 2.5 note (lines 719-720)
   - Problem: Design states "Hook handles this conditional logic" but Step 1.2 doesn't explicitly describe the flag detection implementation
   - Note: Step 1.2 discusses default exit appending but doesn't show how hook detects `--commit` flag in `/handoff` args. Implementation logic is deducible but not explicit.
   - Suggestion: Add explicit flag detection logic in Step 1.2 parser implementation section

3. **Mode Detection Order Example Clarity**
   - Location: Step 1.2 (lines 240-244)
   - Problem: "Mode detection order" mentioned but no concrete example showing when this matters
   - Note: Current text says "First match wins" but doesn't show an input that would match both Mode 3 and Mode 2
   - Suggestion: Add example input that demonstrates why checking Mode 3 before Mode 2 matters

## Positive Observations

**Excellent structure and completeness:**
- Weak Orchestrator Metadata section provides complete execution guidance (model assignments, parallelization, dependencies)
- Common Context section consolidates requirements, constraints, and conventions reducing repetition
- Phase-grouped structure with clear checkpoints at natural boundaries
- Validation steps at each phase checkpoint prevent downstream errors

**Strong cross-phase coherence:**
- Step dependencies clearly documented (registry builder → parser → integration → caching)
- File path references validated (all 6 skill files exist)
- Success criteria clearly defined at each step and phase
- Report locations consistently specified

**Comprehensive test coverage:**
- 8 parser test scenarios from design Component 4 directly mapped
- Unit tests, integration test, and empirical validation included
- Clear validation protocol for empirical testing (corpus extraction, manual review, metrics)

**Good attention to edge cases:**
- Terminal continuation handling (`/commit` empty default exit)
- Mid-chain `/handoff` without `--commit` special case
- Malformed input graceful degradation
- Cache corruption recovery

**Clear execution model assignments:**
- Sonnet for hook implementation (parsing logic, registry builder)
- Sonnet for skill modifications (interpreting design intent for protocol text)
- Haiku for unit tests (standard pytest patterns)
- Sonnet for integration test and empirical validation (multi-step orchestration)
- Haiku for documentation (fragment creation, decision file updates)

**Strong alignment with design:**
- All 7 design decisions (D-1 through D-7) referenced correctly
- Transport format (`[CONTINUATION: ...]`) matches design Component 2
- Consumption protocol template verbatim from design (prevents drift)
- Frontmatter schema matches design specification

## Requirements Validation

Requirements coverage from design document (FR-1–FR-8, NFR-1–NFR-3, C-1–C-2):

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Prose continuation syntax | Satisfied | Step 1.2 implements 3 parsing modes with delimiter detection |
| FR-2: Sequential execution | Satisfied | Consumption protocol in Phase 2 implements peel-first-pass-remainder |
| FR-3: Continuation consumption | Satisfied | Steps 2.1-2.6 add consumption protocol to all cooperative skills |
| FR-4: Structured continuation | Satisfied | Step 1.2 Mode 3 implements `and\n- /skill` list marker detection |
| FR-5: Prose-to-explicit translation | Satisfied | Step 1.2 registry matching + Step 3.5 empirical validation |
| FR-6: Sub-agent isolation | Satisfied | Consumption protocol template includes prohibition (line 614-615) |
| FR-7: Cooperative skill protocol | Satisfied | Phase 2 adds frontmatter declarations + consumption protocol |
| FR-8: Uncooperative skill wrapping | N/A | Explicitly out of scope (design line 36) |
| NFR-1: Light cooperation | Satisfied | Skills understand protocol, not specific downstream skills (template verbatim) |
| NFR-2: Context list for cooperation | Satisfied | Step 1.1 registry builder + Step 1.4 caching |
| NFR-3: Ephemeral continuations | Satisfied | Design D-4 lifecycle + protocol prohibition (no persistence) |
| C-1: No sub-agent leakage | Satisfied | Consumption protocol CRITICAL prohibition (line 614-615) |
| C-2: Explicit stop | Satisfied | Empty continuation = terminal (Step 1.2 line 330, Step 1.3 line 434) |

**Gaps:** None. All in-scope requirements have implementation steps.

**Out of scope items correctly excluded:**
- FR-8 (uncooperative skill wrapping) — design line 36
- Cross-session continuation — design line 37
- Mid-chain error recovery — design line 38

## Recommendations

1. **Add explicit flag detection logic to Step 1.2**
   - Current: "Flag handling: `/handoff --commit` → parser detects flag" (line 343)
   - Add: Explicit implementation guidance showing how hook checks for `--commit` in skill args
   - Location: Step 1.2 "Default exit appending" section

2. **Consider consolidating Mode 2 and Mode 3 examples**
   - Current: Separate examples at lines 250-256 (Mode 2) and 264-269 (Mode 3)
   - Alternative: Add table showing all 3 modes side-by-side for quick reference
   - Benefit: Easier to see parsing behavior differences at a glance

3. **Clarify empirical validation manual review process**
   - Current: "Manual review: classify as correct/false-positive/false-negative" (line 879)
   - Add: Who performs manual review (executor or escalate to user?)
   - Add: Sample size target (all prompts or random sample?)

## Next Steps

1. Proceed to execution — runbook is ready
2. Load `plugin-dev:skill-development` before planning (skill frontmatter context)
3. Execute phases sequentially (Phase 1 → checkpoint → Phase 2 → checkpoint → Phase 3)
4. Follow checkpoint validation procedures at end of Phases 1 and 2
5. Escalate if empirical validation metrics fail targets (0% false positives, <5% false negatives)

## Verification Checklist

✅ Step numbering consistent (1.1-1.4, 2.1-2.6, 3.1-3.8)
✅ Dependency ordering correct (registry → parser → integration → caching)
✅ Metadata accurate (14 total steps: 4 hook + 6 skills + 4 test/doc)
✅ Overall coherence maintained across phases
✅ File paths validated (all 6 skill files exist)
✅ Design decisions (D-1 through D-7) correctly referenced
✅ Requirements coverage complete (all in-scope FRs/NFRs/Cs)
✅ Phase checkpoints at natural boundaries (after 1.4, after 2.6, after 3.8)
✅ Success criteria clearly defined
✅ Model assignments appropriate (sonnet for interpretation, haiku for standard patterns)
