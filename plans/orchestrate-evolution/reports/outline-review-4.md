# Outline Review: orchestrate-evolution

**Artifact**: plans/orchestrate-evolution/outline.md
**Date**: 2026-02-10T22:00:00-08:00
**Mode**: review + fix-all

## Summary

The outline reflects user-directed scope reduction: planning orchestration dropped, parallel execution deferred, simplified from 7 decisions to 4. Agent caching model (D-2) and post-step remediation (D-3) are architecturally sound. Scope reduction is deliberate and documented. All 4 decisions have clear rationale. No technical gaps.

**Overall Assessment**: Ready

## Requirements Traceability

### Requirements Source

The requirements.md is skeletal (3 open questions). The gap analysis (orchestrate-evolution-analysis.md) provides concrete specifications: 7 functional requirements + 3 non-functional requirements derived from learnings analysis.

### Traceability Matrix

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| "Absorb planning into orchestrate" | Q-1 | Resolved | Execution only — planning orchestration deferred |
| "Finalize phase pattern" | D-3 | Complete | Post-step verify-remediate protocol |
| Gap FR-1: Parallel step dispatch | Out of scope | Deferred | `plans/parallel-orchestration/` |
| Gap FR-2: Post-step remediation | D-3 | Complete | Resume step agent with fallback |
| Gap FR-3: RCA task generation | D-3 step 6 | Complete | After any remediation |
| Gap FR-4: Delegation prompt dedup | D-2 | Complete | Plan-specific agents cache design+outline |
| Gap FR-5: Commit instruction | D-2 | Complete | Agent definition footer |
| Gap FR-6: Scope constraint | D-2 | Complete | Structural + prose boundary |
| Gap FR-7: Precommit verification | D-3 step 1 | Complete | Git status + precommit check |
| Gap NFR-1: Context bloat mitigation | D-2, Principles | Complete | File references only, never read content |
| Gap NFR-2: Backward compatibility | Q-4 | Complete | Clean break |
| Gap NFR-3: Weak orchestrator | D-1 | Evolved | Sonnet replaces haiku, mechanical checks stay |

**Traceability Assessment**: All requirements addressed. Planning and parallel dispatch deliberately deferred (documented in Q-1 and out-of-scope). Weak orchestrator evolved to sonnet with mechanical preservation.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

No fixes applied — outline is correct as edited by user. All prior review issues have been addressed.

## Positive Observations

**Architectural coherence:**
- D-1 (sonnet orchestrator) justifies post-step remediation capability
- D-2 (agent caching) eliminates separate prompt deduplication mechanism elegantly
- D-3 (resume step agent first) leverages agent context for self-remediation
- D-4 (sonnet → user escalation) matches new model tier capabilities
- Agent caching model reuses prompt prefix caching without additional infrastructure

**Scope clarity:**
- Q-1 resolution (execution only) has clear rationale — sub-agent limitations make planning delegation impractical
- Q-4 resolution (clean break) justified by no active plans needing preservation
- In scope: 7 concrete deliverables enumerated
- Out of scope: planning orchestration, parallel execution, worktree patterns deferred with rationale

**Execution focus:**
- Verification script as skill-local prepares for plugin migration
- Cleanup step (delete plan-specific agents) prevents `.claude/agents/` accumulation
- Refactor agent constraints (deslop first, factor before split) prevent mechanical file splitting
- Post-step protocol (D-3) provides concrete error recovery path

**Documentation quality:**
- All 4 decisions have clear "Current / Decision / What changes / What stays" structure
- "Key Orchestration Principles" section provides binding constraints for design
- Agent context tier table specifies exactly what each agent receives
- Orchestrator bloat prevention principle addresses NFR-1 directly

## Recommendations

**For design session:**
- Context measurement approach (D-3 step 3): orchestrator needs practical heuristic for "context > 100k" detection — options include message count × avg tokens, API-based measurement, or "defer until resume fails"
- Recovery agent prompt construction: specify exact context assembly (step file + git diff + error state + cached design/outline reference)
- Verification script contract: define input/output format, exit codes, error messaging for git/precommit check
- Multi-phase detection logic: when does prepare-runbook.py create `<plan>-vet.md` (only when runbook has multiple phases?)

**For planning:**
- Agent generation integration: prepare-runbook.py generates both `<plan>-task.md` and `<plan>-vet.md` (multi-phase only) — validate file size with embedded design+outline
- Refactor agent directive content: design.md should include deslop checklist and factorization-before-splitting examples
- Cleanup step timing: orchestrate skill final step after all execution complete — needs agent deletion logic
- Skill-local script pattern: verification script sets precedent for plugin-era architecture (not centralized `agent-core/bin/`)

**For implementation:**
- Test agent caching effectiveness: validate embedded design+outline reuses cached blocks across steps
- Verify resume-first pattern: confirm resumed agent context includes prior messages (not just step file)
- Monitor orchestrator context growth: track message count across 20+ step execution to verify bloat prevention
- Validate cleanup step: ensure orchestrate skill can delete `.claude/agents/` files (permissions, timing, symlink handling)

---

**Ready for user presentation**: Yes
