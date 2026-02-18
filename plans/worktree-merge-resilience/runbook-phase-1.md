## Phase 1: State detection + idempotent resume (type: tdd)

**Goal:** Add `_detect_merge_state(slug)` to `merge.py` and rewrite `merge()` entry to route based on detected state. Enables Phases 2–4 to be exercised independently (resume from mid-merge state).

**Files:** `src/claudeutils/worktree/merge.py`, `tests/test_worktree_merge_merge_head.py`

**Common context for all cycles:**
- `_detect_merge_state(slug)` returns a string: `"merged"`, `"parent_resolved"`, `"parent_conflicts"`, `"submodule_conflicts"`, or `"clean"`
- Detection order matters (D-5): check in order merged → submodule_conflicts → parent_resolved → parent_conflicts → clean
- All test repos: real git, no mocks. Use `tmp_path`, set git user.name/email. Use `mock_precommit` fixture for all cycles.
- `merged` detection: `_is_branch_merged(slug)` (already in utils.py)
- `parent_resolved`/`parent_conflicts` detection: `git rev-parse --verify MERGE_HEAD` (0 = MERGE_HEAD exists)
- Conflict presence: `git diff --name-only --diff-filter=U` (non-empty = unresolved conflicts)
- `submodule_conflicts` detection: `git -C agent-core rev-parse --verify MERGE_HEAD`

---

## Cycle 1.1: `_detect_merge_state` identifies `merged` state

**RED Phase:**

**Test:** `test_detect_state_merged`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- `_detect_merge_state("branch")` returns `"merged"` when branch is already an ancestor of HEAD
- Returns `"clean"` for same repo before branch is merged (control assertion)

**Expected failure:** `ImportError` — `_detect_merge_state` does not yet exist in `merge.py`

**Why it fails:** Function not implemented.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_detect_state_merged -v`

**Test setup:** Create repo, add a commit on a branch, merge it into main with `git merge --no-edit branch`. Monkeypatch chdir. Call `_detect_merge_state("branch")` directly (import from `claudeutils.worktree.merge`).

**GREEN Phase:**

**Implementation:** Add `_detect_merge_state(slug: str) -> str` to `merge.py`.

**Behavior:**
- Check `_is_branch_merged(slug)` (already in utils.py) — return `"merged"` if True
- Check agent-core MERGE_HEAD presence — return `"submodule_conflicts"` if found
- Check parent MERGE_HEAD presence — if present: check `git diff --name-only --diff-filter=U` — return `"parent_resolved"` if empty, `"parent_conflicts"` if non-empty
- Otherwise return `"clean"`

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Add `_detect_merge_state(slug: str) -> str` function near top of file (after existing helpers, before `_phase1_validate_clean_trees`)
  Location hint: After `_format_git_error`, before `_check_clean_for_merge`

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_detect_state_merged -v`
**Verify no regression:** `pytest tests/test_worktree_merge_merge_head.py -v`

---

## Cycle 1.2: `merge()` routes `parent_resolved` state to Phase 4

**Prerequisite:** Read `src/claudeutils/worktree/merge.py:67-90` — understand `_check_clean_for_merge` which currently prevents resume from mid-merge state.

**RED Phase:**

**Test:** `test_merge_resumes_from_parent_resolved`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- Exit code is 0 when `merge(slug)` called on repo with MERGE_HEAD + no unresolved conflicts
- A merge commit is created (HEAD has 2+ parents after call)
- No `CalledProcessError` from clean-tree check

**Expected failure:** `SystemExit(1)` — current `_phase1_validate_clean_trees` calls `_check_clean_for_merge` which detects staged changes (from the manually resolved merge) and exits 1 with "Clean tree required"

**Why it fails:** Phase 1 validation rejects staged files even though they belong to an in-progress merge.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_resumes_from_parent_resolved -v`

**Test setup:**
1. Create repo with branch that has a unique file (`branch-file.txt`) and main that has a conflicting change in another file
2. Start merge manually: `subprocess.run(["git", "merge", "--no-commit", "--no-ff", slug], ...)`
3. All auto-resolved — `git diff --name-only --diff-filter=U` returns empty (no conflicts)
4. Monkeypatch chdir. Invoke `worktree merge slug` via CliRunner.
5. Assert exit 0 and merge commit created.

**GREEN Phase:**

**Implementation:** Rewrite `merge()` entry point to call `_detect_merge_state(slug)` and route.

**Behavior:**
- If `"merged"`: call `_phase4_merge_commit_and_precommit(slug)` only
- If `"parent_resolved"`: call `_phase4_merge_commit_and_precommit(slug)` only
- If `"parent_conflicts"`: report unresolved conflicts and `raise SystemExit(3)` (stub — Phase 3 adds full behavior, Phase 4 adds formatted report)
- If `"submodule_conflicts"`: call `_phase3_merge_parent(slug)` then `_phase4_merge_commit_and_precommit(slug)` (D-5)
- If `"clean"`: run full pipeline `_phase1_validate_clean_trees` → `_phase2_resolve_submodule` → `_phase3_merge_parent` → `_phase4_merge_commit_and_precommit`

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Replace `merge()` body with state detection + routing dispatch
  Location hint: `merge()` function at end of file, lines 257–262

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_resumes_from_parent_resolved -v`
**Verify no regression:** `pytest tests/ -k "merge" --ignore=tests/test_worktree_merge_conflicts.py -v`

---

## Cycle 1.3: `merge()` routes `parent_conflicts` state to exit 3

**RED Phase:**

**Test:** `test_merge_reports_and_exits_3_when_parent_conflicts`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- Exit code is 3 when `merge(slug)` called with MERGE_HEAD present and unresolved conflicts
- MERGE_HEAD still exists after the call (no `--abort` was run)
- Output contains name of conflicted file
- No traceback in output

**Expected failure:** `SystemExit(1)` — current Phase 1 clean-tree check rejects the dirty tree before reaching any conflict detection

**Why it fails:** Current code validates clean tree before checking merge state; staged conflict-marker files fail the clean check.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_reports_and_exits_3_when_parent_conflicts -v`

**Test setup:**
1. Create repo, branch with different content in `src/feature.py`, main with different content in same file
2. Start merge: `subprocess.run(["git", "merge", "--no-commit", "--no-ff", slug], ...)`
3. Verify MERGE_HEAD exists and `git diff --name-only --diff-filter=U` is non-empty
4. Monkeypatch chdir. Invoke `worktree merge slug` via CliRunner.
5. Assert exit_code == 3, MERGE_HEAD still present (subprocess check), conflicted filename in output.

**GREEN Phase:**

**Implementation:** The routing from Cycle 1.2 already dispatches `parent_conflicts` to stub. Implement stub to list conflicts from `git diff --name-only --diff-filter=U` and exit 3.

**Behavior:**
- For `parent_conflicts` route: get conflict list via `git diff --name-only --diff-filter=U`
- Print each conflicted file
- `raise SystemExit(3)` — no `--abort`, no `clean -fd` (D-3, D-7)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Replace stub in `parent_conflicts` branch of `merge()` with conflict listing + exit 3
  Location hint: `parent_conflicts` case in `merge()` dispatch

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_reports_and_exits_3_when_parent_conflicts -v`
**Verify MERGE_HEAD preserved:** subprocess check in test; verify MERGE_HEAD still valid after CliRunner call.
**Verify no regression:** `pytest tests/ -k "merge" -x -v`

**CHECKPOINT after Cycle 1.3:** Verify all in-progress states route correctly:
- `merged` + `parent_resolved` → Phase 4
- `parent_conflicts` → exit 3, MERGE_HEAD preserved
- Run: `pytest tests/test_worktree_merge_merge_head.py -v`

---

## Cycle 1.4: `merge()` routes `submodule_conflicts` state to Phase 3

**RED Phase:**

**Test:** `test_merge_continues_to_phase3_when_submodule_conflicts`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- When agent-core has MERGE_HEAD (submodule mid-merge), calling `merge(slug)` does not exit with "Clean tree required"
- Agent-core MERGE_HEAD is present (test verifies the starting condition)
- After call: either exit 0 (if parent merge auto-resolves), OR exit 3 (if parent conflicts), but NOT exit 1 from clean-tree check

**Expected failure:** `SystemExit(1)` with "Clean tree required" — current Phase 1 detects agent-core is dirty (staged files from mid-merge)

**Why it fails:** `_check_clean_for_merge` checks submodule status; mid-merge submodule has staged changes.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_continues_to_phase3_when_submodule_conflicts -v`

**Test setup:**
1. Use `repo_with_submodule` fixture
2. Create branch on parent repo (no changes — just branch pointer)
3. Manually put agent-core in mid-merge state: create a conflicting commit on agent-core, then `git -C agent-core merge --no-commit --no-ff <commit>` leaving it mid-merge with no conflicts (so parent Phase 3 can proceed)
4. Monkeypatch chdir. Invoke `worktree merge slug` via CliRunner.
5. Assert exit code is NOT 1 from clean-tree check (accept 0 or 3 as valid outcomes)

**GREEN Phase:**

**Implementation:** The routing from Cycle 1.2 dispatches `submodule_conflicts` to `_phase3_merge_parent` + `_phase4_merge_commit_and_precommit`. No additional code needed — this cycle tests existing routing.

**Behavior:**
- `submodule_conflicts` route already added in Cycle 1.2 GREEN
- Verify that `_detect_merge_state` correctly detects agent-core MERGE_HEAD
- If `_detect_merge_state` doesn't yet check agent-core: add that check in detection order (before parent MERGE_HEAD check per D-5)

**Changes:**
- File: `src/claudeutils/worktree/merge.py`
  Action: Verify `_detect_merge_state` checks `git -C agent-core rev-parse --verify MERGE_HEAD` and returns `"submodule_conflicts"` when found (before checking parent MERGE_HEAD)
  Location hint: `_detect_merge_state` body, second check after `_is_branch_merged`

**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_continues_to_phase3_when_submodule_conflicts -v`
**Verify no regression:** `pytest tests/ -k "merge" -x -v`

---

## Cycle 1.5: `merge()` routes `clean` state through full pipeline

**RED Phase:**

**Test:** `test_merge_clean_state_runs_full_pipeline`
**File:** `tests/test_worktree_merge_merge_head.py`

**Assertions:**
- `merge(slug)` on a clean repo with a diverged branch runs all phases:
  - Phase 1: clean tree validated (no exception)
  - Phase 2: submodule check runs (no-op if no submodule divergence)
  - Phase 3: `git merge --no-commit --no-ff slug` runs
  - Phase 4: merge commit created (HEAD has 2 parents), precommit passes
- Exit code is 0
- Merge commit message matches `f"🔀 Merge {slug}"`
- `_is_branch_merged(slug)` returns True after call

**Expected failure:** This test should already pass IF the state machine routes `clean` to the full pipeline. It becomes a regression test that the refactor didn't break the normal (clean) path.

**Why it fails (RED):** If `_detect_merge_state` incorrectly classifies a clean repo (e.g., returns `"merged"` for a non-merged branch), the merge commit would not be created. Write the test before verifying the full state machine — RED confirms state detection is correct.

**Verify RED:** `pytest tests/test_worktree_merge_merge_head.py::test_merge_clean_state_runs_full_pipeline -v`

**Test setup:**
1. Use `repo_with_submodule` and `mock_precommit` fixtures
2. Create branch with one unique file commit
3. Add a different commit on main (diverge)
4. Monkeypatch chdir. Invoke `worktree merge slug` via CliRunner.
5. Assert exit 0, merge commit with 2 parents, `_is_branch_merged` returns True.

**GREEN Phase:**

**Implementation:** The `clean` routing already in `merge()` from Cycle 1.2. Verify all 4 phases called in sequence for `clean` state.

**Behavior:**
- `clean` route: `_phase1_validate_clean_trees` → `_phase2_resolve_submodule` → `_phase3_merge_parent` → `_phase4_merge_commit_and_precommit`
- No changes needed if Cycle 1.2 routing was correct

**Changes:** None (verification that routing is correct).
**Verify GREEN:** `pytest tests/test_worktree_merge_merge_head.py -v`
**Verify no regression:** `pytest tests/ -k "merge" -v`

---

**Phase 1 STOP conditions:**
- RED fails to fail (test passes before GREEN) → STOP, assert is too weak or test setup is incorrect
- `_detect_merge_state` returns wrong state for any git scenario → STOP, debug detection logic
- Regression in existing merge tests → STOP, state machine routing broke existing path
