# Step 3.2 Execution Report

**Step:** Update /plan-adhoc skill with outline and phase-by-phase expansion

**Objective:** Add runbook outline step and phase-by-phase expansion workflow to /plan-adhoc skill

## Changes Made

### 1. Added Point 0.75: Generate Runbook Outline

Location: After Point 0.5, before Point 1

Content:
- Create `plans/<job>/runbook-outline.md` with requirements mapping, phase structure, key decisions, complexity
- Delegate to `runbook-outline-review-agent` (fix-all mode)
- Validation and proceed to phase expansion
- Why outline-first rationale
- Fallback for small runbooks (≤3 phases, ≤10 steps)

### 2. Modified Point 1: Phase-by-Phase Runbook Expansion

Changed from direct task evaluation to phase-by-phase workflow:
- For each phase: generate content → review → apply fixes → finalize
- Generate `runbook-phase-N.md` files
- Delegate to `vet-agent` (review-only mode)
- Planner applies critical/major fixes
- Preserved script evaluation criteria (1.1-1.3)

### 3. Modified Point 2: Assembly and Weak Orchestrator Metadata

Added assembly step:
- Concatenate all phase files into `runbook.md`
- Add Weak Orchestrator Metadata (computed from phases)
- Final consistency check (cross-phase dependencies, step numbering)
- Preserved existing metadata structure

### 4. Modified Point 3: Final Holistic Review

Changed focus to cross-phase review:
- Review assembled runbook (not individual phases)
- Focus on cross-phase issues (numbering, dependencies, metadata)
- Note that individual phases already reviewed
- Preserved fix application policy

### 5. Updated Section Title and Overview

Changed "4-Point Planning Process" to "Planning Process" with overview listing all points (0.5, 0.75, 1, 2, 3, 4)

### 6. Updated Example 2

Rewrote Example 2 to show new workflow:
- Point 0.75: outline generation with review
- Point 1: phase-by-phase expansion (3 phases shown)
- Point 2: assembly and metadata
- Point 3: final holistic review

### 7. Updated Common Pitfalls

Added two new pitfall items:
- Skipping outline generation (Point 0.75) for complex runbooks
- Generating entire runbook monolithically instead of phase-by-phase

## Verification

All changes align with design requirements (design.md lines 422-452):

✓ Point 0.75 creates outline with requirements mapping, phase structure, key decisions, complexity
✓ Outline delegated to runbook-outline-review-agent (fix-all)
✓ Phase-by-phase expansion with per-phase vet-agent reviews
✓ Assembly step concatenates phases and adds metadata
✓ Final review focuses on cross-phase consistency
✓ Fallback documented for small runbooks

## Success Criteria Met

✓ Point 0.75 creates runbook outline
✓ Phase-by-phase expansion with reviews
✓ Assembly step combines phases
✓ Fallback documented for small runbooks

## File Modified

- `agent-core/skills/plan-adhoc/SKILL.md` (in agent-core submodule)

## Status

**Complete** - All changes implemented per design specification. Ready for commit.
