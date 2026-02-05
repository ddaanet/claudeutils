# Runbook Outline Review: Statusline Visual Parity

**Artifact**: plans/statusline-parity/runbook-outline.md
**Design**: plans/statusline-parity/design.md
**Date**: 2026-02-05T18:42:00Z
**Mode**: review + fix-all

## Summary

Runbook outline provides comprehensive coverage of all requirements with balanced phase structure. Original outline lacked explicit RED/GREEN markers required for TDD workflow, had minor requirements mapping inconsistencies, and needed cycle count clarification. All issues have been fixed.

**Overall Assessment**: Ready

## Requirements Coverage

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| R1 | 1 | 1.1-1.3 | Complete | Model display with emoji/color/thinking indicator |
| R2 | 1 | 1.4 | Complete | Directory display with 📁 prefix and CYAN color |
| R3 | 1 | 1.5 | Complete | Git status with ✅/🟡 emoji and colored branch |
| R4 | 1 | 1.6 | Complete | Cost display with 💰 emoji prefix |
| R5 | 2 | 2.1-2.3 | Complete | Context display with 🧠 emoji, color, horizontal bar |
| R6 | 1 | 1.7 | Complete | Mode line with 🎫/💳 emoji and color (fixed from Phase 2) |
| R7 | 3 | 3.1 | Complete | Python environment indicator with 🐍 prefix |
| TTL | 5 | 5.1 | Complete | Update UsageCache TTL from 30s to 10s |

**Coverage Assessment**: All requirements covered with explicit cycle mappings

## Phase Structure Analysis

### Phase Balance

| Phase | Cycles | Complexity | Percentage | Assessment |
|-------|--------|------------|------------|------------|
| 1 | 7 | Low | 47% | Balanced (formatting patterns) |
| 2 | 3 | Medium | 20% | Balanced (token bar algorithm) |
| 3 | 1 | Low | 7% | Balanced (simple detection) |
| 4 | 3 | Medium | 20% | Balanced (integration) |
| 5 | 1 | Low | 7% | Balanced (trivial update) |

**Balance Assessment**: Well-balanced. Phase 1 is larger but appropriate for pattern-based formatting work.

### Complexity Distribution

- **Low complexity phases**: 3 (Phases 1, 3, 5)
- **Medium complexity phases**: 2 (Phases 2, 4)
- **High complexity phases**: 0

**Distribution Assessment**: Appropriate. Complexity escalates in Phase 2 (token bar algorithm) and Phase 4 (integration), with simple patterns in Phase 1.

## Review Findings

### Critical Issues

None identified.

### Major Issues

**1. Missing TDD RED/GREEN markers**
   - Location: All phase cycle descriptions
   - Problem: Cycles described implementation steps without explicit RED/GREEN phases
   - Fix: Added "(RED)" and "(GREEN)" markers to all cycles with test/implementation sequencing
   - **Status**: FIXED

**2. R6 mapping inconsistency**
   - Location: Requirements Mapping table
   - Problem: R6 mapped to "Phase 2: Cycle 2.3" but `format_mode()` described in Phase 1 cycle list
   - Fix: Corrected mapping to "Phase 1: Cycle 1.7"
   - **Status**: FIXED

### Minor Issues

**1. Cycle count ambiguity**
   - Location: Complexity Per Phase table
   - Problem: "15 cycles" could be misread as 15 implementation steps vs 15 RED/GREEN pairs
   - Fix: Added note clarifying each cycle is a RED/GREEN pair, matching design estimate
   - **Status**: FIXED

**2. Phase 1 continuation structure**
   - Location: Phase 1/Phase 2 boundary
   - Problem: Cycle 1.7 (`format_mode()`) was at top of Phase 2 section instead of Phase 1
   - Fix: Moved to "Phase 1 (continued)" subsection for structural clarity
   - **Status**: FIXED

## Fixes Applied

- **Requirements Mapping table** — Corrected R6 mapping from Phase 2 to Phase 1
- **Phase 1 cycles** — Added explicit RED/GREEN markers to all 6 formatter cycles
- **Phase 1 structure** — Added continuation subsection for cycle 1.7
- **Phase 2 cycles** — Added explicit RED/GREEN markers to all 3 token bar cycles
- **Phase 3 cycles** — Added explicit RED/GREEN markers to environment detection cycle
- **Phase 4 cycles** — Added explicit RED/GREEN markers to all 3 integration cycles
- **Phase 5 cycles** — Added explicit RED/GREEN markers to TTL update cycle
- **Complexity table** — Added clarification note on cycle count semantics (RED/GREEN pairs)

## Design Alignment

**Architecture**: Aligned. Outline follows D1-D7 design decisions with correct module boundaries (display.py for formatting, cli.py for composition, context.py for detection).

**Module structure**: Aligned. All changes localized to appropriate modules per existing architecture.

**Key decisions**: Properly referenced:
- D1: Emoji mappings in StatuslineFormatter
- D2: Horizontal token bar algorithm (shell lines 169-215)
- D3: CLI composition pattern
- D4: Model tier extraction strategy
- D5: Bright color constants
- D6: Python environment detection
- D7: TTL adjustment

## Positive Observations

- **Clear traceability**: Every requirement maps to specific cycles with descriptive notes
- **Logical phase grouping**: Related functionality grouped (formatters → token bar → environment → integration → TTL)
- **Appropriate complexity assessment**: Matches design tier assessment (Tier 2, 12-15 cycles)
- **Explicit dependencies**: Token bar (Phase 2) depends on format methods (Phase 1), integration (Phase 4) depends on all prior phases
- **Shell reference integration**: Explicit line number references to shell implementation guide execution
- **Success criteria**: Clear, measurable outcomes (visual parity, all tests pass, no regressions, TTL conformance)

## Recommendations

**For full runbook expansion:**

- **Cycle descriptions**: Expand RED phase descriptions with specific test cases (e.g., "Test `_extract_model_tier('Claude Sonnet 4')` returns 'sonnet'")
- **Shell line references**: Add specific shell line number references in cycle notes for algorithm verification (already in design, should propagate to cycles)
- **Edge case handling**: Expand cycle 4.3 with explicit edge cases (missing data, unknown model names, terminal width constraints)
- **Color validation**: Include visual inspection step in cycle 4.3 to verify ANSI codes render correctly
- **Pattern deduplication**: Note opportunities for test fixture reuse across similar format methods (cycles 1.2-1.7)

**Integration checkpoint guidance:**

- Phase 4 checkpoint should include visual diff against shell output with identical input data
- Consider adding intermediate checkpoint after Phase 2 (token bar complete) for early algorithm validation
- Final checkpoint (end of Phase 4) should validate against conformance report criteria

---

**Ready for full expansion**: Yes

All requirements traced, phase structure is balanced, TDD markers explicit, design alignment verified. Outline provides clear foundation for haiku execution with 15 RED/GREEN cycle pairs.
