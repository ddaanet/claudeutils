# Step 3.4

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 3.4: Integration Test (2-Skill Chain)

**Execution Model:** Sonnet

**File:** `tests/test_continuation_integration.py`

**Test flow:**
1. Hook parses `/design, /plan-adhoc` → emits `additionalContext`
2. First skill reads `additionalContext` → tail-calls `/plan-adhoc` with `[CONTINUATION: /handoff --commit, /commit]`
3. Second skill reads `args` suffix → tail-calls `/handoff --commit` with `[CONTINUATION: /commit]`
4. Verify chain completes correctly

**Report Path:** `plans/continuation-passing/reports/step-3-4-execution.md`

---
