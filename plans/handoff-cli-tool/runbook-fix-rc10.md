# Runbook: Fix handoff-cli RC10 findings

**Source:** plans/handoff-cli-tool/reports/deliverable-review.md (RC10: 0C/2M/13m)
**Tier:** 2 (Lightweight Delegation)
**Scope:** 13 items (2M + 11m), 2 deferred (m-4, m-5)

## Recall Context

From recall-artifact.md:
- `when adding error handling to call chain` — context at failure site, display at top level (M-2)
- `when cli error messages are llm-consumed` — facts only, STOP directive for data-loss (M-2)
- `when testing CLI tools` — Click CliRunner, in-process, isolated filesystem
- `when preferring e2e over mocked subprocess` — real git repos via tmp_path

From session learnings:
- Docstring summaries ≤70 chars to avoid docformatter/ruff D205 cycle

## Phase 1: Behavioral fixes (type: tdd)

### Cycle 1.1: `load_state()` backward compat (M-1)

**Prerequisite:** Read `src/claudeutils/session/handoff/pipeline.py:36-45` — understand `load_state()` deserialization

**RED Phase:**

**Test:** `test_load_state_ignores_unknown_fields`
**Assertions:**
- Call `load_state()` when state file contains `{"input_markdown": "text", "timestamp": "ts", "step_reached": 3}` (extra field from pre-m-7)
- Returns `HandoffState(input_markdown="text", timestamp="ts")`
- No `TypeError` raised

**Expected failure:** `TypeError: HandoffState.__init__() got an unexpected keyword argument 'step_reached'`

**Why it fails:** Current code does `HandoffState(**data)` without filtering keys.

**Verify RED:** `pytest tests/test_session_handoff_cli.py::test_load_state_ignores_unknown_fields -v`

---

**GREEN Phase:**

**Implementation:** Filter state file data to known fields before unpacking.

**Behavior:**
- `load_state()` accepts state files with extra fields by filtering `data` to `HandoffState.__dataclass_fields__` keys

**Approach:** Set intersection of `data.keys()` and `HandoffState.__dataclass_fields__.keys()`, then unpack filtered dict.

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Filter `data` dict before `HandoffState(**data)` call
  Location hint: line 44, between `json.loads` and `return`

**Verify GREEN:** `just green`

### Cycle 1.2: Handoff CLI error handling (M-2)

**Prerequisite:** Read `src/claudeutils/session/handoff/cli.py:35-60` and `src/claudeutils/session/status/cli.py:48-56` — understand current handoff flow and status CLI error pattern

**RED Phase:**

**Test:** `test_handoff_missing_session_file`
**Assertions:**
- Invoke `_handoff` CLI with valid stdin but no `agents/session.md` in repo
- Exit code is 2
- Output contains `**Error:**` and `session` (not a Python traceback)

**Expected failure:** CLI crashes with `FileNotFoundError` traceback (unhandled exception)

**Why it fails:** `overwrite_status(session_path, ...)` calls `session_path.read_text()` without existence check.

**Verify RED:** `pytest tests/test_session_handoff_cli.py::test_handoff_missing_session_file -v`

---

**GREEN Phase:**

**Implementation:** Wrap pipeline calls in try/except, route through `_fail`.

**Behavior:**
- Catch `OSError` and `ValueError` from `overwrite_status` and `write_completed`
- Route through `_fail(f"**Error:** {e}", code=2)` — same pattern as status CLI
- Error handling at top level (CLI), not at failure site (pipeline) — per call-chain decision

**Approach:** Single try/except block around lines 54-55 (both pipeline calls).

**Changes:**
- File: `src/claudeutils/session/handoff/cli.py`
  Action: Wrap `overwrite_status` + `write_completed` calls in try/except (OSError, ValueError)
  Location hint: lines 54-55

**Verify GREEN:** `just green`

### Cycle 1.3: Submodule CleanFileError paths (m-1)

**Prerequisite:** Read `src/claudeutils/session/commit_pipeline.py:95-114,269-273` — understand `_partition_by_submodule` stripping and `validate_files` call site

**RED Phase:**

**Test:** `test_submodule_clean_error_shows_full_path`
**Assertions:**
- Commit pipeline with submodule files that are clean (no changes)
- `CleanFileError` message contains full path with submodule prefix (e.g., `agent-core/fragments/foo.md`)
- Not just the relative path (`fragments/foo.md`)

**Expected failure:** `AssertionError` — error message contains relative path only

**Why it fails:** `_partition_by_submodule` strips prefix (line 107), `validate_files` raises with stripped paths.

**Verify RED:** `pytest tests/test_session_commit.py::test_submodule_clean_error_shows_full_path -v`

---

**GREEN Phase:**

**Implementation:** Prepend submodule path back into CleanFileError paths.

**Behavior:**
- When `validate_files` raises `CleanFileError` for submodule files, catch it, prepend submodule path to each clean file, re-raise

**Approach:** Try/except around `validate_files(files, amend=amend, cwd=sub_cwd)`, catch `CleanFileError`, rebuild with prefixed paths.

**Changes:**
- File: `src/claudeutils/session/commit_pipeline.py`
  Action: Wrap submodule `validate_files` call in try/except CleanFileError, prepend path prefix to error's clean_files
  Location hint: lines 271-273

**Verify GREEN:** `just green`

### Cycle 1.4: Regex backreference safety (m-2)

**Prerequisite:** Read `src/claudeutils/session/handoff/pipeline.py:64-82` — understand `overwrite_status` regex replacement

**RED Phase:**

**Test:** `test_overwrite_status_backreference_in_text`
**Assertions:**
- Call `overwrite_status` with `status_text` containing `\g<1>` (a regex backreference pattern)
- Status line in output file contains literal `\g<1>` text
- No `re.error` raised and no group substitution occurs

**Expected failure:** `re.error` or corrupted output — `re.subn` interprets `\g<1>` in replacement string

**Why it fails:** `replacement` string concatenates `status_text` directly, and `re.subn` processes backreferences.

**Verify RED:** `pytest tests/test_session_handoff.py::test_overwrite_status_backreference_in_text -v`

---

**GREEN Phase:**

**Implementation:** Use function callback for `re.subn` replacement instead of string.

**Behavior:**
- Replace string-based `pattern.subn(replacement, text)` with function-based replacement
- Function returns the composed string, preventing backreference interpretation

**Approach:** Define a lambda/function that returns the desired replacement string. `pattern.subn(lambda m: m.group(1) + "\n**Status:** " + status_text + "\n" + m.group(3), text, count=1)`.

**Changes:**
- File: `src/claudeutils/session/handoff/pipeline.py`
  Action: Replace string replacement with function callback in `re.subn`
  Location hint: lines 75-76

**Verify GREEN:** `just green`

## Phase 2: Mechanical fixes (type: general)

### Step 2.1: Code fixes (m-3, m-12, m-13)

**Files:**
- `src/claudeutils/git_cli.py:32` — Add `"\n"` between header and `"\n\n".join(parts)` in `_build_repo_section`
- `src/claudeutils/worktree/cli.py:104` — Add parentheses: `except (FileNotFoundError, subprocess.CalledProcessError):`
- `src/claudeutils/worktree/cli.py:176` — Add parentheses: `except (subprocess.CalledProcessError, OSError):`
- `src/claudeutils/worktree/cli.py:288` — Remove unreachable `return None` after `_fail`

**Verification:** `just lint`

### Step 2.2: Test fixes (m-6, m-7, m-8, m-9, m-10, m-11)

**Files:**
- `tests/test_session_parser.py:138` — Remove `assert len(data.completed) > 0` (redundant with content assertions)
- `tests/test_session_commit.py:217` — Add `match=` pattern to bare `pytest.raises(CleanFileError)` (same pattern as sibling at line 257)
- `tests/test_worktree_merge_errors.py:83` — Add `match=` pattern to bare `pytest.raises(CalledProcessError)`
- `tests/test_session_commit_pipeline.py:121-127` — Replace ambiguous `"continuation"` assertion string with specific expected content
- `tests/test_session_status.py:263` — Replace disjunctive `or` assertion with specific expected section based on test scenario
- `tests/test_session_integration.py:34-35` — Add `plans/widget/` directory with minimal `brief.md` to test fixture setup

**Verification:** `just test`

### Step 2.3: Final verification

Run `just precommit` — full suite must pass with no regressions.

## Deferrals (carried forward)

- **m-4**: Blocker dependency edges — functionally safe (conservative false-positive)
- **m-5**: `list_plans` relative path — consistent with `_is_dirty()` pattern
- **m-8 (RC9)**: `_AGENT_CORE_PATTERNS` hardcoded submodule name — per design C-1
