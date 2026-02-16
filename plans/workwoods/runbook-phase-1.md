### Phase 1: Plan State Inference (type: tdd)

**Purpose:** Create planstate module foundation with state inference from filesystem artifacts.

**Scope:**
- `src/claudeutils/planstate/__init__.py` - Public API exports
- `src/claudeutils/planstate/models.py` - Data models (PlanState, VetStatus, etc.)
- `src/claudeutils/planstate/inference.py` - Core inference logic
- `tests/test_planstate_inference.py` - Test coverage

**Dependencies:** None (foundation phase)

**Execution Model:** Sonnet (standard TDD implementation)

**Estimated Complexity:** Medium (new module setup with clear requirements)

---

## Cycle 1.1: Empty directory detection (not a plan)

**Prerequisite:** Read design State Inference Rules table for artifact patterns.

**RED Phase:**

**Test:** `test_empty_directory_not_a_plan`
**Assertions:**
- `infer_state(tmp_path / "plans/empty")` returns `None` (not a plan)
- Empty directory in plans/ should be filtered out by list_plans()
- No exception raised for empty directory

**Expected failure:** TypeError or AttributeError (infer_state not implemented)

**Why it fails:** No planstate module exists yet

**Verify RED:** `pytest tests/test_planstate_inference.py::test_empty_directory_not_a_plan -v`

**GREEN Phase:**

**Implementation:** Create planstate module with infer_state() returning None for empty dirs

**Behavior:**
- infer_state() scans for recognized artifacts (requirements.md, design.md, etc.)
- If no artifacts found, return None
- list_plans() filters None results from plan directory scan

**Approach:** Check for artifact existence in priority order (highest status first)

**Changes:**
- File: `src/claudeutils/planstate/__init__.py`
  Action: Create module with public API exports (infer_state, list_plans)
  Location hint: New file

- File: `src/claudeutils/planstate/models.py`
  Action: Define PlanState dataclass (name, status, next_action, gate, artifacts fields)
  Location hint: New file

- File: `src/claudeutils/planstate/inference.py`
  Action: Implement infer_state(plan_dir: Path) -> PlanState | None
  Location hint: New file, returns None for empty dirs

- File: `tests/test_planstate_inference.py`
  Action: Create test with tmp_path fixture, empty plans/<name>/ directory
  Location hint: New file

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_empty_directory_not_a_plan -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Cycle 1.2: Requirements status detection (requirements.md only)

**RED Phase:**

**Test:** `test_requirements_status_detection`
**Assertions:**
- `infer_state(plan_dir).status == "requirements"` when only requirements.md exists
- `infer_state(plan_dir).artifacts == {"requirements.md"}`
- Returns PlanState object with name matching directory name

**Expected failure:** Status is None or wrong value (inference logic not implemented)

**Why it fails:** infer_state() doesn't scan for requirements.md yet

**Verify RED:** `pytest tests/test_planstate_inference.py::test_requirements_status_detection -v`

**GREEN Phase:**

**Implementation:** Scan for requirements.md artifact, set status="requirements"

**Behavior:**
- Check if requirements.md exists in plan_dir
- If found and no higher-status artifacts, return PlanState with status="requirements"
- Extract plan name from directory name

**Approach:** Scan artifacts in priority order (ready → planned → designed → requirements)

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Add requirements.md detection to infer_state()
  Location hint: After empty-dir check, before return None

- File: `tests/test_planstate_inference.py`
  Action: Create test with tmp_path, write requirements.md to plans/<name>/
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_requirements_status_detection -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Cycle 1.3: Designed status detection (design.md exists)

**RED Phase:**

**Test:** `test_designed_status_detection`
**Assertions:**
- `infer_state(plan_dir).status == "designed"` when design.md exists
- Status is "designed" even if requirements.md also exists (higher priority wins)
- `infer_state(plan_dir).artifacts` includes both "requirements.md" and "design.md"

**Expected failure:** Status is "requirements" instead of "designed" (priority logic wrong)

**Why it fails:** Artifact priority not implemented correctly

**Verify RED:** `pytest tests/test_planstate_inference.py::test_designed_status_detection -v`

**GREEN Phase:**

**Implementation:** Scan for design.md before requirements.md in priority order

**Behavior:**
- Check ready → planned → designed → requirements (highest first)
- design.md found → status="designed" regardless of other artifacts
- Collect all artifacts found, not just highest

**Approach:** Reverse priority order in scan (check highest status artifacts first)

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Add design.md detection with higher priority than requirements.md
  Location hint: In infer_state(), check design.md before requirements.md

- File: `tests/test_planstate_inference.py`
  Action: Create test with both requirements.md and design.md present
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_designed_status_detection -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Cycle 1.4: Planned status detection (runbook-phase-*.md files)

**RED Phase:**

**Test:** `test_planned_status_detection`
**Assertions:**
- `infer_state(plan_dir).status == "planned"` when runbook-phase-*.md files exist
- Status is "planned" even if design.md exists (higher priority wins)
- `artifacts` set includes "runbook-phase-1.md", "runbook-phase-2.md" (actual filenames)

**Expected failure:** Status is "designed" instead of "planned" (glob pattern not working)

**Why it fails:** No glob pattern for runbook-phase-*.md files

**Verify RED:** `pytest tests/test_planstate_inference.py::test_planned_status_detection -v`

**GREEN Phase:**

**Implementation:** Use glob pattern to detect runbook-phase-*.md files

**Behavior:**
- Use `plan_dir.glob("runbook-phase-*.md")` to find phase files
- If any found → status="planned"
- Include actual phase filenames in artifacts set

**Approach:** Glob returns iterator, convert to list and check if non-empty

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Add glob pattern for runbook-phase-*.md before design.md check
  Location hint: Priority order in infer_state()

- File: `tests/test_planstate_inference.py`
  Action: Create test with design.md + runbook-phase-1.md, runbook-phase-2.md
  Location hint: New test function, use tmp_path.touch() to create files

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_planned_status_detection -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Cycle 1.5: Ready status detection (steps/ + orchestrator-plan.md)

**RED Phase:**

**Test:** `test_ready_status_detection`
**Assertions:**
- `infer_state(plan_dir).status == "ready"` when steps/ directory and orchestrator-plan.md exist
- Status is "ready" even if runbook-phase-*.md files exist (highest priority)
- `artifacts` includes "steps/" (directory marker) and "orchestrator-plan.md"

**Expected failure:** Status is "planned" instead of "ready" (steps/ detection missing)

**Why it fails:** No detection for steps/ directory and orchestrator-plan.md

**Verify RED:** `pytest tests/test_planstate_inference.py::test_ready_status_detection -v`

**GREEN Phase:**

**Implementation:** Check for steps/ directory AND orchestrator-plan.md (both required for ready)

**Behavior:**
- `(plan_dir / "steps").is_dir()` → steps directory exists
- `(plan_dir / "orchestrator-plan.md").exists()` → orchestrator plan exists
- Both must be true for status="ready"

**Approach:** Directory check first (cheaper), then file check

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Add steps/ + orchestrator-plan.md detection as highest priority
  Location hint: First check in infer_state() priority order

- File: `tests/test_planstate_inference.py`
  Action: Create test with all artifacts including steps/ directory (use mkdir) and orchestrator-plan.md
  Location hint: New test function

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_ready_status_detection -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Cycle 1.6: Next action derivation from status

**RED Phase:**

**Test:** `test_next_action_derivation`
**Assertions:**
- `infer_state(requirements_only).next_action == "/design plans/<name>/requirements.md"` for requirements status
- `infer_state(designed).next_action == "/runbook plans/<name>/design.md"` for designed status
- `infer_state(planned).next_action == "agent-core/bin/prepare-runbook.py plans/<name>"` for planned status (note: per design, this should be the full path)
- `infer_state(ready).next_action == "/orchestrate <name>"` for ready status

**Expected failure:** next_action is empty string or None (derivation not implemented)

**Why it fails:** next_action field not populated from status

**Verify RED:** `pytest tests/test_planstate_inference.py::test_next_action_derivation -v`

**GREEN Phase:**

**Implementation:** Map status to next action command string

**Behavior:**
- requirements → `/design plans/<name>/requirements.md`
- designed → `/runbook plans/<name>/design.md`
- planned → `agent-core/bin/prepare-runbook.py plans/<name>`
- ready → `/orchestrate <name>`

**Approach:** Status-to-command mapping table (dict or match statement)

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Add next_action derivation logic after status determination
  Location hint: After status is set in infer_state(), before return

- File: `tests/test_planstate_inference.py`
  Action: Add parametrized test covering all four status levels
  Location hint: Use @pytest.mark.parametrize with (status, artifacts, expected_next_action) tuples

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_next_action_derivation -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Cycle 1.7: Gate attachment interface (stub vet call)

**Note:** Actual vet.py built in Phase 2. This cycle wires the interface and tests with mock VetStatus.

**RED Phase:**

**Test:** `test_gate_attachment_with_mock`
**Assertions:**
- `infer_state(plan_dir).gate` is None when vet status has no stale chains
- `infer_state(plan_dir).gate == "design vet stale — re-vet before planning"` when mock vet status returns stale design
- Gate is None by default (no vet status available)

**Expected failure:** PlanState has no gate field or gate is always None (interface not wired)

**Why it fails:** Gate field not populated, no integration point for vet status

**Verify RED:** `pytest tests/test_planstate_inference.py::test_gate_attachment_with_mock -v`

**GREEN Phase:**

**Implementation:** Add gate field to PlanState, stub get_vet_status() call with mock in tests

**Behavior:**
- infer_state() calls get_vet_status(plan_dir) if available
- Parse VetStatus.chains to find first stale chain
- Map stale chain to gate message (design → "design vet stale — re-vet before planning")
- Gate is None if no vet status or no stale chains

**Approach:** Accept optional vet_status_func parameter in infer_state() for testing (dependency injection)

**Changes:**
- File: `src/claudeutils/planstate/models.py`
  Action: Add gate: str | None field to PlanState dataclass
  Location hint: After next_action field

- File: `src/claudeutils/planstate/inference.py`
  Action: Add gate computation logic, accept optional vet_status_func for testability
  Location hint: After next_action derivation, before return

- File: `tests/test_planstate_inference.py`
  Action: Create test with mock VetStatus showing stale design.md → design-review.md chain
  Location hint: New test function, use unittest.mock.Mock for VetStatus

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_gate_attachment_with_mock -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Cycle 1.8: list_plans() helper for directory scanning

**RED Phase:**

**Test:** `test_list_plans_directory_scanning`
**Assertions:**
- `list_plans(plans_dir)` returns list of PlanState objects for all plan directories
- Plans in plans/ are included, plans/reports/ is excluded
- Empty directories are excluded (return None from infer_state → filtered)
- Returns empty list if plans_dir doesn't exist

**Expected failure:** NameError (list_plans not defined)

**Why it fails:** Helper function not implemented

**Verify RED:** `pytest tests/test_planstate_inference.py::test_list_plans_directory_scanning -v`

**GREEN Phase:**

**Implementation:** Scan plans/ directory, call infer_state() per plan, filter None results

**Behavior:**
- Use `plans_dir.iterdir()` to list all items
- Skip dotfiles, "reports" directory, "claude" directory
- Call infer_state() for each directory
- Filter out None results (empty dirs, non-plans)
- Return list of PlanState objects

**Approach:** Generator expression with filter for None values

**Changes:**
- File: `src/claudeutils/planstate/inference.py`
  Action: Implement list_plans(plans_dir: Path) -> list[PlanState]
  Location hint: New function after infer_state()

- File: `src/claudeutils/planstate/__init__.py`
  Action: Export list_plans in __all__
  Location hint: Alongside infer_state

- File: `tests/test_planstate_inference.py`
  Action: Create test with multiple plan directories (some valid, some empty, include reports/)
  Location hint: New test function, use tmp_path with multiple subdirs

**Verify GREEN:** `pytest tests/test_planstate_inference.py::test_list_plans_directory_scanning -v`
**Verify no regression:** `pytest tests/test_planstate_inference.py -v`

---

## Phase 1 Checkpoint

**After all cycles complete:**

1. Run `just dev` to verify code quality
2. Functional review: Check that infer_state() returns correct status for all artifact combinations
3. Commit: All Phase 1 implementations and tests

**Expected state:**
- planstate module exists with inference.py, models.py, __init__.py
- All 8 tests pass in test_planstate_inference.py
- list_plans() correctly scans plan directories and filters out non-plans
- Gate interface wired (actual vet integration in Phase 2)
