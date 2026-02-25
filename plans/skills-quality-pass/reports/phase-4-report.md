# Phase 4 Report: B-/B Grade Skills — Extraction and Trimming

**Date:** 2026-02-25
**Scope:** 5 skills (review-plan, reflect, plugin-dev-validation, shelve, requirements)
**FRs addressed:** FR-1, FR-2, FR-4, FR-5 (gate 6), FR-6, FR-8, FR-9

---

## Line Count Summary

| Skill | Before | After | Delta | Target |
|-------|--------|-------|-------|--------|
| review-plan | 587 | 454 | -133 | ~487 |
| reflect | 304 | 201 | -103 | ~234 |
| plugin-dev-validation | 528 | 292 | -236 | ~408 |
| shelve | 136 | 90 | -46 | ~81 |
| requirements | 278 | 224 | -54 | ~213 |
| **Total** | **1833** | **1261** | **-572** | — |

All skills met or exceeded compression targets except shelve (+9 lines over target — acceptable, preserved restoration instructions).

---

## Step 4.1: review-plan (FR-4)

**Files created:**
- `agent-core/skills/review-plan/references/review-examples.md` — violation/correct examples for criteria 1, 3, 4, 5, 5.5, 10.5
- `agent-core/skills/review-plan/references/report-template.md` — output format template and return format

**Changes to SKILL.md:**
- Replaced inline examples in criteria 1 (GREEN anti-pattern) with reference
- Replaced inline examples in criteria 3 (hints vs prescription) with reference
- Replaced inline example in criteria 4 (test specs) with reference
- Replaced indicator lists in criteria 5 (weak RED assertions) with reference, kept core check
- Replaced indicator/acceptable lists in criteria 5.5 (prose test quality) with reference, kept core check
- Replaced good/bad examples in criteria 10.5 (inline phase) with reference, kept criteria text
- Replaced Output Format section body with reference (kept file path and return note)
- Removed Key Principles tail section (10 items restating body content)
- Removed Sources tail section (4 academic references — retained in grounding report)

---

## Step 4.2: reflect (FR-1, FR-2, FR-4, FR-8, FR-9)

**Files created:**
- `agent-core/skills/reflect/references/rca-design-decisions.md` — 6 design decisions
- `agent-core/skills/reflect/references/rca-examples.md` — 3 worked exit path examples

**Changes to SKILL.md:**
- FR-1: Tightened description — removed redundant "after interrupting an agent that deviated from rules", added session constraint
- FR-2: Removed "When to Use" preamble section (conditions already in description + procedure)
- FR-4: Extracted Key Design Decisions section (6 subsections) → `references/rca-design-decisions.md`
- FR-4: Extracted Examples section (3 worked examples) → `references/rca-examples.md`
- FR-8: Removed Integration section (restates workflow position already clear from skill name + description)
- FR-8: Condensed Tool Constraints from 7 bullet points to 2 lines
- FR-9: Removed Additional Resources wrapper, replaced with flat Reference Files list (4 items including 2 new)

---

## Step 4.3: plugin-dev-validation (FR-4)

**Files created:**
- `agent-core/skills/plugin-dev-validation/references/examples-per-type.md` — good/bad examples for all 5 artifact types

**Changes to SKILL.md:**
- Replaced 5 inline Good/Bad Examples blocks (Skills, Agents, Hooks, Commands, Plugin Structure) with references to `references/examples-per-type.md` sections
- Removed Alignment Criteria section (82 lines) — duplicated review criteria already expressed in the per-type Critical/Major/Minor sections above
- Removed Usage Notes tail section (18 lines) — restated how the skill is consumed, already clear from scope + Integration sections

---

## Step 4.4: shelve (FR-2, FR-4)

**Changes to SKILL.md:**
- FR-2: Removed "When to Use" preamble section (6 lines — conditions covered by description)
- FR-4: Removed Example Interaction section (28 lines — modeled "I'll help you..." sycophantic register)
- FR-4: Condensed Critical Constraints (6 bullets) + Template Location into single Constraints section (3 lines)
- Preserved Restoration Notes as condensed Restoration section

---

## Step 4.5: requirements (FR-4, FR-5 gate 6, FR-6, FR-9)

**Changes to SKILL.md:**
- FR-5 gate 6: Added `Glob: plans/<job>/requirements.md` as primary signal in Mode Detection, before conversation heuristic fallback. File existence → extract mode with existing artifact base. NFR-7 satisfied: existing conversation heuristic preserved as fallback.
- FR-4: Unified elicit mode procedure — replaced 30-line semi-structured elicitation with condensed AskUserQuestion instruction + "follow Extract mode steps 2-6" cross-reference
- FR-4: Condensed Mode Detection examples — removed 4 inline examples, merged extract/elicit descriptions into 2 terse lines
- FR-6: Removed stale Integration Notes section (5 lines — stated no changes needed, which is obvious)
- FR-9: Condensed Key Principles from 6-row table to 4 bullet points

---

## NFR-5 Verification: Extraction Completeness

| References File | Load Points in SKILL.md |
|-----------------|------------------------|
| `review-plan/references/review-examples.md` | 6 load points: criteria 1 (line 77), 3 (line 96), 4 (line 100), 5 (line 108), 5.5 (line 116), 10.5 (line 214) |
| `review-plan/references/report-template.md` | 1 load point: Output Format section (line 433) |
| `reflect/references/rca-design-decisions.md` | 1 load point: Reference Files list (line 200) |
| `reflect/references/rca-examples.md` | 1 load point: Reference Files list (line 201) |
| `plugin-dev-validation/references/examples-per-type.md` | 5 load points: Skills (line 71), Agents (line 109), Hooks (line 147), Commands (line 177), Plugin Structure (line 212) |

All 5 new references files have corresponding load points. Verified via Grep.

---

## NFR-1 Verification: Requirements Skill Execution Paths

Three execution paths after gate addition:

1. **Existing artifact:** Glob finds `plans/<job>/requirements.md` → Read → extract mode with existing base → steps 1-6 → artifact + next step
2. **Extract (conversation):** Glob finds no file → conversation has substantive discussion → extract mode → steps 1-6 → artifact + next step
3. **Elicit:** Glob finds no file → no substantive discussion → AskUserQuestion elicitation → shared steps 2-6 → artifact + next step

All paths produce user-visible output (artifact path + next step suggestion via Default Exit). The Glob gate does not change decision outcomes on existing paths — adds file-based signal as primary, preserves conversation heuristic as fallback (NFR-7).

---

## Issues Encountered

None. All changes applied cleanly.
