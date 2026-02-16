### Phase 4: Upgraded wt-ls CLI (type: tdd)

**Purpose:** Upgrade existing ls command with rich output mode and backward-compatible porcelain flag.

**Scope:**
- `src/claudeutils/worktree/cli.py` - ls command modification
- `tests/test_worktree_ls_upgrade.py` - CLI output tests

**Dependencies:** Phase 3 (CLI consumes aggregation)

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** Low-Medium (CLI output formatting with backward compatibility)

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

**RED Phase:**

**Test:** `test_rich_mode_header_format`
**Assertions:**
- First line contains: `<slug|"main"> (<branch>)  <●|○>  <N commits since handoff | "clean">`
- `●` appears when is_dirty=True
- `○` appears when is_dirty=False
- Commits count appears when >0, "clean" appears when 0

**Expected failure:** Rich output not formatted or missing elements

**Why it fails:** Rich output formatting not implemented

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_header_format -v`

**GREEN Phase:**

**Implementation:** Format header line from TreeStatus fields

**Behavior:**
- Call aggregate_trees() from planstate.aggregation
- For each tree in trees list:
  - Format slug (or "main" if is_main=True)
  - Format branch in parentheses
  - Format dirty indicator (● or ○)
  - Format commits/clean status
- Click.echo() each formatted line

**Approach:** String formatting with f-strings, conditional ●/○ selection

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
- Task line appears when task_summary is not None: `  Task: <task_name>`
- Task line omitted when task_summary is None (no pending tasks)
- Indentation is 2 spaces
- Only first pending task shown

**Expected failure:** Task line not displayed or wrong format

**Why it fails:** Task line formatting not added to rich output

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_task_line -v`

**GREEN Phase:**

**Implementation:** Add task line when task_summary exists

**Behavior:**
- Check if tree.task_summary is not None
- If exists: click.echo(f"  Task: {tree.task_summary}")
- If None: skip line (no output)

**Approach:** Conditional output based on task_summary field

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
- Plan line format: `  Plan: <plan-name> [<status>] → <next-action>`
- One plan line per plan in that tree
- Plans from AggregatedStatus.plans filtered to current tree
- Indentation is 2 spaces

**Expected failure:** Plan line not displayed or plans not filtered by tree

**Why it fails:** Plan line formatting not implemented or plan→tree association missing

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_plan_line -v`

**GREEN Phase:**

**Implementation:** Display plan lines for plans in current tree

**Behavior:**
- For each plan in aggregated_status.plans:
  - Check if plan's directory is in current tree (match tree path)
  - Format: f"  Plan: {plan.name} [{plan.status}] → {plan.next_action}"
  - Click.echo() the line
- Multiple plans per tree supported

**Approach:** Filter plans by checking if plan directory is under tree path

**Changes:**
- File: `src/claudeutils/planstate/aggregation.py`
  Action: Add tree_path field to PlanState or store tree association in AggregatedStatus
  Location hint: Modify list_plans() to track source tree

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
- Gate line appears when plan.gate is not None: `  Gate: <gate_message>`
- Gate line omitted when plan.gate is None
- Indentation is 2 spaces
- Only shown for plans with stale vet status

**Expected failure:** Gate line not displayed

**Why it fails:** Gate line formatting not added to rich output

**Verify RED:** `pytest tests/test_worktree_ls_upgrade.py::test_rich_mode_gate_line -v`

**GREEN Phase:**

**Implementation:** Add gate line when plan has gate condition

**Behavior:**
- After plan line, check if plan.gate is not None
- If gate exists: click.echo(f"  Gate: {plan.gate}")
- If None: skip line

**Approach:** Conditional output based on gate field

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
