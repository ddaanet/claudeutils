# Step 3.2

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 3.2: Unit Tests for Registry Builder

**Execution Model:** Haiku

**File:** `tests/test_continuation_registry.py`

**Test scenarios:**
1. Frontmatter scanning extracts `cooperative` and `default-exit`
2. Non-cooperative skills excluded (`cooperative: false` or missing)
3. Cache invalidation on mtime change

**Report Path:** `plans/continuation-passing/reports/step-3-2-execution.md`

---
