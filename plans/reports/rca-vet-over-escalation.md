# RCA: Vet Agent UNFIXABLE Over-Escalation

**Date**: 2026-02-13
**Analyst**: Sonnet
**Status**: Complete

## Executive Summary

Vet agents label straightforward pattern-matching tasks as "UNFIXABLE" requiring design decisions or user input, when solutions are mechanical (find-replace, check existing patterns, apply consistent choice). The workflow-fixes pipeline overhaul unified planning skills but did not address vet judgment calibration. The root cause is **missing UNFIXABLE classification taxonomy** — agents have no documented criteria distinguishing mechanical fixes from truly unfixable issues.

## Problem Statement

Three distinct incidents demonstrate the pattern:

1. **Phase 5 checkpoint (worktree-update):** `create_worktree()` extraction labeled UNFIXABLE as "architectural change" when it was deferred to future phase per design. `_git` naming labeled UNFIXABLE as "expanding beyond scope" when it was mechanical find-replace.

2. **Phase 2 review (worktree-update):** Test file mismatch labeled UNFIXABLE as "design decision needed" when solution was pattern-matching: check existing test files, consolidate to `test_worktree_cli.py`, replace references.

3. **Cycle 0.6 vet (worktree-skill):** Session file filtering labeled UNFIXABLE despite explicit "OUT: Session file filtering (next cycle)" in scope statement.

## Root Cause

**Missing UNFIXABLE classification taxonomy in agent instructions.**

### Evidence from Agent Definitions

**vet-fix-agent.md (lines 333-335):**
```markdown
- If a fix would require architectural changes, mark UNFIXABLE
- If a fix is ambiguous (multiple valid approaches), mark UNFIXABLE
```

**Analysis:** Two classification criteria, both vague:
- "Architectural changes" has no definition — is extracting a function architectural? Is renaming a helper?
- "Ambiguous (multiple valid approaches)" doesn't distinguish "multiple design choices" from "multiple equivalent implementations"

**Missing categories:**
- Deferred work (explicitly out of scope in current phase)
- Mechanical pattern-matching (check existing code, apply consistent choice)
- Scope boundary violations (item is outside provided scope IN/OUT)

### Scope IN/OUT Template Non-Enforcement

**vet-requirement.md (lines 72-73):**
```markdown
- **Scope OUT:** What is NOT yet implemented — do NOT flag these as issues
```

**Execution context fields (line 68):**
- Present in template
- Not validated or enforced in vet-fix-agent.md
- No escalation protocol when OUT items are flagged

**Evidence:** Cycle 0.6 flagged session filtering as UNFIXABLE despite explicit "OUT: Session file filtering (next cycle)" in scope statement. The agent read the scope statement (line 25 references it) but still escalated.

### Taxonomy Absence in Review Criteria

**plan-reviewer.md (lines 103-108):**
```markdown
**UNFIXABLE issues (require escalation):**
- Missing requirements in design (can't invent requirements)
- Fundamental structure problems (need outline revision)
- Cross-phase dependency ordering issues
- Scope conflicts with design decisions
```

**Analysis:** Planning artifacts have specific UNFIXABLE criteria. Implementation artifacts (vet-fix-agent) have only vague guidance. The taxonomy exists for one domain but not the other.

## Contributing Factors

### C1: Workflow-Fixes Scope Exclusion

**workflow-fixes/outline.md (line 28):**
```markdown
**Out of scope:**
- Vet agent deduplication
```

**workflow-fixes/design.md (line 449):**
```markdown
- `agent-core/agents/vet-fix-agent.md` — no changes
```

**Analysis:** Pipeline overhaul unified planning skills and review gates but explicitly excluded vet agent changes. The unification dissolved 6 of 7 architectural gaps (G1-G7) but did not address vet judgment calibration, which was not classified as an architectural gap.

### C2: Agent Treats Uncertainty as Escalation Trigger

**Pattern across all three incidents:**
- Agent encounters item requiring investigation (check existing patterns, verify scope)
- Instead of performing investigation, agent escalates as UNFIXABLE
- Rationale cites "needs design decision" or "expands scope" without attempting pattern-matching

**Example:** Phase 2 test file mismatch labeled UNFIXABLE as "design decision" when solution sequence was:
1. Use Glob to find existing test files: `test_worktree_*.py`
2. Identify pattern: `test_worktree_cli.py` exists
3. Consolidate: replace references to `test_sandbox_registration.py` with `test_worktree_cli.py`
4. No design decision required — apply existing pattern consistently

### C3: No Distinction Between Deferred and Unfixable

**Phase 5 incident:** Design explicitly defers `create_worktree()` extraction to future phase. Vet flags as UNFIXABLE "architectural change."

**Correct classification:** DEFERRED (explicitly out of current phase scope, documented in design)

**Taxonomy gap:** No documented category for "item is out of scope per design" vs "item cannot be done without design revision"

### C4: Scope Boundary Detection Relies on Agent Judgment

**vet-requirement.md delegation template (lines 72-73):**
```markdown
- **Scope OUT:** What is NOT yet implemented — do NOT flag these as issues
```

**Implementation gap:** Template provides OUT list, but no enforcement mechanism:
- No validation that agent respects OUT items
- No detection protocol when OUT items are flagged (analogous to UNFIXABLE grep)
- Agent must use judgment to classify "is this item in OUT scope?" rather than mechanical check

## Classification Taxonomy (Proposed)

### UNFIXABLE Categories

**U1: Missing Requirements**
- Issue cannot be resolved without additional requirements from user
- Design is incomplete or ambiguous on critical decision point
- Example: "Should we use SQLite or PostgreSQL?" when design doesn't specify

**U2: Architectural Change**
- Fix requires changes to module boundaries, data models, or API contracts
- Scope extends beyond localized edits to a single function/class
- Example: Extracting module from monolithic file, changing function signatures used by callers

**U3: Cross-Phase Dependency**
- Issue requires work from a different phase (past or future)
- Cannot be resolved without revisiting earlier work or waiting for later work
- Example: Cycle references data structure created in future cycle

**U4: Scope Conflict with Design**
- Implementation conflicts with explicit design decision
- Fixing would violate documented architectural constraint
- Example: Design says "defer extraction," implementation extracts prematurely

### DEFERRED Categories (NOT unfixable)

**D1: Explicitly Out of Scope**
- Item appears in scope OUT list
- Work is documented as future phase/cycle
- Example: "Session file filtering (next cycle)"

**D2: Design Deviation (Future Phase)**
- Implementation differs from design but design documents deferral
- Future work planned to align with design
- Example: "Design calls for extraction, implementation inlines, future phase will extract"

### MECHANICAL Categories (NOT unfixable)

**M1: Pattern-Matching**
- Solution requires checking existing code for patterns
- Apply consistent choice based on discovered pattern
- Example: Test file naming — check existing `test_*.py` files, apply same convention

**M2: Find-Replace**
- Solution is systematic string replacement across known locations
- No judgment calls beyond "replace all instances"
- Example: Renaming `_git` to `git_helper` — find all call sites, replace

**M3: Scope Alignment**
- Issue is item outside scope IN/OUT boundaries
- Solution is "don't flag it" (remove from report)
- Example: Flagging deferred feature when OUT explicitly lists it

## Evidence Analysis

### Incident 1: Phase 5 Checkpoint

**Issue:** `create_worktree()` not extracted

**Agent classification:** UNFIXABLE (architectural change)

**Actual category:** D2 (Design Deviation - Future Phase)

**Evidence:** Design.md line 34 specifies extraction. Requirements validation table (line 97) shows "Partial" status with note "Logic exists but not extracted (Major Issue #1)." Recommendations section (line 120) states "Phase 6: Extract `create_worktree()` function per design contract."

**Correct action:** Mark as DEFERRED — Phase 6 work, documented in design, not blocking current checkpoint.

---

**Issue:** `_git` naming inconsistent

**Agent classification:** UNFIXABLE (expands beyond scope)

**Actual category:** M2 (Find-Replace)

**Evidence:** 24 call sites in same file. Mechanical find-replace operation. No judgment required beyond "rename consistently."

**Correct action:** Fix directly using Edit tool with `replace_all: true` parameter.

### Incident 2: Phase 2 Review

**Issue:** Test file references don't exist

**Agent classification:** UNFIXABLE (design decision needed)

**Actual category:** M1 (Pattern-Matching)

**Solution sequence:**
1. Glob existing test files: `tests/test_worktree_*.py`
2. Identify `test_worktree_cli.py` exists
3. Consolidate references to existing file
4. Edit phase file: replace `test_sandbox_registration.py` with `test_worktree_cli.py`

**No design decision required** — apply existing pattern.

### Incident 3: Cycle 0.6 Vet

**Issue:** Session file filtering not implemented

**Agent classification:** UNFIXABLE (out of scope for cycle)

**Actual category:** D1 (Explicitly Out of Scope) — BUT should not be flagged at all

**Evidence:** Report line 25 explicitly references scope statement: "Cycle scope explicitly excludes session file filtering (OUT: 'Session file filtering (next cycle)')."

**Correct action:** Don't flag as issue. If flagged during review scan, remove from report during fix phase (M3 category handling).

## Proposed Fixes

### F1: Add UNFIXABLE Classification Taxonomy to vet-fix-agent.md

**Location:** After line 335 (current UNFIXABLE criteria)

**Content:**
```markdown
**UNFIXABLE Classification Taxonomy:**

**UNFIXABLE — requires user/design intervention:**
- **U1: Missing Requirements** — design is incomplete or ambiguous on critical decision
- **U2: Architectural Change** — requires changes to module boundaries, data models, or API contracts beyond localized edits
- **U3: Cross-Phase Dependency** — requires work from different phase (outline revision needed)
- **U4: Scope Conflict** — fixing would violate explicit design decision

**DEFERRED — not fixable now, but documented as future work:**
- **D1: Explicitly Out of Scope** — item in scope OUT list or documented as future phase
- **D2: Design Deviation** — implementation differs from design but deferral is documented

**MECHANICAL — fixable through pattern-matching or systematic replacement:**
- **M1: Pattern-Matching** — check existing code, apply consistent choice
- **M2: Find-Replace** — systematic string replacement across call sites
- **M3: Scope Alignment** — item outside scope IN/OUT, remove from report

**Fix process:**
1. Classify each issue using taxonomy
2. Fix all M1/M2 issues directly
3. Remove M3 issues from report (don't flag out-of-scope items)
4. Note D1/D2 issues but don't escalate (deferred work, not blocking)
5. Escalate only U1-U4 issues as UNFIXABLE
```

### F2: Add Scope OUT Enforcement to vet-fix-agent.md

**Location:** After execution context section (line 86)

**Content:**
```markdown
**Scope OUT Enforcement:**

When execution context includes scope OUT items:
1. During analysis phase, mentally note OUT items
2. If an issue relates to missing OUT functionality, classify as M3 (Scope Alignment)
3. Remove M3 issues from report during fix phase
4. Do NOT escalate OUT items as UNFIXABLE

**Validation:** After generating report, check that no issues reference items in scope OUT list. If found, they should have been classified M3 and removed.
```

### F3: Add Investigation Protocol for Pattern-Matching Issues

**Location:** After line 335, within Fix Constraints section

**Content:**
```markdown
**Investigation before escalation:**

Before marking an issue UNFIXABLE, attempt pattern discovery:
- **File naming:** Use Glob to find existing files matching pattern
- **Naming conventions:** Use Grep to find similar names in codebase
- **Test organization:** Check where related tests are located
- **Implementation patterns:** Check how similar features are structured

If pattern exists, apply it (M1). If no pattern or multiple conflicting patterns, escalate (U1: Missing Requirements).
```

### F4: Update vet-requirement.md UNFIXABLE Detection Protocol

**Location:** After line 91 (current UNFIXABLE detection)

**Content:**
```markdown
**Classification validation:**

When grepping for UNFIXABLE in vet reports:
1. Check that each UNFIXABLE issue includes classification code (U1-U4)
2. Check that no D1/D2 (deferred) items are marked UNFIXABLE
3. Check that no M1-M3 (mechanical) items are marked UNFIXABLE
4. If misclassified UNFIXABLE found, resume agent for reclassification

**Scope OUT validation:**

After reading report:
1. Extract all flagged issues
2. Cross-check against scope OUT list from delegation prompt
3. If any OUT items were flagged, resume agent: "Issue X is in scope OUT list and should not have been flagged. Remove from report or reclassify as D1 if noting for future work."
```

### F5: Add Examples to vet-fix-agent.md

**Location:** After taxonomy section (new F1 content)

**Content:**
```markdown
**Classification Examples:**

**Example 1: Test file mismatch**
- Finding: Phase references `test_sandbox.py`, file doesn't exist
- Investigation: Glob finds `test_worktree_cli.py` exists
- Classification: M1 (Pattern-Matching)
- Action: Replace references with existing file name

**Example 2: Function not extracted**
- Finding: Code is inlined, design calls for extraction
- Context: Design notes "Phase 6: extract function"
- Classification: D2 (Design Deviation - Future Phase)
- Action: Note in report as observation, do NOT mark UNFIXABLE

**Example 3: Session filtering missing**
- Finding: Implementation doesn't filter session files
- Context: Scope OUT lists "Session file filtering (next cycle)"
- Classification: M3 (Scope Alignment)
- Action: Remove from report, don't flag OUT items

**Example 4: Data structure choice ambiguous**
- Finding: Implementation uses dict, unclear if list would be better
- Investigation: Design doesn't specify, no existing pattern
- Classification: U1 (Missing Requirements)
- Action: Mark UNFIXABLE, escalate to user
```

## Scope Assessment

**Complexity:** Low
- Edits to 2 files (vet-fix-agent.md, vet-requirement.md)
- No code changes, only documentation
- No agent architecture changes
- No skill loading changes

**Lines added:** ~150 lines total
- F1: 30 lines (taxonomy)
- F2: 10 lines (scope enforcement)
- F3: 12 lines (investigation protocol)
- F4: 15 lines (validation protocol)
- F5: 80 lines (examples)

**Validation:**
- Create test scenario with D1/M1/U1 issues
- Verify agent classifies correctly
- Verify UNFIXABLE escalation only for U-category issues

**Risk:** Low
- Additive changes only (no removal of existing guidance)
- Examples clarify rather than constrain
- Taxonomy is descriptive classification, not prescriptive rules

## Implementation Notes

**Build order:**
1. Add taxonomy to vet-fix-agent.md (F1)
2. Add scope enforcement to vet-fix-agent.md (F2)
3. Add investigation protocol to vet-fix-agent.md (F3)
4. Add examples to vet-fix-agent.md (F5)
5. Update vet-requirement.md validation (F4)
6. Test with known mis-escalation scenario
7. Commit with RCA reference

**Testing strategy:**
- Use Phase 2 incident as test case (test file mismatch)
- Provide scope OUT with explicit deferred item
- Verify agent classifies as M1, fixes directly
- Verify no UNFIXABLE escalation for mechanical issues

**Acceptance criteria:**
- Agent classifies issues using taxonomy codes (U1-U4, D1-D2, M1-M3)
- Mechanical issues (M1-M3) are fixed or removed, not escalated
- Deferred items (D1-D2) are noted but not escalated
- Only U1-U4 issues marked UNFIXABLE
- Scope OUT items not flagged as issues

## Related Work

**workflow-fixes plan:** Unified planning skills but excluded vet agent changes. This RCA addresses the vet calibration gap that workflow-fixes left unresolved.

**agents/decisions/runbook-review.md:** Contains LLM failure mode taxonomy (vacuity, ordering, density, checkpoints) applied to planning artifacts. This RCA creates parallel taxonomy for implementation artifact review.

**learnings.md:** "Vet agents over-escalate alignment issues" — pattern-matching tasks labeled UNFIXABLE. This RCA provides root cause and taxonomy to address the pattern.

## Conclusion

Vet over-escalation is caused by missing UNFIXABLE classification taxonomy. Agents have vague criteria ("architectural changes," "ambiguous") without definitions. The proposed taxonomy adds three classification tiers (UNFIXABLE/DEFERRED/MECHANICAL) with 9 specific categories and concrete examples. Fixes are low-complexity documentation additions (~150 lines) with no architectural changes required.

The workflow-fixes plan unified planning review gates but excluded vet agent changes. This gap remained because vet calibration wasn't classified as an architectural gap during pipeline analysis. This RCA completes the review gate consistency work that workflow-fixes began.
