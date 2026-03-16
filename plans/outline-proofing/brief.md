## 2026-03-14: Outline proofing — three insertion points, one principle

### Root Cause

No planning artifact should proceed to the next pipeline stage without user validation. Currently three gaps:

1. **/design Moderate** skips outline entirely — routes directly to /runbook or /inline. Scope validated only by brief.md (session handoff artifact, not code-grounded).
2. **/runbook Tier 2** writes `runbook.md` (cycle decomposition) and chains to /inline without any review gate. Tier 2's only self-check is "consolidation self-check" (planner reviewing own output — weakest gate).
3. **/runbook Tier 3** runbook outline goes through automated review (outline-corrector, runbook-simplifier) but not /proof. User sees expanded phases at Phase 3.25 — after expensive expansion work that's wasted if outline decomposition was wrong.

### Evidence (this session)

During /design of remove-fuzzy-recall (Moderate classification):
- Brief specified 2 fuzzy paths in resolver.py; code inspection found 3 (`_find_heading()` fuzzy fallback missed)
- Brief missed validator dependency entirely (`memory_index_checks.py`, `memory_index.py` also use fuzzy matching and must enforce exact before resolver relies on it)
- Tier assessment changed from 1 (~3-4 files) to 2 (~6-8 files) mid-execution
- User caught both scope gaps during discussion, not during any structured review

Second data point for "when routing moderate classification to runbook" (first: recall-cli-integration).

### Design Direction (from discussion)

**The binary:** Work either needs structured planning (outline + /proof) or doesn't need /runbook. No middle ground where a plan exists but isn't user-validated.

**Brief captures intent; outline captures scope after code reading.** The outline forces structured discovery (reading affected code, enumerating files, identifying dependencies). Brief.md is written from session context without code inspection — it's a different artifact with different completeness guarantees.

**Two proof targets are independent:** Design outline captures "what to change." Runbook outline captures "how to decompose and sequence." Proofing "what" doesn't validate "how."

### Proposed Changes

**Pattern at every level:** outline → outline-corrector (automated) → /proof (user validation) → next stage. Automated review catches mechanical issues before user sees it.

**Skill: /design (SKILL.md)**
- Moderate routing: generate lightweight outline → outline-corrector → /proof → route
- Eliminate Tier 1 from /runbook (collapses to /inline after design proof)

**Skill: /runbook (SKILL.md)**
- Tier 2: produce `runbook-outline.md` → outline-corrector → /proof → execute via /inline
- Tier 3: add /proof on runbook-outline.md after outline-corrector + runbook-simplifier, before expansion (between Phase 0.95 and Phase 1)

### Recall Entries

- "when routing moderate classification to runbook" — structural incompleteness gap
- "when design ceremony continues after uncertainty resolves" — two-gate pattern (entry + mid-stream)
- "when design resolves to simple execution" — execution readiness gate at sufficiency
- "when checking complexity before expansion" — check BEFORE expansion, callback if wrong
- "when using inline execution lifecycle" — /inline lifecycle wraps Tier 1/2

### Open Questions

None — direction agreed in discussion. Implementation details (exact outline format for Moderate, Tier 2 outline content) are design-phase decisions.
