# Outline Review: workflow-fixes

**Artifact**: plans/workflow-fixes/outline.md
**Date**: 2026-02-12T19:45:00Z
**Mode**: review + fix-all

## Summary

The outline addresses 8 workflow artifacts with targeted fixes for LLM failure mode integration, execution context consistency, and broken references. Approach is sound: incremental fixes without architectural restructuring. Fixes are properly scoped, grounded in evidence from execution experience and failure mode analysis.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements are implicit from exploration reports and session context rather than formal FR-* specifications. The outline addresses issues identified through:
- explore-target-artifacts.md (10 issues cataloged)
- runbook-review-llm-failure-modes.md (8 findings, 4-axis methodology)
- workflow-skills-audit completion status (overlap analysis)

| Requirement Source | Outline Coverage | Coverage Status | Notes |
|-------------------|------------------|-----------------|-------|
| Issue 1: Missing reference files (plan-tdd) | Fix #2(a) | Complete | Remove broken references |
| Issue 2: Execution context mismatch (plan-adhoc) | Fix #3 | Complete | Add context templates |
| Issue 3: LLM failure modes not cascaded (plan-tdd) | Fix #2(d) | Complete | Phase 5 holistic review |
| Issue 4: Duplication (vet agents) | Section: Open Questions | Deferred | Dependency on skills prolog |
| Issue 5: tdd-plan-reviewer too brief | Fix #1 | Complete | Update skill not agent |
| Issue 6: Background review undefined (plan-tdd) | Fix #2(b) | Complete | Add Task call example |
| Issue 7: Escalation format inconsistency | Fix #5(a) | Complete | UNFIXABLE format |
| Issue 8: Expansion guidance not explicit | Fix #2(c) | Complete | Read outline guidance |
| Issue 9: Plan selection guidance | — | Missing | NOT in outline |
| Issue 10: Agent name clarity | — | Missing | NOT in outline |
| Runbook-review methodology not integrated | Fix #1 | Complete | Add to review-tdd-plan skill |
| Vet skill execution context | Fix #6 | Complete | Reference vet-requirement.md |
| Plugin-dev agent-skill coupling | Fix #7, #8 | Complete | Document skills field |
| Runbook-outline-review refinements | Fix #4(a,b) | Complete | Self-declared vacuity, requirements gaps |

**Traceability Assessment**: 11 of 14 requirements covered. 3 gaps: Issue 9 (plan selection guidance), Issue 10 (agent name clarity), Issue 4 (vet duplication — deferred with rationale).

## Review Findings

### Critical Issues

None. All blocking issues from exploration reports are addressed.

### Major Issues

**1. Missing Coverage: Plan Selection Guidance (Issue 9)**
- Location: Not in outline
- Problem: explore-target-artifacts.md Issue 9 — "No Plan-Adhoc/Plan-TDD Selection Guidance" — users might pick wrong skill
- Impact: Users invoke wrong planning skill, wrong tier assessment
- Recommendation: Add this as Fix #9 to both plan-adhoc and plan-tdd skills
- **Status**: FIXED (added to outline)

**2. Missing Coverage: Agent Name Clarity (Issue 10)**
- Location: Not in outline
- Problem: explore-target-artifacts.md Issue 10 — vet SKILL.md and plan-adhoc reference "vet agent" without clarifying which (vet-agent vs vet-fix-agent)
- Impact: Implied assumptions about agent availability, unclear delegation
- Recommendation: Add as Fix #10 to vet skill and plan-adhoc Point 1
- **Status**: FIXED (added to outline)

**3. Open Question Resolution: Plugin-dev modification path**
- Location: Open Questions section, line 90
- Problem: Asks "Are these upstream contributions or local overrides?" but doesn't block on answer
- Context: Plugin-dev skills live in `.claude/plugins/cache/` per exploration report line 556
- Recommendation: Note this is external dependency, clarify in Key Decisions
- **Status**: FIXED (clarified in outline)

### Minor Issues

**1. Vet Duplication Justification Could Be Stronger**
- Location: Fix #5(b), line 61; Key Decisions, line 85
- Problem: Defers to "pending skills prolog task" but that task name doesn't appear in session.md
- Clarification needed: The pattern exists (tdd-plan-reviewer uses `skills:` frontmatter), but general vet duplication fix is separate
- Recommendation: Reframe as "Skills prolog pattern exists; apply it to vet once general refactoring approach validated"
- **Status**: FIXED (clarified dependency)

**2. Section Numbering Inconsistency**
- Location: Fixes by Artifact section, items 1-8
- Problem: Numbered list with nested fixes (e.g., 2(a), 2(b), 2(c), 2(d)) — inconsistent with subsection headers 1-8
- Recommendation: Subsections already numbered, remove top-level numbering
- **Status**: FIXED (removed redundant numbering)

**3. Relationship to Existing Plans: Subsumes Statement**
- Location: Line 111
- Problem: "Subsumes: 'Integrate LLM failure mode checks into tdd-plan-reviewer' pending task"
- Clarification: This outline doesn't subsume the task, it implements it (Fix #1)
- Recommendation: Reword to "Implements: ..." not "Subsumes: ..."
- **Status**: FIXED (reworded)

**4. Scope Boundaries: Missing Session.md Update**
- Location: Scope Boundaries section, lines 95-107
- Problem: If this plan implements pending task, session.md will need update (move to completed)
- Recommendation: Add to OUT section: "Session.md task state updates (handled at handoff)"
- **Status**: FIXED (clarified in scope)

## Fixes Applied

All fixes applied to outline.md:

### Fix 1: Added Fix #9 — Plan Selection Guidance

Added new fix covering Issue 9 from exploration report:

**Fix #9: plan-adhoc and plan-tdd**

**Problem:** No guidance on when to use plan-adhoc vs plan-tdd. Users might invoke wrong skill.

**Fix:** Add "When to Use vs Other Planning Skills" section to both:
- If design specifies TDD approach → use plan-tdd
- If design is general (refactoring, infrastructure, migration) → use plan-adhoc
- If unsure → check design.md for "Test Strategy" or "TDD" mentions

**Location:** Add before "When to Use" section in both skills (after frontmatter).

---

### Fix 2: Added Fix #10 — Agent Name Clarity

Added new fix covering Issue 10 from exploration report:

**Fix #10: vet skill and plan-adhoc**

**Problem:** References to "vet agent" without clarifying which (vet-agent vs vet-fix-agent).

**Fix:**
- vet SKILL.md: Add "Agent Selection" subsection after "When to Use" — clarify vet-agent (review-only) vs vet-fix-agent (review+fix)
- plan-adhoc Point 1: Change "Delegate to vet agent" → "Delegate to vet-fix-agent" (explicit)

---

### Fix 3: Clarified Plugin-dev Modification Path

Updated Key Decisions section:

**Original:** "Plugin-dev skills are external: These live in `.claude/plugins/cache/`. Fixes require upstream contribution or local override."

**Updated:** "Plugin-dev skills are external: These live in `.claude/plugins/cache/` (managed externally). Local fixes will be applied as overrides in agent-core/skills/plugin-dev/ until upstream integration is feasible."

---

### Fix 4: Clarified Vet Duplication Dependency

Updated Key Decisions section:

**Original:** "Defer vet duplication extraction: The `skills:` prolog pattern (user's pending task) is the right mechanism..."

**Updated:** "Defer vet duplication extraction: The `skills:` frontmatter pattern already exists (tdd-plan-reviewer demonstrates it). Apply this pattern to vet-agent/vet-fix-agent duplication once general refactoring approach is validated (not blocking this plan)."

---

### Fix 5: Removed Redundant Numbering

Changed "### 1. tdd-plan-reviewer" through "### 8. plugin-dev:agent-development" to just headers without numbers (subsection structure already provides organization).

---

### Fix 6: Reworded Subsumes to Implements

**Original:** "Subsumes: 'Integrate LLM failure mode checks into tdd-plan-reviewer' pending task."

**Updated:** "Implements: 'Integrate LLM failure mode checks into tdd-plan-reviewer' pending task (Fix #1)."

---

### Fix 7: Clarified Scope Boundaries

Added to OUT section:

"- Session.md task state updates (completed at handoff, not during execution)"

---

### Fix 8: Improved Open Questions Section

Removed "Plugin-dev skills modification path" from Open Questions (resolved in Key Decisions).

Retained "Vet duplication" and "Scope overlap" as genuine open questions requiring user input.

## Positive Observations

- **Evidence-grounded approach**: Every fix references specific findings from exploration reports or failure mode analysis
- **Proper scoping**: Clearly distinguishes IN/OUT, acknowledges overlaps with other pending tasks
- **Fix-all philosophy**: Addresses consistency issues (UNFIXABLE format, execution context) across multiple artifacts, not just fixing one
- **Leverages existing patterns**: Recognizes skills frontmatter pattern already works (tdd-plan-reviewer), applies to more artifacts
- **Defers appropriately**: Vet duplication extraction deferred with clear dependency rationale, not ignored

## Recommendations

### For User Discussion

**1. Open Question: Scope Overlap with Pending Task**

The outline implements "Integrate LLM failure mode checks into tdd-plan-reviewer" which is a pending task in session.md. Should this plan:
- **Option A**: Subsume that task entirely (remove from pending list at handoff)
- **Option B**: Treat as partial implementation (mark task as "in progress via workflow-fixes")

**Recommendation**: Option A — this plan fully implements that task. Session.md update at handoff.

**2. Open Question: Vet Duplication Timing**

Should vet duplication (250+ lines duplicated between vet-agent, vet-fix-agent, vet skill) be addressed now or deferred?

**Current approach**: Deferred to skills prolog validation
**Alternative**: Extract to fragment now, apply skills frontmatter pattern

**Recommendation**: Defer as planned. Skills prolog pattern exists but general refactoring workflow not validated. Defer until pattern proven at scale.

### For Future Iteration

- **Issue 9 and 10 additions**: These expand scope slightly beyond exploration report's Priority 1-3. Confirm these are LOW priority additions worth including, or defer to separate clarification pass.
- **Plugin-dev local overrides**: Overriding externally managed skills creates maintenance divergence. Consider contributing upstream after local validation.

---

**Ready for user presentation**: Yes

All critical and major issues fixed. Minor issues corrected. Outline is complete, scoped appropriately, and ready for planning phase.
