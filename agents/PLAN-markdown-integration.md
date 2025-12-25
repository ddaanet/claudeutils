# Execution Plan: Integrate fix_markdown_structure

**For:** Code role agent (haiku)

**Prerequisites:** Read `START.md`, `AGENTS.md`, `agents/role-code.md`

**Context:** Move `scripts/fix_markdown_structure.py` into `src/claudeutils/markdown.py`
with CLI command `claudeutils markdown`.

**Decisions:**

- Command name: `markdown`
- File discovery: stdin (preserve current behavior)
- Output: print modified file paths (preserve current)
- Error handling: error on non-.md files (change from silent skip)

---

## Phase 1: Create Module + Migrate Tests

### Test Group 1: Module Import and Core Functions (8 tests)

**File:** `tests/test_markdown.py`

**MUST read before writing tests:**

- `scripts/fix_markdown_structure.py` → understand function signatures
- `scripts/test_fix_markdown_structure.py` → copy test cases

#### Test 1: Import process_lines

**Given:** New module `src/claudeutils/markdown.py` exists (create as empty file first)

**When:** Import statement runs

```python
from claudeutils.markdown import process_lines
```

**Then:** Import succeeds without error

**Requires:** Create `src/claudeutils/markdown.py` with `process_lines` function stub

**Does NOT require:** Any function implementation yet

---

#### Test 2: process_lines fixes dunder references

**Given:** Input with `__init__.py` in heading

```python
input_lines = ["## About __init__.py\n"]
expected = ["## About `__init__.py`\n"]
```

**When:** `process_lines(input_lines)` called

**Then:** Returns expected output

**Requires:**

- Copy `fix_dunder_references()` from `scripts/fix_markdown_structure.py`
- Wire into `process_lines()`

**Does NOT require:** Other fix functions yet

---

#### Test 3: process_lines fixes metadata blocks

**Given:** Multiple consecutive `**Label:**` lines

```python
input_lines = [
    "**File:** `role.md`\n",
    "**Model:** Sonnet\n",
    "\n",
]
expected = [
    "- **File:** `role.md`\n",
    "- **Model:** Sonnet\n",
    "\n",
]
```

**When:** `process_lines(input_lines)` called

**Then:** Returns expected output

**Requires:** Copy `fix_metadata_blocks()`, wire into `process_lines()`

**Does NOT require:** Other fix functions yet

---

#### Test 4: process_lines fixes warning lines

**Given:** Multiple consecutive `⚠️` lines

```python
input_lines = [
    "⚠️ Warning one\n",
    "⚠️ Warning two\n",
]
expected = [
    "- ⚠️ Warning one\n",
    "- ⚠️ Warning two\n",
]
```

**When:** `process_lines(input_lines)` called

**Then:** Returns expected output

**Requires:** Copy `fix_warning_lines()`, wire into `process_lines()`

**Does NOT require:** Other fix functions yet

---

#### Test 5: process_lines fixes nested lists

**Given:** Lettered sub-items

```python
input_lines = [
    "2. Parent:\n",
    "   a. Child 1\n",
    "   b. Child 2\n",
]
expected = [
    "2. Parent:\n",
    "   1. Child 1\n",
    "   2. Child 2\n",
]
```

**When:** `process_lines(input_lines)` called

**Then:** Returns expected output

**Requires:** Copy `fix_nested_lists()`, wire into `process_lines()`

**Does NOT require:** `fix_numbered_list_spacing()` yet

---

#### Test 6: process_lines fixes numbered list spacing

**Given:** Numbered list without blank line before

```python
input_lines = [
    "**Execution phase:**\n",
    "4. Batch reads\n",
]
expected = [
    "**Execution phase:**\n",
    "\n",
    "4. Batch reads\n",
]
```

**When:** `process_lines(input_lines)` called

**Then:** Returns expected output

**Requires:** Copy `fix_numbered_list_spacing()`, wire into `process_lines()`

**Does NOT require:** `process_file()` yet

---

#### Test 7: process_file returns True when modified

**Given:** Temp file with fixable content

```python
content = "## About __init__.py\n"
filepath = tmp_path / "test.md"
filepath.write_text(content)
```

**When:** `process_file(filepath)` called

**Then:**

- Returns `True`
- File content is `"## About `__init__.py`\n"`

**Requires:**

- Copy `process_file()` function
- Import `Path` from `pathlib`

**Does NOT require:** CLI command yet

---

#### Test 8: process_file returns False when unchanged

**Given:** Temp file with already-fixed content

```python
content = "## About `__init__.py`\n"
filepath = tmp_path / "test.md"
filepath.write_text(content)
```

**When:** `process_file(filepath)` called

**Then:**

- Returns `False`
- File content unchanged

**Requires:** No new code (validates idempotency)

**Does NOT require:** CLI command yet

---

**CHECKPOINT 1:** Run `just role-code tests/test_markdown.py` - awaiting approval

All 8 tests must pass. At this point:

- `src/claudeutils/markdown.py` has all core functions
- `tests/test_markdown.py` has 8 passing tests
- **MUST NOT** proceed to Phase 2 without user approval

---

## Phase 2: Add CLI Command

### Test Group 2: CLI Integration (6 tests)

**File:** `tests/test_cli_markdown.py`

**MUST read before writing tests:**

- `src/claudeutils/cli.py` → understand CLI structure
- `tests/test_cli_list.py` → understand CLI test patterns

#### Test 9: Help text shows markdown command

**Given:** CLI parser setup

**When:** Run `uv run claudeutils --help` via subprocess

**Then:** Output contains `markdown` in available commands

**Requires:**

- Add `markdown` subparser in `cli.py` `main()` function
- No handler implementation yet

**Does NOT require:** Command functionality

---

#### Test 10: markdown command processes file from stdin

**Given:**

- Temp directory with `test.md` containing `"## About __init__.py\n"`
- Stdin piped with file path

**When:** Run `echo "test.md" | uv run claudeutils markdown` in temp dir

**Then:**

- Exit code 0
- File modified to `"## About `__init__.py`\n"`
- Stdout contains `test.md`

**Requires:**

- Add `handle_markdown()` function in `cli.py`
- Read file paths from stdin (match script behavior)
- Call `markdown.process_file()` for each path
- Print modified file paths to stdout

**Does NOT require:** Error handling yet

---

#### Test 11: markdown command skips unchanged files

**Given:** Temp file `test.md` with `"## About `__init__.py`\n"` (already fixed)

**When:** Run `echo "test.md" | uv run claudeutils markdown`

**Then:**

- Exit code 0
- File unchanged
- Stdout empty (no modified files to report)

**Requires:** No new code (validates `process_file()` returns False correctly)

**Does NOT require:** Error handling yet

---

#### Test 12: markdown command errors on non-.md file

**Given:** Temp file `test.txt` (not markdown)

**When:** Run `echo "test.txt" | uv run claudeutils markdown`

**Then:**

- Exit code 1
- Stderr contains error message about non-.md file

**Requires:**

- Add validation in `handle_markdown()` to check file extension
- Print error and `sys.exit(1)` for non-.md files

**Does NOT require:** Missing file handling yet

---

#### Test 13: markdown command errors on missing file

**Given:** Non-existent file path `missing.md`

**When:** Run `echo "missing.md" | uv run claudeutils markdown`

**Then:**

- Exit code 1
- Stderr contains error message about missing file

**Requires:**

- Add existence check in `handle_markdown()`
- Print error and `sys.exit(1)` for missing files

**Does NOT require:** Multiple file handling yet

---

#### Test 14: markdown command processes multiple files

**Given:**

- Temp files: `test1.md`, `test2.md` (both fixable)
- `test3.md` (already fixed)

**When:** Run `echo -e "test1.md\ntest2.md\ntest3.md" | uv run claudeutils markdown`

**Then:**

- Exit code 0
- `test1.md` and `test2.md` modified
- Stdout contains `test1.md` and `test2.md` (one per line)
- Does NOT contain `test3.md`

**Requires:** No new code (loop over stdin lines already implemented)

**Does NOT require:** CLI complete

---

**CHECKPOINT 2:** Run `just role-code tests/test_cli_markdown.py` - awaiting approval

All 6 tests must pass. At this point:

- `src/claudeutils/cli.py` has `handle_markdown()` function
- `tests/test_cli_markdown.py` has 6 passing tests
- Command is functional: `uv run claudeutils markdown`
- **MUST NOT** proceed to Phase 3 without user approval

---

## Phase 3: Update Justfile

**File:** `justfile`

**No tests required** - manual verification only.

### Step 15: Update format recipe

**Current line 67:**

```
| uv run scripts/fix_markdown_structure.py >> "$tmpfile"
```

**Change to:**

```
| uv run claudeutils markdown >> "$tmpfile"
```

**Verification:**

1. Run `just format`
2. Verify output identical to previous behavior
3. Verify no errors

**CHECKPOINT 3:** Run `just format` on unchanged repo - awaiting approval

- Command succeeds without errors
- No files modified (repo already formatted)
- **MUST NOT** proceed to Phase 4 without user approval

---

## Phase 4: Cleanup

### Step 16: Remove old script files

**MUST NOT proceed** without user confirmation.

**Delete:**

1. `scripts/fix_markdown_structure.py`
2. `scripts/test_fix_markdown_structure.py`

**Verification:**

1. Run `just dev` → all tests pass
2. Run `just format` → still works
3. Grep for `fix_markdown_structure` → only found in `agents/PLAN-*` files

**CHECKPOINT 4:** Run `just dev` - awaiting approval

- All checks pass
- Old files deleted
- Integration complete

---

## Constraints

**MUST:**

- Stop at every checkpoint
- Copy exact test cases from `scripts/test_fix_markdown_structure.py`
- Preserve all function signatures and behavior
- Use type annotations (already present in script)
- Follow CLI patterns from existing subcommands

**NEVER:**

- Proceed past checkpoint without approval
- Modify test assertions (copy exactly)
- Add new features not in original script
- Change formatting logic

---

## File Size Limits

- `src/claudeutils/markdown.py`: ~200 lines (copy of 193-line script)
- `tests/test_markdown.py`: ~320 lines (copy of 317-line test file)
- `tests/test_cli_markdown.py`: ~100 lines (new CLI tests)
- `src/claudeutils/cli.py`: +30 lines (new subcommand)

All within limits (hard cap: 400 lines).
