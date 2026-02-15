# RCA: Runbook Outline Review Defects (worktree-fixes)

**Source:** Round 2 review of `plans/worktree-fixes/runbook-outline.md`
**Date:** 2026-02-14

---

## Findings

5 minor issues found and fixed. Three systemic patterns identified.

## Pattern 1: Cycle-per-bullet decomposition

**Instances:** M-4 (cycles 1.4-1.6 → 2 cycles), M-5 (cycles 1.10-1.11 → 1 cycle)

**Symptom:** Outline generator maps design description bullets to cycles 1:1 without evaluating behavioral separability. `_resolve_session_md_conflict()` (~40 lines) got 3 cycles; `focus_session()` (19 lines) got 2 cycles.

**Mechanism:** Design says three things about `_resolve_session_md_conflict()`: uses `extract_task_blocks()`, preserves continuation lines, uses `find_section_bounds()`. Each became a cycle. But these are aspects of one change — you can't "use extract_task_blocks()" without preserving continuation lines (that's what the function does). The RED phase for cycle 1.5 would be identical to 1.4's GREEN verification.

**Detection heuristic:** For each function being modified: if proposed cycles touching that function > function LOC / 20, consolidation likely needed.

**Deeper check:** For each cycle pair (N, N+1) on the same function, verify N+1's RED assertion would *fail* given N's GREEN implementation. If not, cycles are behaviorally vacuous.

**Round 1 review gap:** Round 1 caught one vacuous cycle (`find_section_bounds()` scaffolding) but missed three more instances. It checked for scaffolding vacuity (existence-check-only tests) but not behavioral vacuity (cycle N+1's RED entailed by cycle N's GREEN).

**Fix:** `agents/decisions/runbook-review.md` vacuous cycle detection should cover both scaffolding vacuity AND behavioral vacuity. Add the "would N+1's RED fail after N's GREEN?" check.

## Pattern 2: Review-then-append, not review-then-integrate

**Instance:** M-2 (duplicate Expansion Guidance sections)

**Symptom:** Round 1 review recommendations were appended as "## Expansion Guidance (from outline review)" — a second section with the same heading concept. Original "## Expansion Guidance" section already existed 60 lines above.

**Mechanism:** Review agents produce findings as structured output. Fix application defaults to "append" when the fix is prose guidance rather than code. No structural constraint forces integration into existing sections.

**Fix:** Review-fix workflow should include an integration step: when recommendations target an existing section, merge into that section rather than creating a parallel one.

## Pattern 3: Codebase-blind cross-referencing

**Instance:** M-1 (confabulated test name `test_conflicting_pending_tasks`)

**Symptom:** Round 1 review agent referenced `test_worktree_merge_conflicts.py::test_conflicting_pending_tasks`. No such test exists. Actual test: `test_merge_conflict_session_md`.

**Mechanism:** LLM agents generate identifiers from semantic context ("conflicting pending tasks" → `test_conflicting_pending_tasks`) rather than filesystem state. Without explicit Grep verification, agents confabulate plausible names.

**Fix:** Any outline/runbook cross-reference to an existing test or function name must be verified via Grep before inclusion. Confabulated identifiers propagate to execution agents who waste cycles searching for nonexistent artifacts.

---

## Relationship to Existing RCAs

- **Pattern 1** extends vacuous cycle detection in `agents/decisions/runbook-review.md` (already covers scaffolding vacuity, needs behavioral vacuity)
- **Pattern 2** is new — review integration workflow gap
- **Pattern 3** relates to `rca-vet-over-escalation` (agents confabulating issues from inferred rather than verified state)
