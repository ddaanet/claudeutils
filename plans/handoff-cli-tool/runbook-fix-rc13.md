# Fix RC13 — Runbook

**Spec:** outline.md | **Findings:** reports/deliverable-review.md (RC13, 0C/0M/22m)
**Scope:** 18 actionable items (4 dismissed: m-4, m-20, m-21, m-22)
**Tier:** 2 (lightweight delegation)

## Dismissed

- **m-4:** Defensive `len > 3` guard — harmless, git never produces empty paths
- **m-20:** Scope observation (standalone bugfix in wrong plan) — not actionable
- **m-21:** Trailing newline config change — trivial churn
- **m-22:** .gitignore broadening — scope note, not a defect

## Recall Constraints

From learnings (already in context):
- Docformatter: keep docstring summary ≤70 chars (4 indent + 3 `"""` + content + 3 `"""` = 80)
- Git status porcelain: don't strip XY prefix — use raw `splitlines()`, `line[3:]`
- Design spec context: load outline.md before modifying code — design defines correct behavior

From recall-artifact.md:
- Testing: Click CliRunner, real git repos via tmp_path, mock only for error injection
- Error handling: context at failure site, display at top level, `_fail()` pattern

---

## Phase 1: Code fixes (type: tdd)

### Cycle 1.1: Section comparison consistency (m-7 + m-5)

**Prerequisite:** Read `pipeline.py:115-183` — `_extract_completed_section` and `_detect_write_mode`

**RED Phase:**

**Test:** `test_detect_write_mode_newline_insensitive` in `test_session_handoff_committed.py`
**Assertions:**
- Completed section ending with/without trailing newline → same mode returned
- Committed `"- item\n"` vs current `"  - item\n"` (different indentation) → autostrip does NOT trigger (not treated as subset match)

**Expected failure:** `AssertionError` — stripped comparison treats different indentation as identical

**Verify RED:** `pytest tests/test_session_handoff_committed.py::test_detect_write_mode_newline_insensitive -v`

**GREEN Phase:**

**Behavior:**
- Normalize `_extract_completed_section` return — consistent trailing whitespace handling
- Subset check in `_detect_write_mode`: compare full lines (preserve indentation), filter only truly empty lines

**Changes:**
- `pipeline.py:115-140` — normalize extraction output
- `pipeline.py:170-183` — full-line comparison in subset check

**Verify GREEN:** `just green`

---

### Cycle 1.2: Blank line preservation (m-1)

**Prerequisite:** Read `pipeline.py:198-233` — `write_completed` append/autostrip branches

**RED Phase:**

**Test:** `test_write_completed_preserves_inter_group_spacing` in `test_session_handoff.py`
**Assertions:**
- New content with blank line between two `### ` groups
- After append mode: output section contains the blank line between groups
- After autostrip mode: blank lines in new (uncommitted) content preserved

**Expected failure:** `AssertionError` — `if line.strip()` filter drops blank lines from combined output

**Verify RED:** `pytest tests/test_session_handoff.py::test_write_completed_preserves_inter_group_spacing -v`

**GREEN Phase:**

**Behavior:**
- Append: keep all lines from current content (including blanks) when combining
- Autostrip: keep blank lines in uncommitted content filter

**Changes:**
- `pipeline.py:203` — remove `if line.strip()` from append list comprehension
- `pipeline.py:226-229` — remove blank-line exclusion from autostrip filter, keep only committed-set exclusion

**Verify GREEN:** `just green`

---

### Cycle 1.3: Eliminate redundant git calls (m-2)

**Refactoring — no RED phase. Existing tests validate behavior preservation.**

**Implementation:**
- `_detect_write_mode` returns `(mode, committed_section)` tuple (committed section text or `""`)
- `write_completed` destructures return, passes committed section to autostrip branch
- Autostrip branch uses passed data — eliminates duplicate `_find_repo_root` + `git show HEAD:`

**Changes:**
- `pipeline.py:143-167` — change return type, return committed section alongside mode
- `pipeline.py:198-233` — destructure return, pass committed section to autostrip

**Verify:** `just green` — all existing tests pass unchanged

---

### Cycle 1.4: Status old-format error accuracy (m-3)

**Prerequisite:** Read `status/cli.py:33-65` — `_count_raw_tasks` and format check

**RED Phase:**

**Test:** `test_status_malformed_task_line_error` in `test_session_status.py`
**Assertions:**
- Session with `- [ ] bare task no metadata` (starts with `- [` but no `**` bold or `—` separator)
- Error message contains "malformed" or describes the actual issue
- Error message does NOT say "Old-format" when the issue is malformed content

**Expected failure:** `AssertionError` — current error unconditionally says "Old-format tasks missing metadata"

**Verify RED:** `pytest tests/test_session_status.py::test_status_malformed_task_line_error -v`

**GREEN Phase:**

**Behavior:**
- Error message accurately describes the mismatch: "N task lines without required metadata (** and —)"
- Optionally report which lines failed to parse

**Changes:**
- `status/cli.py:61-64` — improve error message to describe actual issue, not assume old-format

**Verify GREEN:** `just green`

---

### Cycle 1.5: Empty git_changes output (m-6)

**Prerequisite:** Read `handoff/cli.py:68-72` — diagnostics output

**RED Phase:**

**Test:** `test_handoff_skips_empty_git_block` in `test_session_handoff_cli.py`
**Assertions:**
- When git tree is clean after writes (git_changes returns empty/whitespace-only)
- Output does NOT contain empty fenced code block (``` with no content between)
- Output either omits the block entirely or shows "No changes" indication

**Expected failure:** `AssertionError` — current always emits `\`\`\`\n\n\`\`\`` wrapper

**Verify RED:** `pytest tests/test_session_handoff_cli.py::test_handoff_skips_empty_git_block -v`

**GREEN Phase:**

**Behavior:**
- Check `git_changes()` return; if empty/whitespace-only, skip code block emission

**Changes:**
- `handoff/cli.py:69-70` — wrap in conditional, skip when empty

**Verify GREEN:** `just green`

---

## Phase 2: Test quality (type: general)

### Step 2.1: Quick fixes (m-8, m-9, m-11, m-13, m-16)

**Prerequisite:** Read each file at referenced lines

- **m-8** `test_session_status.py`: Move `SESSION_FIXTURE` definition before line 253 (first usage)
- **m-9** `test_session_commit_pipeline.py:108-125`: Replace generic assertion words ("continuation", "other line") with specific expected content from the fixture
- **m-11** `test_session_handoff.py:217-248`: Two tests exercise same `_write_completed_section` path — remove the weaker one or merge
- **m-13** `test_session_handoff_committed.py:99-100`: Rewrite comment to describe mode-detection rationale (why overwrite vs append), not agent behavior
- **m-16** `test_session_handoff.py:217`: Assess pre-H-2 accumulated content test — if fully covered by committed detection tests in `test_session_handoff_committed.py`, remove

**Verify:** `just test`

### Step 2.2: Restructuring (m-10, m-12)

**Prerequisite:** Read full test files for context

- **m-10** `test_planstate_aggregation.py:102-197`: Split conflated function into separate positive-path and negative-path test functions
- **m-12** `test_session_commit_pipeline.py:157-212` + `test_session_commit_pipeline_ext.py:22-35`: Extract shared submodule setup helper to conftest or shared module; both files use it

**Verify:** `just test`

### Step 2.3: New test coverage (m-14, m-15, m-17)

**Prerequisite:** Read existing tests in target files for pattern consistency

- **m-14** `test_session_handoff_committed.py`: Add test for autostrip error fallback — when `git show HEAD:` raises CalledProcessError in autostrip branch, falls back to overwrite behavior
- **m-15** `test_session_handoff_cli.py`: Add test for `step_reached="write_session"` resume — state file exists with write_session, CLI resumes from session writes
- **m-17** `test_session_handoff_committed.py`: Add direct `_detect_write_mode` unit test exercising all 3 modes (overwrite when no diff, append when committed removed, autostrip when committed preserved with additions)

**Verify:** `just test`

---

## Phase 3: Prose (type: inline)

- **m-18** `agent-core/skills/handoff/SKILL.md:146`: Replace "STOP — fix issues and retry" with "STOP — output result and wait for guidance" (aligns with communication rule 1: stop and report, don't retry autonomously)
- **m-19** `agent-core/skills/handoff/SKILL.md:27`: Replace opaque "(H-2)" with "(compares completed section against HEAD)" — agents can't resolve outline section identifiers

**Verify:** Read modified lines
