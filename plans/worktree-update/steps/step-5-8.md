# Cycle 5.8

**Plan**: `plans/worktree-update/runbook.md`
**Execution Model**: haiku
**Phase**: 5

---

## Cycle 5.8: Session file handling — warn and ignore `--session` when branch exists

**Objective:** Handle session file logic correctly when reusing existing branches (session already committed).

**RED Phase:**

**Test:** `test_new_session_handling_branch_reuse`
**Assertions:**
- When branch exists and `--session` provided: warning printed, `--session` ignored
- No attempt to commit session to existing branch (branch already has its session)
- When branch doesn't exist and `--session` provided: normal session commit flow
- Warning message mentions branch reuse as reason for ignoring `--session`

**Expected failure:** AssertionError: no warning printed, or session commit attempted on existing branch, or error raised

**Why it fails:** Session handling doesn't account for branch reuse scenario

**Verify RED:** `pytest tests/test_worktree_new.py::test_new_session_handling_branch_reuse -v`

---

**GREEN Phase:**

**Implementation:** Add conditional session handling based on branch existence

**Behavior:**
- When branch exists (from 5.1 detection) AND `--session` provided:
  - Print warning: "Branch <slug> exists, ignoring --session (session already committed)"
  - Skip session commit logic
- When branch doesn't exist and `--session` provided:
  - Proceed with existing session commit flow (unchanged)
- When `--task` mode: session handling via temp file (from 5.7), branch reuse logic still applies

**Approach:** Conditional logic linking branch existence check from 5.1 to session commit decision

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add session handling conditional in `new` command
  Location hint: Where session commit logic exists
- File: `src/claudeutils/worktree/cli.py`
  Action: Check branch existence flag from earlier detection
  Location hint: Use same boolean/result from 5.1's branch check
- File: `src/claudeutils/worktree/cli.py`
  Action: Print warning and skip session commit if branch exists
  Location hint: Conditional around session commit code
- File: `src/claudeutils/worktree/cli.py`
  Action: Preserve existing session commit flow for new branches
  Location hint: Else branch of conditional

**Verify GREEN:** `pytest tests/test_worktree_new.py::test_new_session_handling_branch_reuse -v`
- Must pass

**Verify no regression:** `pytest tests/test_worktree_new.py -v`
- All Phase 5 tests still pass

---

**Checkpoint: Post-Phase 5**

**Type:** Full checkpoint (Fix + Vet + Functional)

**Process:**
1. **Fix:** Run `just dev`. If failures, sonnet quiet-task diagnoses and fixes. Commit when passing.
2. **Vet:** Review all Phase 1-5 changes for quality, clarity, design alignment. Apply all fixes. Commit.
3. **Functional:** Review all implementations against design.
   - Check: Are path computations real or stubbed? Does branch detection actually work?
   - Check: Is task mode integration tested end-to-end or just mocked?
   - If stubs found: STOP, report which implementations need real behavior
   - If all functional: Proceed to Phase 6

**Rationale:** Phase 5 is major integration point — `new` command orchestrates all prior functions. Validate completeness before proceeding to `rm` and `merge` commands.

# Phase 6: Update `rm` Command

**Complexity:** Medium (5 cycles)
**Files:**
- `src/claudeutils/worktree/cli.py`
- `tests/test_worktree_cli.py`

**Description:** Refactor `rm` command with improved removal logic — submodule-first ordering, container cleanup, safe branch deletion.

**Dependencies:** Phase 1 (needs `wt_path()` for path resolution)

---
