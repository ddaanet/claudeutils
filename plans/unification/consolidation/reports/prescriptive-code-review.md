# TDD Runbook Review: Composition API

**Runbook**: plans/unification/consolidation/runbook.md
**Reviewed**: 2026-01-26
**Reviewer**: tdd-plan-reviewer agent

---

## Executive Summary

**Total cycles**: 11
**Violations found**: 7 critical (prescriptive code), 0 warnings
**Overall assessment**: **NEEDS MAJOR REVISION**

**Critical finding**: 7 out of 11 cycles contain prescriptive implementation code in GREEN phases, violating TDD principles. These cycles provide exact function implementations rather than behavior descriptions with hints.

---

## Critical Issues

### Issue 1: Cycle 1.1 - Complete get_header_level() implementation prescribed

**Location**: Lines 117-142
**Severity**: CRITICAL
**Problem**: GREEN phase contains complete function implementation with exact code

**Evidence**:
```python
def get_header_level(line: str) -> int | None:
    """
    Detect markdown header level from a line.

    Args:
        line: Single line of text.

    Returns:
        Header level (1-6) if line is header, None otherwise.
    """
    match = re.match(r'^(#+)\s', line)
    return len(match.group(1)) if match else None
```

**Why this violates TDD**: Agent becomes code copier, not implementer. Tests should drive the discovery of the regex pattern and logic, not scripts prescribing exact solution.

**Recommendation**: Replace with behavior description
```markdown
**GREEN Phase:**

**Implementation**: Minimal get_header_level() to pass tests

**Behavior**:
- Parse line to detect hash marks at start
- Count consecutive hashes (1-6)
- Return count if valid header pattern, None otherwise
- Must handle space after hashes

**Hint**: Use regex to match start-of-line hash pattern. Consider re.match() with pattern group extraction.
```

---

### Issue 2: Cycle 1.2 - Complete increase_header_levels() implementation prescribed

**Location**: Lines 229-252
**Severity**: CRITICAL
**Problem**: GREEN phase provides exact implementation with regex pattern and replacement logic

**Evidence**:
```python
def increase_header_levels(content: str, levels: int = 1) -> str:
    """..."""
    pattern = r'^(#{1,})\s'
    replacement = r'\1' + '#' * levels + ' '
    return re.sub(pattern, replacement, content, flags=re.MULTILINE)
```

**Why this violates TDD**: Prescribes exact regex pattern, replacement string construction, and re.sub() flags. No room for test-driven discovery.

**Recommendation**:
```markdown
**GREEN Phase:**

**Implementation**: Minimal increase_header_levels() to pass tests

**Behavior**:
- Process multi-line markdown content
- Find all header lines (start with #)
- Add specified number of hash marks to each
- Preserve non-header lines unchanged
- Default levels=1

**Hint**: Use regex with MULTILINE flag to process multiple lines. Consider re.sub() for replacement.
```

---

### Issue 3: Cycle 1.3 - Complete utility functions prescribed

**Location**: Lines 326-368
**Severity**: CRITICAL
**Problem**: Both normalize_newlines() and format_separator() fully implemented in GREEN phase

**Evidence**:
```python
def normalize_newlines(content: str) -> str:
    """..."""
    if not content or content.endswith('\n'):
        return content
    return content + '\n'

def format_separator(style: str = "---") -> str:
    """..."""
    if style == "---":
        return "\n---\n\n"
    elif style == "blank":
        return "\n\n"
    elif style == "none":
        return ""
    else:
        raise ValueError(f"Unknown separator style: {style}")
```

**Why this violates TDD**: Complete logic including edge cases, error handling, all branches prescribed upfront.

**Recommendation**:
```markdown
**GREEN Phase:**

**Implementation**: Minimal normalize_newlines() and format_separator() to pass tests

**Behavior**:
- normalize_newlines: Ensure content ends with exactly one newline
- format_separator: Return formatted separator string based on style
- Support styles: "---", "blank", "none"

**Hint**: Simple string operations and conditionals. Tests define expected output formats.
```

---

### Issue 4: Cycle 2.1 - Complete load_config() implementation prescribed

**Location**: Lines 482-507
**Severity**: CRITICAL
**Problem**: Exact YAML loading implementation provided (happy path)

**Evidence**:
```python
def load_config(config_path: Path) -> dict:
    """..."""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config
```

**Why this violates TDD**: Prescribes yaml.safe_load(), file handling pattern, encoding. Agent has no implementation decisions to make.

**Recommendation**:
```markdown
**GREEN Phase:**

**Implementation**: Minimal load_config() for happy path

**Behavior**:
- Read YAML file from config_path
- Parse YAML into Python dict
- Return parsed configuration
- Must pass test assertions (basic structure, optional fields, defaults, anchors)

**Hint**: Use yaml.safe_load() with UTF-8 encoding. No error handling in this cycle.
**Implementation Hint**: Happy path only - no validation, no error handling
```

---

### Issue 5: Cycle 2.2 - Complete error handling implementation prescribed

**Location**: Lines 585-629
**Severity**: CRITICAL
**Problem**: Exact validation and error handling logic prescribed

**Evidence**:
```python
def load_config(config_path: Path) -> dict:
    """..."""
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML: {e}")

    # Validate required fields
    if not config:
        raise ValueError("Empty configuration file")
    if 'fragments' not in config:
        raise ValueError("Missing required field: fragments")
    if 'output' not in config:
        raise ValueError("Missing required field: output")
    if not config['fragments']:
        raise ValueError("fragments list cannot be empty")

    return config
```

**Why this violates TDD**: Complete error handling logic including all validation checks, exception types, error messages. Nothing left for test-driven discovery.

**Recommendation**:
```markdown
**GREEN Phase:**

**Implementation**: Add error handling to load_config()

**Behavior**:
- Raise FileNotFoundError if config file missing
- Raise yaml.YAMLError if YAML malformed
- Raise ValueError if required fields missing (fragments, output)
- Validate fragments list not empty
- Must match test exception patterns

**Hint**: Check file existence before reading. Catch yaml.YAMLError during parsing. Validate dict structure after loading.
**Implementation Hint**: Add file existence check, YAML parsing errors, field validation
```

---

### Issue 6: Cycle 3.1 - Complete compose() implementation prescribed

**Location**: Lines 724-761
**Severity**: CRITICAL
**Problem**: Full compose function implementation with exact logic flow

**Evidence**:
```python
def compose(
    fragments: list[Path] | list[str],
    output: Path | str,
) -> None:
    """..."""
    # Convert to Path objects
    output_path = Path(output) if isinstance(output, str) else output
    fragment_paths = [Path(f) if isinstance(f, str) else f for f in fragments]

    # Create output directory
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Compose fragments
    with open(output_path, 'w', encoding='utf-8') as out:
        for i, frag_path in enumerate(fragment_paths):
            content = frag_path.read_text(encoding='utf-8')
            content = normalize_newlines(content)
            out.write(content)

            # Write separator (except after last fragment)
            if i < len(fragment_paths) - 1:
                out.write("\n---\n\n")  # Hardcoded separator
```

**Why this violates TDD**: Complete implementation including type conversion, directory creation, file I/O, separator logic. Agent becomes transcriber.

**Recommendation**:
```markdown
**GREEN Phase:**

**Implementation**: Minimal compose() for happy path

**Behavior**:
- Accept fragments as list of Path or str
- Write composed output to output path
- Support single fragment (direct copy)
- Support multiple fragments (joined with separator)
- Auto-create output parent directories
- Must pass all 4 tests

**Hint**: Convert strings to Path objects. Use Path.mkdir(parents=True, exist_ok=True) for directories. Hardcode separator "\n---\n\n" for now.
**Implementation Hint**: Minimal compose - no title, no options, hardcoded separator "\n---\n\n"
```

---

### Issue 7: Cycle 4.1 - Complete CLI command implementation prescribed

**Location**: Lines 1213-1272
**Severity**: CRITICAL
**Problem**: Full CLI command with exact click decorators, options, and error handling

**Evidence**:
```python
@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Override output path from config')
@click.option('--validate', '-v', type=click.Choice(['strict', 'warn']),
              default='strict', help='Validation mode')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Show plan without writing')
def compose_cmd(config_file, output, validate, verbose, dry_run):
    """Compose markdown from YAML configuration."""
    try:
        config_path = Path(config_file)
        config = load_config(config_path)

        if verbose:
            click.echo(f"Loading config: {config_file}")

        if dry_run:
            click.echo(f"Dry-run: Would compose to {config.get('output')}")
            return

        output_path = Path(output) if output else Path(config['output'])
        fragments = [Path(f) for f in config['fragments']]

        compose(
            fragments=fragments,
            output=output_path,
            title=config.get('title'),
            adjust_headers=config.get('adjust_headers', False),
            separator=config.get('separator', '---'),
            validate_mode=validate,
        )

        if verbose:
            click.echo(f"Composed {len(fragments)} fragments to {output_path}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(4)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(3)
```

**Why this violates TDD**: Complete CLI implementation with all decorators, options, logic flow, error handling. Nothing for agent to discover through tests.

**Recommendation**:
```markdown
**GREEN Phase:**

**Implementation**: Add compose CLI command to main group

**Behavior**:
- Accept config_file as required argument
- Support --output override option
- Support --validate mode (strict/warn)
- Support --verbose flag for detailed output
- Support --dry-run flag (show plan, don't write)
- Load config, call compose() function
- Handle errors with appropriate exit codes
- Must pass all 3 tests

**Hint**: Use @main.command() decorator. Use click.argument() and click.option() for parameters. Use click.echo() for output. Use SystemExit(code) for exit codes.
```

---

## Warnings

None - all issues are critical violations.

---

## Cycle-by-Cycle Analysis

### Cycle 1.1: Header Level Detection
- **RED/GREEN sequencing**: VALID (tests will fail with ImportError)
- **Prescriptive code**: VIOLATION (complete implementation provided)
- **Assessment**: Needs revision

### Cycle 1.2: Header Level Increase
- **RED/GREEN sequencing**: VALID
- **Prescriptive code**: VIOLATION (regex pattern and logic prescribed)
- **Assessment**: Needs revision

### Cycle 1.3: Content Normalization Utilities
- **RED/GREEN sequencing**: VALID
- **Prescriptive code**: VIOLATION (both functions fully implemented)
- **Assessment**: Needs revision

### Cycle 2.1: Basic YAML Configuration Loading
- **RED/GREEN sequencing**: VALID
- **Prescriptive code**: VIOLATION (YAML loading prescribed)
- **Implementation Hint**: Present but insufficient - code still fully prescribed
- **Assessment**: Needs revision

### Cycle 2.2: Configuration Error Handling
- **RED/GREEN sequencing**: VALID
- **Prescriptive code**: VIOLATION (all validation logic prescribed)
- **Implementation Hint**: Present but code still prescriptive
- **Assessment**: Needs revision

### Cycle 3.1: Basic Fragment Composition
- **RED/GREEN sequencing**: VALID
- **Prescriptive code**: VIOLATION (complete compose() logic)
- **Implementation Hint**: Present but code fully prescribed
- **Assessment**: Needs revision

### Cycle 3.2: Title and Separator Options
- **RED/GREEN sequencing**: QUESTIONABLE (may pass on first run)
- **Prescriptive code**: VIOLATION (parameter handling prescribed)
- **Assessment**: Needs revision + sequence check

### Cycle 3.3: Header Adjustment Integration
- **RED/GREEN sequencing**: QUESTIONABLE (may pass on first run)
- **Prescriptive code**: VIOLATION (integration logic prescribed)
- **Assessment**: Needs revision + sequence check

### Cycle 3.4: Validation Modes
- **RED/GREEN sequencing**: QUESTIONABLE (tests may pass immediately)
- **Prescriptive code**: NO CODE BLOCK (references Cycle 3.1)
- **Assessment**: Acceptable (validation only)

### Cycle 4.1: CLI Basic Command
- **RED/GREEN sequencing**: VALID
- **Prescriptive code**: VIOLATION (complete CLI command)
- **Assessment**: Needs revision

### Cycle 4.2: CLI Options and Overrides
- **RED/GREEN sequencing**: QUESTIONABLE (may pass immediately)
- **Prescriptive code**: NO CODE BLOCK (references Cycle 4.1)
- **Assessment**: Acceptable (validation only)

### Cycle 4.3: CLI Error Handling and Exit Codes
- **RED/GREEN sequencing**: QUESTIONABLE (may pass immediately)
- **Prescriptive code**: NO CODE BLOCK (references Cycle 4.1)
- **Assessment**: Acceptable (validation only)

---

## Recommendations

### Priority 1: Remove Prescriptive Code (CRITICAL)

**All affected cycles (1.1, 1.2, 1.3, 2.1, 2.2, 3.1, 4.1) must be revised to:**

1. Remove complete implementation code blocks
2. Replace with behavior descriptions
3. Provide implementation hints (not solutions)
4. Let tests drive discovery

**Pattern to follow**:
```markdown
**GREEN Phase:**

**Implementation**: Minimal {function_name}() to pass tests

**Behavior**:
- What the function should do (not how)
- What inputs it accepts
- What outputs it returns
- What edge cases it handles

**Hint**: Suggested approach, libraries, or patterns (not exact code)
**Implementation Hint**: What to focus on in this cycle (minimal scope)
```

### Priority 2: Fix RED/GREEN Sequencing

**Cycles 3.2, 3.3, 3.4, 4.2, 4.3** - Verify RED phase will actually fail:
- Tests should fail with ImportError, AttributeError, or AssertionError
- If tests might pass immediately, restructure cycle sequencing
- Split "validation only" cycles from "implementation" cycles

**Suggested restructuring**:
- Cycle X.1: Simplest functional happy path (not trivial stub, but minimal features)
- Cycle X.2: Add next feature incrementally
- Cycle X.3: Add error handling
- Cycle X.4: Add validation modes

### Priority 3: Strengthen Implementation Hints

Current hints like "Happy path only - no error handling" are good but insufficient when complete code follows.

**Better pattern**:
```markdown
**Implementation Hint**:
- Happy path only - defer error handling to next cycle
- Hardcode separator value for now
- Focus on basic file reading and writing
- Use existing utility functions (normalize_newlines)
```

---

## Overall Assessment

**Status**: NEEDS MAJOR REVISION before execution

**Strengths**:
- Test specifications are well-defined with clear assertions
- RED phases have clear failure expectations
- Stop conditions and error handling documented
- Implementation hints present (though overshadowed by code)

**Critical Issues**:
- 7/11 cycles prescribe exact implementation code
- Violates TDD principle: tests should drive implementation
- Agents will become code copiers, not implementers
- No room for test-driven discovery and learning

**Risk if executed as-is**:
- Agents copy code from runbook instead of writing from tests
- TDD learning benefits lost
- False sense of test coverage (tests written after seeing solution)
- Defeats purpose of RED/GREEN discipline

---

## Next Steps

1. **Apply fixes to all 7 critical violations** - Remove implementation code, replace with behavior descriptions
2. **Review RED/GREEN sequencing** - Verify tests will fail in RED phase
3. **Validate revised runbook** - Re-run tdd-plan-reviewer to confirm fixes
4. **Execute with /orchestrate** - Only after violations resolved

---

**Review complete**: 2026-01-26
**Recommendation**: DO NOT EXECUTE until prescriptive code violations resolved
