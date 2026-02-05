# Cycle 3.1

**Plan**: `plans/statusline-parity/runbook.md`
**Execution Model**: haiku
**Phase**: 3
**Report Path**: `plans/statusline-parity/reports/cycle-3-1-notes.md`

---

## Cycle 3.1: Python Environment Detection

**Objective**: Create `get_python_env()` function and `PythonEnv` model to detect active Python environment

**Script Evaluation**: Direct execution (TDD cycle)
**Execution Model**: Haiku

**Implementation:**

### RED Phase

**Test:** `test_get_python_env` in `tests/test_statusline_context.py`

**Test description - Environment variable detection:**

Create test cases verifying that `get_python_env()` correctly detects Python environments from environment variables. Test the function with multiple scenarios: when VIRTUAL_ENV is set (simulating an active venv), when CONDA_DEFAULT_ENV is set (simulating a Conda environment), when both are set (Conda takes precedence), and when neither is set (returns None).

For each case, verify the returned `PythonEnv` model contains the correct environment name extracted from the variable. VIRTUAL_ENV should be extracted as the basename of the path (e.g., `/path/to/venv` → `venv`). CONDA_DEFAULT_ENV is already a simple name (e.g., `myenv`) and should be returned as-is. When both variables exist, verify Conda takes priority.

Test edge cases: empty string values should be treated as absent, whitespace-only values should be normalized or treated as None, and missing variables should gracefully return `PythonEnv(name=None)`.

**Assertions:**
- `get_python_env()` with `VIRTUAL_ENV="/path/to/myenv"` returns `PythonEnv(name="myenv")`
- `get_python_env()` with `CONDA_DEFAULT_ENV="conda-env"` returns `PythonEnv(name="conda-env")`
- `get_python_env()` with both set returns Conda name (priority test)
- `get_python_env()` with neither set returns `PythonEnv(name=None)`
- `get_python_env()` with `VIRTUAL_ENV=""` (empty) returns `PythonEnv(name=None)`
- Basename extraction: `VIRTUAL_ENV="/Users/david/venv"` returns `"venv"` not the full path

**Expected failure:** `ImportError: cannot import name 'get_python_env' from 'claudeutils.statusline.context'` or `ImportError: cannot import name 'PythonEnv' from 'claudeutils.statusline.models'`

**Why it fails:** Function and model don't exist yet

**Verify RED:** `pytest tests/test_statusline_context.py::test_get_python_env -v`

---

### GREEN Phase

**Implementation:** Add `PythonEnv` model to models.py and `get_python_env()` function to context.py

**Behavior:**

Create a `PythonEnv` Pydantic model in models.py with an optional `name` field (type `str | None`, default `None`). This model represents a detected Python environment with just the environment name.

Implement `get_python_env()` function in context.py that:
- Checks `os.environ.get("CONDA_DEFAULT_ENV")` first (takes priority)
- If Conda env is set and non-empty, extract and return the name as-is
- Otherwise checks `os.environ.get("VIRTUAL_ENV")` for venv environments
- If venv path is set and non-empty, extract the basename of the path as the environment name
- Returns `PythonEnv` model instance with detected name or None if neither variable is set
- Handles edge cases: empty/whitespace values treated as absent

**Approach:** Simple environment variable checks per D6 design. Shell reference lines 465-472 show the same detection logic.

**Changes:**
- File: `src/claudeutils/statusline/models.py`
  Action: Add `PythonEnv` Pydantic model with optional `name: str | None` field
  Location hint: After existing models (e.g., after GitStatus)

- File: `src/claudeutils/statusline/context.py`
  Action: Add `get_python_env()` function that returns PythonEnv
  Location hint: In the file's main function section, can be called by CLI later
  Implementation detail: Use `os.path.basename()` to extract venv name from VIRTUAL_ENV path

**Verify GREEN:** `pytest tests/test_statusline_context.py::test_get_python_env -v`
- Must pass

**Verify no regression:** `just test`
- All existing tests pass

---

**Expected Outcome**: GREEN verification, no regressions
**Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED (ImportError), passes during GREEN, no breaks
**Report Path**: plans/statusline-parity/reports/cycle-3-1-notes.md

---
