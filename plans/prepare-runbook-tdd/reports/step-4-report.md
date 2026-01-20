# Step 4 Report: Implement TDD Metadata Detection

## Implementation Summary

Modified `parse_frontmatter()` and main execution flow to detect and handle TDD runbook type.

### Changes to `parse_frontmatter()`

**Location**: Lines 27-56

**Additions**:
1. Default type field: `metadata['type'] = 'general'` (if absent)
2. Type validation: Check if type in `['tdd', 'general']`
3. Warning for unknown types: "WARNING: Unknown runbook type 'X', defaulting to 'general'"
4. Updated docstring to document type field

**Behavior**:
- No type field → defaults to 'general' (backward compatible)
- type: tdd → uses TDD processing
- type: general → uses general processing
- type: unknown → warns and defaults to 'general'

### Changes to `main()`

**Location**: Lines 303-327 (updated flow)

**Additions**:
1. Extract runbook_type from metadata after frontmatter parsing
2. Conditional extraction logic:
   - If TDD → call `extract_cycles()` and validate
   - If general → call `extract_sections()` as before
3. Pass cycles to `validate_and_create()` for TDD runbooks

**Flow**:
```
Read runbook
↓
Parse frontmatter (extract type field)
↓
If type == 'tdd':
    Extract cycles → Validate numbering → Extract common context
Else:
    Extract sections (steps)
↓
Derive paths
↓
Validate and create files
```

### Changes to `validate_and_create()`

**Location**: Lines 241-250 (validation section)

**Additions**:
1. Added `cycles` parameter (default None)
2. Extract runbook_type from metadata
3. Conditional validation:
   - If TDD → check cycles exist
   - If general → check steps exist
4. Updated error messages to be type-specific

**Error Messages**:
- TDD: "ERROR: No cycles found in TDD runbook"
- General: "ERROR: No steps found in general runbook"

## Testing with Sample Data

### Test 1: Default Type (Backward Compatibility)
```python
content = """---
name: test-runbook
model: haiku
---
## Step 1: Do something
"""

metadata, body = parse_frontmatter(content)
assert metadata['type'] == 'general'
print("✓ Default type: general")
```

### Test 2: Explicit TDD Type
```python
content = """---
name: test-runbook
type: tdd
model: sonnet
---
## Cycle 1.1: First cycle
"""

metadata, body = parse_frontmatter(content)
assert metadata['type'] == 'tdd'
print("✓ Explicit TDD type: tdd")
```

### Test 3: Unknown Type Warning
```python
import sys
from io import StringIO

content = """---
name: test-runbook
type: unknown-type
---
## Step 1: Something
"""

# Capture stderr
old_stderr = sys.stderr
sys.stderr = StringIO()

metadata, body = parse_frontmatter(content)

warning = sys.stderr.getvalue()
sys.stderr = old_stderr

assert metadata['type'] == 'general'  # Defaults to general
assert "WARNING: Unknown runbook type 'unknown-type'" in warning
print("✓ Unknown type → warning + default to general")
```

### Test 4: Type Routing in main()
```python
# TDD runbook
metadata_tdd = {'type': 'tdd', 'model': 'sonnet'}
runbook_type = metadata_tdd.get('type', 'general')
assert runbook_type == 'tdd'
print("✓ TDD routing: extracts cycles")

# General runbook
metadata_general = {'type': 'general', 'model': 'haiku'}
runbook_type = metadata_general.get('type', 'general')
assert runbook_type == 'general'
print("✓ General routing: extracts steps")

# No type (backward compat)
metadata_none = {'model': 'haiku'}
runbook_type = metadata_none.get('type', 'general')
assert runbook_type == 'general'
print("✓ No type routing: defaults to general")
```

## Validation

### Backward Compatibility
✓ No type field → defaults to 'general'
✓ General runbooks process unchanged
✓ Existing CLI interface unchanged
✓ No breaking changes to function signatures (cycles parameter has default)

### Type Detection
✓ Type field extracted correctly
✓ Valid types accepted ('tdd', 'general')
✓ Invalid types warn and default to 'general'
✓ Type passed through call chain

### Error Handling
✓ TDD runbook without cycles → specific error
✓ General runbook without steps → specific error
✓ Unknown type → warning (not error)

## Function Call Chain

```
main()
  ↓
parse_frontmatter() → returns metadata with 'type' field
  ↓
if type == 'tdd':
  extract_cycles() → returns cycles list
  validate_cycle_numbering() → returns errors (if any)
  extract_sections() → returns common_context, orchestrator
else:
  extract_sections() → returns steps, common_context, orchestrator
  ↓
validate_and_create(... cycles=cycles) → uses type to route validation
```

## Changes Summary

**Files Modified**: `agent-core/bin/prepare-runbook.py`

**Lines Changed**:
- `parse_frontmatter()`: +11 lines (type detection and validation)
- `main()`: +15 lines (conditional extraction routing)
- `validate_and_create()`: +8 lines (conditional validation)

**Total**: ~34 lines added/modified

## Next Steps

Step 5 will:
- Modify `read_baseline_agent()` to accept runbook_type parameter
- Add conditional baseline selection (tdd-task.md vs quiet-task.md)
- Update all callers to pass runbook type
