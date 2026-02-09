# Phase 2: Tier 2 Fixes (Low Complexity, Parallelizable)

**Scope:** 6 steps, ~200 lines total (4 edits + 2 new files), single session
**Model:** Haiku execution (steps 3-7), Sonnet for N1 audit (step 8)
**Complexity:** Low-moderate (multi-file edits, clear scope, internal sequencing for Gap 4 → Gap 1)

**Parallelization:**
- Steps 3, 6, 7, 8 are fully independent and can run in parallel
- Steps 4-5 (Gap 4) are prerequisites for Phase 3 Step 9 (Gap 1)
- All Phase 2 steps must complete before Phase 3 starts

**Conditional output:**
- Step 8 produces either: (a) audit report + `scripts/check_skill_steps.py` + justfile entry, OR (b) audit report documenting decision not to ship lint

---

## Step 3: Create defense-in-depth.md Decision Document

**Objective:** Document the layered mitigation pattern as a reusable principle for future quality gate design, covering the Gap 3 + Gap 5 interaction and general defense-in-depth approach.

**Design Reference:** DD-6 (design lines 137-146)

**File:** `agents/decisions/defense-in-depth.md` (new)

**Content Structure:**

```markdown
## Defense-in-Depth Pattern

**Decision Date:** 2026-02-08

**Decision:** Quality gates should be layered with multiple independent checks to prevent single-point failures. No single gate should be trusted as the sole enforcement mechanism.

**Rationale:** [From DD-6 — multiple quality gates interact to catch different failure modes]

**Pattern layers (from outer to inner):**
1. **Outer defense:** D+B hybrid ensures precommit appears in execution path (gates prose steps from skipping validation)
2. **Middle defense:** Precommit catches line limits, lint, test failures (hard validation at commit time)
3. **Inner defense:** Vet-fix-agent catches quality and alignment issues (semantic review before commit)
4. **Deepest defense:** Conformance tests catch spec-to-implementation drift (executable contracts)

**Gap 3 + Gap 5 interaction:**
- Gap 3 (prose gate skipping): D+B hybrid fix ensures precommit runs (outer defense)
- Gap 5 (WIP-only bypass): `--test`/`--lint` flags provide legitimate within-path bypass of line limits
- Defense-in-depth: D+B (outer) + WIP-only restriction (inner) close this interaction — D+B ensures gates run, WIP-only ensures bypass is scoped to appropriate commits

**Example application:**
[Describe how statusline-parity iterations demonstrate gap in single-layer validation]

**Applicability:**
- This pattern applies beyond parity tests — use for any quality gate design
- When adding new quality mechanisms, consider which layer they belong to
- Multiple layers compensate for individual gate weaknesses (e.g., tests can pass but miss visual conformance)

**Related decisions:**
- DD-3 (WIP-only restriction) — inner defense layer
- DD-5 (Vet alignment) — inner defense layer
- DD-1 (Conformance tests) — deepest defense layer
```

**Implementation:**
Write new file to `agents/decisions/defense-in-depth.md` with the structure above. Expand sections marked with [brackets] using design context from DD-6 and RCA (plans/reflect-rca-parity-iterations/rca.md).

**Expected Outcome:**
- New decision document exists at specified path
- Contains ~60-80 lines documenting layered mitigation pattern
- Includes Gap 3 + Gap 5 interaction analysis
- References related design decisions (DD-3, DD-5, DD-1)

**Validation:**
- Read created file, verify structure matches template
- Verify all four layers documented with clear descriptions
- Verify Gap 3 + Gap 5 interaction explained

**Success Criteria:**
- File exists at `agents/decisions/defense-in-depth.md`
- Contains pattern description, layer enumeration, Gap 3+5 interaction, applicability guidance
- Between 60-80 lines total
- Decision date is 2026-02-08

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-3-execution.md`

---

## Step 4: Expand "Conformance Validation for Migrations" in testing.md

**Objective:** Update the existing conformance validation section to document tests as executable contracts and the conformance exception to prose test descriptions.

**Design Reference:** DD-2 (design lines 79-93), partial fulfillment of Gap 4

**File:** `agents/decisions/testing.md` (existing, edit)

**Current State:**
- Section "Conformance Validation for Migrations" at lines 128-140
- Currently 13 lines, sparse content
- Basic pattern documented but missing precision guidance

**Changes Required:**

Expand section to ~30 lines covering:

1. **Tests as executable contracts (DD-1 principle):**
   - When design includes external reference (shell prototype, API spec, visual mockup), tests bake expected behavior into assertions
   - Reference consumed at authoring time, tests become permanent living documentation
   - Example: statusline-parity tests should assert exact expected strings from shell reference (e.g., `🥈 sonnet \033[35m…`), not just structure ("contains emoji")

2. **Exact expected strings requirement:**
   - For conformance work, test assertions include exact expected output from the reference
   - This eliminates translation loss between spec and implementation
   - Addresses RC5 from RCA: "Visual Parity Validated" false completion claims are detectable when tests include exact strings

3. **Conformance exception to prose descriptions:**
   - Standard TDD: Use prose descriptions, not full test code (per workflow-advanced.md)
   - Conformance exception: Prose descriptions MUST include exact expected strings from reference
   - This is not full test code — it is precise prose

4. **Example contrast table (from DD-2 lines 86-91):**
   ```
   | Standard prose | Conformance prose |
   |----------------|-------------------|
   | "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator" |
   ```

**Implementation:**
Locate "## Conformance Validation for Migrations" section (around line 128). Expand from ~13 lines to ~30-35 lines with the four elements above. Preserve existing content (comparison pattern, benefits, example, impact) and integrate new content.

**Expected Outcome:**
- Section expanded with tests-as-executable-contracts principle
- Exact expected strings requirement documented
- Conformance exception to prose descriptions explained
- Example contrast table included (standard vs conformance prose)

**Validation:**
- Read updated section, verify ~30-35 lines total
- Verify all four elements present (contracts, exact strings, prose exception, example table)
- Verify existing content preserved (decision date, pattern, benefits, impact)

**Success Criteria:**
- Section length ~30-35 lines (was ~13 lines)
- Contains all four elements from design DD-2
- Example contrast table matches design lines 86-91
- Existing "Decision Date: 2026-02-05" and other fields preserved

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-4-execution.md`

---

## Step 5: Add Conformance Exception to "Prose Test Descriptions Save Tokens" in workflow-advanced.md

**Objective:** Update the prose test descriptions decision to document the conformance exception — when to use precise prose with exact expected strings instead of abstracted behavioral prose.

**Design Reference:** DD-2 (design lines 79-93), completes Gap 4

**File:** `agents/decisions/workflow-advanced.md` (existing, edit)

**Current State:**
- Section "Prose Test Descriptions Save Tokens" at lines 187-199
- Documents token savings from prose descriptions vs. full test code
- No exception documented for conformance work

**Changes Required:**

Add conformance exception after existing "Impact" line (line 199), before next heading. New content (~10-12 lines):

```markdown
**Conformance exception:**

For conformance-type work with exact specifications (external reference, API spec, visual mockup), prose descriptions MUST include the exact expected strings from the reference.

This is not full test code — it is precise prose that preserves the specification.

**Example contrast:**

| Standard prose | Conformance prose |
|----------------|-------------------|
| "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator" |

**Rationale:** Standard prose is efficient for behavioral tests. For conformance work, the specification IS the exact string — abstracting it introduces translation loss. Precise prose preserves spec fidelity while maintaining token efficiency (still more compact than full test code).
```

**Implementation:**
Locate "### Prose Test Descriptions Save Tokens" section (around line 187). Find the "Impact:" line (line 199). After this line, insert the conformance exception content above.

**Expected Outcome:**
- Section expanded with conformance exception (~10-12 lines added)
- Example contrast table matches Step 4 and design DD-2
- Rationale explains when to use precise vs. abstracted prose

**Validation:**
- Read updated section, verify exception content appears after "Impact" line
- Verify example table matches design lines 86-91
- Verify rationale explains conformance work vs. standard behavioral tests

**Success Criteria:**
- Exception content added after line 199 (or current "Impact" line location)
- Example table included with both rows (standard prose, conformance prose)
- Rationale paragraph explains spec preservation vs. token efficiency trade-off

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-5-execution.md`

---

## Step 6: Add Planning-Time File Size Awareness to plan-tdd Skill

**Objective:** Update plan-tdd skill to include convention for noting current file sizes when adding content and proactively planning splits when approaching the 400-line limit.

**Design Reference:** DD-4 (design lines 108-119)

**File:** `agent-core/skills/plan-tdd/SKILL.md` (existing, edit)

**Current State:**
- Skill documents TDD runbook creation process
- No guidance on file size awareness during planning

**Changes Required:**

Add file size awareness convention to planner guidance sections. Exact location depends on current structure — search for sections discussing cycle planning or implementation details. Add ~15 lines:

```markdown
### Planning-Time File Size Awareness

**Convention:** When a cycle adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each cycle adding content to existing file: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: Include a split step in the same phase
3. Threshold is 350, not 400 — leaves 50-line margin for vet fixes and minor additions

**Why 350:** The 400-line limit is a hard fail at commit time. Planning to the exact limit creates brittleness. A 50-line margin is pragmatic.

**Example:**
- Cycle 3.2 adds format_model() to display.py (current: ~320 lines, adding ~40)
- Cycle 3.2: Implement format_model() (~360 lines total)
- Cycle 3.3: Split display.py into display_core.py + display_formatters.py

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.
```

**Implementation:**
Locate planner guidance sections in plan-tdd/SKILL.md (likely within Phase 1-3 or cycle planning sections). Insert the file size awareness convention content above. Integrate with existing guidance — if there's a "Cycle Planning" section, add this as a subsection.

**Expected Outcome:**
- Convention documented with process steps (note sizes, check threshold, plan splits)
- Rationale explains 350-line margin (not 400)
- Example demonstrates notation and split planning
- Clarifies this is planning convention, not runtime enforcement

**Validation:**
- Read updated skill, verify convention content present
- Verify 350-line threshold explained with margin rationale
- Verify example shows both notation and split step

**Success Criteria:**
- ~15 lines added to plan-tdd/SKILL.md
- Contains process steps, threshold (350), example, runtime enforcement note
- Integrated with existing planner guidance sections

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-6-execution.md`

---

## Step 7: Add Planning-Time File Size Awareness to plan-adhoc Skill

**Objective:** Update plan-adhoc skill with the same file size awareness convention as plan-tdd, adapted for non-TDD context.

**Design Reference:** DD-4 (design lines 108-119)

**File:** `agent-core/skills/plan-adhoc/SKILL.md` (existing, edit)

**Current State:**
- Skill documents ad-hoc runbook creation process
- No guidance on file size awareness during planning

**Changes Required:**

Add file size awareness convention to planner guidance sections. Content is nearly identical to Step 6, adapted for non-TDD terminology (~15 lines):

```markdown
### Planning-Time File Size Awareness

**Convention:** When a step adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each step adding content to existing file: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: Include a split step in the same phase
3. Threshold is 350, not 400 — leaves 50-line margin for vet fixes and minor additions

**Why 350:** The 400-line limit is a hard fail at commit time. Planning to the exact limit creates brittleness. A 50-line margin is pragmatic.

**Example:**
- Step 2.3 adds authentication handlers to routes.py (current: ~330 lines, adding ~35)
- Step 2.3: Implement authentication handlers (~365 lines total)
- Step 2.4: Split routes.py into routes_auth.py + routes_core.py

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.
```

**Implementation:**
Locate planner guidance sections in plan-adhoc/SKILL.md (likely within Point 1 phase-by-phase expansion or step planning sections). Insert the file size awareness convention content. Integrate with existing guidance.

**Expected Outcome:**
- Convention documented with process steps (adapted from plan-tdd Step 6)
- Example uses ad-hoc terminology (step numbers, not cycle numbers)
- Rationale and threshold (350) identical to plan-tdd version

**Validation:**
- Read updated skill, verify convention content present
- Verify example uses ad-hoc terminology (not TDD cycles)
- Verify threshold and rationale match plan-tdd Step 6

**Success Criteria:**
- ~15 lines added to plan-adhoc/SKILL.md
- Contains process steps, threshold (350), example adapted for ad-hoc context
- Integrated with existing planner guidance sections

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-7-execution.md`

---

## Step 8: Manual Skill Audit → Decision on Lint Script

**Objective:** Audit all skills for tool-call-first convention compliance, categorize findings, and decide whether to ship `scripts/check_skill_steps.py` as a hard fail linter.

**Design Reference:** DD-7 (design lines 148-158)

**Model:** Sonnet (requires semantic judgment for categorization)

**Process:**

1. **Discover all skill files:**
   ```bash
   find agent-core/skills -name "SKILL.md" -type f | sort
   ```

2. **For each skill file, audit numbered steps:**
   - Locate all numbered step headings (`### N.`, `### N.M.`)
   - For each step: Check if first 5 lines after heading contain a tool call (Read, Write, Edit, Bash, Grep, Glob, Task, etc.)
   - Categorize:
     - **Compliant:** Step has tool call in first 5 lines
     - **Legitimately exempt:** Step is prose-only checkpoint or decision point (e.g., "Assess complexity", "Decide on approach")
     - **Non-compliant:** Step should have tool call but doesn't (e.g., delegates to haiku but opens with prose, not Task call)

3. **Produce audit report:**
   Write to `plans/reflect-rca-parity-iterations/reports/n1-audit.md`:
   - Audit summary: Total skills, total steps, compliance percentage
   - Breakdown by category (compliant, exempt, non-compliant)
   - List of non-compliant steps with file paths
   - List of legitimately exempt steps with rationale

4. **Decision threshold (from DD-7):**
   - **If ≥80% comply with few false positives (<10% of compliant flagged):**
     - Ship lint: Create `scripts/check_skill_steps.py` with `<!-- no-tool-call-check -->` exemption marker
     - Update justfile: Add skill step validation to precommit recipe
     - Document decision: "Lint ships — 80% threshold met, convention validated"
   - **If <80% comply or many false positives (≥10%):**
     - Don't ship: Convention remains guidance only
     - Document decision: "Lint not shipped — compliance below threshold, convention needs refinement"

5. **Conditional outputs:**
   - **Path A (ship lint):** Audit report + `scripts/check_skill_steps.py` + justfile edit
   - **Path B (don't ship):** Audit report documenting decision rationale

**Expected Outcome:**
- Audit report exists with compliance metrics
- Decision documented (ship or don't ship) with threshold analysis
- If shipping: Lint script and justfile edit created

**Validation:**
- Read audit report, verify all skills audited
- Verify decision threshold correctly applied (≥80% = ship, <80% = don't ship)
- If shipping: Verify script exists and justfile updated

**Success Criteria:**
- Audit report at `plans/reflect-rca-parity-iterations/reports/n1-audit.md` with compliance percentage
- Decision documented with threshold evidence
- Conditional outputs match decision (Path A or Path B)

**Report Path:** `plans/reflect-rca-parity-iterations/reports/n1-audit.md`

**Note:** This step uses sonnet model due to semantic categorization required (distinguishing "legitimately exempt" from "non-compliant" requires judgment about step intent).

---

## Phase 2 Checkpoint

**Completion Criteria:**
- Step 3: defense-in-depth.md created with layered mitigation pattern (~60-80 lines)
- Step 4: testing.md "Conformance Validation for Migrations" expanded (~30 lines)
- Step 5: workflow-advanced.md "Prose Test Descriptions Save Tokens" has conformance exception (~10 lines added)
- Step 6: plan-tdd/SKILL.md has file size awareness convention (~15 lines)
- Step 7: plan-adhoc/SKILL.md has file size awareness convention (~15 lines)
- Step 8: N1 audit report complete with decision (conditional: lint ships or doesn't ship)

**Verification before proceeding to Phase 3:**
- Gap 4 changes (Steps 4-5) must be committed before Phase 3 begins
- Gap 4 defines "precise test descriptions" that Gap 1 (Phase 3 Step 9) mandates

**Next Phase:** Phase 3 (Tier 3 fixes — Gap 1 conformance test cycles, N2 vet alignment)
