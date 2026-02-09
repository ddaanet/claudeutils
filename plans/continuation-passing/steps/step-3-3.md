# Step 3.3

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 3.3: Unit Tests for Consumption Protocol

**Execution Model:** Haiku

**File:** `tests/test_continuation_consumption.py`

**Test scenarios:**
1. Peel first entry from `[CONTINUATION: /a, /b, /c]` → target: `/a`, remainder: `/b, /c`
2. Last entry consumption → target: `/commit`, remainder: empty
3. Empty continuation → terminal (no tail-call)

**Report Path:** `plans/continuation-passing/reports/step-3-3-execution.md`

---
