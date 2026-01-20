# Step 7 Report: Implement Cycle Validation

## Implementation Summary

Created `validate_cycle_structure()` function and integrated validation into main flow to check for mandatory TDD sections.

### New Function: `validate_cycle_structure()`

**Location**: Lines 112-135

**Signature**:
```python
def validate_cycle_structure(cycle):
    """Validate that cycle contains mandatory TDD sections.

    Args:
        cycle: Cycle dictionary with 'number', 'content' keys

    Returns: List of error/warning messages (empty if valid)
    """
```

**Validation Checks**:
1. **RED phase** (mandatory): Case-insensitive search for 'red' in content
2. **GREEN phase** (mandatory): Case-insensitive search for 'green' in content
3. **Stop Conditions** (mandatory): Case-insensitive search for 'stop condition' in content
4. **Dependencies** (non-critical): Case-insensitive search for 'dependencies' or 'dependency'

**Error Messages**:
- Missing RED: `"ERROR: Cycle {number} missing required section: RED phase"`
- Missing GREEN: `"ERROR: Cycle {number} missing required section: GREEN phase"`
- Missing Stop Conditions: `"ERROR: Cycle {number} missing required section: Stop Conditions"`
- Missing Dependencies: `"WARNING: Cycle {number} missing dependencies section"`

### Integration in `main()`

**Location**: Lines 343-365 (TDD validation section)

**Validation Flow**:
```python
# 1. Extract cycles
cycles = extract_cycles(body)

# 2. Validate numbering
errors = validate_cycle_numbering(cycles)
if errors:
    print errors and exit

# 3. Validate structure (NEW)
all_messages = []
critical_errors = []
for cycle in cycles:
    messages = validate_cycle_structure(cycle)
    all_messages.extend(messages)
    critical_errors.extend([m for m in messages if m.startswith('ERROR:')])

# 4. Print all messages
for msg in all_messages:
    print(msg, file=sys.stderr)

# 5. Stop if critical errors
if critical_errors:
    print(f"\nERROR: Found {len(critical_errors)} critical validation error(s)", file=sys.stderr)
    sys.exit(1)
```

**Separation of Concerns**:
- Numbering validation (sequential, duplicates) → separate check
- Structure validation (mandatory sections) → separate check
- Both must pass before file generation

## Validation Logic

### Subsection Detection

**Method**: Case-insensitive substring search

**Rationale**:
- Flexible: Accepts "RED", "Red", "red", "### RED Phase", etc.
- Simple: No complex regex needed
- Robust: Catches variations in formatting

**Examples of Detected Patterns**:
- `### RED Phase` ✓
- `**RED**: Write failing test` ✓
- `## RED` ✓
- `Start with red phase...` ✓ (keyword in text)

### Critical vs Warning

**Critical (ERROR)**:
- Missing RED phase → Cannot follow TDD cycle
- Missing GREEN phase → Cannot follow TDD cycle
- Missing Stop Conditions → Cannot determine cycle completion

**Non-Critical (WARNING)**:
- Missing Dependencies → Cycle may not have dependencies (first cycle, independent work)

**Behavior**:
- Errors → Script exits with code 1
- Warnings → Printed to stderr but script continues

## Testing with Sample Data

### Test 1: Valid Cycle Structure
```python
cycle_valid = {
    'number': '1.1',
    'content': '''## Cycle 1.1: Test

**Dependencies**: None

### RED Phase
Write failing test...

### GREEN Phase
Implement logic...

### REFACTOR Phase
Clean up...

**Stop Conditions**:
- Tests pass
- Code clean
'''
}

messages = validate_cycle_structure(cycle_valid)
assert messages == [], f"Expected no errors, got: {messages}"
print("✓ Valid cycle: no errors")
```

### Test 2: Missing RED Phase
```python
cycle_no_red = {
    'number': '1.2',
    'content': '''## Cycle 1.2: Test

### GREEN Phase
Implement logic...

**Stop Conditions**: Tests pass
'''
}

messages = validate_cycle_structure(cycle_no_red)
assert any('RED phase' in m for m in messages)
assert any(m.startswith('ERROR:') for m in messages)
print("✓ Missing RED: error detected")
```

### Test 3: Missing GREEN Phase
```python
cycle_no_green = {
    'number': '1.3',
    'content': '''## Cycle 1.3: Test

### RED Phase
Write test...

**Stop Conditions**: Tests pass
'''
}

messages = validate_cycle_structure(cycle_no_green)
assert any('GREEN phase' in m for m in messages)
assert any(m.startswith('ERROR:') for m in messages)
print("✓ Missing GREEN: error detected")
```

### Test 4: Missing Stop Conditions
```python
cycle_no_stop = {
    'number': '1.4',
    'content': '''## Cycle 1.4: Test

### RED Phase
Write test...

### GREEN Phase
Implement...
'''
}

messages = validate_cycle_structure(cycle_no_stop)
assert any('Stop Conditions' in m for m in messages)
assert any(m.startswith('ERROR:') for m in messages)
print("✓ Missing Stop Conditions: error detected")
```

### Test 5: Missing Dependencies (Warning)
```python
cycle_no_deps = {
    'number': '1.1',
    'content': '''## Cycle 1.1: First cycle

### RED Phase
Write test...

### GREEN Phase
Implement...

**Stop Conditions**: Done
'''
}

messages = validate_cycle_structure(cycle_no_deps)
warnings = [m for m in messages if m.startswith('WARNING:')]
errors = [m for m in messages if m.startswith('ERROR:')]

assert len(warnings) == 1
assert len(errors) == 0
assert 'dependencies' in warnings[0].lower()
print("✓ Missing Dependencies: warning (not error)")
```

### Test 6: Case Insensitive Detection
```python
cycle_lowercase = {
    'number': '2.1',
    'content': '''## Cycle 2.1: Test

**dependencies**: Cycle 1.1

Start with red phase by writing tests.
Then green phase to make them pass.
Finally refactor if needed.

**stop conditions**: All tests pass
'''
}

messages = validate_cycle_structure(cycle_lowercase)
errors = [m for m in messages if m.startswith('ERROR:')]
assert len(errors) == 0
print("✓ Case insensitive: detects lowercase keywords")
```

## Integration Testing

### Test: Full Validation Flow
```python
# Simulated main() flow
cycles = [
    {
        'number': '1.1',
        'major': 1,
        'minor': 1,
        'content': '''### RED Phase
Test...
### GREEN Phase
Code...
**Stop Conditions**: Done
'''
    }
]

# Numbering validation
errors = validate_cycle_numbering(cycles)
assert len(errors) == 0

# Structure validation
all_messages = []
critical_errors = []
for cycle in cycles:
    messages = validate_cycle_structure(cycle)
    all_messages.extend(messages)
    critical_errors.extend([m for m in messages if m.startswith('ERROR:')])

# Should have 1 warning (missing dependencies), no errors
warnings = [m for m in all_messages if m.startswith('WARNING:')]
assert len(warnings) == 1
assert len(critical_errors) == 0

print("✓ Full validation flow: numbering + structure")
```

## Validation Results

✓ Validation detects missing RED phase
✓ Validation detects missing GREEN phase
✓ Validation detects missing Stop Conditions
✓ Warning issued for missing dependencies (non-critical)
✓ Case-insensitive detection works
✓ Critical errors stop execution
✓ Warnings do not stop execution
✓ All messages printed to stderr
✓ Error count summary displayed

## Error Output Example

```
ERROR: Cycle 1.2 missing required section: RED phase
ERROR: Cycle 1.3 missing required section: GREEN phase
ERROR: Cycle 2.1 missing required section: Stop Conditions
WARNING: Cycle 1.1 missing dependencies section

ERROR: Found 3 critical validation error(s)
```

## Changes Summary

**Files Modified**: `agent-core/bin/prepare-runbook.py`

**Lines Added**:
- `validate_cycle_structure()`: 24 lines (new function)
- Structure validation integration in `main()`: 20 lines

**Total**: ~44 lines added

## Design Decisions

### Why Case-Insensitive Substring Search
- **Flexibility**: Accepts various formatting styles
- **Simplicity**: No complex regex patterns
- **Robustness**: Catches keywords in different contexts
- **Trade-off**: May have false positives (keyword in unrelated text)

### Why Separate Numbering and Structure Validation
- **Clarity**: Each validation has clear purpose
- **Independence**: Can test each separately
- **Reporting**: Can report all errors together before exit
- **Extensibility**: Easy to add more structure checks

### Why Warnings for Dependencies
- **Flexibility**: First cycle may not have dependencies
- **UX**: Don't force boilerplate sections
- **Guidance**: Inform user but don't block
- **Alternative**: Could make mandatory, but seems too strict

## Next Steps

Step 8 will:
- Update CLI help text to mention TDD support
- Update error messages to use correct terminology
- Ensure consistency in output (step vs cycle)
- Review all print statements
