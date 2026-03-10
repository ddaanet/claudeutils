# Deliverable Review: pipeline-review-protocol

**Date:** 2026-03-10
**Methodology:** agents/decisions/deliverable-review.md
**Conformance baseline:** plans/pipeline-review-protocol/outline.md (no design.md — inline execution, outline is authoritative)
**Review type:** Re-review after fix commit `f0b6bd3c` (prose routing bias fix)

## Inventory

Plan-scoped deliverables (excluding unrelated branch work: handoff-cli-tool agents, bootstrap tests):

| Type | File | Change |
|------|------|--------|
| Agentic prose | agent-core/skills/proof/SKILL.md | +141 (new) |
| Agentic prose | agent-core/skills/design/SKILL.md | +26/-7 |
| Agentic prose | agent-core/skills/design/references/write-outline.md | +14/-8 |
| Agentic prose | agent-core/skills/design/references/write-design.md | +6 |
| Agentic prose | agent-core/skills/inline/SKILL.md | +18/-10 |
| Configuration | agent-core/skills/inline/references/review-dispatch-template.md | +11/-31 (renamed) |
| Agentic prose | agent-core/skills/requirements/SKILL.md | +4/-6 |
| Agentic prose | agent-core/skills/runbook/SKILL.md | +1/-1 |
| Agentic prose | agent-core/skills/runbook/references/general-patterns.md | +2/-2 |
| Agentic prose | agent-core/skills/runbook/references/examples.md | +1/-1 |
| Agentic prose | agent-core/skills/runbook/references/tdd-cycle-planning.md | +19/-2 |
| Agentic prose | agent-core/skills/runbook/references/tier3-outline-process.md | +2/-1 |
| Agentic prose | agent-core/skills/runbook/references/tier3-planning-process.md | +20/-5 |
| Agentic prose | agent-core/skills/review-plan/SKILL.md | +1 |
| Agentic prose | agent-core/skills/review-plan/references/review-examples.md | +4/-5 |
| Agentic prose | agent-core/skills/handoff/SKILL.md | +1 |
| Configuration | .claude/skills/proof | +1 (symlink) |

**Total:** 17 files, ~272 net lines. All agentic prose except 2 config entries.

## Critical Findings

None.

## Major Findings

Carried forward from 2026-03-09 review — unchanged by fix commit:

1. **`proof <artifact>.md` planstate not implemented**
   - outline.md Scope IN: "`proof <artifact>.md` planstate"
   - proof/SKILL.md contains no planstate management (no lifecycle.md entry on loop entry/exit)
   - No hosting skill integration point writes planstate
   - **Impact:** Planstate is for cross-session visibility — `claudeutils _worktree ls` should show `proof outline.md` when a plan is blocked on human validation. Without it, a plan mid-proof looks identical to a plan mid-execution.
   - **Drift origin:** Outline specified planstate in Scope IN but didn't assign it to any C1-C4 component. Outline-corrector at the time didn't check scope-to-component traceability — standalone scope item missed. Prevention fix applied to outline-corrector.

2. **`/proof` handles runbook as single artifact, not per-phase-file**
   - tier3-planning-process.md invokes `/proof plans/<job>/runbook-phase-*.md`
   - proof/SKILL.md Entry section: "Read the artifact under review" — singular
   - A runbook is one artifact composed of multiple phase files. /proof should receive it as a unit, not iterate per file.
   - **Impact:** /proof's loop mechanics (reword, accumulate, sync) need multi-file artifact support — reading all phase files as one review target.
   - **Drift origin:** Outline C2 table row 5 uses the glob pattern. /proof (C1) was built with single-file semantics. Cross-component interface mismatch — C2 feeds multi-file to C1's single-file loop. Outline-corrector at the time didn't check cross-component interface compatibility. Prevention fix applied to outline-corrector.

## Minor Findings

### New (introduced by fix commit)

3. **Stale filename in review-dispatch-template.md example**
   - review-dispatch-template.md:64: `IN: SKILL.md (~1500 words), references/corrector-template.md`
   - File was renamed from `corrector-template.md` to `review-dispatch-template.md` in this commit
   - Example references the old name — reader looking for `corrector-template.md` won't find it
   - Axis: accuracy

### Carried forward

4. **Author-corrector coupling table duplicated**
   - Identical table at proof/SKILL.md:108-113 and design/SKILL.md:165-170
   - Maintenance risk: table changes require two-file update
   - Axis: consistency

5. **Corrector subagent_type inconsistency for runbook-phase-\*.md**
   - proof/SKILL.md:81: `runbook-phase-*.md | runbook-corrector (/review-plan) | corrector`
   - All other rows use the specific corrector agent name as subagent_type
   - Functionally correct but naming pattern is inconsistent
   - Axis: consistency

### Supplementary (not in outline scope)

6. **runbook references updated from pipeline-contracts.md to review-requirement.md**
   - examples.md, general-patterns.md: routing reference path updated
   - Correct companion change — review-requirement.md is the canonical routing table
   - Not in outline scope but appropriately coupled

## Fix-Specific Assessment

The fix commit (`f0b6bd3c`) addresses prose routing bias — 3 routing gates + inline review dispatch rewrite. No new issues introduced.

**Routing consistency verified across 3 documents:**
- design/SKILL.md routing (lines 134-142): Simple→/inline, Moderate+agentic-prose→/inline, Moderate non-prose→/runbook ✓
- design/SKILL.md Continuation (lines 179-184): prepend logic matches routing rules ✓
- write-outline.md sufficiency gate (lines 183-198): prose hard gate with commutativity rationale, inline criteria scoped to non-prose paths ✓

**Review dispatch rewrite:**
- inline/SKILL.md Phase 4a references `review-requirement.md` routing table — artifact type grouping matches table categories ✓
- Two dispatch patterns (fix-capable vs report-only) clearly differentiated ✓
- review-dispatch-template.md: recall changed from pre-resolved content to artifact reference — consistent with learnings ("When corrector template inlines recall content") ✓
- Template generalized from corrector-specific to reviewer-generic ✓

## Gap Analysis

| Outline Scope IN | Status | Reference |
|-----------------|--------|-----------|
| `/proof` skill (replacing discussion-protocol.md) | Covered | proof/SKILL.md (+141 lines), discussion-protocol.md deleted |
| `proof <artifact>.md` planstate | **Missing** | No planstate in skill or hosting skills |
| Integration in /requirements (Step 5) | Covered | requirements/SKILL.md |
| Integration in /design (Phase B) | Covered | write-outline.md |
| Integration in /design (Post-design) | Covered | write-design.md (C.4.5) |
| Integration in /runbook (Post-outline) | Covered | tier3-planning-process.md |
| Integration in /runbook (Post-expansion) | Covered | tier3-planning-process.md |
| Author-corrector coupling in /design | Covered | design/SKILL.md:155-173 |
| Automatic corrector dispatch after "apply" | Covered | proof/SKILL.md:72-95 |

| Outline Scope OUT | Status |
|------------------|--------|
| New corrector agents | Respected |
| Changes to validate-runbook.py | Partially violated (+12 lines, vacuity check — justified by author-corrector coupling) |
| Changes to prepare-runbook.py | Respected |
| Hook-based enforcement | Respected |
| Changes to /inline or /orchestrate | Partially violated (inline Phase 4a rewrite — justified by routing bias fix) |
| Continuation infrastructure | Respected |

**Note on scope OUT violations:** Both are justified companion changes. validate-runbook.py: author-corrector coupling obligation. inline Phase 4a: routing bias fix required review dispatch rewrite to align with review-requirement.md routing table.

## Summary

- **Critical:** 0
- **Major:** 2 (planstate gap, /proof multi-file artifact support) — both carried forward, unchanged
- **Minor:** 3 (1 new: stale filename in example; 2 carried forward: table duplication, subagent_type naming)

The fix commit is clean — routing logic is internally consistent across all three documents, no new issues introduced. The 2 Major findings from the original review remain. Both trace to the outline-corrector missing scope-to-component traceability and cross-component interface checks — prevention fixes applied to outline-corrector.
