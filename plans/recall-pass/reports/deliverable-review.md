# Deliverable Review: recall-pass

**Date:** 2026-02-24
**Methodology:** agents/decisions/deliverable-review.md

## Inventory

| Type | File | + | - | Net |
|------|------|---|---|-----|
| Agentic prose | agent-core/skills/design/SKILL.md | +28 | -3 | +25 |
| Agentic prose | agent-core/skills/runbook/SKILL.md | +34 | -9 | +25 |
| Agentic prose | agent-core/skills/recall/SKILL.md | +115 | -0 | +115 |
| Agentic prose | agent-core/skills/orchestrate/SKILL.md | +1 | -0 | +1 |
| Agentic prose | agent-core/skills/deliverable-review/SKILL.md | +1 | -0 | +1 |
| Agentic prose | agent-core/skills/when/SKILL.md | +1 | -1 | 0 |
| Agentic prose | agent-core/skills/how/SKILL.md | +1 | -1 | 0 |
| Agentic prose | agents/decisions/pipeline-contracts.md | +2 | -2 | 0 |
| Agentic prose | agent-core/agents/brainstorm-name.md | +4 | -2 | +2 |
| Configuration | .claude/skills/recall | +1 | -0 | +1 |
| **Total** | **10 files** | **+188** | **-18** | **+170** |

All deliverables are agentic prose (LLM-consumed instructions) except one configuration symlink.

**Design conformance summary:** Implementation matches the outline.md Scope IN section. All 5 specified deliverables are present and substantive.

## Critical Findings

None.

## Major Findings

### 1. FIXED — Outline stale on Q-4/D-7, contradicted requirements

**File:** `plans/recall-pass/outline.md:69` (D-7) and `:69` (Q-4)
**Axis:** Conformance (internal document consistency)
**Original severity:** Major
**Status:** Fixed in-session

outline.md D-7 said "no mid-design recall" and Q-4 resolved "No" — contradicting requirements.md FR-11 which resolved Q-4 as "yes, recall at A.5 and C.1."

**Fix applied:** D-7 rewritten to "Progressive recall within design" describing re-evaluation at A.5 and C.1. Q-4 updated to "Yes — re-evaluate at A.5 and C.1 (FR-11: new information changes what's relevant)."

### 2. FIXED — FR-11 within-session boundaries lacked recall re-evaluation

**Files:** `design/SKILL.md`, `runbook/SKILL.md`
**Axis:** Functional completeness (FR-11 acceptance criteria)
**Original severity:** Major (reclassified from Minor after discussion — these are functionally different recall passes, not compaction insurance re-reads)
**Status:** Fixed in-session

FR-11 lists cognitive boundaries where recall should happen. Three within-session boundaries had no corresponding skill instructions:

- Before design outline (A.5): post-exploration, codebase findings change which entries are relevant
- Before full design (C.1): post-discussion, approach commitment changes which entries matter
- Before runbook outline (Phase 0.75): post-discovery, structural findings change which learnings apply

**Key reframing:** These are not "re-read for insurance" — they are re-evaluation passes. Each discovery phase produces new understanding that changes which recall entries are relevant. The initial A.1 recall surfaces non-obvious connections for a weakly specified task; subsequent recalls progressively refine the artifact as the task becomes better specified.

**Fix applied:** Added "Recall re-evaluation" paragraphs at A.5, C.1 (design skill) and Phase 0.75 (runbook skill). Each describes what changed and why different entries may now be relevant.

**Not fixed (by design):**
- Before Phase 1 (expansion): Phase 0.5 → Phase 1 is compact procedural distance; low value
- Before /requirements: no artifact exists yet (first stage — initial recall, not re-evaluation)

### 3. FIXED — Pipeline contracts didn't reflect progressive refinement

**File:** `agents/decisions/pipeline-contracts.md`
**Axis:** Conformance (contract accuracy)
**Status:** Fixed in-session

T1 output showed recall-artifact.md as generated once. T2 input showed it as static. Updated to reflect progressive refinement: T1 output notes "progressively refined at A.1, A.5, C.1"; T2 output notes "augmented at Phase 0.5, re-evaluated at Phase 0.75."

### 4. FIXED — Deliverable-review skill lacked lightweight recall fallback

**File:** `agent-core/skills/deliverable-review/SKILL.md`
**Axis:** Functional completeness (FR-11 review boundary)
**Status:** Fixed in-session (identified via /reflect RCA)

Skill said "read recall-artifact.md if present; if absent, proceed without it" — no fallback recall when artifact doesn't exist. Other skills (runbook Tier 1/2) already had the fallback pattern. Added lightweight recall (memory-index → batch-resolve) as fallback.

## Minor Findings

### FR-10 artifact format lacks explicit "Applies when" field

FR-10 requires: "Entries include 'applies when' conditions." The artifact template in design/SKILL.md has `Source` and `Relevance` fields but no `Applies when`. The runbook Common Context template addresses FR-10's intent ("DO/DO NOT rules with explicit applicability markers" for haiku consumers), placing the responsibility on the planner during curation rather than the artifact format. Architecturally sound — the planner adds formatting per model tier — but the artifact template doesn't prompt artifact authors to capture scope conditions that the planner later needs.

### Unspecified deliverables (justified)

Three deliverables are not in the outline's IN scope:

- **agent-core/agents/brainstorm-name.md** — YAML frontmatter formatting fix + H1 title. Bug fix, not recall-related.
- **agent-core/skills/when/SKILL.md**, **agent-core/skills/how/SKILL.md** — Stale reference fix: "already loaded via CLAUDE.md @-reference" → "already in context from a prior /recall, /when, or /how invocation." Necessary for on-demand memory-index pattern.
- **agent-core/skills/recall/SKILL.md** — Interactive recall skill. Not in outline scope (outline covers pipeline integration, not interactive use). Justified as the interactive counterpart filling a documented gap (agents self-retrieve at ~3%).

All are defensible. None are excess.

## Gap Analysis

| Requirement | Status | Reference |
|---|---|---|
| FR-1: Design-stage recall | Covered | design/SKILL.md A.1 Recall Artifact Generation |
| FR-2: Planning-stage recall | Covered | runbook/SKILL.md Phase 0.5 step 2 |
| FR-3: Execution-stage injection | Covered | runbook/SKILL.md Common Context template |
| FR-4: Review-stage recall | Covered | orchestrate/SKILL.md checkpoint template, deliverable-review/SKILL.md Layer 2 |
| FR-5: Persistent artifacts | Covered | File-based artifact format in design/SKILL.md |
| FR-6: Reference forwarding | Covered | Phase 0.5 reads and augments Pass 1 artifact |
| FR-7: Named enumeration | Covered | Artifact format: heading name + source path |
| FR-8: Mechanical filterability | Dissolved | D-2: baked at planning time, no runtime filtering |
| FR-9: Model-tier formatting | Covered | Common Context template + Tier 1/2 format guidance |
| FR-10: Applicability scoping | Partial | Intent in Common Context template, no artifact format field |
| FR-11: Cognitive boundaries | Covered | A.1, A.5, C.1 (design); Phase 0.5, Phase 0.75 (runbook); Common Context (implementation); checkpoint + deliverable-review (review). Phase 1 and /requirements deferred by design. |
| NFR-1: Token economy | Covered | ≤1.5K budget in Common Context, multiplicative cost noted |
| NFR-2: Incremental adoption | Covered | D-10 prioritization (Pass 2+3 first) |
| NFR-3: Composability | Covered | Extends existing Common Context mechanism |
| C-1: Prescriptive retrieval | Covered | Fixed pipeline points |
| C-2: Existing corpus format | Covered | No corpus changes |
| C-3: Pipeline integration | Covered | Modified existing skill procedures |
| C-4: Fire-and-forget | Covered | Content complete at injection time |
| C-5: Haiku orchestrator | Dissolved | D-2: orchestrator doesn't interact with recall content |

**Remaining gap:** FR-10 (artifact format field). Low risk — planner receives guidance via Common Context formatting instructions.

## Summary

| Severity | Count | Fixed |
|----------|-------|-------|
| Critical | 0 | — |
| Major | 4 | 4 |
| Minor | 2 | 0 |

All major findings fixed in-session. Remaining minor findings are low-risk (FR-10 format field, justified unspecified deliverables).
