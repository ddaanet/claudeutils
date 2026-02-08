# Step 5

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 5: Add Conformance Exception to "Prose Test Descriptions Save Tokens" in workflow-advanced.md

**Objective:** Update the prose test descriptions decision to document the conformance exception — when to use precise prose with exact expected strings instead of abstracted behavioral prose.

**Design Reference:** DD-2 (design lines 79-93), completes Gap 4

**File:** `agents/decisions/workflow-advanced.md` (existing, edit)

**Current State:**
- Section "Prose Test Descriptions Save Tokens" (around lines 187-199)
- Documents token savings from prose descriptions vs. full test code
- No exception documented for conformance work

**Changes Required:**

Add conformance exception after existing "Impact" line (around line 199), before next heading. New content (~10-12 lines):

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
Locate "### Prose Test Descriptions Save Tokens" section (around line 187). Find the "Impact:" line (around line 199). After this line, insert the conformance exception content above.

**Expected Outcome:**
- Section expanded with conformance exception (~10-12 lines added)
- Example contrast table matches Step 4 and design DD-2
- Rationale explains when to use precise vs. abstracted prose

**Validation:**
- Read updated section, verify exception content appears after "Impact" line
- Verify example table matches design lines 86-91
- Verify rationale explains conformance work vs. standard behavioral tests

**Success Criteria:**
- Exception content added after "Impact" line (or current location)
- Example table included with both rows (standard prose, conformance prose)
- Rationale paragraph explains spec preservation vs. token efficiency trade-off

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-5-execution.md`

---
