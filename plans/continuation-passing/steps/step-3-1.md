# Step 3.1

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 3.1: Unit Tests for Continuation Parser

**Execution Model:** Haiku

**File:** `tests/test_continuation_parser.py`

**Test scenarios** (from design Component 4):
1. Single skill with args → default exit appended
2. Inline prose (`, /` delimiter) → correct split
3. Multi-line list (`and\n- /skill`) → correct entries
4. Path args not treated as skills
5. Connecting words in prose not continuation
6. Flag handling (`/handoff --commit`)
7. Unknown skill ignored
8. Terminal skill (`/commit`) → empty continuation

**Report Path:** `plans/continuation-passing/reports/step-3-1-execution.md`

---
