## 2026-02-21: Delivered status — design decisions from discussion

**Problem:** Plans at "ready" remain "ready" after execution and merge. `#status` shows `→ /orchestrate` for completed work. No terminal state in plan lifecycle.

**Terminology (needs grounding):**
- "Completed" = ready for delivery (execution done, review passed)
- "Delivered" = merged into main (our context) or released/deployed (other contexts)
- "Review-pending" = execution complete, deliverable review not yet run
- "Defective" = deliverable review found blocking issues, rework needed
- **Action:** `/ground` lifecycle terminology before design — validate against established delivery frameworks (kanban, DORA, CI/CD). Check if "defective" is standard or if "rejected"/"failed"/"rework" is more common.

**Full lifecycle (proposed, pre-grounding):**
`requirements → designed → planned → ready → review-pending → [defective ↔ review-pending] → completed → delivered`

**Decisions:**
- D-1: Post-ready states form a review loop: review-pending (orchestration done) → defective (review failed) or completed (review passed) → delivered (merged).
- D-2: `delivered.md` created at `_worktree merge` into main. In-main: completed and delivered in sequence (no merge gap).
- D-3: Marker files with minimal content (date, source). Not empty. Detection: `exists()` check. Content for humans, not parsed.
- D-4: `_determine_status` priority: `delivered > completed > defective > review-pending > ready > planned > designed > requirements`.
- D-5: `_derive_next_action` returns empty for delivered, re-review for defective.
- D-6: `#status` excludes delivered plans from Unscheduled Plans.

**Deliverable review gate:** `/deliverable-review` required before merge into main — biggest impact on delivery quality. Self-review shortcut when: no behavioral changes, no cross-file contracts, vet already passed. Gate is on the review-pending → completed transition.

**Scope IN:** `_determine_status`, `_derive_next_action`, 4 new marker files (review-pending, defective, completed, delivered), marker creation in merge/orchestration/review paths, `#status` filtering, deliverable review as pre-merge gate with complexity shortcut, tests.

**Affected files:** `src/claudeutils/planstate/inference.py`, merge logic, `tests/test_planstate_inference.py`, `agent-core/fragments/execute-rule.md` (terminology).

**Adjacent:** `plans/worktree-merge-resilience/diagnostic.md` — merge-artifact diagnostic (separate task). `worktree-merge-data-loss` is delivered/removable (first use of new status).
