# Runbook: Fix RC14 Minors

**Input:** `plans/handoff-cli-tool/reports/deliverable-review.md` (RC14)
**Design:** `plans/handoff-cli-tool/outline.md`
**Tier:** 2 (lightweight delegation)
**Type:** general (all steps are refactoring/style — no new behavior)

## Recall

Resolved entries (rationale format):
- `when extracting git helper functions` — `_git(*args)` pattern, `cwd` param addition is the canonical consolidation approach
- `when detecting vacuous assertions from skipped RED` — verify assertions distinguish correct from empty/default output
- `when writing integration test assertions` — assert on content presence, not structure
- `when fixture shadowing creates dead code` — grep for function defs duplicating fixture names
- `when preferring e2e over mocked subprocess` — real git repos via tmp_path

## Steps

### Step 1: m-1 — Factor out hint logic (Simple)

**File:** `src/claudeutils/session/commit_pipeline.py:199-213`
**Finding:** Both inner branches set `prev_was_hint = True` — redundant per-branch assignment obscures intent.

**Fix:** Move `prev_was_hint = True` before the inner `if/else`. Inner conditional only controls whether to append the line:

```python
elif prev_was_hint and line and line[0] in (" ", "\t"):
    prev_was_hint = True  # stays True for any continuation
    if not (line[0] == "\t" or (len(line) > 1 and line[1] == " ")):
        result.append(line)  # single-space: keep line
```

**Verify:** `just test tests/test_session_commit_pipeline.py`

### Step 2: m-2 — Consolidate `_git_output` into `_git` (Moderate)

**Files:** `src/claudeutils/git.py`, `src/claudeutils/session/commit_gate.py`
**Finding:** `_git_output()` duplicates `_git()` with minor differences (`cwd` param, `check=False` default). TODO on line 41.

**Fix:**
1. `git.py:_git()` — add `cwd: Path | None = None` param, pass to `subprocess.run`
2. `commit_gate.py` — replace `_git_output(...)` call in `_head_files` with `_git(..., check=False, cwd=cwd)`. Add import `from claudeutils.git import _git`.
3. Remove `_git_output` function and its `subprocess` import (if no other callers)
4. Check: `_dirty_files` uses raw `subprocess.run` directly (intentional — porcelain format, no strip). Leave as-is.

**Verify:** `just test tests/test_session_commit_gate.py tests/test_session_commit_pipeline_ext.py tests/test_session_commit_cli.py`

### Step 3: m-4, m-5 — Loosen tight assertions (Simple)

**Files:** `tests/test_session_commit_pipeline_ext.py:133-136`, `tests/test_session_status.py:132`

**m-4 fix:** Replace exact warning string assertion with key fragment checks:
```python
assert "no changes found" in result.output
assert "agent-core" in result.output
```

**m-5 fix:** Replace `== "▶ Build widget (sonnet) | Restart: Yes"` with fragment checks:
```python
assert "▶" in arrow_line
assert "Build widget" in arrow_line
assert "sonnet" in arrow_line
assert "Restart" in arrow_line
```

**Verify:** `just test tests/test_session_commit_pipeline_ext.py tests/test_session_status.py`

### Step 4: m-6 — Fix vacuous test (Simple)

**File:** `tests/test_session_handoff.py:217-232`
**Finding:** `test_write_completed_with_accumulated_content` doesn't commit session.md before calling `write_completed`, so `_detect_write_mode` returns `"overwrite"` — same path as basic overwrite test.

**Fix:** Initialize a git repo, commit `SESSION_WITH_COMPLETED`, then modify to add new content. This makes `_detect_write_mode` return `"autostrip"` (old preserved + additions). Assert that old committed content is stripped and new content kept.

```python
def test_write_completed_with_accumulated_content(tmp_path: Path) -> None:
    """Autostrip removes committed content, keeps new additions."""
    session_file = tmp_path / "session.md"
    session_file.write_text(SESSION_WITH_COMPLETED)
    # Commit original so _detect_write_mode sees diff
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=tmp_path, ...)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, ...)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, ...)
    # Accumulate new content alongside committed content
    accumulated = SESSION_WITH_COMPLETED.replace(
        "- Old task B\n", "- Old task B\n- New task done.\n"
    )
    session_file.write_text(accumulated)

    write_completed(session_file, ["- New task done."])

    content = session_file.read_text()
    assert "- New task done." in content
    assert "- Old task A" not in content
    assert "- Old task B" not in content
```

**Verify:** `just test tests/test_session_handoff.py`

### Step 5: m-7 — Add state-clear assertion (Simple)

**File:** `tests/test_session_handoff_cli.py:371-391`
**Finding:** `test_handoff_resume_from_write_session` doesn't assert state file cleared after resume.

**Fix:** Add assertion after the existing checks:
```python
assert not (tmp_path / "tmp" / ".handoff-state.json").exists()
```

**Verify:** `just test tests/test_session_handoff_cli.py`

### Step 6: m-3 — Standardize submodule helpers (Moderate)

**Files:** `tests/test_git_cli.py`, `tests/test_session_handoff_cli.py`, `tests/test_session_commit_pipeline_ext.py`
**Finding:** Three different submodule setup approaches. Canonical: `pytest_helpers.create_submodule_origin` + `add_submodule`.

**Fix:**
1. `test_session_handoff_cli.py:142-236` — Replace 20-line manual setup in `test_handoff_shows_submodule_changes` with `create_submodule_origin` + `add_submodule` from `pytest_helpers`.
2. `test_git_cli.py:15-67` — `_add_submodule_gitlink` uses plumbing intentionally (no clone). **Evaluate:** if `create_submodule_origin` + `add_submodule` works for the test's purpose (testing `_git changes` output), migrate. If plumbing is needed for test semantics, document why in a comment and leave.
3. `test_session_commit_pipeline_ext.py` — already uses the canonical helper. No changes.

**Verify:** `just test tests/test_git_cli.py tests/test_session_handoff_cli.py tests/test_session_commit_pipeline_ext.py`

### Step 7: Final validation

`just precommit`

All steps are independent — no ordering dependency between steps 1-6. Step 7 must run last.
