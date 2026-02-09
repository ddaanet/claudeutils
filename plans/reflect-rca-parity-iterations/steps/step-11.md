# Step 11

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 11: Add Memory Index Entries for All New Decisions

**Objective:** Update memory-index.md with entries for all new decisions and guidance created in Phases 1-3, enabling future on-demand discovery.

**Design Reference:** All DD-1 through DD-8, implementation coverage

**File:** `agents/memory-index.md` (existing, append)

**Coverage Required:**

All changes from Phases 1-3 that introduce new knowledge or modify existing conventions:

1. **defense-in-depth.md** (Phase 2 Step 3, Q5) — Layered mitigation pattern
2. **Conformance precision** (Phase 2 Steps 4-5, Gap 4) — testing.md + workflow-advanced.md updates
3. **WIP-only restriction** (Phase 1 Step 1, Gap 5) — commit skill flag scope
4. **Planning-time file size awareness** (Phase 2 Steps 6-7, Gap 2) — plan-tdd + plan-adhoc convention
5. **Vet alignment** (Phase 3 Step 10, N2) — vet-fix-agent standard criterion
6. **Tool-call-first audit report** (Phase 2 Step 8, N1) — conditional lint decision based on compliance threshold

**New Entries Format:**

```markdown
