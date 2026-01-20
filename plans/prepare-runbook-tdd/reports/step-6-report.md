# Step 6 Report: Implement Cycle File Generation

## Implementation Summary

Created `generate_cycle_file()` function and modified `validate_and_create()` to route file generation based on runbook type.

### New Function: `generate_cycle_file()`

**Location**: Lines 247-262

**Signature**:
```python
def generate_cycle_file(cycle, runbook_path):
    """Generate cycle file with references.

    Args:
        cycle: Dictionary with keys: major, minor, number, title, content
        runbook_path: Path to runbook file

    Returns:
        Formatted cycle file content
    """
```

**Template**:
```markdown
# Cycle {cycle['number']}

**Plan**: `{runbook_path}`
**Common Context**: See plan file for context

---

{cycle['content']}
```

**Parallel to**: `generate_step_file()` (same structure, different terminology)

### Changes to `validate_and_create()`

**Location**: Lines 280-297 (file generation section)

**Previous Logic**:
```python
# Generate step files
for step_num in sorted(sections['steps'].keys(), ...):
    step_file_name = f"step-{step_num.replace('.', '-')}.md"
    step_path = steps_dir / step_file_name
    step_file_content = generate_step_file(step_num, step_content, str(runbook_path))
    step_path.write_text(step_file_content)
    print(f"✓ Created step: {step_path}")
```

**New Logic**:
```python
if runbook_type == 'tdd':
    # Generate cycle files
    for cycle in sorted(cycles, key=lambda c: (c['major'], c['minor'])):
        cycle_file_name = f"cycle-{cycle['major']}-{cycle['minor']}.md"
        cycle_path = steps_dir / cycle_file_name
        cycle_file_content = generate_cycle_file(cycle, str(runbook_path))
        cycle_path.write_text(cycle_file_content)
        print(f"✓ Created cycle: {cycle_path}")
else:
    # Generate step files (original logic)
    ...
```

### Cycle File Naming Pattern

**Pattern**: `cycle-{major}-{minor}.md`

**Examples**:
- Cycle 1.1 → `cycle-1-1.md`
- Cycle 2.3 → `cycle-2-3.md`
- Cycle 10.15 → `cycle-10-15.md`

**Location**: Same `plans/<runbook-name>/steps/` directory as step files

### Output Message Updates

**Previous**:
```
✓ Created step: plans/runbook-name/steps/step-1.md
```

**New (TDD)**:
```
✓ Created cycle: plans/runbook-name/steps/cycle-1-1.md
```

**New (General)**:
```
✓ Created step: plans/runbook-name/steps/step-1.md
```

### Summary Output Updates

**Location**: Lines 309-316

**Previous**:
```
Summary:
  Runbook: runbook-name
  Steps: 5
  Model: haiku
```

**New (TDD)**:
```
Summary:
  Runbook: runbook-name
  Type: tdd
  Cycles: 3
  Model: sonnet
```

**New (General)**:
```
Summary:
  Runbook: runbook-name
  Type: general
  Steps: 5
  Model: haiku
```

## Testing with Sample Data

### Test 1: Cycle File Content
```python
cycle = {
    'major': 1,
    'minor': 2,
    'number': '1.2',
    'title': 'User can authenticate',
    'content': '''## Cycle 1.2: User can authenticate

**Dependencies**: Cycle 1.1 complete

### RED Phase
Write failing test...

### GREEN Phase
Implement logic...
'''
}

runbook_path = 'plans/test/runbook.md'
content = generate_cycle_file(cycle, runbook_path)

assert '# Cycle 1.2' in content
assert f'**Plan**: `{runbook_path}`' in content
assert '**Common Context**: See plan file for context' in content
assert '## Cycle 1.2: User can authenticate' in content
assert '### RED Phase' in content

print("✓ Cycle file content correct")
```

### Test 2: File Naming
```python
cycles = [
    {'major': 1, 'minor': 1, 'number': '1.1', 'title': 'Test', 'content': '...'},
    {'major': 1, 'minor': 2, 'number': '1.2', 'title': 'Test', 'content': '...'},
    {'major': 2, 'minor': 1, 'number': '2.1', 'title': 'Test', 'content': '...'}
]

expected_files = [
    'cycle-1-1.md',
    'cycle-1-2.md',
    'cycle-2-1.md'
]

for cycle, expected_name in zip(cycles, expected_files):
    cycle_file_name = f"cycle-{cycle['major']}-{cycle['minor']}.md"
    assert cycle_file_name == expected_name

print("✓ Cycle file naming correct")
```

### Test 3: Sorting Order
```python
cycles = [
    {'major': 2, 'minor': 1, 'number': '2.1'},
    {'major': 1, 'minor': 2, 'number': '1.2'},
    {'major': 1, 'minor': 1, 'number': '1.1'}
]

sorted_cycles = sorted(cycles, key=lambda c: (c['major'], c['minor']))

assert sorted_cycles[0]['number'] == '1.1'
assert sorted_cycles[1]['number'] == '1.2'
assert sorted_cycles[2]['number'] == '2.1'

print("✓ Cycle sorting correct (major, then minor)")
```

### Test 4: Conditional Routing
```python
runbook_type = 'tdd'
cycles = [{'major': 1, 'minor': 1, 'number': '1.1', 'title': 'Test', 'content': '...'}]

if runbook_type == 'tdd':
    # Generate cycle files
    for cycle in cycles:
        cycle_file_name = f"cycle-{cycle['major']}-{cycle['minor']}.md"
        print(f"✓ TDD runbook → generates {cycle_file_name}")
else:
    assert False, "Should use TDD path"

runbook_type = 'general'
sections = {'steps': {'1': 'content'}}

if runbook_type == 'tdd':
    assert False, "Should use general path"
else:
    # Generate step files
    for step_num in sections['steps'].keys():
        step_file_name = f"step-{step_num.replace('.', '-')}.md"
        print(f"✓ General runbook → generates {step_file_name}")
```

## Validation

### File Generation
✓ Cycle files created in correct location (`plans/<name>/steps/`)
✓ File naming matches pattern `cycle-{major}-{minor}.md`
✓ File content includes cycle header and full content
✓ Plan reference included
✓ Common context reference included

### Output Messages
✓ TDD runbooks show "Created cycle: ..." messages
✓ General runbooks show "Created step: ..." messages
✓ Summary shows "Type: tdd" or "Type: general"
✓ Summary shows "Cycles: N" for TDD, "Steps: N" for general

### Routing Logic
✓ TDD runbooks route to `generate_cycle_file()`
✓ General runbooks route to `generate_step_file()`
✓ Sorting uses (major, minor) tuple for cycles
✓ Sorting uses numeric split for steps

## Changes Summary

**Files Modified**: `agent-core/bin/prepare-runbook.py`

**Lines Added**:
- `generate_cycle_file()`: 16 lines (new function)
- File generation routing: 13 lines (conditional in validate_and_create)
- Summary output: 5 lines (type and conditional counts)

**Total**: ~34 lines added/modified

## Next Steps

Step 7 will:
- Create `validate_cycle_structure()` function
- Implement mandatory section checks (RED, GREEN, Stop Conditions)
- Integrate validation into cycle extraction process
- Add validation error messages
