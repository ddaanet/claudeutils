# Outline Review: orchestrate-evolution

**Artifact**: plans/orchestrate-evolution/outline.md
**Date**: 2026-02-10T17:15:00-08:00
**Mode**: review + fix-all

## Summary

The outline has been updated since review-2 to replace `agent-core/bin/check-step.sh` references with skill-script approach and add refactor agent behavior constraints. The outline remains architecturally sound with 7 key decisions, 4 resolved questions, and binding orchestration principles.

**Overall Assessment**: Ready

## Requirements Traceability

The requirements document is skeletal (3 open questions, no explicit FR/NFR). The gap analysis provides concrete specifications (7 functional + 3 non-functional requirements).

### Requirements Source Mapping

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| "Absorb planning into orchestrate" | Q-1 resolution, D-2, D-6 | Complete | Planning mode + execution mode |
| "Finalize phase pattern" | D-5 | Complete | Post-step verify-remediate protocol |
| Gap FR-1: Parallel step dispatch | D-4 | Complete | First-class parallel dispatch with groups |
| Gap FR-2: Post-step remediation | D-5 | Complete | Resume step agent with fallback |
| Gap FR-3: RCA task generation | D-5 step 6 | Complete | After any remediation |
| Gap FR-4: Delegation prompt deduplication | D-6 | Complete | Plan-specific agents ARE deduplication |
| Gap FR-5: Commit instruction in prompts | D-2 | Complete | Plan-specific agent "Clean tree requirement" footer |
| Gap FR-6: Scope constraint in prompts | D-2 | Complete | File references + prose "execute ONLY this step" reinforcement |
| Gap FR-7: Precommit verification | D-5 step 1 | Complete | `just precommit` in verify step |
| Gap NFR-1: Context bloat mitigation | D-2, D-6 | Complete | File references, no inline content |
| Gap NFR-2: Backward compatibility | Q-4 | Complete | Clean break, no compatibility |
| Gap NFR-3: Weak orchestrator preservation | D-1 | Partial | Sonnet replaces haiku, but mechanical checks preserved |

**Traceability Assessment**: All requirements covered (11 complete, 1 partial).

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None — all issues from review-2 have been addressed.

## Fixes Applied

No fixes applied (outline already correct).

## Positive Observations

**Improvements since review-2:**
- Skill-script approach correctly replaces centralized `agent-core/bin/check-step.sh`
- Refactor agent behavior constraints added to Key Orchestration Principles (deslop directives, factorization before splitting, resume pattern)
- All 7 issues from review-2 remain fixed

**Architectural soundness:**
- D-2 (file references only) prevents context bloat effectively
- D-6 (plan-specific agents as deduplication) reuses existing mechanism elegantly
- D-5 (resume step agent first with fallback) leverages agent context for self-remediation
- Two-tier context injection (D-3) matches execution vs review needs
- Refactor agent constraints prevent mechanical splitting without quality improvement

**Scope discipline:**
- Out of scope section correctly defers plan-skill rewrites
- In scope section is concrete and actionable
- Skill-script approach keeps orchestrate skill self-contained

**Clarity:**
- All 4 open questions resolved with clear decisions
- "Key Orchestration Principles" provides binding constraints
- Agent context tier table specifies exactly what each agent receives
- Q-1 planning mode breakdown into 9 steps is concrete and executable

## Recommendations

**For planner:**
- Agent context tier table is critical reference — expand during planning with concrete examples
- Planning mode error handling needs specification (UNFIXABLE in design-vet-agent → escalate path)
- D-5 context > 100k token check needs concrete measurement approach (how does orchestrator measure before resume decision?)
- Verification script implementation pattern: consider reusable pattern for future skills (skill-local scripts vs centralized bin/)

**For implementation:**
- Test planning mode end-to-end: 9 steps with multiple restart boundaries is complex orchestration
- Validate parallel dispatch with real Task tool batching (session learnings showed sequential launch pattern breaking parallelism)
- Verify refactor agent behavior with deslop directives — may need example-heavy skill file

---

**Ready for user presentation**: Yes
