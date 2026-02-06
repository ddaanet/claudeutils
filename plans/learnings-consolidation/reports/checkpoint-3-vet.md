# Vet Review: Phase 3 Checkpoint (Agent Definitions)

**Scope**: remember-task agent, memory-refactor agent (agent-core/agents/)
**Date**: 2026-02-06T15:30:00
**Mode**: review + fix

## Summary

Phase 3 introduces two new agents for learnings consolidation: remember-task (autonomous consolidation with pre-checks) and memory-refactor (file splitting at 400-line limit). Both agents follow quiet execution pattern and embed required protocols. One critical issue found (missing Bash tool), otherwise agents are well-structured and align with design.

**Overall Assessment**: Needs Minor Changes (critical fix applied, minor improvements noted)

## Issues Found

### Critical Issues

1. **Memory-refactor missing Bash tool access**
   - Location: agent-core/agents/memory-refactor.md:6
   - Problem: Agent executes `validate-memory-index.py` in step 5 but Bash not in tools list. This would cause runtime failure when agent attempts to run the validator script.
   - Fix: Add "Bash" to tools array
   - **Status**: FIXED

### Major Issues

None found.

### Minor Issues

1. **Conservative bias documented twice in remember-task**
   - Location: agent-core/agents/remember-task.md:58, 83
   - Note: Conservative bias principle stated in each pre-check section AND in summary section after check 3. This is acceptable for clarity but slightly redundant.

2. **Memory-refactor size targets could be more explicit**
   - Location: agent-core/agents/memory-refactor.md:97-100
   - Note: "Balanced distribution" heuristic is good but could specify that all new files should be within 100-300 range, not just average. Current text: "New files: 100-300 lines each (balanced distribution)" is actually clear enough.

3. **Filename pattern examples are consistent**
   - Location: agent-core/agents/memory-refactor.md:60, 94
   - Note: Examples use consistent pattern (`workflow-advanced-tdd.md`), good for clarity.

4. **Report section ordering consistent**
   - Location: agent-core/agents/remember-task.md:138-185
   - Note: Report structure documented in logical order (summary → decisions → escalations → consolidation details). Well-organized.

5. **Input format examples clear**
   - Location: agent-core/agents/remember-task.md:20-40, memory-refactor.md:18-32
   - Note: Both agents provide clear example inputs showing expected format. Good for agent understanding.

## Fixes Applied

- agent-core/agents/memory-refactor.md:6 — Added "Bash" to tools array to support validate-memory-index.py execution

## Requirements Validation

**Design decision alignment:**

| Decision | Status | Evidence |
|----------|--------|----------|
| D-4: Embedded protocol | Satisfied | remember-task.md:89-90 (source comment), lines 94-133 (protocol steps 1-4a embedded) |
| D-5: Pre-consolidation checks | Satisfied | remember-task.md:47-86 (3 checks: supersession, contradiction, redundancy with thresholds) |
| D-6: Reactive refactoring | Satisfied | memory-refactor.md:9-18 (triggering context), lines 37-81 (6-step process) |
| NFR-2: Sonnet model | Satisfied | Both agents: model: sonnet in frontmatter |
| NFR-3: Report location | Satisfied | remember-task.md:189 (tmp/consolidation-report.md), memory-refactor.md:126 (filepath list) |

**Protocol embedding verification:**

Compared remember-task.md consolidation protocol (lines 94-133) against design requirement (extract remember skill steps 1-4a):

| Skill Step | Agent Section | Status |
|------------|---------------|--------|
| 1. Understand Learning | Line 94-96 | ✓ Present, faithful |
| 2. File Selection | Line 98-106 | ✓ Present, routing preserved |
| 3. Draft Update | Line 107-120 | ✓ Present, principles preserved |
| 4. Apply + Verify | Line 122-126 | ✓ Present, Edit/Write/Read pattern |
| 4a. Discovery Updates | Line 128-133 | ✓ Present, memory index + CLAUDE.md + rules |

**Pre-check thresholds verification:**

| Check | Threshold | Location | Status |
|-------|-----------|----------|--------|
| Supersession | >50% keyword overlap + negation | Line 55 | ✓ Specified |
| Redundancy | >70% phrase overlap | Line 76 | ✓ Specified |
| Contradiction | Semantic comparison | Line 60-68 | ✓ Algorithm clear |

**Conservative bias:**
- Line 83-86: Explicit guidance for all three checks
- Escalation preferred over silent errors: ✓

**Refactoring process verification:**

Memory-refactor agent 6-step process (lines 37-81):
1. Read and Analyze: ✓ H2/H3 boundaries, dependencies
2. Identify Split Points: ✓ Heuristics (H2 first, then H3, 100-300 lines)
3. Create New Files: ✓ Filename pattern, preserve structure
4. Update Original File: ✓ Cross-references, preserve preamble
5. Run Validator Autofix: ✓ validate-memory-index.py with autofix expectations
6. Verify Integrity: ✓ Content preservation, size targets, validation

**Gaps:** None identified.

---

## Positive Observations

**Remember-task agent:**
- Clear separation between pre-checks (lines 47-86) and consolidation protocol (lines 88-133)
- Conservative bias principle explicitly documented with concrete guidance
- Report structure comprehensive (6 sections covering all escalation cases)
- Quiet execution pattern correctly implemented (filepath return, no content in response)
- Source tracking comment enables protocol synchronization maintenance
- Pre-check algorithms concrete enough to implement (thresholds, keyword overlap, phrase matching)

**Memory-refactor agent:**
- 6-step process is logical and complete (read → identify → create → update → validate → verify)
- Heuristics for split points are clear (H2 boundaries first, preserve semantic groupings)
- Content preservation constraints explicit (no summarization, no pruning)
- Validator autofix integration documented with expectations
- Output format shows line counts for transparency
- Return protocol appropriate for multi-file operations (one filepath per line)

**Cross-agent consistency:**
- Both use quiet execution pattern (report to file, return filepath)
- Both use sonnet model (per NFR-2)
- Both have clear role statements and input specifications
- Both follow consistent frontmatter structure

**Design anchoring:**
- Remember-task faithfully embeds remember skill protocol (steps 1-4a)
- Pre-check algorithms match D-5 specification (supersession, contradiction, redundancy)
- Memory-refactor implements D-6 reactive refactoring (triggered by file limit)
- Conservative bias principle from D-5 correctly applied

## Recommendations

**Protocol synchronization:**
- When remember skill updates, check source comment in remember-task.md (line 89) and verify protocol sections (lines 94-133) match new skill version
- Consider adding skill version tracking (e.g., "Source: remember SKILL.md v2.1") if protocol changes become frequent

**Pre-check algorithm refinement:**
- Current thresholds (50% keyword overlap, 70% phrase overlap) are reasonable starting points
- Monitor false positive/negative rates in production and adjust thresholds if needed
- Consider documenting threshold rationale (why 50% vs 40% or 60%) if values change

**Memory-refactor edge cases:**
- Current implementation handles standard cases (oversized files with clear H2/H3 boundaries)
- Edge case: Files with single topic (no logical split points) — agent should escalate rather than force split
- Edge case: Files with >600 lines after first split — agent may need second round (mentioned in constraints but not in process)

**Testing coverage:**
- Phase 4 tests focus on learning-ages.py and integration validation
- Consider adding agent definition validation tests (parse frontmatter, verify section presence) if agent structure becomes more complex
