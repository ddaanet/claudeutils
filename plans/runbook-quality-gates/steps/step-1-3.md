# Cycle 1.3

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.3: model-tags — violation detection (skill/fragment/agent file with non-opus tag, exit 1)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` — understand `check_model_tags` return type (list of violation dicts) from Cycle 1.2.

**RED Phase:**

**Test:** `test_model_tags_violation`
**Assertions:**
- Running `model-tags` on `VIOLATION_MODEL_TAGS` fixture exits with code 1
- Report contains `**Result:** FAIL`
- Report `Violations` section names the artifact-type file path and current model (`haiku`)
- Report contains `**Expected:** opus`
- Report `Summary` shows `Failed: 1`

**Fixture:** `VIOLATION_MODEL_TAGS` — cycle with `File: agent-core/skills/myskill/SKILL.md` in Changes and `**Execution Model**: Haiku`.

**Expected failure:** `AssertionError` — `check_model_tags` from Cycle 1.2 only implements the no-violation path: it writes a PASS report and exits 0 for all inputs; no violation branch exists yet.

**Why it fails:** Cycle 1.2 GREEN implements only the happy path (`No violations → write PASS report, exit 0`). `VIOLATION_MODEL_TAGS` fixture triggers the violation branch, which doesn't exist — `model-tags` exits 0 and writes PASS, causing the exit-code and Result assertions to fail.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_model_tags_violation -v`

---

**GREEN Phase:**

**Implementation:** Complete violation detection in `check_model_tags`.

**Behavior:**
- When artifact-type file found and model is not `opus`: append violation dict with `file`, `current_model`, `expected_model="opus"`, `location` (cycle/step identifier)
- `write_report` formats violation dicts into Violations section per report format spec
- Non-empty violations list → write FAIL report, exit 1

**Approach:** The violation condition is `file_matches_artifact_prefix AND model_lower != 'opus'`. `workflow-*.md` requires `fnmatch.fnmatch(path, 'agents/decisions/workflow-*.md')` or glob-style check. Exit code: `sys.exit(0)` if no violations, `sys.exit(1)` if violations.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Complete violation detection in `check_model_tags`; update `write_report` to format violation dicts; update handler to call `sys.exit(1)` on violations
  Location hint: Inside `check_model_tags` and `write_report` functions

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_model_tags_violation -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---

**Checkpoint:** `just test tests/test_validate_runbook.py` — all tests pass.

# Phase 2: `lifecycle` subcommand (type: tdd)

**Target files:**
- `agent-core/bin/validate-runbook.py` (modify)
- `tests/test_validate_runbook.py` (modify)

**Depends on:** Phase 1 (script scaffold, importlib infrastructure, `write_report` function)

**Parsing targets:** `File:` + `Action:` fields across all cycles/steps to build create→modify dependency graph.

---
