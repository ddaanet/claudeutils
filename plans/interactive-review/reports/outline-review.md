# Outline Review: interactive-review

**Artifact**: plans/interactive-review/outline.md
**Date**: 2026-03-12
**Mode**: review + fix-all (PDR — post-research rewrite)

## Summary

Well-grounded outline with clear decision rationale traced to Fagan, Phabricator, and cognitive load research. All requirements covered with explicit traceability. Key design decisions (batch-apply, 5 verdicts, orientation phase) are selected with rationale, not left as "explore options." Two major clarity issues (planstate ambiguity, scope IN/OUT revisit contradiction) and three minor issues fixed.

**Overall Assessment**: Ready

## Requirements Traceability

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1 | D-5 (Linear Iteration), D-9 (Mode Selection) | Complete | Item-by-item with auto-detect and explicit flag |
| FR-2 | D-7 (Granularity Detection) | Complete | 6 artifact types with detection patterns + user override |
| FR-3 | D-4 (Per-Item Presentation) | Complete | Domain-relevant recall per item, null recall silent |
| FR-4 | D-1 (Verdict Vocabulary) | Complete | 5 verdicts; `absorb` folded into kill sub-action (grounded in convergence range) |
| FR-5 | D-2 (Batch-Apply) | N/A — Lifted | Batch-apply replaces immediate edits per user direction |
| FR-6 | D-6 (Discuss Sub-Loop) | Complete | Learnings, tasks, artifacts via existing proof mechanics |
| FR-7 | D-8 (Terminal Actions), step 1 | Complete | Summary format: N approved/revised/killed/skipped + cross-item outputs |
| C-1 | Approach, D-9 | Complete | Extension within /proof, not separate skill |
| C-2 | D-6 | Complete | Discuss sub-loop reuses reword-accumulate-sync scoped to one item |

**Traceability Assessment**: All active requirements covered. FR-5 correctly treated as lifted.

## Scope-to-Component Traceability

Single-component design (SKILL.md + reference file). All scope items trace to affected files.

| Scope IN Item | Component | Notes |
|---------------|-----------|-------|
| Item-by-item iteration mode | SKILL.md | D-5 |
| Verdict vocabulary (5 + kill sub-actions) | SKILL.md | D-1 |
| Orientation phase | SKILL.md | D-3 |
| Batch-apply with accumulation | SKILL.md + references/item-review.md | D-2, accumulation format in reference |
| Per-item recall context | SKILL.md | D-4 |
| Granularity detection + override | references/item-review.md | D-7, pattern table |
| Discuss sub-loop | SKILL.md | D-6, reuses existing mechanics |
| Cross-item outputs | SKILL.md | D-6, FR-6 |
| Review summary | SKILL.md | D-8 step 1 |
| Mode selection | SKILL.md | D-9 |
| Linear iteration with revisit | SKILL.md | D-5 |

**Scope Assessment**: All items assigned. No orphans.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **Planstate update ambiguity in D-8**
   - Location: D-8, step 6
   - Problem: "Update planstate" was ambiguous — could imply a new planstate mechanism. Interactive review runs within /proof, which already manages planstate transitions (review-pending on entry, reviewed on exit per SKILL.md lines 33-34 and 72). A separate planstate step suggests duplicated or conflicting state management.
   - Fix: Replaced with explicit statement that interactive review reuses /proof's existing entry/exit transitions
   - **Status**: FIXED

2. **Scope IN/OUT revisit contradiction**
   - Location: Scope IN "Linear iteration with revisit" vs Scope OUT "Random-access navigation"
   - Problem: Revisit IS a form of random access (user says "revisit 3" to jump to item 3). A reader seeing both listings gets contradictory signals. D-5 explains the distinction (no preview of upcoming items, revisit only after completion), but scope lists don't carry that nuance.
   - Fix: Scope IN clarified to "Linear iteration with post-completion revisit (revisit completed items by number, no preview of upcoming)." Scope OUT clarified to "Random-access navigation during iteration (deliberate exclusion per cognitive load research; post-completion revisit is in-scope)."
   - **Status**: FIXED

### Minor Issues

1. **"Open Questions: None" overconfident**
   - Location: Open Questions section
   - Problem: Two implementation-relevant questions exist: (a) batch-apply edit ordering must be bottom-to-top to avoid line-shift (flagged in prior corrector review), (b) grounding report section 4 describes immediate-apply as default, contradicting the outline's batch-only approach. These aren't design-blocking but deserve documentation.
   - Fix: Added two open questions with context: edit ordering as implementation detail, grounding report divergence as documentation note
   - **Status**: FIXED

2. **TOC generation method unspecified**
   - Location: D-3, step 2
   - Problem: "Numbered list with per-item title + one-line summary" — who generates the summary? The agent summarizes each extracted item, but this wasn't explicit. Could be misread as expecting pre-existing summaries in the artifact.
   - Fix: Added "agent-generated" qualifier to TOC summary description
   - **Status**: FIXED

3. **D-7 granularity table includes all 6 artifact types without implementation priority**
   - Location: D-7 table
   - Problem: Source files (function/class) and diff output (hunk markers) represent significantly more parsing complexity than markdown-based types. Table presents all 6 as equivalent implementation targets. Requirements don't exclude them, but implementation ordering matters.
   - Assessment: Not fixed — the table is design-accurate (FR-2 says "adapt item granularity to artifact type" with these types listed). Implementation ordering is a runbook concern, not an outline concern. Noted for runbook planning.
   - **Status**: NOTED (not a fix target — implementation sequencing)

## Fixes Applied

- D-8 step 6 — replaced "Update planstate" with explicit reuse of /proof's existing entry/exit transitions
- Scope IN — clarified "Linear iteration with revisit" to specify post-completion revisit semantics
- Scope OUT — clarified "Random-access navigation" to specify "during iteration" boundary with post-completion revisit carve-out
- Open Questions — replaced "None" with two implementation-relevant questions (edit ordering, grounding report divergence)
- D-3 step 2 — added "agent-generated" qualifier to TOC summary description

## Positive Observations

- **Grounding quality is strong.** Every key decision cites specific frameworks with rationale for adaptation. The grounding report is thorough and the outline references it correctly.
- **FR-5 lift handled cleanly.** D-2 explains the lift, provides rationale (draft-then-submit universality, structural prevention of agent failure pattern), and the accumulation format is explicit and machine-readable.
- **Dogfooding feedback incorporated.** Plain text not blockquote, numbered list not table, orientation phase with checkpoint — all traced to brief.md observations.
- **C-2 satisfaction is elegant.** Discuss sub-loop reuses existing /proof mechanics scoped to one item, rather than inventing new loop structures.
- **Kill sub-actions preserve verdict count.** Folding `absorb` into kill's sub-action flow keeps the vocabulary within the 3-5 convergence range while preserving the capability.

## Recommendations

- During user discussion: confirm `skip` verdict is desired — it's a design addition beyond FR-4 (grounding-justified but not in original requirements)
- Runbook planning should sequence artifact types by implementation complexity: markdown-based types (requirements, outline, design, runbook) first, source files and diffs later
- The `references/item-review.md` file boundary (what goes in SKILL.md vs reference) should be defined during design — the outline correctly identifies the split need but doesn't specify the boundary

---

**Ready for user presentation**: Yes
