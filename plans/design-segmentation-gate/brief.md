# Design Segmentation Gate

## Problem

Multi-sub-problem designs (like handoff-cli-tool with 3 independent subcommands + shared infra) proceed through design as one unit, then execute and review as one unit. Deliverable review of ~6000 lines generates ~8 minors per full-scope pass. Fix cycles resolve old minors but new ones appear at the same rate — convergence stalls.

The multi-sub-problem learning says "together through design, split after design." But no gate enforces the split. The outline exits design as one plan, enters runbook as one plan, and arrives at deliverable review as one 51-file surface.

## Proposal

Add a segmentation gate after design finalization (outline reviewed) and before runbook generation. When the outline contains independently-scoped sub-problems:
- Split into separate plans per sub-problem
- Each gets own lifecycle, own deliverable review scope
- Shared infrastructure either gets its own plan or is reviewed as part of the first consumer

## Open Questions

- Where does the gate live? Design skill step, outline-corrector check, or new reviewer?
- What criteria trigger the split? Number of sub-problems? Total estimated deliverable count? Independence of scope sections?
- How does the parent plan transition? `designed` (terminal) with child plan references?
- Should this reuse outline-corrector (already reviews outlines post-A.5) or be a separate mechanism?

## Context

- Evidence: handoff-cli-tool RC9→RC15 (15 review rounds, convergence on minors after RC12)
- Learning: "When multi-sub-problem plans reach design" in learnings.md
- Related: outline-corrector already reviews outlines — could extend rather than build new
