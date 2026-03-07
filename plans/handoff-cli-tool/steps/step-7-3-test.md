# Cycle 7.3

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 7

---

## Phase Context

End-to-end tests with real git repos via `tmp_path`. Verifies complete pipelines through CLI entry points.

---

---

## Cycle 7.3: Commit integration

**RED Phase:**

**Test:** `test_commit_parent_integration`, `test_commit_submodule_integration`, `test_commit_amend_integration`
**File:** `tests/test_session_integration.py`

**Prerequisite:** Shared `tmp_path` fixture creating git repo with submodule (from conftest)

**Assertions — parent-only:**
- Create modified file in `tmp_path` repo (uncommitted change, appears in `git status --porcelain`)
- CliRunner invokes `_session commit` with stdin specifying the file + message
- Git log shows new commit with expected message
- Output contains `[branch hash] message` format
- Exit code 0

**Assertions — submodule:**
- Create dirty file in submodule directory
- CliRunner with stdin specifying submodule file, submodule message, and parent message
- Submodule git log shows new commit
- Parent git log shows new commit (with submodule pointer update)
- Output contains `<path>:` labeled submodule output followed by parent output
- Exit code 0

**Assertions — amend:**
- Create initial commit, then create new dirty file
- CliRunner with `amend` option → amend the previous commit
- Git log shows only one commit (amended, not new)
- Output contains `Date:` line (amend output format)
- Exit code 0

**Expected failure:** End-to-end commit pipeline wiring

**Why it fails:** Full pipeline through real git operations

**Verify RED:** `pytest tests/test_session_integration.py::test_commit_parent_integration -v`

---
