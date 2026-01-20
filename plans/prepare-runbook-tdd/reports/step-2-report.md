# Step 2 Report: Design Cycle Detection and Parsing Logic

## Cycle Detection Regex

### Pattern
```python
cycle_pattern = r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'
```

### Capture Groups
- Group 1: Major cycle number (X in X.Y)
- Group 2: Minor cycle number (Y in X.Y)
- Group 3: Cycle name/title

### Test Cases
```python
# Valid matches
"## Cycle 1.1: User can authenticate" → (1, 1, "User can authenticate")
"## Cycle 2.3: System validates token" → (2, 3, "System validates token")
"## Cycle 10.15: Complex workflow" → (10, 15, "Complex workflow")

# Non-matches (correctly rejected)
"## Step 1: Some step" → No match
"## Cycle 1: Missing minor" → No match
"## Cycle 1.1.2: Too many numbers" → No match
"## Cycle A.1: Non-numeric" → No match
```

### Differentiation from Step Pattern
- Step pattern: `r'^## Step\s+([\d.]+):\s*(.*)'` (allows X or X.Y or X.Y.Z)
- Cycle pattern: `r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'` (requires exactly X.Y)
- No ambiguity: "Cycle" keyword makes patterns mutually exclusive

## Conditional Extraction Logic

### Control Flow
```python
def extract_sections(content, runbook_type='general'):
    """Extract sections based on runbook type."""
    if runbook_type == 'tdd':
        # Extract cycles instead of steps
        return extract_cycles_and_context(content)
    else:
        # Existing step extraction logic
        return extract_steps_and_context(content)
```

### Alternative: Single Function with Conditional Pattern
```python
def extract_sections(content, runbook_type='general'):
    """Extract sections based on runbook type."""
    if runbook_type == 'tdd':
        section_pattern = r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'
    else:
        section_pattern = r'^## Step\s+([\d.]+):\s*(.*)'

    # Shared parsing logic with pattern parameter
    sections = parse_with_pattern(content, section_pattern, runbook_type)
    return sections
```

**Decision**: Use separate `extract_cycles()` function for clarity and maintainability.

## Cycle Numbering Validation

### Algorithm: Sequential Major Numbers
```python
def validate_major_numbers(cycles):
    """Check major numbers are sequential starting from 1."""
    major_nums = sorted(set(c['major'] for c in cycles))

    if not major_nums:
        return ["No cycles found"]

    if major_nums[0] != 1:
        return [f"ERROR: First cycle must start at 1.x, found {major_nums[0]}.x"]

    errors = []
    for i in range(len(major_nums) - 1):
        if major_nums[i+1] != major_nums[i] + 1:
            errors.append(f"ERROR: Gap in major cycle numbers: {major_nums[i]} -> {major_nums[i+1]}")

    return errors
```

### Algorithm: Sequential Minor Numbers Within Major
```python
def validate_minor_numbers(cycles):
    """Check minor numbers are sequential within each major cycle."""
    # Group by major number
    by_major = {}
    for cycle in cycles:
        major = cycle['major']
        if major not in by_major:
            by_major[major] = []
        by_major[major].append(cycle['minor'])

    errors = []
    for major, minors in by_major.items():
        sorted_minors = sorted(minors)

        if sorted_minors[0] != 1:
            errors.append(f"ERROR: Cycle {major}.x must start at {major}.1, found {major}.{sorted_minors[0]}")

        for i in range(len(sorted_minors) - 1):
            if sorted_minors[i+1] != sorted_minors[i] + 1:
                errors.append(f"ERROR: Gap in cycle {major}.x: {major}.{sorted_minors[i]} -> {major}.{sorted_minors[i+1]}")

    return errors
```

### Algorithm: Duplicate Detection
```python
def validate_no_duplicates(cycles):
    """Check for duplicate cycle numbers."""
    seen = set()
    errors = []

    for cycle in cycles:
        cycle_id = f"{cycle['major']}.{cycle['minor']}"
        if cycle_id in seen:
            errors.append(f"ERROR: Duplicate cycle number: {cycle_id}")
        seen.add(cycle_id)

    return errors
```

### Combined Validation
```python
def validate_cycle_numbering(cycles):
    """Run all numbering validations."""
    errors = []
    errors.extend(validate_major_numbers(cycles))
    errors.extend(validate_minor_numbers(cycles))
    errors.extend(validate_no_duplicates(cycles))
    return errors
```

## Cycle Content Extraction

### Section Parsing Strategy
```python
def extract_cycles(content):
    """Extract cycles from TDD runbook."""
    cycle_pattern = r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'
    lines = content.split('\n')

    cycles = []
    current_cycle = None
    current_content = []

    for i, line in enumerate(lines):
        # Check for cycle header
        match = re.match(cycle_pattern, line)
        if match:
            # Save previous cycle
            if current_cycle is not None:
                current_cycle['content'] = '\n'.join(current_content).strip()
                cycles.append(current_cycle)

            # Start new cycle
            major = int(match.group(1))
            minor = int(match.group(2))
            title = match.group(3).strip()

            current_cycle = {
                'major': major,
                'minor': minor,
                'number': f"{major}.{minor}",
                'title': title
            }
            current_content = [line]

        # Check for next H2 (stop condition for current cycle)
        elif line.startswith('## ') and current_cycle is not None:
            # Check if it's a special section (Common Context, etc.)
            if line in ['## Common Context', '## Orchestrator Instructions']:
                # End current cycle, let main parser handle special sections
                current_cycle['content'] = '\n'.join(current_content).strip()
                cycles.append(current_cycle)
                current_cycle = None
                current_content = []
            else:
                # Not a cycle or special section, skip
                pass

        # Accumulate content
        elif current_cycle is not None:
            current_content.append(line)

    # Save final cycle
    if current_cycle is not None:
        current_cycle['content'] = '\n'.join(current_content).strip()
        cycles.append(current_cycle)

    return cycles
```

### Subsection Preservation
- Full cycle content captured (including RED/GREEN/REFACTOR subsections)
- H3 headers preserved in content
- Stop conditions included
- Markdown formatting maintained

## Cycle Data Structure

### Structure Definition
```python
cycle = {
    'major': int,        # Major cycle number (X in X.Y)
    'minor': int,        # Minor cycle number (Y in X.Y)
    'number': str,       # Full cycle number "X.Y"
    'title': str,        # Cycle name/title
    'content': str       # Full cycle markdown content (including header)
}
```

### Example
```python
{
    'major': 1,
    'minor': 2,
    'number': '1.2',
    'title': 'User can authenticate',
    'content': '''## Cycle 1.2: User can authenticate

**Dependencies**: Cycle 1.1 complete

**Objective**: Implement authentication endpoint

### RED Phase
Write failing test for authentication...

### GREEN Phase
Implement authentication logic...

### REFACTOR Phase
Extract validation logic...

**Stop Conditions**:
- Tests pass
- No code duplication
'''
}
```

## Error Messages

### Validation Failures
```python
ERROR_MESSAGES = {
    'no_cycles': "ERROR: No cycles found in TDD runbook",
    'first_cycle': "ERROR: First cycle must start at 1.1, found {major}.{minor}",
    'major_gap': "ERROR: Gap in major cycle numbers: {prev} -> {curr}",
    'minor_gap': "ERROR: Gap in cycle {major}.x: {major}.{prev} -> {major}.{curr}",
    'minor_start': "ERROR: Cycle {major}.x must start at {major}.1, found {major}.{minor}",
    'duplicate': "ERROR: Duplicate cycle number: {number}",
    'malformed': "ERROR: Malformed cycle header at line {line_num}: {line}",
}
```

### Warnings
```python
WARNING_MESSAGES = {
    'missing_type': "WARNING: Cycle headers detected but missing 'type: tdd' in frontmatter",
    'unknown_type': "WARNING: Unknown runbook type '{type}', defaulting to 'general'",
}
```

## Design Decisions

### Why Separate extract_cycles() Function
- **Clarity**: Clear separation between step and cycle logic
- **Maintainability**: Easier to modify cycle-specific logic without affecting steps
- **Testing**: Can test cycle extraction independently
- **Alternative rejected**: Single function with complex conditionals would be harder to understand

### Why Strict Numbering Validation
- **Consistency**: Ensures predictable file naming and ordering
- **Error detection**: Catches copy-paste errors or missing cycles
- **UX**: Clear error messages help users fix issues quickly
- **Alternative rejected**: Flexible numbering could lead to confusion

### Why Preserve Full Cycle Content
- **Completeness**: All cycle information available in step file
- **Context**: Subsections provide critical context for execution
- **Reusability**: Can extract specific phases if needed later
- **Alternative rejected**: Extracting only specific subsections would require complex parsing

## Edge Cases Handled

1. **Empty runbook**: No cycles found → clear error
2. **Non-sequential numbering**: Gap detection → specific error with numbers
3. **Duplicate cycles**: Duplicate detection → error with cycle number
4. **Missing minor start**: First minor must be .1 → error
5. **Missing major start**: First major must be 1 → error
6. **Mixed step/cycle format**: Patterns mutually exclusive → no ambiguity
7. **Common Context section**: Stop cycle extraction at special sections → correct boundary detection

## Validation

### Regex Testing
```python
import re

cycle_pattern = r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'

# Valid cases
assert re.match(cycle_pattern, "## Cycle 1.1: Test").groups() == ('1', '1', 'Test')
assert re.match(cycle_pattern, "## Cycle 10.5: Another").groups() == ('10', '5', 'Another')

# Invalid cases
assert re.match(cycle_pattern, "## Step 1: Test") is None
assert re.match(cycle_pattern, "## Cycle 1: Missing minor") is None
assert re.match(cycle_pattern, "## Cycle A.1: Non-numeric") is None

print("✓ All regex tests passed")
```

### Validation Algorithm Testing (Pseudocode)
```python
# Test sequential major numbers
cycles = [
    {'major': 1, 'minor': 1},
    {'major': 2, 'minor': 1},
    {'major': 3, 'minor': 1}
]
assert validate_major_numbers(cycles) == []  # No errors

cycles_gap = [
    {'major': 1, 'minor': 1},
    {'major': 3, 'minor': 1}  # Missing major 2
]
assert "Gap in major cycle numbers: 1 -> 3" in validate_major_numbers(cycles_gap)[0]

# Test sequential minor numbers
cycles = [
    {'major': 1, 'minor': 1},
    {'major': 1, 'minor': 2},
    {'major': 1, 'minor': 3}
]
assert validate_minor_numbers(cycles) == []  # No errors

cycles_gap = [
    {'major': 1, 'minor': 1},
    {'major': 1, 'minor': 3}  # Missing 1.2
]
assert "Gap in cycle 1.x: 1.1 -> 1.3" in validate_minor_numbers(cycles_gap)[0]

print("✓ All validation tests passed")
```

## Conclusion

Complete design specification for cycle detection and parsing:
- ✓ Regex pattern tested with examples
- ✓ Validation algorithms with pseudocode
- ✓ Example data structures
- ✓ Error messages defined
- ✓ Edge cases identified
- ✓ Design decisions documented

Ready for implementation in Step 3.
