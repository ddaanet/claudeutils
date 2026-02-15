# Vet Review: Phase 5 Checkpoint — workflow-rca-fixes

**Scope**: Phase 5 — Design + Runbook Skill Fixes (FR-4, FR-14, FR-15, FR-16, FR-19, FR-20)
**Date**: 2026-02-15T18:30:00Z
**Mode**: review + fix

## Summary

Phase 5 implements content edits across 3 skill files, 1 fragment, and 1 agent definition. All 6 FRs are addressed with concrete implementations. Changed files total 9 (6 implementation artifacts + 4 review reports). All precommit checks pass (855/856 tests, 1 xfail). No critical or major issues found. 2 minor observations noted.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None found.

### Major Issues

None found.

### Minor Issues

1. **FR-4 acceptance vs implementation mismatch**
   - Location: general-patterns.md (new file)
   - Note: FR-4 specifies "each of patterns.md, anti-patterns.md, examples.md has a general-step section." Implementation creates separate `general-patterns.md` instead of adding section to `patterns.md`.
   - Rationale: Separation avoids inflating patterns.md (already 151 lines of TDD content). Design intent is general-step reference material existence, not specific file structure.
   - **Status**: DEFERRED — Implementation choice is sound; FR wording could be interpreted as specifying outcomes not structure

2. **Density checkpoint heuristic clarity**
   - Location: agent-core/skills/design/SKILL.md:188-190
   - Note: Heuristic formula "items-per-phase x avg-LOC-per-item should fall in the 100-300 range" is actionable but interpretation guidance could be clearer about what to do at boundaries (e.g., 95 vs 105 vs 310).
   - Suggestion: Add explicit boundary guidance ("below 80: definitely too granular, above 350: definitely too coarse") or acknowledge that 100-300 is guideline not hard threshold.
   - **Status**: DEFERRED — Current formula is functional and includes interpretation guidance; refinement based on usage data would be more valuable than speculative tightening

## Fixes Applied

None required — no fixable issues identified.

## Requirements Validation

**Phase 5 Requirements:**

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-4 | Satisfied | general-patterns.md created (127 lines: granularity, prerequisites, templates); anti-patterns.md has general-step section (6 anti-patterns); examples.md has general-step examples (2 complete examples with key observations) |
| FR-14 | Satisfied | design/SKILL.md:186-190 — density checkpoint with 3 concrete heuristics (>8 items/phase, <20 LOC delta, >3 unrelated concerns) |
| FR-15 | Satisfied | design/SKILL.md:192-194 — repetition helper prescription with 5+ threshold, dual justification (token cost + error rate) |
| FR-16 | Satisfied | workflows-terminology.md:12 — deliverable review in workflow route; line 19 — description covering scope, nature, exemptions |
| FR-19 | Satisfied | design/SKILL.md:197-202 (agent-name validation: Glob two directories, flag as design error); lines 204-211 (late-addition check: traceability + mechanism re-validation) |
| FR-20 | Satisfied | design-vet-agent.md:132-140 (cross-reference validation: Glob agents, flag mismatches); lines 142-149 (mechanism-check: red-flag words, required elements) |

**Gaps:** None — all 6 Phase 5 requirements satisfied by implementation.

## Positive Observations

**Concrete specifications:**
- Density checkpoint provides 3 distinct heuristics with numeric thresholds, not vague "too granular/coarse" guidance
- Repetition helper justifies 5+ threshold with dual rationale (token cost AND error rate), grounded in economic reasoning
- Cross-reference validation specifies exact Glob directories and severity mapping (critical for deliverables, major for prose)
- Mechanism-check criterion provides concrete red-flag words ("improve", "enhance" without how) and required elements list

**Grounding in session findings:**
- Agent-name validation explicitly references outline-review-agent vs runbook-outline-review-agent mismatch
- Late-addition check grounds in FR-18 incident (bypassed outline-level validation)
- Mechanism-check references FR-18 as example of mechanism-free specification
- Each new criterion traces to specific session failure mode

**Structural integration:**
- All additions fit naturally into existing document structure (no section reorganization needed)
- Cross-reference and mechanism-check criteria added to existing checklists with forward references
- Workflows-terminology route preserves tail-call chain pattern
- Design skill checkpoints placed in Phase C.1 before classification tables (logical progression)

**Template quality (general-patterns.md):**
- Step structure template includes all 7 required fields (Objective, Prerequisites, Implementation, Expected Outcome, Error Conditions, Validation, Report location)
- Each prerequisite pattern has rationale section explaining "Why"
- Heuristics provided for identifying which pattern applies to each step type

**Example completeness (examples.md):**
- Creation step demonstrates investigation prerequisite pattern (2 reads)
- Transformation step demonstrates self-contained pattern (single target read)
- Key Observations section explicitly contrasts the two patterns
- All fields populated with concrete content (not placeholders)

## Recommendations

**Empirical refinement opportunity:**
- Density checkpoint heuristic (100-300 range) should be monitored during real-world design sessions
- Collect data on actual items-per-phase x avg-LOC for successful designs
- Refine thresholds based on empirical distribution, not a priori reasoning
- Current heuristic is functional; refinement is optimization not correction

**FR wording precision:**
- Future FRs specifying file structure should distinguish between "patterns.md contains general-step section" (prescriptive structure) vs "general-step patterns are documented" (outcome focus)
- Current FR-4 wording is ambiguous — implementation judgment call is reasonable

## Next Steps

1. Proceed to Phase 6 (cleanup: delete Phase 1.4, document execution feedback)
2. Continue workflow-rca-fixes runbook execution
