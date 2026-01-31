# Design Review: Claude Tools Recovery Runbook

**Date**: 2026-01-31
**Reviewer**: Opus 4.5
**Status**: Option C recommended (hybrid)

---

## Problem Summary

Step 0-2 failed because it references `tests/test_account.py` (nonexistent) and assumes hasattr-only provider tests exist (none found). The steps directory contains 44 files from two separate runbook generations: 13 files matching the current runbook (0-1, 1-1..1-5, 2-1..2-4, 3-1..3-3) and 31 orphaned files from a previous generation (0-2..0-4, 1-6..1-7, 2-5..2-10, 3-4..3-14, 4-1..4-8). The orchestrator plan correctly references only 13 steps, but step-0-2 through step-0-4 from the old generation collide with the namespace and were executed instead of being skipped.

---

## Root Cause Analysis

**Why does step-0-2 exist when the runbook only documents Cycle 0.1?**

Two separate runbook generations left artifacts in the same `steps/` directory:

- **Generation 1** (previous session): Produced ~44 step files covering a larger runbook with 4+ phases (R0 with 4 cycles, R1 with 7, R2 with 10, R3 with 14, R4 with 8). These files reference `tests/test_account.py` and assume hasattr patterns exist -- consistent with an earlier codebase state or inferred structure.

- **Generation 2** (session documented in session.md): Regenerated `runbook.md` with 13 cycles across 4 phases (R0-R3). Used `/plan-tdd` which "discovers actual file structure via Glob." Ran `prepare-runbook.py` which generated 13 step files. But `prepare-runbook.py` did not clean the `steps/` directory before writing, so the 31 orphaned files from Generation 1 remained.

**The root cause is `prepare-runbook.py` not performing a clean sweep of the steps directory before generation.** It writes new files but does not delete stale ones. When the orchestrator encountered `step-0-2`, it found the Generation 1 artifact referencing a nonexistent file.

**Secondary cause:** The orchestrator plan lists steps by cycle ID (`Step 0-1`, `Step 1-1`, etc.) and maps them to step files by convention (`step-{phase}-{cycle}.md`). The plan correctly skips from `Step 0-1` to `Step 1-1`, but whatever dispatch mechanism was used attempted `step-0-2` rather than following the orchestrator plan exclusively.

**The design itself is sound.** The recovery design (`design.md`) correctly identifies phases, integration points, and mock strategy. The current runbook (`runbook.md`) is well-structured with 13 cycles that cover the design's intent. The issue is purely in the toolchain (prepare-runbook.py directory hygiene) and step file namespace collision.

---

## Option Evaluation

### Option A: Pragmatic (Sonnet's recommendation)

**Actions:** Delete `test_provider_protocol_exists()`, skip to Phase R1, delete orphaned step files 0-2..0-4.

**Pros:**
- Minimal disruption, immediate resumption
- Phase R0 objective is effectively achieved (one vacuous test remains)
- Current runbook is correct for phases R1-R3

**Cons:**
- Only deletes 3 orphaned step files (0-2, 0-3, 0-4); leaves 28 others (1-6..1-7, 2-5..2-10, 3-4..3-14, 4-1..4-8)
- Does not address the root cause (prepare-runbook.py hygiene)
- Risk: future steps may also collide if orchestrator dispatch is not strictly bound to the orchestrator plan

**Assessment:** Sonnet correctly identified the immediate fix but underestimated the orphan scope. There are 31 orphaned files, not 3. If only 3 are deleted, later phases may encounter similar collisions (e.g., step-1-6 and step-1-7 exist but the runbook only has cycles 1.1-1.5).

### Option B: Regenerate runbook

**Actions:** Pause execution, regenerate runbook with `/plan-tdd`.

**Pros:**
- Produces a clean, consistent artifact set
- Validates the pipeline end-to-end

**Cons:**
- Wasteful: the current runbook content is correct (13 cycles, proper TDD structure, passed review)
- Cost: /plan-tdd + review + prepare-runbook.py cycle is expensive in tokens and time
- Same bug may recur if prepare-runbook.py still does not clean the directory

**Assessment:** The runbook content does not need regeneration. The problem is stale files in the steps directory, not incorrect runbook content.

### Option C: Hybrid (recommended)

**Actions:**
1. Delete `test_provider_protocol_exists()` (one remaining vacuous test)
2. Delete ALL 31 orphaned step files (not just 3)
3. Proceed with Phase R1 using the current runbook
4. File a pending task to fix prepare-runbook.py (clean steps/ before generation)

**Pros:**
- Immediate resumption with no collision risk
- Addresses the full orphan scope, not a partial cleanup
- Current runbook is correct and reviewed (PASS from tdd-plan-reviewer)
- Root cause addressed via pending task (prevents recurrence)

**Cons:**
- Does not fix prepare-runbook.py now (deferred)
- Requires manual identification and deletion of orphans

**Assessment:** This is the right balance. The runbook is good, the step files matching the runbook are good, and only the stale files need removal.

---

## Recommendation: Option C (Hybrid)

**Rationale:** The design is correct. The runbook is correct. The orchestrator plan is correct. The only problem is 31 stale step files from a previous generation polluting the namespace. Deleting them and proceeding is the highest-value action.

Regeneration (Option B) would cost significant tokens to reproduce identical runbook content. Partial cleanup (Option A) leaves collision risk for later phases.

---

## Action Steps for Orchestrator

**Immediate (before resuming execution):**

1. **Delete vacuous test:** Remove `test_provider_protocol_exists()` from `tests/test_account_providers.py` (lines 13-21). Commit.

2. **Delete all 31 orphaned step files:**
   - `step-0-2.md`, `step-0-3.md`, `step-0-4.md`
   - `step-1-6.md`, `step-1-7.md`
   - `step-2-5.md` through `step-2-10.md`
   - `step-3-4.md` through `step-3-14.md`
   - `step-4-1.md` through `step-4-8.md`

   Retain only: `step-0-1.md`, `step-1-1.md`..`step-1-5.md`, `step-2-1.md`..`step-2-4.md`, `step-3-1.md`..`step-3-3.md` (13 files matching runbook)

3. **Verify alignment:** Confirm orchestrator-plan.md references exactly 13 steps matching retained step files.

4. **Resume execution:** Continue from Phase R1, Cycle 1.1 (`step-1-1.md`).

**Pending (for future sessions):**

- Fix `prepare-runbook.py` to clean `steps/` directory before writing new files (delete all `step-*.md` or move to a timestamped generation directory)
- Add this to session.md pending tasks

---

## Appendix: File Inventory

**Retained step files (13, matching runbook):**
step-0-1, step-1-1, step-1-2, step-1-3, step-1-4, step-1-5, step-2-1, step-2-2, step-2-3, step-2-4, step-3-1, step-3-2, step-3-3

**Orphaned step files (31, from previous generation):**
step-0-2, step-0-3, step-0-4, step-1-6, step-1-7, step-2-5, step-2-6, step-2-7, step-2-8, step-2-9, step-2-10, step-3-4, step-3-5, step-3-6, step-3-7, step-3-8, step-3-9, step-3-10, step-3-11, step-3-12, step-3-13, step-3-14, step-4-1, step-4-2, step-4-3, step-4-4, step-4-5, step-4-6, step-4-7, step-4-8

---

*Review by Opus 4.5. Design is sound; toolchain artifact hygiene caused the regression.*
