# Step 4

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 4: Expand "Conformance Validation for Migrations" in testing.md

**Objective:** Update the existing conformance validation section to document tests as executable contracts and the conformance exception to prose test descriptions.

**Design Reference:** DD-2 (design lines 79-93), partial fulfillment of Gap 4

**File:** `agents/decisions/testing.md` (existing, edit)

**Current State:**
- Section "Conformance Validation for Migrations" (around line 128)
- Currently ~13 lines, sparse content
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
