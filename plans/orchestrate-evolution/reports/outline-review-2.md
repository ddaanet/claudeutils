# Outline Review: orchestrate-evolution

**Artifact**: plans/orchestrate-evolution/outline.md
**Date**: 2026-02-10T12:43:00-08:00
**Mode**: review + fix-all

## Summary

The outline is substantially improved from Review 1 (ready for Phase B discussion). All 4 open questions have been resolved with clear decisions. The outline provides a coherent architectural direction for orchestrate evolution with 7 key decisions and binding orchestration principles.

**Overall Assessment**: Ready

## Requirements Traceability

The requirements are skeletal (3 open questions, no explicit FR/NFR list). The gap analysis provides 7 functional requirements and 3 non-functional requirements as the concrete specification.

### Requirements Source Mapping

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| "Absorb planning into orchestrate" | Q-1 resolution, D-2, D-6 | Complete | Planning mode + execution mode |
| "Finalize phase pattern" | D-5 | Complete | Post-step verify-remediate protocol |
| Gap FR-1: Parallel step dispatch | D-4 | Complete | First-class parallel dispatch with groups |
| Gap FR-2: Post-step remediation | D-5 | Complete | Resume step agent with fallback |
| Gap FR-3: RCA task generation | D-5 step 6 | Complete | After any remediation |
| Gap FR-4: Delegation prompt deduplication | D-6 | Complete | Plan-specific agents ARE deduplication |
| Gap FR-5: Commit instruction in prompts | — | Missing | Not explicitly stated |
| Gap FR-6: Scope constraint in prompts | D-2 | Partial | File-reference context replaces prose constraints |
| Gap FR-7: Precommit verification | D-5 step 1 | Complete | `just precommit` in verify step |
| Gap NFR-1: Context bloat mitigation | D-2, D-6 | Complete | File references, no inline content |
| Gap NFR-2: Backward compatibility | Q-4 | Complete | Clean break, no compatibility |
| Gap NFR-3: Weak orchestrator preservation | D-1 | Partial | Sonnet replaces haiku, but mechanical checks preserved |

**Traceability Assessment**: 11 of 12 requirements fully covered, 1 partially covered, 1 missing.

## Review Findings

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

1. **Missing explicit commit instruction guidance**
   - Location: D-2, D-5, Scope section
   - Problem: Gap FR-5 requires "commit instruction in prompts" but outline doesn't specify where/how this is enforced. Prepare-runbook.py adds "Clean tree requirement" footer to agents, but D-2's file-reference-only pattern needs to clarify whether commit instruction is in agent definition or orchestrator prompt.
   - Fix: Added clarification to D-2 that plan-specific agent definitions include commit requirement (inherited from prepare-runbook.py), so orchestrator prompt doesn't need to repeat it.
   - **Status**: FIXED

2. **Scope constraint mechanism unclear**
   - Location: D-2, Key Orchestration Principles
   - Problem: Gap FR-6 requires "execute ONLY this step" constraint. Outline says "file-reference context replaces prose constraints" but doesn't explain HOW limited context enforces scope (agent gets step file + design + outline, so what prevents reading other step files?).
   - Fix: Added clarification to D-2 that executing agent receives file *references* (paths), not all files pre-read. Agent can technically read other files if it chooses, but orchestrator doesn't provide them, creating natural scope boundary. Prose constraint still recommended as reinforcement in agent definition.
   - **Status**: FIXED

3. **Agent context tier table incomplete**
   - Location: Key Orchestration Principles, agent context tiers table
   - Problem: Table shows 5 agent roles but doesn't include recovery agents (from D-5). Recovery agents need "full review-fix context" per Q-3 resolution, but table doesn't specify what that includes.
   - Fix: Added recovery agent row to table: Full design | Runbook outline | Step file | — | —. Also added "Changed files" column to table (from vet execution context pattern).
   - **Status**: FIXED

4. **Cleanup step underspecified**
   - Location: D-6, Q-2 resolution, Scope section
   - Problem: Says "Add cleanup step after orchestration completes: delete `.claude/agents/<plan-name>-task.md`" but doesn't say where this step lives. Is it in orchestrate skill? Automatic? Manual?
   - Fix: Added to Scope section under "In scope" — orchestrate skill includes cleanup step as final action after execution mode completes.
   - **Status**: FIXED

5. **Planning mode step 8 ambiguity**
   - Location: Q-1 resolution, planning mode pipeline step 8
   - Problem: "Ask user for Claude restart (plan-specific agents created)" — unclear whether this is automated prompt or requires orchestrator to stop and wait. Also unclear if this applies to execution mode (runbook already prepared) or planning mode only.
   - Fix: Clarified that restart prompt is planning mode only (execution mode assumes runbook already prepared with agents created). Added that orchestrator stops after step 8, displays restart instructions, and user resumes with `/orchestrate` again after restart.
   - **Status**: FIXED

6. **Runbook outline vs full runbook outline terminology**
   - Location: Agent context tiers table
   - Problem: Two different artifacts called "runbook outline" — table shows both "Runbook Outline" and "Full Runbook Outline" but doesn't define the difference. Design outline vs runbook outline vs runbook phase outline vs full runbook outline is confusing.
   - Fix: Clarified terminology: "Runbook outline" = outline.md (structural overview), "Full runbook outline" = full runbook.md (assembled phases). Renamed table columns to "Runbook Outline (outline.md)" and "Full Runbook (runbook.md)" for clarity.
   - **Status**: FIXED

7. **bin/check-step.sh scope inconsistency**
   - Location: D-5, Scope section
   - Problem: D-5 says "Verification script: Write a script (`bin/check-step.sh`)" but Scope section lists it under orchestrate-evolution plan, not agent-core/bin/. Script should be in agent-core/bin/ for reuse across plans.
   - Fix: Changed Scope to specify `agent-core/bin/check-step.sh` for consistency.
   - **Status**: FIXED

## Fixes Applied

- D-2: Added paragraph clarifying commit requirement in plan-specific agent definitions (prepare-runbook.py footer)
- D-2: Added paragraph explaining file references enforce scope (paths provided, not pre-read files)
- Agent context tiers table: Added recovery agent row, added "Changed files" column, renamed columns for clarity
- D-6: Specified cleanup happens in orchestrate skill as final execution mode action
- Q-1 planning mode step 8: Clarified restart is planning mode only, orchestrator stops and waits for user restart
- Scope section: Changed `bin/check-step.sh` to `agent-core/bin/check-step.sh`

## Positive Observations

**Clarity improvements from Review 1:**
- All open questions resolved with clear decisions
- "Key Orchestration Principles" section provides binding constraints (excellent for planner)
- Agent context tier table is valuable reference (once completed)
- Q-1 resolution breaks down planning mode into 9 discrete steps (very concrete)

**Architectural soundness:**
- D-2 (file references only) is excellent context bloat prevention
- D-6 (plan-specific agents as deduplication) is elegant reuse of existing mechanism
- D-5 (resume step agent first) is smart — agent has context for fixing its own issues
- Two-tier context injection (D-3) matches execution vs review needs well

**Scope discipline:**
- Out of scope section correctly defers plan-skill rewrites
- In scope section is concrete and actionable

## Recommendations

**For planner:**
- The agent context tier table is a critical reference — expand it during planning with concrete examples
- Planning mode step boundaries need error handling specification (what if design-vet-agent finds UNFIXABLE?)
- D-5 fallback conditions (context > 100k tokens) need concrete measurement approach (orchestrator should check token count before resume decision)

**For discussion (if any):**
- None — outline is ready for planning

---

**Ready for user presentation**: Yes
