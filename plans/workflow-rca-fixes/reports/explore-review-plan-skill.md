# Exploration: review-plan Skill Structure

**Artifact:** `/Users/david/code/claudeutils-wt/workflow-improvements/agent-core/skills/review-plan/SKILL.md`
**Analysis Date:** 2026-02-14
**Size:** 480 lines total

---

## Document Structure

### Section Numbering

| Section | Heading | Lines | Scope |
|---------|---------|-------|-------|
| — | Frontmatter (YAML + Purpose) | 1-37 | Skill metadata, invocation rules |
| — | Document Validation | 39-45 | Phase type detection (TDD vs general) |
| — | Review Criteria | 48-284 | Core validation rules |
| 1 | GREEN Phase Anti-Pattern | 50-87 | CRITICAL: TDD only |
| 2 | RED/GREEN Sequencing | 88-102 | TDD only |
| 3 | Implementation Hints vs Prescription | 103-117 | TDD only |
| 4 | Test Specifications | 119-135 | TDD only |
| 5 | Weak RED Phase Assertions | 137-160 | CRITICAL: TDD only |
| 5.5 | Prose Test Quality | 161-181 | TDD only |
| 6 | Metadata Accuracy | 182-188 | All phases |
| 7 | Empty-First Cycle Ordering | 190-196 | TDD only |
| 8 | Consolidation Quality | 198-219 | All phases |
| 9 | File Reference Validation | 220-235 | CRITICAL: All phases |
| 10 | General Phase Step Quality | 237-256 | General only |
| 10.1 | Prerequisite Validation | 239-242 | General |
| 10.2 | Script Evaluation | 244-246 | General |
| 10.3 | Step Clarity | 249-252 | General |
| 10.4 | Conformance Validation | 254-256 | General |
| 11 | LLM Failure Modes | 258-283 | CRITICAL: All phases |
| 11.1 | Vacuity | 262-266 | All phases |
| 11.2 | Dependency Ordering | 268-271 | All phases |
| 11.3 | Density | 273-277 | All phases |
| 11.4 | Checkpoint Spacing | 279-282 | All phases |
| — | Review Process | 286-378 | Execution workflow (5 phases) |
| — | Output Format | 421-444 | Report structure and examples |
| — | Invocation | 448-465 | Integration with /plan workflow |
| — | Key Principles | 468-480 | Summary of 10 design principles |

---

## Section 11: LLM Failure Modes (CRITICAL)

**Location:** Lines 258-283
**Applicability:** All phases (TDD and general equally)
**Severity:** CRITICAL — explicitly listed as blocking issue type

### Content Analysis

**11.1 Vacuity** (262-266)
- **TDD:** Cycles where RED can pass with trivial assertions (`assert callable(X)`, import checks)
- **General:** Steps that only create scaffolding without functional outcome
- **Integration patterns:** Wiring steps where called function already tested
- **Fix:** Merge into nearest behavioral cycle/step
- **Basis:** References `agents/decisions/runbook-review.md` (external decision file)

**11.2 Dependency Ordering** (268-271)
- **Condition:** Item N tests behavior depending on structure from item N+k (k>0)
- **Scope:** Foundation-first within phases (existence → structure → behavior → refinement)
- **Fix scope:** Reorder within phase; cross-phase = UNFIXABLE (requires outline revision)
- **Critical distinction:** Within-phase ordering is fixable; cross-phase is escalation

**11.3 Density** (273-277)
- **Adjacent items:** Testing same function with <1 branch point difference
- **Parametrization:** Single edge cases expressible as parametrized row in prior item
- **Phase-level:** Entire phases with ≤3 items, all Low complexity
- **Fixes:** Merge adjacent, parametrize edge cases, collapse trivial phases

**11.4 Checkpoint Spacing** (279-282)
- **Gap thresholds:** >10 items OR >2 phases without checkpoint
- **Risk domains:** Complex data manipulation phases without intermediate verification
- **Fix:** Insert checkpoint recommendation

### Cross-References

Section 11 references `agents/decisions/runbook-review.md`:
- "Criteria from `agents/decisions/runbook-review.md` (four axes)"
- External document defines "four axes" framework
- No axis details repeated in SKILL.md — only TDD/general-specific interpretation

---

## TDD-Specific vs General-Specific Detection

### TDD-Only Sections (Sections 1-7, 5.5)
- **Section 1:** GREEN phase prescriptive code (TDD anti-pattern, doesn't apply to general)
- **Section 2:** RED/GREEN sequencing (TDD cycle structure)
- **Section 3:** Implementation hints vs prescription (TDD guidance pattern)
- **Section 4:** Test specifications (TDD assertion quality)
- **Section 5:** Weak RED phase assertions (TDD prose test quality)
- **Section 5.5:** Prose test code in RED (TDD format violation)
- **Section 7:** Empty-first cycle ordering (TDD cycle-level concern)

### General-Only Sections (Section 10)
- **Section 10.1:** Prerequisite validation (creation steps require investigation)
- **Section 10.2:** Script evaluation sizing (small/medium/large classification)
- **Section 10.3:** Step clarity (Objective/Implementation/Outcome structure)
- **Section 10.4:** Conformance validation (design spec verification)

### All-Phases Sections (Sections 6, 8, 9, 11)
- **Section 6:** Metadata accuracy (cycle/step counting)
- **Section 8:** Consolidation quality (merged items, trivial work placement)
- **Section 9:** File reference validation (CRITICAL)
- **Section 11:** LLM failure modes (CRITICAL)

---

## General-Step Detection Patterns

The skill explicitly handles both TDD and general phase types:

**Detection mechanism (Document Validation section, lines 39-45):**
- Scan for `## Cycle` / `### Cycle` headers → TDD
- Scan for `## Step` / `### Step` headers → general
- Mixed artifacts valid — apply type-appropriate criteria per phase
- Default (no type marker) → general

**Review Process Phase 1a (lines 288-293):**
```
1a. Determine phase type(s):
- Scan for ## Cycle / ### Cycle headers → TDD
- Scan for ## Step / ### Step headers → general
- Mixed is valid — apply type-appropriate criteria per phase
```

**Per-phase typing implementation:**
- No global "phase type" setting — each section/phase independently classified
- Mixed runbooks allowed (TDD phases + general phases in same file)
- Review Process iterates by detected type, applies appropriate criteria

**Step-specific criteria (Section 10):**
- 10.1: Prerequisite validation — required for "creation steps" (new code touching existing paths)
- 10.2: Script evaluation — size classification (small ≤25 lines, medium 25-100 prose, large >100)
- 10.3: Step clarity — Objective/Implementation/Expected Outcome structure
- 10.4: Conformance validation — spec-referenced behavior verification

---

## Existing LLM Failure Mode Checks

**Four axes** (from `agents/decisions/runbook-review.md`):

1. **Vacuity** — Cycles/steps with no behavioral content (import checks, existence assertions, scaffolding-only)
2. **Dependency Ordering** — Items depending on structure not yet established; within-phase reordering fixable, cross-phase escalates
3. **Density** — Adjacent items with minimal differentiation; candidates for merge or parametrization
4. **Checkpoint Spacing** — Gaps >10 items or >2 phases without intermediate verification

**Implementation approach:**
- Criteria stated but no algorithms provided
- "Merge" and "collapse" are fix patterns, not specifics of detection
- Density fix: "adjacent items testing same function with <1 branch point difference" — heuristic, not quantified
- Checkpoint insertion: gap thresholds provided (>10 items, >2 phases)

**Detection methods in Section 11:**
- Vacuity: Manual inspection of cycle/step content for behavioral vs scaffolding intent
- Ordering: Dependency analysis (item X requires structure from item Y, Y > X)
- Density: Content similarity across adjacent items
- Checkpoints: Item count gap measurement

**No automated detection algorithms** — all checks require human/LLM analysis, no formalization into code patterns.

---

## Size & Scope Assessment

**Total lines:** 480
**Substantive content:** ~370 lines (excluding frontmatter, whitespace)
**Breakdown:**
- Review Criteria (Sections 1-11): ~240 lines
- Review Process (5 phases): ~95 lines
- Output/Invocation/Principles: ~70 lines

**Depth:**
- 11 primary criteria (13 if counting 5.5, 10.1-10.4 subsections as separate)
- 3 critical severity (Sections 1, 5, 9, 11)
- 4 critical severity LLM failure mode axes (Section 11 subsections)
- 7 TDD-specific, 4 general-specific, 4 all-phases checks

**Coverage:**
- Addresses per-phase type differentiation without explicit type parameter
- Handles mixed artifacts (both TDD and general in same file)
- Escalation pathway for unfixable issues (cross-phase ordering, design gaps)
- Detailed fix patterns and examples for each criterion

---

## Key Gaps & Observations

**Observation 1: Section 11 foundation in external file**
- Section 11 states "Criteria from `agents/decisions/runbook-review.md` (four axes)"
- Actual decision file not examined — interpretation here is from SKILL.md re-expression
- Four-axes definition lives in decision file, not duplicated in skill

**Observation 2: TDD/general detection is heuristic-based**
- Relies on markdown header patterns (`## Cycle`, `## Step`)
- No programmatic type field in phase metadata
- Allows mixed types in same file; per-phase type detection flexible

**Observation 3: LLM failure mode checks lack quantified thresholds**
- Density: "<1 branch point difference" is qualitative heuristic
- Vacuity: "no behavioral content" requires interpretation
- Checkpoint spacing: >10 items, >2 phases are stated thresholds but no automated threshold enforcement visible
- Ordering: dependency analysis is manual, not rule-based

**Observation 4: General-step detection focused on creation patterns**
- Prerequisite validation specifically targets "creation steps (new code touching existing paths)"
- Transformation steps (delete, move, rename) explicitly exempt from prerequisite requirement
- Script evaluation based on prose/code size, not outcome validation

**Observation 5: Fix-all policy with escalation boundary**
- All critical, major, minor issues fixed directly (no triage/deferral)
- Unfixable issues escalated (cross-phase reordering, design gaps)
- UNFIXABLE vs DEFERRED distinction preserved (DEFERRED = out-of-scope, doesn't block)

---

## Recommendations for RCA Fixes

**For FR-1 (runbook-review overhaul):**
- Section 11 LLM failure modes already documented but lack algorithmic grounding
- General-step detection patterns (Section 10) could benefit from explicit prerequisite checklist
- Consider extracting Section 10 logic into reusable prerequisite validation helper

**For FR-2 (vet agent overhaul):**
- File reference validation (Section 9) uses Glob/Grep — portable to vet agent pattern library
- UNFIXABLE detection relies on grep pattern matching — consistent with vet-fix-agent design

**For FR-3 (outline review agent):**
- Density/checkpoint spacing detection (Sections 11.3-11.4) could guide outline phase review
- Cross-phase dependency detection (Section 11.2) critical for outline validation before runbook expansion
