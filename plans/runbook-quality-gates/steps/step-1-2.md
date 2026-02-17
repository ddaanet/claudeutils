# Cycle 1.2

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.2: model-tags — happy path (no violations, exit 0, report written)

**Execution Model**: Sonnet

**Prerequisite:** Read `agent-core/bin/validate-runbook.py` lines 1–50 — understand importlib setup and `write_report` signature established in Cycle 1.1.

**RED Phase:**

**Test:** `test_model_tags_happy_path`
**Assertions:**
- Running `model-tags` on a fixture with no artifact-type file references exits with code 0
- Report file exists at expected path
- Report contains `**Result:** PASS`
- Report `Summary` section contains `Failed: 0`

**Fixture:** `VALID_TDD` — valid TDD runbook with non-architectural file references and sonnet model tag.

**Expected failure:** `AssertionError` — `model-tags` handler is still a stub (exit 0 without writing report), or `FileNotFoundError` if report not written.

**Why it fails:** `model-tags` handler has no logic; report not written.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_model_tags_happy_path -v`

---

**GREEN Phase:**

**Implementation:** Implement `check_model_tags(content, path)` function and wire to `model-tags` subcommand handler.

**Behavior:**
- Reads runbook: if `path` is a directory, call `assemble_phase_files(path)` to get content; if file, read directly
- For each cycle/step in content: extract `**Execution Model**:` using `extract_step_metadata(step_content)`; extract `File:` references from `**Changes:**` section via regex `r'- File: `?([^`\n]+)`?'`
- Artifact-type paths requiring opus: `agent-core/skills/`, `agent-core/fragments/`, `agent-core/agents/`, and files matching `agents/decisions/workflow-*.md`
- No violations → write PASS report, exit 0

**Approach:** Iterate extracted cycles from `extract_cycles(content)`. For each cycle, get its text block. Extract model with `extract_step_metadata`. Find File references with `re.findall`. Check each file path against ARTIFACT_PREFIXES. No violation if model is `opus` or file is not an artifact type.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Add `ARTIFACT_PREFIXES` constant and `check_model_tags(content, path)` function; wire to `model-tags` handler in `main()`
  Location hint: After importlib block, before `main()`

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_model_tags_happy_path -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
