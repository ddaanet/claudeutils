### Phase 4: Upgraded wt-ls CLI (type: tdd)

**Purpose:** Upgrade existing ls command with rich output mode and backward-compatible porcelain flag.

**Scope:**
- `src/claudeutils/worktree/cli.py` - ls command modification
- `tests/test_worktree_ls_upgrade.py` - CLI output tests

**Dependencies:** Phase 3 (CLI consumes aggregation)

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** Low-Medium (CLI output formatting with backward compatibility)

**Total Steps:** 6 cycles

---

## Cycle 4.1: Add --porcelain flag to ls command

**Prerequisite:** Read current cli.py ls implementation (lines 145-151) to understand existing structure.

**RED Phase:**

**Test:** `test_porcelain_flag_exists`
**Assertions:**
- `claudeutils _worktree ls --porcelain` runs without error
- `claudeutils _worktree ls --help` shows --porcelain flag in help text
- Flag is boolean (no argument required)

**Expected failure:** Unrecognized option --porcelain (flag not added)

**Why it fails:** ls command doesn't accept --porcelain flag yet

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_flag_exists -v`

**GREEN Phase:**

**Implementation:** Add @click.option for --porcelain flag to ls command

**Behavior:**
- Add `@click.option("--porcelain", is_flag=True, help="Machine-readable output")`
- Accept porcelain parameter in ls function signature
- When porcelain=True: use existing logic
- When porcelain=False: use new rich output (stub for now)

**Approach:** Click boolean flag, default False (rich output is new default)

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add @click.option("--porcelain") decorator above ls command
  Location hint: Above @worktree.command() decorator for ls (around line 145)

- File: `src/claudeutils/worktree/cli.py`
  Action: Update ls() function signature to accept porcelain: bool parameter
  Location hint: ls function definition (line 146)

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test invoking CLI with --porcelain flag via CliRunner
  Location hint: New file, use click.testing.CliRunner

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_flag_exists -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.2: Porcelain mode preserves existing behavior

**RED Phase:**

**Test:** `test_porcelain_mode_backward_compatible`
**Assertions:**
- Output format matches existing ls output: `<slug>\t<branch>\t<path>`
- Tab-separated fields preserved
- Main tree excluded (existing behavior)
- Uses existing _parse_worktree_list() logic

**Expected failure:** Output format changed or incompatible with existing consumers

**Why it fails:** Porcelain mode not wired to existing logic

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_mode_backward_compatible -v`

**GREEN Phase:**

**Implementation:** When porcelain=True, execute existing ls logic unchanged

**Behavior:**
- if porcelain: run existing code path (_parse_worktree_list + tab output)
- else: run new rich output path (to be implemented)
- Preserve exact output format for porcelain mode

**Approach:** Conditional branch on porcelain flag

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add if/else branch in ls() based on porcelain parameter
  Location hint: Inside ls function body

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with real worktree, verify tab-separated output matches expected format
  Location hint: New test function, use tmp_path with git worktree

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_porcelain_mode_backward_compatible -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.3: Rich mode header format (slug/branch, dirty indicator, commits)

**Prerequisite:** Verify `src/claudeutils/planstate/aggregation.py` exists with `aggregate_trees()` function (Phase 1-3 dependency). If missing, STOP — Phase 4 requires completed planstate module.

**RED Phase:**

**Test:** `test_rich_mode_header_format`
**Assertions:**
- For worktree with slug="test-wt", branch="feature", is_dirty=True, commits_since_handoff=3:
  - Output contains: `test-wt (feature)  ●  3 commits since handoff`
- For main tree with is_dirty=False, commits_since_handoff=0:
  - Output contains: `main (main)  ○  clean`
- Dirty indicator: `●` when is_dirty=True, `○` when is_dirty=False
- Commit status: "N commits since handoff" when >0, "clean" when 0

**Expected failure:** Rich output not formatted or missing elements (AttributeError accessing TreeStatus fields)

**Why it fails:** Rich output formatting not implemented

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_header_format -v`

**GREEN Phase:**

**Implementation:** Format header line from TreeStatus fields

**Behavior:**
- Call aggregate_trees() from planstate.aggregation to get list of TreeStatus objects
- For each tree: format and output header line with slug/branch, dirty indicator, commit status
- Slug display: show tree.slug, or "main" when tree.is_main=True
- Dirty indicator: "●" when tree.is_dirty=True, "○" when False
- Commit status: "N commits since handoff" when tree.commits_since_handoff > 0, "clean" when 0
- Output each formatted header line via click.echo()

**Hint:** Use f-string formatting with conditional expressions for dirty indicator and commit status

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Import aggregate_trees from planstate.aggregation
  Location hint: Top of file, with other imports

- File: `src/claudeutils/worktree/cli.py`
  Action: Implement rich output formatting in else branch of porcelain check
  Location hint: Inside ls function, else clause

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with real git repo, verify header line format
  Location hint: New test function, parse output and check format

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_header_format -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.4: Task line formatting (first pending task)

**RED Phase:**

**Test:** `test_rich_mode_task_line`
**Assertions:**
- For tree with task_summary="Implement foo feature":
  - Output contains exactly: `  Task: Implement foo feature` (2-space indent)
- For tree with task_summary=None:
  - Output does NOT contain any line starting with "  Task:"
- Task line appears directly after header line for same tree

**Expected failure:** Task line not displayed (no conditional task_summary output in rich mode)

**Why it fails:** Task line formatting not added to rich output

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_task_line -v`

**GREEN Phase:**

**Implementation:** Add task line when task_summary exists

**Behavior:**
- After header line, check if current tree has task_summary
- When task_summary is not None: output task line with 2-space indent showing task name
- When task_summary is None: skip task line (no output for that tree)
- Task line format: "  Task: " followed by task_summary content

**Hint:** Use conditional to check task_summary is not None before outputting line

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add task line output after header in rich formatting loop
  Location hint: After header line in tree iteration

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with session.md containing pending task, verify Task line appears
  Location hint: New test function, write session.md to worktree

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_task_line -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.5: Plan line formatting (plan-name [status] → next-action)

**RED Phase:**

**Test:** `test_rich_mode_plan_line`
**Assertions:**
- For tree containing plan "foo" with status="designed", next_action="/runbook plans/foo/design.md":
  - Output contains exactly: `  Plan: foo [designed] → /runbook plans/foo/design.md` (2-space indent)
- For tree with multiple plans (foo, bar):
  - Output contains both plan lines in same tree section
- For tree with no plans:
  - Output does NOT contain any line starting with "  Plan:"
- Plans filtered by tree: only plans in current tree's plans/ directory shown

**Expected failure:** Plan line not displayed (AttributeError accessing PlanState fields or plan filtering not implemented)

**Why it fails:** Plan line formatting not implemented or plan→tree association missing

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_plan_line -v`

**GREEN Phase:**

**Implementation:** Display plan lines for plans in current tree

**Behavior:**
- After task line (or header if no task), iterate through aggregated_status.plans
- Filter to plans belonging to current tree (plan directory under tree path)
- For each matching plan: output plan line with 2-space indent
- Plan line format: "  Plan: " + plan name + " [" + status + "] → " + next_action
- Support multiple plans per tree (output one line per plan)

**Hint:** Compare plan directory path against current tree path to filter; output each plan line with click.echo()

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py` (Phase 1-3 artifact)
  Action: Verify PlanState includes tree association for filtering (may need tree_path field or path-based filtering)
  Location hint: Check AggregatedStatus.plans structure; if tree association missing, add in aggregation logic

- File: `src/claudeutils/worktree/cli.py`
  Action: Add plan line output after task line in rich formatting loop
  Location hint: After task line in tree iteration

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with plans/ directory in worktree, verify Plan line appears
  Location hint: New test function, create plan directory with requirements.md

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_plan_line -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Cycle 4.6: Gate line formatting (advisory condition display)

**RED Phase:**

**Test:** `test_rich_mode_gate_line`
**Assertions:**
- For plan with gate="vet stale — re-vet first":
  - Output contains exactly: `  Gate: vet stale — re-vet first` (2-space indent)
  - Gate line appears directly after plan line for same plan
- For plan with gate=None:
  - Output does NOT contain any line starting with "  Gate:" for that plan
- Gate line only shown when plan.gate is not None

**Expected failure:** Gate line not displayed (no conditional gate output in rich mode)

**Why it fails:** Gate line formatting not added to rich output

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_gate_line -v`

**GREEN Phase:**

**Implementation:** Add gate line when plan has gate condition

**Behavior:**
- After each plan line, check if that plan has a gate condition
- When plan.gate is not None: output gate line with 2-space indent showing gate message
- When plan.gate is None: skip gate line for that plan
- Gate line format: "  Gate: " followed by gate message content

**Hint:** Check plan.gate immediately after outputting each plan line; use conditional to skip when None

**Changes:**
- File: `src/claudeutils/worktree/cli.py`
  Action: Add gate line output after plan line in rich formatting loop
  Location hint: After plan line in tree iteration

- File: `tests/test_worktree_ls_upgrade.py`
  Action: Create test with stale design.md (source newer than report), verify Gate line appears
  Location hint: New test function, use os.utime() to make source newer

**Verify GREEN:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_gate_line -v`
**Verify no regression:** `pytest tests/test_worktree_ls_upgrade.py -v`

---

## Phase 4 Checkpoint

**After all cycles complete:**

1. Run `just dev` to verify code quality
2. Functional review: Check that rich output displays correctly with real worktrees
3. Backward compatibility check: Verify porcelain mode exactly matches old output
4. File growth check: If cli.py exceeds 400 lines, extract rich formatting to format.py or display.py module
5. Commit: All Phase 4 implementations and tests

**Expected state:**
- ls command accepts --porcelain flag
- Porcelain mode preserves exact backward compatibility
- Rich mode displays header, task, plan, and gate lines correctly
- All 6 tests pass in test_worktree_ls_upgrade.py
- Integration test with real worktrees verifies correct plan status display
