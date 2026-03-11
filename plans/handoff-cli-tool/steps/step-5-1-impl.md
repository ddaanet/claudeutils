# Cycle 5.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 5

---

## Phase Context

Markdown stdin parser (commit-specific format) and scripted vet check.

---

---

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/session/commit/parse.py`

**Behavior:**
- `CommitInput` dataclass: `files: list[str]`, `options: set[str]`, `submodules: dict[str, str]`, `message: str`
- `parse_commit_input(text: str) -> CommitInput` — section-based parsing
- Split on `## ` at line start. Known section names: `Files`, `Options`, `Submodule <path>`, `Message`
- `## Message` is always last — everything from `## Message` to EOF is message body
- Blockquote stripping: remove leading `> ` or `>` from each line
- Valid options: `no-vet`, `just-lint`, `amend`. Unknown → raise `CommitInputError`
- `CommitInputError` exception for missing required sections or unknown options

**Approach:** Sequential parsing — find each `## ` boundary, classify section, delegate to section-specific parser. Message section greedily consumes to EOF (safe for `## ` in blockquotes).

**Changes:**
- File: `src/claudeutils/session/commit/parse.py`
  Action: Create with `CommitInput`, `CommitInputError`, `parse_commit_input()`

**Verify lint:** `just lint`
**Verify GREEN:** `pytest tests/test_session_commit.py -v`
**Verify no regression:** `just precommit`

---
