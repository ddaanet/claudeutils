# Test Improvement Plan: fix_markdown_structure.py

## Context

Script location: `scripts/fix_markdown_structure.py`

- Not a Python package, not part of build
- Current tests: inline `run_tests()` function (lines 171-248)
- Test file location: `scripts/test_fix_markdown_structure.py` (pytest will discover it)

## Refactoring

**Extract `process_lines()` function:**

```python
def process_lines(lines: list[str]) -> list[str]:
    """Apply all markdown structure fixes to lines."""
    # Current fix pipeline from process_file() lines 145-158
    lines = [fix_dunder_references(line) for line in lines]
    lines = fix_metadata_blocks(lines)
    lines = fix_warning_lines(lines)
    lines = fix_nested_lists(lines)
    lines = fix_numbered_list_spacing(lines)
    return lines
```

**Update `process_file()`:**

```python
def process_file(filepath: Path) -> bool:
    with open(filepath, encoding="utf-8") as f:
        original_lines = f.readlines()

    lines = process_lines(original_lines)

    if lines == original_lines:
        return False

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(lines)
    return True
```

**Remove:**

- `run_tests()` function (lines 171-248)
- `--test` flag handling in `main()` (lines 268-270)

## Test Structure

**File:** `scripts/test_fix_markdown_structure.py`

All tests use `process_lines()` or individual fix functions directly.

### Per-Function Tests

Each function gets 4 test cases:

**`test_fix_dunder_references()`:**

1. Existing: `## Minimal __init__.py` → `` ## Minimal `__init__.py` ``
2. Single: `# __name__` → `` # `__name__` ``
3. Mixed: heading with dunder + non-heading line (only heading changes)
4. Idempotent: already backticked input returns unchanged

**`test_fix_metadata_blocks()`:**

1. Existing: 2+ consecutive metadata → list items, single metadata unchanged
2. Single: one `**Label:**` line stays unchanged
3. Mixed: metadata block + unrelated lines (only block converted)
4. Idempotent: already list-formatted metadata unchanged

**`test_fix_warning_lines()`:**

1. Existing: 2+ consecutive warnings → list items
2. Single: one warning line stays unchanged
3. Mixed: warning block + unrelated lines
4. Idempotent: already list-formatted warnings unchanged

**`test_fix_nested_lists()`:**

1. Existing: `a. Child` → `1. Child`
2. Single: one lettered item converts
3. Mixed: lettered items + regular lines
4. Idempotent: already numbered items unchanged

**`test_fix_numbered_list_spacing()`:**

1. Existing: `**Label:**\n1. Item` → adds blank line
2. Mixed: label followed by non-list text (no blank added)
3. Idempotent: already has blank line unchanged

### Integration Test

**`test_process_lines_integration()`:**

Input combining all fix types:

```python
[
    "## About __init__.py\n",           # dunder fix
    "**File:** agents/role.md\n",       # metadata block
    "**Model:** Sonnet\n",              # metadata block
    "\n",
    "⚠️ Warning one\n",                 # warning lines
    "⚠️ Warning two\n",                 # warning lines
    "1. Parent:\n",
    "   a. Child 1\n",                   # nested list
    "   b. Child 2\n",                   # nested list
    "**Phase:**\n",                     # spacing
    "1. Execute\n",
]
```

Expected: all fixes applied correctly.

## Implementation Steps

1. Extract `process_lines()` function
2. Update `process_file()` to use it
3. Remove `run_tests()` and `--test` handling
4. Create `scripts/test_fix_markdown_structure.py`
5. Migrate 5 existing tests
6. Add coverage cases (single/mixed/idempotent per function)
7. Add integration test
8. Run: `pytest scripts/test_fix_markdown_structure.py`

## Pytest Discovery

Pytest will discover `scripts/test_fix_markdown_structure.py` automatically when run from project root.

Test import: `from fix_markdown_structure import process_lines, fix_*`
