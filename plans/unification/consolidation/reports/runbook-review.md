# TDD Runbook Review: Composition API

**Date**: 2026-01-24
**Runbook**: plans/unification/consolidation/runbook.md
**Design**: plans/unification/consolidation/design/compose-api.md
**Reviewer**: Sonnet 4.5

---

## Executive Summary

**Status**: **NEEDS REVISION** - Several critical issues identified

**Overall Assessment**:

The runbook demonstrates solid TDD structure and reasonable coverage, but has several issues that will break RED/GREEN discipline and create confusion during execution:

- **Critical**: Multiple cycles (2.2, 3.2, 3.3, 3.4, 4.2, 4.3) will likely pass immediately (GREEN without RED)
- **Major**: CLI command naming inconsistency will cause import errors
- **Major**: Exit code mapping doesn't match design specification
- **Moderate**: Missing test coverage for edge cases and error scenarios
- **Minor**: Some implementation hints would improve executability

**Recommendation**: Revise runbook to fix RED/GREEN sequencing and CLI naming issues before execution.

---

## Detailed Findings

### 1. Completeness Review

**Question**: Are all features from the design document covered in cycles?

#### ✅ Covered Features

**Core utilities (fully covered)**:
- `get_header_level()` - Cycle 1.1
- `increase_header_levels()` - Cycle 1.2
- `normalize_newlines()` - Cycle 1.3
- `format_separator()` - Cycle 1.3

**Composition function (well covered)**:
- Basic composition - Cycle 3.1
- Title injection - Cycle 3.2
- Header adjustment - Cycle 3.3
- Separator styles - Cycle 3.2
- Validation modes - Cycle 3.4

**Configuration loading (covered)**:
- YAML parsing - Cycle 2.1
- Error handling - Cycle 2.2

**CLI interface (covered)**:
- Basic command - Cycle 4.1
- Options and overrides - Cycle 4.2
- Error handling and exit codes - Cycle 4.3

#### ❌ Missing or Incomplete Coverage

**Configuration features**:
1. **YAML anchors with sources** - Cycle 2.1 line 451-467 has ONE test for YAML anchors, but it's malformed:
   ```python
   fragments:
     - *core/file1.md  # This is INVALID YAML
     - *core/file2.md
   ```
   Should be:
   ```python
   fragments:
     - agent-core/fragments/file1.md  # After anchor expansion
   ```
   The test won't work as written because `*core` is an anchor reference, not a string prefix.

2. **Path resolution** - No tests for relative vs absolute paths in config
3. **Config with empty sources dict** - Only tests with sources present
4. **Fragment order preservation** - No explicit test verifying order is maintained

**Composition edge cases**:
1. **Empty fragment files** - No test for composing empty markdown files
2. **Fragments without trailing newlines** - normalize_newlines tested standalone but not in compose()
3. **Invalid separator style** - format_separator() will raise ValueError but not tested
4. **Output to existing file (overwrite)** - No explicit test

**CLI edge cases**:
1. **Invalid YAML syntax** - Mentioned in design (exit code 1) but not in CLI tests
2. **Output to read-only directory** - PermissionError → exit code 3, not tested
3. **Fragment error in strict mode** - Test at line 1363-1376 expects exit code 2, but this conflicts with implementation at line 1192-1194 which uses exit code 4 for FileNotFoundError

**Error handling gaps**:
1. **Multiple missing fragments** - Design says "list all missing files" but no test validates this
2. **Warn mode summary** - Design says print "Composed X of Y fragments" but test only checks for WARNING in stderr

**Recommendation**:
- Fix YAML anchor test or remove it (YAML anchors work automatically, no special testing needed)
- Add tests for empty fragments and file overwriting
- Clarify exit code mapping (design vs implementation conflict)
- Consider adding order preservation test

---

### 2. Executability Review

**Question**: Are instructions clear, actionable, and unambiguous for haiku agent?

#### ✅ Strong Executability

**Clear structure**:
- Each cycle has RED/GREEN phases explicitly labeled
- Expected failures clearly stated
- Stop conditions well-defined
- File paths specified absolutely in Common Context

**Good batching strategy**:
- Tests grouped in coherent 3-5 test batches
- Avoids excessive granularity while maintaining RED/GREEN

**Explicit verification steps**:
- Each cycle specifies which pytest command to run
- Expected outcomes stated clearly

#### ⚠️ Executability Issues

**Issue 1: CLI command naming inconsistency (CRITICAL)**

**Location**: Cycle 4.1, line 1164

**Problem**: Function named `compose_cmd` but design shows `compose_command`. The decorator `@main.command()` will register it as "compose_cmd" by default, not "compose".

**Evidence**:
- Line 1164: `def compose_cmd(config_file, output, validate, verbose, dry_run):`
- Line 1106: `result = runner.invoke(main, ['compose', str(config)])` (test expects 'compose')

**Impact**: All CLI tests will fail with "Error: No such command 'compose'"

**Fix**: Either:
```python
# Option 1: Rename function
def compose(config_file, ...):

# Option 2: Explicit name
@main.command(name='compose')
def compose_cmd(...):
```

**Issue 2: Exit code mapping inconsistency (MAJOR)**

**Location**: Cycle 4.3, line 1363-1386

**Problem**: Exit codes in implementation don't match design specification.

**Design specification** (line 546-551):
- 0 = Success
- 1 = Configuration error (invalid YAML, missing required fields)
- 2 = Fragment error (missing file in strict mode)
- 3 = Output error (cannot write file)
- 4 = Argument error (invalid options)

**Implementation in Cycle 4.1** (line 1192-1200):
```python
except FileNotFoundError as e:
    click.echo(f"Error: {e}", err=True)
    raise SystemExit(4)  # ← Should be 2!
except ValueError as e:
    click.echo(f"Configuration error: {e}", err=True)
    raise SystemExit(1)  # ← Correct
except Exception as e:
    click.echo(f"Error: {e}", err=True)
    raise SystemExit(3)  # ← Should be 2 for fragment errors
```

**Test expectation** (line 1376):
```python
assert result.exit_code == 2  # Expects 2 for fragment error
```

**Impact**: Test at line 1363-1376 will fail because implementation uses exit code 4 for FileNotFoundError.

**Fix**: Update implementation in Cycle 4.1:
```python
except FileNotFoundError as e:
    click.echo(f"Error: {e}", err=True)
    raise SystemExit(2)  # Fragment error
except ValueError as e:
    click.echo(f"Configuration error: {e}", err=True)
    raise SystemExit(1)  # Config error
except (PermissionError, IOError) as e:
    click.echo(f"Output error: {e}", err=True)
    raise SystemExit(3)  # Output error
```

**Issue 3: Test for YAML anchor expansion won't work (MODERATE)**

**Location**: Cycle 2.1, line 451-467

**Problem**: The test uses invalid YAML syntax for anchor references.

**Current code**:
```python
config_file.write_text("""
sources:
  core: &core agent-core/fragments

fragments:
  - *core/file1.md  # Invalid: can't concatenate anchor with /file1.md
  - *core/file2.md
output: result.md
""")

config = load_config(config_file)
assert 'agent-core/fragments/file1.md' in config['fragments'][0]
```

**Why it's invalid**: `*core/file1.md` is not valid YAML. You can't use `/` directly after an anchor reference.

**Valid YAML anchor usage**:
```yaml
sources:
  core: &core agent-core/fragments

fragments:
  - !join [*core, "/file1.md"]  # Need custom YAML tag (complex)
  # OR just use the paths directly:
  - agent-core/fragments/file1.md
  - agent-core/fragments/file2.md
```

**Better approach**: Remove this test. YAML anchors work automatically via PyYAML, no special testing needed. If you want to test anchors, test them properly:

```python
config_file.write_text("""
base_path: &base agent-core/fragments

fragments:
  - agent-core/fragments/file1.md
  - agent-core/fragments/file2.md

# Use anchor in a different field to verify YAML parsing works
source_dir: *base
output: result.md
""")

config = load_config(config_file)
assert config['source_dir'] == 'agent-core/fragments'
```

**Recommendation**: Remove test_load_config_with_sources_anchors or replace with valid YAML anchor test.

**Issue 4: Import organization unclear**

**Location**: Multiple cycles add imports incrementally

**Problem**: Tests in Cycle 2.2 add `import pytest` and `import yaml` (line 556-557) but it's unclear if these should be at top of file or in specific test functions.

**Recommendation**: Add to Common Context that all imports go at top of test file:
```python
# tests/test_compose.py
import pytest
import yaml
from pathlib import Path
from claudeutils.compose import (
    compose, load_config, get_header_level,
    increase_header_levels, normalize_newlines, format_separator
)
```

#### ✅ Good Executability Patterns

1. **Explicit file operations**: Uses Read/Write/Edit tools (line 56-59)
2. **Clear test structure**: Each test has descriptive docstring
3. **Verification commands**: Explicit pytest commands with -v flag
4. **Stop conditions**: Well-defined conditions for stopping execution

---

### 3. Context Sufficiency Review

**Question**: Does each cycle have adequate information for isolated execution?

#### ✅ Strong Context Provision

**Common Context section is excellent** (lines 24-63):
- Key design decisions listed
- TDD protocol clearly stated
- Batching strategy explained
- Project paths specified
- Conventions documented
- Error codes defined

**Each cycle includes**:
- Objective statement
- Script evaluation note
- Execution model
- Expected failure message
- Why it fails explanation
- Stop conditions
- Report path

#### ⚠️ Context Gaps

**Gap 1: Missing existing CLI structure information**

**Location**: Cycle 4.1

**Problem**: Instructions say "Add compose command to CLI" but don't specify:
- What does `main` look like? Is it a Click group or command?
- Where in the file should compose_cmd be added?
- Are there existing imports that need to be preserved?

**Recommendation**: Add to Common Context:
```
CLI structure (src/claudeutils/cli.py):
- `main` is a Click group decorated with @click.group()
- Add new commands with @main.command() decorator
- Existing imports: (list them)
```

**Gap 2: Unclear test file organization**

**Problem**: Multiple test files (test_compose.py, test_cli_compose.py) but relationship unclear.

**Recommendation**: Clarify in Common Context:
```
Test organization:
- tests/test_compose.py: Unit tests for compose module (Cycles 1-3)
- tests/test_cli_compose.py: CLI integration tests (Cycles 4.x)
- Both files independent, can be run separately
```

**Gap 3: Missing pyproject.toml dependency context**

**Location**: Cycle 4.1 assumes dependencies exist

**Problem**: Line 22 says "Prerequisites: PyYAML>=6.0, click>=8.0.0 dependencies added to pyproject.toml" but doesn't specify where in pyproject.toml or what the section looks like.

**Recommendation**: Either add these in a Cycle 0 (dependency setup) or clarify that they're already present.

---

### 4. Test Sequencing Review (CRITICAL SECTION)

**Question**: Will new tests RED before GREEN implementation?

#### ❌ RED/GREEN Violations (CRITICAL)

**Violation 1: Cycle 2.2 - Error handling tests will pass immediately**

**Location**: Cycle 2.2, lines 542-618

**Problem**: Cycle 2.1 already implements error handling (lines 508-526):
```python
if not config_path.exists():
    raise FileNotFoundError(...)
try:
    config = yaml.safe_load(f)
except yaml.YAMLError as e:
    raise yaml.YAMLError(...)
if 'fragments' not in config:
    raise ValueError("Missing required field: fragments")
if 'output' not in config:
    raise ValueError("Missing required field: output")
```

**Impact**: All tests in Cycle 2.2 will pass immediately on first run (GREEN without RED).

**Evidence**: Line 607 even says:
> **GREEN Phase:**
>
> **Implementation**: Error handling already added in Cycle 2.1, tests should pass

**This is a RED/GREEN violation**: Tests should fail first, then pass after implementation.

**Fix**: Move error handling from Cycle 2.1 to Cycle 2.2. Cycle 2.1 should only implement happy path:
```python
# Cycle 2.1 (minimal implementation)
def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config
```

Then Cycle 2.2 adds validation:
```python
# Cycle 2.2 (add error handling)
def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(...)
    # ... rest of validation
```

**Violation 2: Cycle 3.2 - Title and separator tests will pass immediately**

**Location**: Cycle 3.2, lines 792-885

**Problem**: Cycle 3.1 implementation (lines 710-778) already includes:
- Title handling: `if title: out.write(f"# {title}\n\n")`
- Separator handling: `sep = format_separator(separator)`

**Impact**: Tests will pass on first run (no RED phase).

**Evidence**: Line 873 says:
> **Verify RED**: pytest tests/test_compose.py::test_compose_with_title -v
> - Should pass (implementation already supports this)

**Fix**: Split Cycle 3.1 into basic composition (no title, no separator options) and Cycle 3.2 adds features:

```python
# Cycle 3.1 (minimal - no title, hardcoded separator)
def compose(fragments, output, ...):
    # No title parameter
    # Hardcoded separator = "\n---\n\n"

# Cycle 3.2 (add title and separator)
def compose(fragments, output, title=None, separator="---", ...):
    if title:
        out.write(f"# {title}\n\n")
    sep = format_separator(separator)
```

**Violation 3: Cycle 3.3 - Header adjustment tests will pass immediately**

**Location**: Cycle 3.3, lines 889-967

**Problem**: Cycle 3.1 already implements header adjustment (line 766-767):
```python
if adjust_headers:
    content = increase_header_levels(content, 1)
```

**Impact**: All tests pass on first run.

**Evidence**: Line 950 says:
> **Verify RED**: pytest tests/test_compose.py::test_compose_adjust_headers -v
> - Tests should pass (feature implemented in 3.1)

**Fix**: Remove adjust_headers from Cycle 3.1, add in Cycle 3.3.

**Violation 4: Cycle 3.4 - Validation mode tests will pass immediately**

**Location**: Cycle 3.4, lines 971-1065

**Problem**: Cycle 3.1 already implements both strict and warn modes (lines 739-760).

**Impact**: All tests pass on first run.

**Fix**: Cycle 3.1 should only implement strict mode. Cycle 3.4 adds warn mode.

**Violation 5: Cycle 4.2 - CLI options will pass immediately**

**Location**: Cycle 4.2, lines 1215-1333

**Problem**: Cycle 4.1 already implements all options (lines 1158-1162):
```python
@click.option('--output', '-o', ...)
@click.option('--validate', '-v', ...)
@click.option('--verbose', ...)
@click.option('--dry-run', ...)
```

**Impact**: Tests pass on first run.

**Fix**: Cycle 4.1 should implement basic command with config file only. Cycle 4.2 adds options.

**Violation 6: Cycle 4.3 - Error handling tests will pass immediately**

**Location**: Cycle 4.3, lines 1336-1423

**Problem**: Cycle 4.1 already implements error handling (lines 1192-1200).

**Impact**: Tests pass on first run (except for exit code bug).

**Fix**: Cycle 4.1 should have no error handling (let exceptions bubble). Cycle 4.3 adds try/except and exit codes.

#### Summary of RED/GREEN Violations

**Total cycles with violations**: 6 out of 11 (55%)

**Affected cycles**:
- Cycle 2.2: Error handling
- Cycle 3.2: Title and separator
- Cycle 3.3: Header adjustment
- Cycle 3.4: Validation modes
- Cycle 4.2: CLI options
- Cycle 4.3: CLI error handling

**Pattern**: Cycles 3.1 and 4.1 implement "too much" functionality, causing later cycles to test features that already exist.

**Root cause**: Runbook author anticipated full implementation in early cycles rather than building incrementally.

---

### 5. Implementation Hints Review

**Question**: Are there cycles where implementation sequencing is critical for RED/GREEN?

#### 🔧 Recommended Implementation Hints

**Hint 1: Cycle 3.1 - File operations sequencing**

**Location**: Cycle 3.1, compose() implementation

**Issue**: Multiple file operations need careful sequencing to ensure proper RED/GREEN.

**Add this hint**:
```
IMPLEMENTATION SEQUENCING HINT:

To ensure proper RED phase, implement compose() in this exact order:

1. First, make test_compose_single_fragment pass:
   - Path conversion
   - Read fragment
   - Write to output (no transformations)

2. Then make test_compose_multiple_fragments_with_separator pass:
   - Add separator logic (hardcoded "\n---\n\n")

3. Then make test_compose_creates_output_directory pass:
   - Add output_path.parent.mkdir(parents=True, exist_ok=True)

4. Finally make test_compose_accepts_string_paths pass:
   - Already works from step 1 if path conversion correct

DO NOT implement title, adjust_headers, or validate_mode parameters in this cycle.
```

**Hint 2: Cycle 2.1 - Minimal implementation**

**Add this hint**:
```
IMPLEMENTATION SEQUENCING HINT:

Implement ONLY the happy path in this cycle:
- Read YAML file
- Parse with yaml.safe_load()
- Return dict

DO NOT add:
- File existence checking
- YAML error handling
- Field validation

These are added in Cycle 2.2.
```

**Hint 3: Cycle 4.1 - CLI minimal version**

**Add this hint**:
```
IMPLEMENTATION SEQUENCING HINT:

Implement minimal CLI command:
- Accept CONFIG_FILE argument only
- Load config with load_config()
- Call compose() with config values
- No error handling (let exceptions bubble up)
- No --output, --validate, --verbose, --dry-run options

Options are added in Cycle 4.2.
Error handling is added in Cycle 4.3.
```

**Hint 4: Cycle 1.2 - Regex pattern**

**Location**: Cycle 1.2, increase_header_levels()

**Issue**: Regex pattern is tricky, easy to get wrong.

**Add this hint**:
```
IMPLEMENTATION HINT:

The regex pattern must match:
- Line start: ^
- One or more # chars: (#{1,})
- Single space: \s
- MULTILINE flag required

Replacement adds '#' * levels to captured group:
- r'\1' (captured hashes) + '#' * levels + ' '

Common mistake: Forgetting MULTILINE flag causes only first header to match.
```

---

## Specific Recommendations

### Immediate Actions Required

**1. Fix RED/GREEN sequencing (CRITICAL)**

Restructure implementation to ensure tests fail before passing:

**Cycle 2.1**: Remove all error handling
```python
# MINIMAL IMPLEMENTATION - Happy path only
def load_config(config_path: Path) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config
```

**Cycle 2.2**: Add error handling
```python
# ADD: File existence check, YAML parsing errors, field validation
def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(...)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(...)
    if 'fragments' not in config:
        raise ValueError(...)
    if 'output' not in config:
        raise ValueError(...)
    return config
```

**Cycle 3.1**: Remove title, adjust_headers, separator options, validation modes
```python
# MINIMAL IMPLEMENTATION
def compose(fragments: list, output: Path) -> None:
    output_path = Path(output) if isinstance(output, str) else output
    fragment_paths = [Path(f) if isinstance(f, str) else f for f in fragments]

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as out:
        for i, frag_path in enumerate(fragment_paths):
            content = frag_path.read_text(encoding='utf-8')
            content = normalize_newlines(content)
            out.write(content)

            if i < len(fragment_paths) - 1:
                out.write("\n---\n\n")  # Hardcoded separator
```

**Cycle 3.2**: Add title and separator parameters

**Cycle 3.3**: Add adjust_headers parameter

**Cycle 3.4**: Add validate_mode parameter

**Cycle 4.1**: Remove options and error handling
```python
@main.command(name='compose')  # FIX: explicit name
@click.argument('config_file', type=click.Path(exists=True))
def compose(config_file):  # FIX: rename function or use explicit name
    """Compose markdown from YAML configuration."""
    config_path = Path(config_file)
    config = load_config(config_path)

    fragments = [Path(f) for f in config['fragments']]
    compose(
        fragments=fragments,
        output=Path(config['output']),
    )
```

**Cycle 4.2**: Add options (--output, --validate, --verbose, --dry-run)

**Cycle 4.3**: Add error handling with correct exit codes

**2. Fix CLI command naming (CRITICAL)**

Change line 1164:
```python
# BEFORE
def compose_cmd(config_file, output, validate, verbose, dry_run):

# AFTER (Option 1: rename function)
def compose(config_file, output, validate, verbose, dry_run):

# AFTER (Option 2: explicit name)
@main.command(name='compose')
def compose_cmd(config_file, output, validate, verbose, dry_run):
```

**3. Fix exit code mapping (CRITICAL)**

Update Cycle 4.3 implementation to match design:
```python
except FileNotFoundError as e:
    click.echo(f"Error: {e}", err=True)
    raise SystemExit(2)  # Fragment error (was 4)
except ValueError as e:
    click.echo(f"Configuration error: {e}", err=True)
    raise SystemExit(1)  # Config error (correct)
except (PermissionError, IOError) as e:
    click.echo(f"Output error: {e}", err=True)
    raise SystemExit(3)  # Output error
```

Update Cycle 4.3 test at line 1382:
```python
# Line 1382-1386: This test is checking Click's built-in validation
# Click returns exit code 2 for usage errors when exists=True fails
# This is acceptable - remove or adjust comment
```

**4. Fix or remove YAML anchor test (MODERATE)**

Remove test_load_config_with_sources_anchors (lines 451-467) or replace with valid YAML:
```python
def test_load_config_yaml_anchor_expansion(tmp_path):
    """YAML anchors expand correctly via PyYAML."""
    config_file = tmp_path / "compose.yaml"
    config_file.write_text("""
base_path: &base /path/to/fragments

fragments:
  - /path/to/fragments/file1.md
  - /path/to/fragments/file2.md

output: result.md
verified_base: *base
""")

    config = load_config(config_file)
    assert config['verified_base'] == '/path/to/fragments'
```

### Optional Improvements

**5. Add missing test coverage (OPTIONAL)**

Consider adding tests for:
- Empty fragment files
- Overwriting existing output files
- Invalid separator style → ValueError
- Multiple missing fragments in strict mode
- Warn mode summary message

**6. Add implementation hints (RECOMMENDED)**

Add sequencing hints to:
- Cycle 2.1: "Implement happy path only, no error handling"
- Cycle 3.1: "Minimal compose - no title, options, or validation modes"
- Cycle 4.1: "Basic command only - no options or error handling"

**7. Clarify Common Context (RECOMMENDED)**

Add to Common Context section:
- Existing CLI structure (`main` is a Click group)
- Test file organization (test_compose.py vs test_cli_compose.py)
- Import organization (all imports at top of file)

---

## Risk Assessment

### High Risk Issues (Must Fix)

1. **RED/GREEN violations in 6 cycles** - Will confuse executor, violate TDD discipline
2. **CLI command naming bug** - All CLI tests will fail immediately
3. **Exit code inconsistency** - Test expectations don't match implementation

### Medium Risk Issues (Should Fix)

1. **Invalid YAML anchor test** - Will fail with YAML parsing error
2. **Missing implementation hints** - May lead to incorrect implementation order

### Low Risk Issues (Nice to Fix)

1. **Missing edge case tests** - Reduces coverage but doesn't break execution
2. **Context gaps** - Executor can infer from existing code

---

## Conclusion

The runbook has solid structure and reasonable coverage, but **critical RED/GREEN sequencing issues** will break TDD discipline in over half the cycles. The implementation is too ambitious in early cycles (3.1, 4.1), causing later cycles to test already-implemented features.

**Must fix before execution**:
1. Restructure Cycles 2.1, 3.1, 4.1 to minimal implementations
2. Move features to appropriate later cycles for proper RED/GREEN
3. Fix CLI command naming bug
4. Fix exit code mapping inconsistency
5. Remove or fix invalid YAML anchor test

**Recommended improvements**:
1. Add implementation sequencing hints
2. Clarify Common Context with CLI structure and test organization
3. Consider adding edge case tests

**Estimated revision effort**: 2-3 hours to restructure implementations and fix critical issues.
