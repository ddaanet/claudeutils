# Review: Inline TDD Cycle Dispatch Implementation

**Scope**: Changes since b213939 — agent-core/skills/inline/SKILL.md, agents/decisions/orchestration-execution.md, agents/memory-index.md
**Date**: 2026-03-01
**Mode**: review + fix

## Summary

Three-file change adding cycle-scoped prompt composition to the inline skill (procedure), orchestration-execution decision (rationale), and memory-index (discoverability). Core implementation is correct — extraction boundaries, common context inclusion, and adjacent cycle exclusion all satisfy requirements. Two structural issues found: C-1 constraint violation (rationale leaked into skill) and FR-2 format gap (decision lacked anti-pattern statement).

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

1. **C-1 violation: rationale duplicated in skill file**
   - Location: agent-core/skills/inline/SKILL.md:100
   - Problem: Trailing sentence "Rationale: visible future cycles cause GREEN phases to implement ahead of minimal-passing-implementation discipline" is "why" content. C-1 requires skill has the how, decision has the why. This rationale belongs only in the decision file.
   - Fix: Remove rationale sentence from skill paragraph.
   - **Status**: FIXED

2. **FR-2 AC gap: decision missing anti-pattern statement**
   - Location: agents/decisions/orchestration-execution.md:374
   - Problem: FR-2 AC requires "Documents the anti-pattern (passing full runbook to test-driver)." The original paragraph mixed procedure and rationale in a single dense block without calling out the anti-pattern. Surrounding decisions use explicit anti-pattern/correct-pattern format.
   - Fix: Restructure into anti-pattern/correct-pattern format. Move procedural elements to "Correct pattern" (minimal — just enough to ground the rationale). Anti-pattern states the problem directly.
   - **Status**: FIXED

### Minor Issues

1. **Decision paragraph procedural overlap with skill**
   - Location: agents/decisions/orchestration-execution.md:374
   - Note: The "Correct pattern" mentions prompt composition components (cycle spec + Common Context + recall entries) which overlaps with the skill's procedural content. Acceptable here because the decision needs enough concrete grounding to be useful via recall without requiring the reader to also load the skill. The overlap is minimal (one summary phrase vs full procedure).
   - **Status**: DEFERRED -- minimal overlap needed for standalone recall utility; eliminating it would make the decision too abstract to apply

## Fixes Applied

- agent-core/skills/inline/SKILL.md:100 -- Removed trailing rationale sentence ("Rationale: visible future cycles...") to satisfy C-1 constraint (skill = how, decision = why)
- agents/decisions/orchestration-execution.md:374-375 -- Restructured prompt composition paragraph into anti-pattern/correct-pattern format. Anti-pattern now explicitly states "passing the full runbook to the test-driver." Correct pattern grounds the structural enforcement rationale with minimal procedural context.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Cycle-scoped prompt composition in /inline skill | Satisfied | SKILL.md:100 — extraction boundaries, common context, exclusion rule, context absence enforcement |
| FR-2: Decision with prompt composition rationale | Satisfied (after fix) | orchestration-execution.md:374-375 — anti-pattern/correct-pattern format, references both supporting decisions |
| FR-3: Memory-index keywords | Satisfied | memory-index.md:245 — added "cycle-scoped prompt composition extraction" |
| C-1: No duplication (skill=how, decision=why) | Satisfied (after fix) | Rationale removed from skill, procedural overlap in decision is minimal and justified |
| C-2: No delegation.md changes | Satisfied | No changes to delegation fragment |

## Positive Observations

- Cross-references to "When Limiting Agent Scope" and "When Agent Context Has Conflicting Signals" are accurate (verified: lines 17 and 302 of orchestration-execution.md)
- Skill content uses imperative form consistently ("Extract", "Include", "Do NOT include")
- Summary table in SKILL.md updated to reflect new dispatch rule — good internal consistency
- Memory-index keywords are sufficient for recall discovery: "cycle-scoped", "prompt composition", "extraction" all match the topic space
