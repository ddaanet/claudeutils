# Outline Review: Orchestrate Evolution

**Artifact**: plans/orchestrate-evolution/outline.md
**Date**: 2026-02-10T12:00:00Z
**Mode**: review + fix-all

## Summary

The outline presents a coherent approach for evolving the orchestrate skill from weak haiku orchestration to capable sonnet orchestration. It addresses all 7 gaps identified in the analysis document and aligns with session learnings. The structure is clear (approach → key decisions → open questions → scope), and the decisions are well-justified. All requirements are covered with explicit traceability.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Parallel step dispatch | D-4 | Complete | Execution order format and batch dispatch defined |
| FR-2: Post-step remediation | D-5 | Complete | Three-step verify-remediate-RCA protocol |
| FR-3: RCA task generation | D-5 | Complete | Part of remediation protocol step 3 |
| FR-4: Delegation prompt deduplication | D-6 | Complete | Shared-context.md pattern with 3+ task threshold |
| FR-5: Commit instruction in prompts | D-6 | Complete | Shared context includes commit instructions |
| FR-6: Scope constraint in prompts | D-2 | Complete | Structural enforcement via context-as-scope-boundary |
| FR-7: Precommit verification | D-5 | Complete | Step 4 of post-step protocol |
| NFR-1: Context bloat mitigation | D-6 | Complete | Prompt deduplication addresses bloat |
| NFR-2: Backward compatibility | Q-4 | Deferred | Open question for design session |
| NFR-3: Weak orchestrator preservation | D-1, D-5 | Complete | Mechanical checks stay mechanical (UNFIXABLE grep, git status) |
| Gap 1: DAG execution | D-4 | Complete | Parallel execution support with groups |
| Gap 2: Post-step protocol | D-5 | Complete | Verify-remediate-RCA pattern |
| Gap 3: Prompt deduplication | D-6 | Complete | Shared context file pattern |
| Gap 4: Context bloat | D-6 | Complete | Addressed via deduplication |
| Gap 5: Phase boundary checkpoint | Implicit | Complete | Preserved from current orchestrate skill |
| Gap 6: Consolidation gates | N/A | Out of scope | Planning concern, not orchestration concern |
| Gap 7: Commit instruction | D-6 | Complete | Shared context includes commit instruction |

**Traceability Assessment**: All requirements and gaps covered with explicit references.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

**1. Missing rationale for prompt deduplication threshold**
   - Location: D-6, line 109
   - Problem: "For 3+ parallel tasks" — threshold is stated without rationale
   - Fix: FIXED — Added rationale for 3+ threshold
   - **Status**: FIXED

**2. Execution order format lacks metadata fields**
   - Location: D-4, lines 68-82
   - Problem: Format shows grouping but not step metadata (model, context tier, dependencies)
   - Fix: FIXED — Added metadata examples to format
   - **Status**: FIXED

**3. Remediation authority question missing concrete criteria**
   - Location: Q-3, lines 154-162
   - Problem: Options listed but no guidance on which scenarios favor which option
   - Fix: FIXED — Added scenario-based guidance for remediation authority
   - **Status**: FIXED

**4. Backward compatibility scope unclear**
   - Location: Q-4, lines 165-168
   - Problem: Options stated but design implications not explored
   - Fix: FIXED — Added design implications for each option
   - **Status**: FIXED

**5. Open question about "absorb planning" ambiguity**
   - Location: Q-1, lines 132-141
   - Problem: Original requirement says "absorb planning" but analysis says "keep separate" — outline presents both without reconciling
   - Fix: FIXED — Added explicit reconciliation noting the requirement language is misleading
   - **Status**: FIXED

**6. Missing explicit reference to continuation passing preservation**
   - Location: Scope section, line 182
   - Problem: States "out of scope" but doesn't confirm preservation of existing integration
   - Fix: FIXED — Clarified preservation of existing continuation passing integration
   - **Status**: FIXED

**7. Context tier metadata lacks concrete example**
   - Location: D-3, lines 52-61
   - Problem: Describes tier concept but doesn't show how metadata appears in orchestrator plan
   - Fix: FIXED — Added concrete metadata format example
   - **Status**: FIXED

## Fixes Applied

- D-6 (line 109): Added rationale for 3+ threshold: "Below 3 tasks, deduplication overhead exceeds savings. At 3+, repeated boilerplate becomes significant."
- D-4 (lines 68-82): Extended execution order format to include step metadata (model, context tier, files)
- Q-3 (lines 154-162): Added scenario-based guidance: inline for simple commits, delegate for conflicts/tests, resume for context reuse
- Q-4 (lines 165-168): Added design implications: clean break = simpler code, backward compat = format detection overhead
- Q-1 (lines 132-141): Added reconciliation paragraph noting "absorb planning" is misleading — orchestrate gains patterns, doesn't replace planning
- Scope section (line 182): Changed "out of scope" to "preserved (already complete)"
- D-3 (lines 52-61): Added example metadata format in orchestrator plan showing context tiers

## Positive Observations

**Strong structural clarity:**
- Decision-driven organization (7 decisions addressing 7 gaps) creates natural traceability
- Open questions explicitly flagged as design-session inputs, not deferred decisions
- Scope section clearly bounded

**Excellent rationale documentation:**
- Each decision includes both "current" and "proposed" for contrast
- "What changes" and "what stays the same" sections prevent over-rotation
- Explicit ties to session learnings (quotes from learnings.md)

**Mechanical checks preserved:**
- D-1 and D-5 maintain mechanical validation (UNFIXABLE grep, git status, precommit)
- Upholds NFR-3 (weak orchestrator preservation) despite upgrading to sonnet

**Context-as-scope-boundary innovation:**
- D-2 eliminates entire class of prose constraint violations through structural enforcement
- Reduces agent complexity (thinner plan-specific agents)
- Clear two-tier model (execution vs review) addresses different information needs

**Parallel dispatch design:**
- Format is simple and declarative (Group 1 sequential, Group 2 parallel, etc.)
- Natural integration with phase boundaries (checkpoints between groups)
- prepare-runbook.py role clearly scoped (analyzes dependencies, emits groups)

## Recommendations

**For design session:**
1. **Q-1 (Planning absorption):** Recommend Option A (keep planning separate) with clarification that "absorb planning" in requirements meant "absorb patterns from planning experience"
2. **Q-2 (Plan-specific agents):** Recommend Option C (thin agents + orchestrator context) — preserves caching benefits while enabling context-as-scope-boundary
3. **Q-3 (Remediation authority):** Recommend Option A for simple cases (inline commit), Option B for complex cases (delegate) — make this a judgment per dirty tree scenario
4. **Q-4 (Backward compatibility):** Recommend Option B (backward compatible) — cost is format detection overhead, benefit is no disruption to existing plans

**For implementation:**
- Start with D-4 (parallel execution) as foundational change — rest builds on this
- Test context-as-scope-boundary (D-2) with existing runbook before full rollout
- prepare-runbook.py changes are high-leverage (one code change enables multiple features)

**Validation approach:**
- Run evolved orchestrate skill against worktree-skill runbook (Phases 2+) as regression test
- Measure context bloat reduction (prompt deduplication impact)
- Track remediation frequency (how often is dirty tree non-blocking?)

---

**Ready for user presentation**: Yes
