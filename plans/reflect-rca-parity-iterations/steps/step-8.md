# Step 8

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 1

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
# Phase 3: Tier 3 Fixes (Moderate, Depends on Gap 4)

**Scope:** 2 steps, ~40 lines total, single session
**Model:** Haiku execution
**Complexity:** Moderate (multi-file skill edits, dependency on Gap 4 completion)

**Dependency:** Phase 3 starts AFTER Phase 2 is fully committed. Gap 4 (Phase 2 Steps 4-5) defines what "precise test descriptions" means; Gap 1 (Phase 3 Step 9) mandates when they're required.

---
