# Step 3.2 Self-Review: vet-requirement.md Updates

**File:** `agent-core/fragments/vet-requirement.md`
**FRs:** FR-9 (UNFIXABLE validation), FR-10 (execution context enforcement)

## Changes Applied

**1. Four-status taxonomy (FR-9)**
- "Three issue statuses" updated to "Four issue statuses"
- Added OUT-OF-SCOPE status between DEFERRED and UNFIXABLE
- All four status descriptions aligned with `agent-core/agents/vet-taxonomy.md`
- Added cross-reference to taxonomy file for subcategory codes and investigation format
- Added clarification paragraph distinguishing OUT-OF-SCOPE from DEFERRED

**2. UNFIXABLE validation steps (FR-9)**
- Detection steps expanded from 5 to 6 with validation-then-resume flow
- Added concrete validation checklist: subcategory code, investigation summary (4 gates), scope OUT cross-reference
- Added resume protocol with specific reclassification guidance examples
- Changed "ALL UNFIXABLE issues" to "ALL validated UNFIXABLE issues" in anti-pattern

**3. Execution context enforcement (FR-10)**
- Required context fields header now includes enforcement language: "must be structured lists, not empty prose. Fail loudly if any field is missing or contains only placeholder text"
- Each field strengthened with specificity requirements (IN: concrete artifacts; OUT: matchable against findings; Changed files: non-empty; Requirements: specific FRs)
- Delegation template updated: IN/OUT now show nested structured lists with concrete examples
- Changed files and requirements fields now show structured list format
- Added enforcement paragraph: orchestrator must halt if fields incomplete

## Verification

- Four statuses match vet-taxonomy.md exactly (FIXED, DEFERRED, OUT-OF-SCOPE, UNFIXABLE)
- Subcategory codes referenced (U-REQ, U-ARCH, U-DESIGN) match taxonomy
- Investigation summary 4-gate format matches taxonomy
- Resume protocol is concrete: specifies when to resume and what guidance to provide
- Execution context enforcement uses "must" language and specifies fail conditions
- Template shows structured IN/OUT with nested bullet examples

## Alignment Check

- FR-9 satisfied: UNFIXABLE validation with subcategory check, investigation summary check, scope OUT cross-reference, and resume-for-reclassification protocol
- FR-10 satisfied: structured field requirements, fail-loudly enforcement, concrete template with examples
- No conflicts with existing vet process (steps 1-5 in main process unchanged)
- Taxonomy reference points to correct location (`agent-core/agents/vet-taxonomy.md`)
