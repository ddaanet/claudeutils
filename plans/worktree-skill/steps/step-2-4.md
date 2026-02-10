# Cycle 2.4

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 2
**Report Path**: `plans/worktree-skill/reports/cycle-2-4-notes.md`

---

## Cycle 2.4: Jobs conflict status advancement

**NFR-2: Deterministic jobs.md conflict resolution with status ordering.**

**RED: Test behavior**

Create test fixture with two jobs.md versions:
- **Ours:** Plans table with "worktree-skill" status = "designed", "plugin-migration" status = "planned"
- **Theirs:** Same table with "worktree-skill" status = "planned", "plugin-migration" status = "planned"

Call `resolve_jobs_conflict(ours, theirs)` and assert:
- Result advances "worktree-skill" to "planned" (theirs has higher status)
- "plugin-migration" remains "planned" (no change, same status)
- Status ordering: requirements < designed < outlined < planned < complete

Additional test: verify "outlined" status ordering (between designed and planned) for plans using that intermediate state.

**Expected failure:** Function doesn't exist yet.

**GREEN: Implement behavior**

Create function `resolve_jobs_conflict(ours: str, theirs: str) -> str`:

**Algorithm hints:**
1. Define status ordering tuple: `("requirements", "designed", "outlined", "planned", "complete")`
2. Parse both versions for plan rows: regex `^\| ([^\|]+) \| ([^\|]+) \|` with `re.MULTILINE` on table body
3. Build plan→status maps for ours and theirs (strip whitespace from captured groups)
4. For each plan in theirs: compare status index (position in ordering tuple)
5. If theirs status index > ours status index: update ours plan's status
6. Reconstruct jobs.md with updated statuses: replace status cells in ours's table rows
7. Return merged content with advanced statuses

**Approach notes:**
- Table parsing must skip header rows (starts after `|------|--------|-------|`)
- Status comparison is index-based (tuple position), not string comparison
- Plans not in ours: ignore (merge doesn't add new plans, only updates existing)
- Preserve notes column exactly (no changes to notes text)

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-2-4-notes.md

### Phase 3: Merge Orchestration and Source Conflicts

**Complexity:** High
**Cycles:** ~13
**Model:** sonnet (implementation)
**Checkpoint:** full
**Files:** `src/claudeutils/worktree/merge.py`, `src/claudeutils/worktree/conflicts.py`, `tests/test_worktree_merge.py`
**Depends on:** Phase 2 (conflicts.py)

This phase implements the 3-phase merge ceremony (pre-checks, submodule resolution, parent merge) plus source conflict resolution with precommit validation. The merge is fully idempotent and handles both session and source conflicts deterministically.

---
