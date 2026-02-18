## Phase 3: Parent merge preservation + untracked handling (type: tdd)

**Goal:** Remove `git merge --abort` + `git clean -fd` from `_phase3_merge_parent` (D-3, NFR-2). Add untracked-file-collision detection and `git add` + retry logic (D-4, FR-3). Update two existing tests that assert the old abort behavior.

**Files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_errors.py`

**Depends on:** Cycles 1.3 (exit 3 path exists) and 2.1 (Phase 2 pass-through stable before testing Phase 3 behavior).

**Common context for all cycles:**
- Primary change: lines 170-175 in `_phase3_merge_parent` — remove `_git("merge", "--abort")` + `_git("clean", "-fd")` + `click.echo(f"Merge aborted: ...")` + `raise SystemExit(1)`. Replace with: report conflict list + `raise SystemExit(3)`.
- Untracked file failure mode: `git merge --no-commit --no-ff slug` exits non-zero AND MERGE_HEAD is NOT present → git refused to start the merge. Error text in `result.stderr` contains "Your local changes to the following files would be overwritten by merge:" or "error: Untracked working tree file" followed by file paths.
- D-4: Parse file list from stderr, `git add` each file, retry merge. Same code path handles same-content (auto-merges) and different-content (produces conflict markers).
- All test repos: real git repos, no mocks. Use `mock_precommit` for success-path tests.
- Existing tests in `test_worktree_merge_errors.py` that need updating:
  - `test_merge_aborts_cleanly_when_untracked_file_blocks` (line 93): currently asserts `exit_code != 0` and "Merge failed" or "untracked" in output. With D-4, same-content → merge succeeds (update test to different-content scenario expecting exit 3).
  - `test_merge_conflict_surfaces_git_error` (line 158): currently asserts `exit_code != 0` and "conflict" or "aborted" in output. Update to assert `exit_code == 3` and MERGE_HEAD preserved (no abort).

---

## Cycle 3.1: Source conflict → MERGE_HEAD preserved, no abort, exit 3 (FR-2, NFR-2)

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:137-175` — understand `_phase3_merge_parent` in full: the `git merge --no-commit --no-ff` call, the MERGE_HEAD check, the auto-resolution of agent-core/session/learnings, and the abort block at lines 170-175.

**RED Phase:**

**Test:** Update `test_merge_conflict_surfaces_git_error` in `tests/test_worktree_merge_errors.py`

Update assertions to:
- `result.exit_code == 3` (was `!= 0`)
- `subprocess.run(["git", "rev-parse", "MERGE_HEAD"], ...)` returns 0 after merge call (MERGE_HEAD still present)
- `"aborted"` NOT in `result.output` (old message removed)
- `"conflict"` or conflicted filename in `result.output` (some conflict indication)
- `"Traceback"` not in `result.output`

**Expected failure:** After updating the test: current code aborts (exit 1, MERGE_HEAD gone, "Merge aborted" in output) → test fails because:
- exit_code is 1 not 3
- MERGE_HEAD is absent (--abort removed it)
- "aborted" IS in output

**Why it fails:** Lines 170-175 abort the merge and exit 1; state is destroyed.

**Verify RED:** `pytest tests/test_worktree_merge_errors.py::test_merge_conflict_surfaces_git_error -v`

**GREEN Phase:**

**Implementation:** Remove abort block from `_phase3_merge_parent`. Replace with conflict listing + exit 3.

**Behavior:**
- In the `if conflicts:` branch (lines 170-175): remove `_git("merge", "--abort")`, `_git("clean", "-fd")`, `click.echo(f"Merge aborted: ...")`
- Replace with: list each conflict file via stdout, `raise SystemExit(3)` (no abort, no clean)
- MERGE_HEAD remains intact; staged auto-resolutions (session.md, learnings.md, agent-core) remain staged
- Note: `_format_conflict_report` (Phase 4) will replace the simple listing; for now, a basic `click.echo` of conflict file names suffices

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Remove lines 170-175; add conflict listing + `raise SystemExit(3)` in the `if conflicts:` branch
  Location hint: `_phase3_merge_parent`, lines 170-175

**Verify GREEN:** `pytest tests/test_worktree_merge_errors.py::test_merge_conflict_surfaces_git_error -v`

**CHECKPOINT after Cycle 3.1 — NFR-2 invariant:**
```
grep -n "merge.*--abort\|clean.*-fd" src/claudeutils/worktree/merge.py
```
Expected: no matches. If any `--abort` or `clean -fd` remain in merge.py, STOP and remove them (D-7).

---

## Cycle 3.2: Untracked file collision handling — `git add` + retry (FR-3, D-4)

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:137-160` — understand how Phase 3 detects the merge-abort (no MERGE_HEAD) vs merge-conflict (MERGE_HEAD present) distinction. The untracked file case produces no MERGE_HEAD (git refused before starting the merge).

**RED Phase:**

**Tests:** Update `test_merge_aborts_cleanly_when_untracked_file_blocks` + new test `test_merge_untracked_file_conflict_markers`.

Both in `tests/test_worktree_merge_errors.py`.

**Test A — updated `test_merge_aborts_cleanly_when_untracked_file_blocks`:**
Change the test setup so the untracked file on main has DIFFERENT content from the branch version (different-content case). This way, after `git add` + retry, the merge produces conflict markers (exit 3). The test becomes a conflict-path test rather than an error test.

Updated assertions for `test_merge_aborts_cleanly_when_untracked_file_blocks`:
- `result.exit_code == 3` (was `!= 0`)
- MERGE_HEAD exists after call (merge started after git add + retry)
- Conflict markers (`<<<<<<<`) present in the untracked file (file now tracked and conflicted)
- `"Traceback"` not in output

**Test B — new `test_merge_untracked_file_same_content_auto_resolved`:**
Assertions:
- When untracked file on main has SAME content as branch, `merge(slug)` exits 0
- File is tracked after merge (no longer untracked)
- `"Traceback"` not in output

**Expected failure (both tests):**
- Test A: currently `exit_code != 0` check passes, but after update to `exit_code == 3` + MERGE_HEAD check: current code exits with "Merge failed: error: Untracked working tree file..." (exit 1), no MERGE_HEAD, no conflict markers → test fails
- Test B: currently no test; new test fails because current code exits 1 on untracked file (doesn't attempt git add + retry)

**Why it fails:** `_phase3_merge_parent` detects no-MERGE_HEAD case as fatal error (exit 1) without attempting recovery.

**Verify RED:**
- `pytest tests/test_worktree_merge_errors.py::test_merge_aborts_cleanly_when_untracked_file_blocks -v`
- `pytest tests/test_worktree_merge_errors.py::test_merge_untracked_file_same_content_auto_resolved -v`

**GREEN Phase:**

**Implementation:** Add untracked-file collision detection and `git add` + retry logic to `_phase3_merge_parent`.

**Behavior:**
- When `git merge --no-commit --no-ff slug` fails (non-zero return) AND MERGE_HEAD is absent (merge refused before starting):
  - Inspect `result.stderr` for untracked-file markers: `"error: Untracked working tree file"` or `"Your local changes to the following files would be overwritten by merge"`
  - Parse file paths from the error output (files listed one per line after the marker, before the next blank line)
  - For each file: `git add <file>` (converts untracked to tracked, letting git perform three-way merge on retry)
  - Retry: `git merge --no-commit --no-ff slug` a second time
  - The retry result is handled by the normal conflict pipeline:
    - If retry exit 0: continue (auto-resolved or clean merge)
    - If retry exit non-zero + MERGE_HEAD: proceed to conflict reporting (exit 3)
  - If no untracked-file markers in stderr: this is an unrecognized error → `click.echo(f"Merge failed: {stderr}")` + `raise SystemExit(1)` (preserves existing behavior for other error types)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: In `_phase3_merge_parent`, in the no-MERGE_HEAD branch (currently `click.echo(f"Merge failed: {stderr}")` + `raise SystemExit(1)` at lines 155-157): add untracked detection + git add + retry before falling through to existing error path
  Location hint: `_phase3_merge_parent`, between lines 154 and 157 (after the no-MERGE_HEAD check)

**Verify GREEN:**
- `pytest tests/test_worktree_merge_errors.py -v`
- `pytest tests/ -k "merge" -v` (full regression check)

---

**Phase 3 STOP conditions:**
- MERGE_HEAD absent after Cycle 3.1 GREEN → STOP, --abort still being called (verify with grep)
- Untracked file `git add` fails (file doesn't exist) → STOP, path parsing from stderr incorrect
- Cycle 3.2 retry never triggers → STOP, untracked detection pattern not matching git's actual error message (verify with real git output)
- Regression in auto-resolution tests (session.md, learnings.md) → STOP, changed code broke existing conflict handling path
- NFR-2 grep fails → STOP before proceeding to Phase 4
