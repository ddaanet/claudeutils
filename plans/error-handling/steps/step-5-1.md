# Step 5.1

**Plan**: `plans/error-handling/runbook.md`
**Execution Model**: opus
**Phase**: 5

---

## Step 5.1: Add hook error protocol to error-handling.md (D-6)

**Objective**: Formalize the hook error protocol in error-handling.md — what happens when hooks crash, timeout, or produce invalid output. The CPS hook already silently catches errors; this step makes the intended degraded-mode behavior explicit.
**Script Evaluation**: Small (≤25 lines — append ~8-10 lines to ~18-line fragment)
**Execution Model**: Opus (fragment artifact)

**Prerequisite**: Read `agent-core/fragments/error-handling.md` (post-Step-1.1 state) — understand current content before adding hook protocol subsection.

**Implementation**:
Add "Hook Error Protocol (D-6)" subsection at the end of `agent-core/fragments/error-handling.md`:

Three failure modes, each with defined behavior:
- **Hook crash**: stderr output visible to user + session continues (intentional degraded mode — CPS hook design silently catches errors, this formalizes that as the intended behavior, not a bug)
- **Hook timeout**: degraded mode for that event — hook behavior absent for the current invocation; session continues without hook processing
- **Invalid hook output**: fallback to no-hook behavior — hook result ignored; session continues as if hook were not installed

Apply D-4 constraint: addition must stay focused (8-10 lines). No narrative explanation of why hooks fail.

**Expected Outcome**: error-handling.md grows to ~26-28 lines total (12 original + ~6 from Step 1.1 + ~8-10 from this step). Hook Error Protocol subsection present with all 3 failure modes.

**Error Conditions**:
- If adding more than 12 lines, STOP — revisit scope (D-4 constraint violated)

**Validation**:
- "Hook Error Protocol" or "D-6" heading present
- All 3 failure modes present: crash, timeout, invalid output
- "degraded mode" concept documented for timeout case
- File total length ≤ 30 lines

---
