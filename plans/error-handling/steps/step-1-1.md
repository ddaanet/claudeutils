# Step 1.1

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 1

---

## Step 1.1: Add prevention-first principle to error-handling.md

**Objective**: Document fault prevention (Layer 0) in error-handling.md — establish the prevention-first principle across all subsystems by referencing existing prerequisite-validation.md patterns.
**Script Evaluation**: Small (≤25 lines inline — append ~4-6 lines to existing 12-line fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-handling.md` — understand existing content and minimalist structure (12 lines by design).

**Implementation**:
Add a new "Prevention Layer (L0)" subsection at the end of `agent-core/fragments/error-handling.md` (after the existing exception note). Content:
- Prevention-first principle: validate before execute — ~80% of errors caught before propagation
- Reference `prerequisite-validation.md` (existing patterns document the validation checklist)
- Cross-system scope: all three subsystems (orchestration, task lifecycle, CPS chains) benefit from validated preconditions before execution begins
- Keep addition to 4-6 lines only (D-4 constraint — error-handling.md is intentionally minimalist)

**Expected Outcome**: error-handling.md grows from 12 lines to ~16-18 lines. New subsection "Prevention Layer (L0)" present with prerequisite-validation.md reference.

**Error Conditions**:
- If adding more than 8 lines, STOP — revisit scope (D-4 constraint violated)

**Validation**:
- File has "Prevention Layer" or "L0" heading
- `prerequisite-validation.md` referenced
- File stays under 20 lines total

---
