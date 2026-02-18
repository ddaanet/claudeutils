# Outline Review: worktree-merge-resilience

**Artifact**: plans/worktree-merge-resilience/outline.md
**Date**: 2026-02-18
**Mode**: review + fix-all

## Summary

The outline is well-structured with clear decisions, explicit scope boundaries, and phase typing. Three gaps existed: NFR-2 (no data loss) was only implicit in D-3, C-2 (agent capability) was unaddressed, and FR-4's Phase 4 lacked specificity on output content. All fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | D-2, D-6, Phase 2 | Complete | Submodule conflict pass-through with explicit `check=False` |
| FR-2 | D-3, Phase 3 | Complete | Abort removal, merge state preservation |
| FR-3 | D-4, Phase 3 | Complete | Content comparison approach, retry after removal |
| FR-4 | Phase 4 | Complete | Was partial — added output contract detail (file list, diff stats, divergence, hint) |
| FR-5 | D-5, Phase 1 | Complete | 5-state machine with routing |
| NFR-1 | D-1, Phase 5 | Complete | Exit code 3 = conflicts need resolution |
| NFR-2 | D-3, D-7 | Complete | Was implicit — added D-7 cross-cutting invariant |
| C-1 | Affected Files, Phase 5 | Complete | SKILL.md Mode C update |
| C-2 | D-8, Phase 5 | Complete | Was missing — added D-8 and Phase 5 note |

**Traceability Assessment**: All requirements covered. Three gaps identified and fixed (NFR-2, C-2, FR-4 detail).

## Review Findings

### Critical Issues

None.

### Major Issues

1. **NFR-2 not explicitly traced**
   - Location: Key Decisions, Scope Boundaries
   - Problem: "No data loss on any code path" was only implied by D-3's description of removing `--abort` + `clean -fd`. No explicit decision or scope entry.
   - Fix: Added D-7 as cross-cutting invariant; added NFR-2 to Scope Boundaries IN list.
   - **Status**: FIXED

2. **C-2 (agent capability) not addressed**
   - Location: entire outline
   - Problem: Constraint requiring non-interactive resolution compatibility had no coverage. Output format decisions affect whether agents can parse and act on conflict reports.
   - Fix: Added D-8 specifying structured stderr output with relative paths; added C-2 to Phase 5 and Scope Boundaries IN list.
   - **Status**: FIXED

3. **FR-4 Phase 4 lacked output specifics**
   - Location: Phase Typing, Phase 4
   - Problem: Phase 4 said only "Output contract" without enumerating what the requirements specify (conflict type, diff stats, divergence, hint).
   - Fix: Expanded Phase 4 description to list all four output components from FR-4 acceptance criteria.
   - **Status**: FIXED

### Minor Issues

1. **D-3 lacked explicit FR/NFR tags**
   - Location: D-3 decision text
   - Problem: D-3 described the FR-2 fix but didn't reference FR-2 or NFR-2 by identifier.
   - Fix: Added "(FR-2, NFR-2)" to D-3 header and appended "No code path discards staged auto-resolutions or working tree state."
   - **Status**: FIXED

## Fixes Applied

- D-3 — Added FR-2/NFR-2 tags and explicit no-discard statement
- After D-6 — Added D-7 (NFR-2 cross-cutting data loss invariant)
- After D-6 — Added D-8 (C-2 non-interactive agent compatibility)
- Phase 4 — Expanded output contract to enumerate all FR-4 acceptance criteria items
- Phase 5 — Added C-2 reference and machine-parseability verification note
- Scope Boundaries IN — Added NFR-2 and C-2 entries

## Positive Observations

- State machine design (D-5) with 5 explicit states provides clear resume semantics
- Open Questions section resolves both requirements Q-1 and Q-2 with rationale, linking to decisions D-4 and D-1
- Phase typing is well-chosen: TDD for behavioral logic (Phases 1-4), General for exit code threading + docs (Phase 5)
- Exploration report provides thorough code analysis grounding the design decisions

## Recommendations

- During design elaboration, specify the structured output format for FR-4 (stderr template/schema) to ensure C-2 compatibility
- Consider whether Phase 1 clean-tree validation needs relaxation for resume scenarios (D-5 `parent_conflicts` state implies dirty tree)
- The exploration report notes justfile has parallel merge logic — confirm whether justfile changes are in scope or if only Python merge.py is modified

---

**Ready for user presentation**: Yes
