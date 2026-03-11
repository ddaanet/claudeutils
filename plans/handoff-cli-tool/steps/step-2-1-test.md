# Cycle 2.1

**Plan**: `plans/handoff-cli-tool/runbook.md`
**Execution Model**: sonnet
**Phase**: 2

---

## Phase Context

Shared parser for session.md consumed by both status and handoff subcommands. Extends existing `worktree/session.py` parsing.

---

---

## Cycle 2.1: Parse all session.md sections with parametrized tests

**RED Phase:**

**Test:** `test_parse_session_sections[status_line]`, `test_parse_session_sections[completed]`, `test_parse_session_sections[in_tree_tasks]`, `test_parse_session_sections[worktree_tasks]`
**File:** `tests/test_session_parser.py`

**Assertions:**
- `parse_status_line(content)` returns the text between `# Session Handoff:` date line and first `## ` heading, stripped
- `parse_completed_section(content)` returns list of lines under `## Completed This Session` heading (up to next `## `)
- `parse_tasks(content, section="In-tree Tasks")` returns list of `ParsedTask` objects with `model`, `command`, `restart`, `worktree_marker` fields populated. Task with `→ slug` has `worktree_marker="slug"`. Task with `→ wt` has `worktree_marker="wt"`
- `parse_tasks(content, section="Worktree Tasks")` returns same structure for worktree section
- Each task has `plan_dir` attribute populated from continuation lines (`Plan:` or `plans/<name>/` in command)

**Edge case tests:**
- `test_parse_status_line_missing` — content without `# Session Handoff:` returns None
- `test_parse_tasks_old_format` — task line without pipe-separated metadata returns ParsedTask with `model=None`, `restart=False`
- `test_parse_tasks_empty_section` — section heading present but no tasks returns `[]`
- `test_parse_completed_section_empty` — heading present, no content returns `[]`

**Fixture:** `SESSION_MD_FIXTURE` — realistic session.md with:
```markdown
# Session Handoff: 2026-03-07

**Status:** Phase 1 complete — infrastructure ready.

## Completed This Session

**Phase 1 infrastructure:**
- Extracted git helpers
- Created package structure

## In-tree Tasks

- [ ] **Build parser** — `/runbook plans/parser/design.md` | sonnet
  - Plan: parser | Status: outlined
- [ ] **Fix bug** — `just fix-bug` | haiku
- [x] **Done task** — `/commit` | sonnet

## Worktree Tasks

- [ ] **Parallel work** → `my-slug` — `/design plans/parallel/problem.md` | opus | restart
- [ ] **Future work** → `wt` — `/design plans/future/problem.md` | sonnet
```

**Expected failure:** `ImportError` or `AttributeError` — functions don't exist yet

**Why it fails:** No `session/parse.py` module with these functions

**Verify RED:** `pytest tests/test_session_parser.py -v`

---
