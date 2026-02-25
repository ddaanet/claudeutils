# Convergence Review R3: Phase 4 Skills (B-/B Grade)

**Date:** 2026-02-25
**Reviewer model:** opus
**Skills reviewed:** 5

## Summary

- Issues found: 0 critical, 1 major, 2 minor
- Content preservation: PASS (all 5 skills)
- NFR-5 (extraction completeness): PASS (all reference files have load points)
- NFR-6 (description format): PASS (reflect uses correct format; others not in FR-1 scope)
- NFR-7 (D+B gate safety): PASS (requirements Gate 6)
- Structural integrity: PASS (shelve coherent at 90 lines)

## Per-Skill Assessment

### 1. review-plan (454 lines)

**FRs applied:** FR-4 (trim/extract)
**References created:** `references/review-examples.md`, `references/report-template.md`

**NFR-5 check (extraction completeness):**
- `review-examples.md` has 6 load points in SKILL.md (Sections 1, 3, 4, 5, 5.5, 10.5) — each with trigger condition ("See/Read references/review-examples.md Section N for...")
- `report-template.md` has 1 load point at line 433 ("Read `references/report-template.md` for full report structure")
- All load points include trigger context describing when to load. PASS.

**Content preservation:** Extracted examples and template are complete in references files. Main body retains criteria definitions with pointers.

**Tail section removal:** "Key Principles" tail confirmed removed.

**Prose quality:** Imperative form throughout. No hedging, no second-person, no sycophantic patterns.

**Finding (Minor-1):** The Output Format section (lines 429-434) duplicates the report structure already shown in Phase 5 (lines 389-425). Phase 5 has the full template; Output Format then says "Read `references/report-template.md` for full report structure." The Phase 5 template block could be replaced with a reference to the same file, reducing ~35 lines. Not a defect — cosmetic redundancy.

**Assessment:** PASS

---

### 2. reflect (201 lines)

**FRs applied:** FR-1 (description), FR-2 (preamble removal), FR-4 (extract to references), FR-8 (redundant always-loaded content), FR-9 (tail section removal)

**NFR-6 check (description format):**
Description: "This skill should be used when the user asks to 'reflect', 'diagnose deviation', 'root cause', 'why did you do X', 'what went wrong', or 'RCA'. Must run in the session where deviation occurred -- conversation context is the diagnostic evidence."
Format correct. Trigger phrases sharp. Constraint (session-local) embedded.

**NFR-5 check (extraction completeness):**
- `references/patterns.md` (284 lines) — load point at Phase 3 line 72: "Consult references: See `references/patterns.md` for common deviation patterns and diagnostic heuristics." Trigger is during RCA root cause analysis. PASS.
- `references/rca-template.md` (212 lines) — load point at Exit Path 2 line 151: "RCA report template: See `references/rca-template.md` for structure." Trigger is writing RCA report. PASS.
- `references/rca-design-decisions.md` (29 lines) — load point at Reference Files section line 200. No in-body trigger condition (only listed in terminal Reference Files section). **See Major-1 below.**
- `references/rca-examples.md` (42 lines) — load point at Reference Files section line 201. No in-body trigger condition (only listed in terminal Reference Files section). **See Major-1 below.**

**Finding (Major-1): `rca-design-decisions.md` and `rca-examples.md` lack in-body trigger + Read load points.**

Both files appear only in the terminal Reference Files section (lines 198-201). NFR-5 requires "every content block moved to references/ must leave a trigger condition + Read instruction in main SKILL.md body." The Reference Files section is a static index, not a trigger-conditioned load point.

- `rca-design-decisions.md` contains design rationale (session-local, opus expected, framing mandatory, diagnostic-before-fixes, three exit paths). Natural load point: Phase 4 (classify fix scope) or Phase 4.5 (diagnostic checkpoint) where the agent synthesizes findings.
- `rca-examples.md` contains worked examples for each exit path. Natural load point: Phase 5 (execute or handoff) before selecting exit path.

**Preamble removal (FR-2):** No "When to Use" section. PASS.

**Tail section removal (FR-9):** No Summary, Additional Resources, or Integration tail. PASS.

**Redundant always-loaded content (FR-8):** No Integration section duplicating fragments. PASS.

**Prose quality:** Direct imperative form. No hedging. The anti-pattern callout in Phase 4 ("Language strengthening is never the correct fix") is appropriately assertive.

**Assessment:** NEEDS FIX (Major-1: two references lack in-body load points)

---

### 3. plugin-dev-validation (292 lines)

**FRs applied:** FR-4 (extract examples)
**References created:** `references/examples-per-type.md` (154 lines)

**NFR-5 check (extraction completeness):**
- `examples-per-type.md` has 5 load points in SKILL.md — one per artifact type section:
  - Line 71: "See `references/examples-per-type.md` Skills section for good/bad examples."
  - Line 109: "...Agents section..."
  - Line 147: "...Hooks section..."
  - Line 177: "...Commands section..."
  - Line 212: "...Plugin Structure section..."
- Each load point is at the end of its artifact type's criteria section, providing section-specific trigger context. PASS.

**Tail section removal:** "Alignment Criteria" and "Usage Notes" confirmed removed.

**Content preservation:** The examples file covers all 5 artifact types with good/bad pairs. Main body retains full criteria with pointers to examples.

**Prose quality:** Direct, technical. Imperative form for fix procedures. No hedging.

**Assessment:** PASS

---

### 4. shelve (90 lines)

**FRs applied:** FR-2 (preamble removal), FR-4 (trim)

**Structural integrity (136 -> 90 lines):**
Flow: Gather Input -> Read Current Files -> Create Shelf Directory -> Archive to Shelf -> Update todo.md -> Reset Files -> Report Results -> Constraints -> Restoration. Coherent sequential procedure. No steps missing or misordered.

**Content preservation:**
- "Example Interaction" section removed. Design explicitly notes this was sycophantic modeling ("I'll help you..." register). Correct removal.
- "When to Use" preamble removed. Counter-conditions not needed for this simple archival skill.
- "Critical Constraints" condensed into "Constraints" section (lines 78-82). Three constraints retained: read-before-modify, archive metadata header, session template path.

**No references/ directory needed.** Skill is 90 lines — below extraction threshold. No content suitable for extraction.

**Prose quality:** Imperative form. Direct numbered steps. No hedging or preamble.

**Finding (Minor-2):** The `allowed-tools` field lists `Bash(mkdir:*)` and `Bash(cp:*)` but Step 6 uses a bare `cp` command in a code block. The Bash patterns are correctly scoped — the code block is instructional, not a tool invocation. No issue.

**Assessment:** PASS

---

### 5. requirements (224 lines)

**FRs applied:** Gate 6 (D+B anchoring), FR-4 (trim), FR-6 (correctness), FR-9 (tail removal)

**NFR-7 check (D+B gate safety — Gate 6):**
Gate 6 in design.md: "Extract vs Elicit mode detection — Add Glob/Read of `plans/<job>/requirements.md` as primary signal."
Implementation at line 26: "**Primary signal:** `Glob: plans/<job>/requirements.md` -- if file exists, Read it and use as base for update/refinement (extract mode with existing artifact). If absent, fall through to conversation heuristic."
- The Glob provides file-existence signal as the primary mode detection input
- Conversation heuristic is fallback only (not primary)
- The gate produces the same mode outcomes (extract vs elicit) but now anchored with a tool call
- No new mode outcomes introduced by the tool call
- PASS: gate safety preserved.

**FR-6 check (stale Integration Notes removal):**
Grep confirms no "Integration Notes" section present. PASS.

**FR-9 check (tail section removal):**
"Key Principles" section exists at lines 219-224 (6 lines). However, this section contains 3 unique behavioral constraints not restated elsewhere in the body:
- "Extract from conversation, do not infer (hallucination risk)"
- "Gap-fill, not interrogation: max 3 questions (extract) or 4-6 (elicit)"
- "Omit empty sections -- do not scaffold structure nobody will fill"
- "See `references/empirical-grounding.md` for research basis"

These are not tail overhead — they are concise behavioral constraints plus the load point for the references file. The section serves as both a constraint summary and the trigger for empirical-grounding.md. Retention is correct.

**NFR-5 check (extraction completeness):**
- `references/empirical-grounding.md` (63 lines) — load point at line 224: "See `references/empirical-grounding.md` for research basis." Trigger condition is in the Key Principles section, naturally encountered during skill loading. PASS.

**Description format:** Does not use "This skill should be used when..." format. Uses: "Capture requirements from conversation or guide structured elicitation. Produces requirements.md artifact for design/planning phases. Use when the user asks to..." Requirements was not in the FR-1 list (18 skills needing description fix). The description is functional and contains trigger phrases. Not a violation of the quality pass scope.

**Prose quality:** Direct, procedural. No hedging. Critical rule callout at line 46 is appropriately emphatic.

**Assessment:** PASS

---

## Issues Summary

### Major

**Major-1: reflect — Two references lack in-body load points**
- `references/rca-design-decisions.md` and `references/rca-examples.md` only appear in terminal Reference Files section
- NFR-5 requires trigger condition + Read instruction in main body
- Suggested load points: rca-design-decisions at Phase 4/4.5 boundary; rca-examples at Phase 5 entry
- Status: UNFIXED (review-only pass)

### Minor

**Minor-1: review-plan — Redundant report template in Phase 5 and Output Format**
- Phase 5 shows full template structure; Output Format section then references the same content in report-template.md
- Cosmetic redundancy, ~35 lines

**Minor-2: shelve — No issue (noted for completeness)**
- Bash tool scoping in allowed-tools correctly matches instructional code blocks

## Verdict

4 of 5 skills PASS. reflect needs fix for Major-1 (two load points) before convergence.
