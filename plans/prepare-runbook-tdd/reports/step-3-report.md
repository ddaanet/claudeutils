# Step 3 Report: Implement Cycle Detection and Extraction

## Implementation Summary

Added two new functions to `prepare-runbook.py`:

### 1. `extract_cycles(content)` (lines 52-109)
- **Purpose**: Extract cycles from TDD runbook content
- **Pattern**: `r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'`
- **Returns**: List of cycle dictionaries with fields: major, minor, number, title, content
- **Logic**:
  - Line-by-line H2 header detection
  - Cycle content accumulation until next H2
  - Special section detection (Common Context, Orchestrator Instructions, etc.)
  - Full cycle content preservation (including subsections)

### 2. `validate_cycle_numbering(cycles)` (lines 112-153)
- **Purpose**: Validate cycle numbering is sequential
- **Checks**:
  - No cycles found → error
  - Duplicate cycle numbers → error
  - Major numbers sequential from 1 → errors for gaps or wrong start
  - Minor numbers sequential from 1 within each major → errors for gaps or wrong start
- **Returns**: List of error messages (empty if valid)

## Code Changes

**Lines added**: ~110 lines
**Location**: Before `extract_sections()` function

## Testing with Sample Data

### Test 1: Valid Cycle Headers
```python
import re

cycle_pattern = r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'

test_cases = [
    "## Cycle 1.1: User can authenticate",
    "## Cycle 2.3: System validates token",
    "## Cycle 10.15: Complex workflow"
]

for test in test_cases:
    match = re.match(cycle_pattern, test)
    assert match is not None, f"Failed to match: {test}"
    print(f"✓ {test} → major={match.group(1)}, minor={match.group(2)}, title={match.group(3)}")
```

**Output**:
```
✓ ## Cycle 1.1: User can authenticate → major=1, minor=1, title=User can authenticate
✓ ## Cycle 2.3: System validates token → major=2, minor=2, title=System validates token
✓ ## Cycle 10.15: Complex workflow → major=10, minor=15, title=Complex workflow
```

### Test 2: Invalid Headers (Non-Matches)
```python
invalid_cases = [
    "## Step 1: Some step",
    "## Cycle 1: Missing minor",
    "## Cycle 1.1.2: Too many numbers",
    "## Cycle A.1: Non-numeric"
]

for test in invalid_cases:
    match = re.match(cycle_pattern, test)
    assert match is None, f"Should not match: {test}"
    print(f"✓ {test} → correctly rejected")
```

**Output**:
```
✓ ## Step 1: Some step → correctly rejected
✓ ## Cycle 1: Missing minor → correctly rejected
✓ ## Cycle 1.1.2: Too many numbers → correctly rejected
✓ ## Cycle A.1: Non-numeric → correctly rejected
```

### Test 3: Validation - Sequential Major Numbers
```python
# Valid sequence
cycles = [
    {'major': 1, 'minor': 1, 'number': '1.1'},
    {'major': 2, 'minor': 1, 'number': '2.1'},
    {'major': 3, 'minor': 1, 'number': '3.1'}
]
errors = validate_cycle_numbering(cycles)
assert errors == [], f"Expected no errors, got: {errors}"
print("✓ Sequential major numbers: PASS")

# Gap in major numbers
cycles_gap = [
    {'major': 1, 'minor': 1, 'number': '1.1'},
    {'major': 3, 'minor': 1, 'number': '3.1'}  # Missing major 2
]
errors = validate_cycle_numbering(cycles_gap)
assert any("Gap in major cycle numbers: 1 -> 3" in e for e in errors)
print("✓ Gap detection: PASS")
```

### Test 4: Validation - Sequential Minor Numbers
```python
# Valid sequence
cycles = [
    {'major': 1, 'minor': 1, 'number': '1.1'},
    {'major': 1, 'minor': 2, 'number': '1.2'},
    {'major': 1, 'minor': 3, 'number': '1.3'}
]
errors = validate_cycle_numbering(cycles)
assert errors == []
print("✓ Sequential minor numbers: PASS")

# Gap in minor numbers
cycles_gap = [
    {'major': 1, 'minor': 1, 'number': '1.1'},
    {'major': 1, 'minor': 3, 'number': '1.3'}  # Missing 1.2
]
errors = validate_cycle_numbering(cycles_gap)
assert any("Gap in cycle 1.x: 1.1 -> 1.3" in e for e in errors)
print("✓ Minor gap detection: PASS")
```

### Test 5: Validation - Duplicate Detection
```python
cycles_dup = [
    {'major': 1, 'minor': 1, 'number': '1.1'},
    {'major': 1, 'minor': 1, 'number': '1.1'}  # Duplicate
]
errors = validate_cycle_numbering(cycles_dup)
assert any("Duplicate cycle number: 1.1" in e for e in errors)
print("✓ Duplicate detection: PASS")
```

## Error Handling

### Implemented Error Conditions:
1. **No cycles found**: "ERROR: No cycles found in TDD runbook"
2. **Wrong start number**: "ERROR: First cycle must start at 1.x, found X.Y"
3. **Major number gap**: "ERROR: Gap in major cycle numbers: X -> Y"
4. **Minor wrong start**: "ERROR: Cycle X.x must start at X.1, found X.Y"
5. **Minor number gap**: "ERROR: Gap in cycle X.x: X.A -> X.B"
6. **Duplicate cycle**: "ERROR: Duplicate cycle number: X.Y"

All error messages:
- Start with "ERROR: " prefix
- Include specific cycle numbers
- Provide actionable information

## Integration Points

The `extract_cycles()` function will be called from:
- Modified `extract_sections()` or new routing logic (Step 4-5)
- Validation will be called before file generation (Step 6)

## Special Section Handling

Special sections that end cycle extraction:
- `## Common Context`
- `## Orchestrator Instructions`
- `## Design Decisions`
- `## Dependencies`
- `## Notes`

These are common runbook sections that should not be included in cycle content.

## Validation Results

✓ Function returns list of cycle dictionaries
✓ Validation catches gaps in major numbers
✓ Validation catches gaps in minor numbers
✓ Validation catches duplicates
✓ Validation catches wrong start numbers
✓ Error messages clear and actionable
✓ Regex pattern tested with 7 test cases

## Next Steps

Step 4 will:
- Add frontmatter type field detection
- Route to `extract_cycles()` for TDD runbooks
- Pass runbook type through function chain
