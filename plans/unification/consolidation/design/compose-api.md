# Composition API: Unified Design Document

**Date**: 2026-01-19
**Status**: Final Design Deliverable for Phase 3
**Purpose**: Unified specification for markdown composition engine supporting CLAUDE.md generation and role file assembly

---

## Table of Contents

1. [Overview](#1-overview)
2. [Design Philosophy](#2-design-philosophy)
3. [Section 3.1: Core Composition Module](#31-core-composition-module)
4. [Section 3.2: CLI Entry Point](#32-cli-entry-point)
5. [Section 3.3: YAML Schema](#33-yaml-schema)
6. [Integration Notes](#4-integration-notes)
7. [Implementation Notes](#5-implementation-notes)
8. [Examples](#6-examples)

---

## 1. Overview

### Purpose

The composition API provides a unified interface for assembling markdown fragments into cohesive documents. It consolidates the approaches from existing implementations (tuick's programmatic composition and emojipack's YAML-driven configuration) into a single, flexible system.

### Key Capabilities

1. **Fragment composition** - Combine multiple markdown files in specified order
2. **Markdown-aware transformations** - Adjust header levels, normalize formatting
3. **Configuration-driven** - YAML as primary interface with CLI overrides
4. **Metadata injection** - Add titles and decorators to composed output
5. **Robust error handling** - Graceful and strict validation modes

### Target Use Cases

- **CLAUDE.md generation** - Flat composition from core + local fragments
- **Role file assembly** - Hierarchical composition with header adjustment
- **Documentation building** - Flexible fragment assembly for technical docs
- **Skill compositions** - Future extension for skill file generation

---

## 2. Design Philosophy

### Core Principles

1. **Simple, focused functions** - Each function does one thing well
2. **Markdown-aware** - Understands header syntax, preserves structure
3. **Configuration-first** - YAML as primary interface, CLI args as secondary
4. **Fail-safe** - Explicit error handling, no silent failures
5. **Reusable components** - Text utilities available independently

### Pattern Consolidation

**From tuick implementation**:

- Programmatic API with clear function signatures
- Header level adjustment for hierarchical composition
- Title injection for document decoration
- Output directory auto-creation

**From emojipack implementation**:

- YAML configuration for declarative composition
- Path deduplication via YAML anchors
- Ordered fragment processing
- Fail-fast error handling

**Unified approach**:

- YAML configuration as primary interface (emojipack pattern)
- Programmatic API for advanced use cases (tuick pattern)
- Conditional header adjustment (tuick feature, configurable)
- Both strict and warn validation modes

---

## 3.1 Core Composition Module

### 3.1.1 Module Overview

**Module**: `src/claudeutils/compose.py`

**Purpose**: Markdown fragment composition engine with configurable transformations

**Scope**:

In scope:

- Fragment loading and validation
- Content concatenation with separators
- Header level manipulation
- YAML configuration parsing
- Output file generation
- Error handling strategies

Out of scope:

- Content validation (malformed markdown detection)
- Large file optimization (MB+ files)
- Non-UTF-8 encoding support
- Per-fragment metadata preservation
- Markdown linting or reformatting

### 3.1.2 API Surface

#### Primary Function: `compose()`

**Signature**:

```python
def compose(
    fragments: list[Path] | list[str],
    output: Path,
    title: str | None = None,
    adjust_headers: bool = False,
    separator: str = "---",
    validate_mode: str = "strict",
) -> None:
    """
    Compose multiple markdown fragments into a single output file.

    Args:
        fragments: List of fragment file paths (Path or str).
                   Paths are processed in order.
        output: Path to output file. Parent directory is created if needed.
        title: Optional markdown header to prepend (e.g., "# Role Name").
               If provided, inserted as single `#` header before fragments.
        adjust_headers: If True, increase all fragment headers by 1 level.
                       Example: `# Header` becomes `## Header`.
                       Useful for composing role files with hierarchy.
        separator: Fragment separator style. Options:
                  - "---" (markdown horizontal rule, default)
                  - "blank" (blank line only)
                  - "none" (no separator)
        validate_mode: Error handling strategy. Options:
                      - "strict" (default): fail on missing file
                      - "warn": log warning and continue

    Returns:
        None

    Raises:
        FileNotFoundError: If validate_mode="strict" and fragment missing
        PermissionError: If output directory cannot be created
        IOError: If output file cannot be written

    Side effects:
        - Creates output parent directory if needed
        - Overwrites existing output file
        - Logs warnings to stderr if validate_mode="warn"
    """
```

**Usage example**:

```python
from pathlib import Path
from claudeutils.compose import compose

compose(
    fragments=[
        Path("docs/intro.md"),
        Path("docs/features.md"),
        Path("docs/usage.md"),
    ],
    output=Path("docs/README.md"),
    title="Documentation",
    adjust_headers=False,
    separator="---",
    validate_mode="strict",
)
```

#### Configuration Function: `load_config()`

**Signature**:

```python
def load_config(config_path: Path) -> dict:
    """
    Load and parse YAML composition configuration file.

    Args:
        config_path: Path to YAML configuration file.

    Returns:
        Parsed configuration dict with structure:
        {
            'sources': {
                'key': 'path/to/fragments',
                ...
            },
            'fragments': [
                'sources_key/file.md',
                ...
            ],
            'output': 'output.md',
            'title': str | None,  # optional
            'adjust_headers': bool,  # optional, default False
            'separator': str,  # optional, default "---"
            'validate_mode': str,  # optional, default "strict"
        }

    Raises:
        FileNotFoundError: If config file does not exist
        yaml.YAMLError: If config is malformed YAML
        ValueError: If config missing required fields (fragments, output)
    """
```

**Usage example**:

```python
from pathlib import Path
from claudeutils.compose import load_config, compose

config = load_config(Path("composition.yaml"))
fragments = [Path(f) for f in config['fragments']]
compose(
    fragments=fragments,
    output=Path(config['output']),
    title=config.get('title'),
    adjust_headers=config.get('adjust_headers', False),
    separator=config.get('separator', '---'),
    validate_mode=config.get('validate_mode', 'strict'),
)
```

### 3.1.3 Text Manipulation Utilities

#### `increase_header_levels()`

**Signature**:

```python
def increase_header_levels(content: str, levels: int = 1) -> str:
    """
    Increase markdown header levels by specified amount.

    Args:
        content: Markdown content string.
        levels: Number of header levels to increase (default 1).
               Example: levels=1 converts `# Header` to `## Header`.

    Returns:
        Content with adjusted headers.

    Example:
        >>> content = "# Title\\n## Section\\n### Subsection"
        >>> increase_header_levels(content, 1)
        "## Title\\n### Section\\n#### Subsection"
    """
```

**Implementation**:

```python
def increase_header_levels(content: str, levels: int = 1) -> str:
    # Pattern: line start, one or more #, single space, rest of line
    pattern = r'^(#{1,})\s'
    replacement = r'\1' + '#' * levels + ' '
    return re.sub(pattern, replacement, content, flags=re.MULTILINE)
```

#### `normalize_newlines()`

**Signature**:

```python
def normalize_newlines(content: str) -> str:
    """
    Ensure content ends with single newline.

    Args:
        content: String content.

    Returns:
        Content with single trailing newline.

    Example:
        >>> normalize_newlines("text")
        "text\\n"
        >>> normalize_newlines("text\\n")
        "text\\n"
    """
```

**Implementation**:

```python
def normalize_newlines(content: str) -> str:
    if not content or content.endswith('\n'):
        return content
    return content + '\n'
```

#### `format_separator()`

**Signature**:

```python
def format_separator(style: str = "---") -> str:
    """
    Format fragment separator based on style.

    Args:
        style: Separator style. Options:
              - "---" (default): markdown horizontal rule
              - "blank": single blank line
              - "none": empty string (no separator)

    Returns:
        Separator string ready for output.

    Example:
        >>> format_separator("---")
        "\\n---\\n\\n"
        >>> format_separator("blank")
        "\\n\\n"
        >>> format_separator("none")
        ""
    """
```

**Implementation**:

```python
def format_separator(style: str = "---") -> str:
    if style == "---":
        return "\n---\n\n"
    elif style == "blank":
        return "\n\n"
    elif style == "none":
        return ""
    else:
        raise ValueError(f"Unknown separator style: {style}")
```

#### `get_header_level()`

**Signature**:

```python
def get_header_level(line: str) -> int | None:
    """
    Detect markdown header level from a line.

    Args:
        line: Single line of text.

    Returns:
        Header level (1-6) if line is header, None otherwise.

    Example:
        >>> get_header_level("# Title")
        1
        >>> get_header_level("### Subsection")
        3
        >>> get_header_level("Not a header")
        None
    """
```

**Implementation**:

```python
def get_header_level(line: str) -> int | None:
    match = re.match(r'^(#+)\s', line)
    return len(match.group(1)) if match else None
```

### 3.1.4 Composition Algorithm

**Pseudo-code**:

```
FUNCTION compose(fragments, output, title, adjust_headers, separator, validate_mode):

    # Phase 1: Preparation
    output_path = Path(output).absolute()
    fragment_paths = [Path(f) for f in fragments]

    # Phase 2: Validation
    IF validate_mode == "strict":
        missing = [p for p in fragment_paths if not p.exists()]
        IF missing is not empty:
            RAISE FileNotFoundError(missing)

    # Phase 3: Directory setup
    TRY:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    EXCEPT PermissionError:
        RAISE PermissionError(f"Cannot create {output_path.parent}")

    # Phase 4: Composition
    TRY:
        output_file = OPEN output_path for writing

        # 4a: Write title if provided
        IF title is not None:
            output_file.write(f"# {title}\n\n")

        # 4b: Process each fragment
        FOR i, fragment_path IN ENUMERATE(fragment_paths):

            # Skip if missing in warn mode
            IF NOT fragment_path.exists():
                IF validate_mode == "warn":
                    LOG_WARNING(f"Skipping missing: {fragment_path}")
                    CONTINUE

            # Read fragment
            content = fragment_path.read_text(encoding='utf-8')

            # Apply transformations
            IF adjust_headers:
                content = increase_header_levels(content, 1)

            content = normalize_newlines(content)

            # Write content
            output_file.write(content)

            # Write separator (except after last fragment)
            IF i < LEN(fragment_paths) - 1:
                sep = format_separator(separator)
                output_file.write(sep)

        output_file.close()

    EXCEPT IOError as e:
        RAISE IOError(f"Cannot write output: {output_path}: {e}")

    # Phase 5: Reporting
    LOG_INFO(f"Composed {len(fragment_paths)} fragments to {output_path}")
    PRINT(f"Built {output_path}")
```

**Algorithm Properties**:

- **Deterministic**: Same input always produces same output
- **Fail-fast (strict)**: Detects problems before writing
- **Order-preserving**: Fragments processed in exact order
- **Idempotent**: Running twice produces identical result
- **Reversible**: Can trace output back to inputs

### 3.1.5 Error Handling

**Exception Hierarchy**:

```
CompositionError (base)
├── FragmentNotFoundError
│   └── Multiple missing fragments in strict mode
├── ConfigurationError
│   ├── MissingFieldError
│   ├── InvalidFieldError
│   └── MalformedConfigError
├── OutputError
│   ├── CannotCreateDirectoryError
│   └── CannotWriteFileError
```

**Strict mode** (validate\_mode="strict", default):

- Pre-validate all fragments before writing
- Fail fast on first missing file
- Raise FileNotFoundError with list of missing files
- No partial output created

**Warn mode** (validate\_mode="warn"):

- Log warnings to stderr for missing files
- Continue with available fragments
- Partial output created with available content
- Print summary at end (X fragments skipped)

### 3.1.6 Module Structure

```
src/claudeutils/compose.py
├── Imports
├── Constants
│   └── SEPARATOR_STYLES = {"---", "blank", "none"}
│   └── VALIDATE_MODES = {"strict", "warn"}
├── Exception classes
│   ├── CompositionError
│   ├── FragmentNotFoundError
│   └── ConfigurationError
├── Text utilities
│   ├── increase_header_levels()
│   ├── normalize_newlines()
│   ├── get_header_level()
│   └── format_separator()
├── Core functions
│   ├── compose()
│   ├── load_config()
│   └── _validate_fragments()  # Private helper
└── __all__ exports
    └── compose, load_config, increase_header_levels, normalize_newlines, get_header_level, format_separator
```

---

## 3.2 CLI Entry Point

### 3.2.1 Command Structure

**Root command**:

```bash
claudeutils compose [OPTIONS] CONFIG_FILE
```

**Subcommands** (future):

```bash
claudeutils compose role <name> [output]
claudeutils compose validate <config-file>
```

### 3.2.2 Primary Command Arguments

**Primary command**: `claudeutils compose <config-file>`

**Arguments**:

| Argument      | Type | Required | Description                            |
| ------------- | ---- | -------- | -------------------------------------- |
| `CONFIG_FILE` | Path | Yes      | Path to YAML composition configuration |

**Options**:

| Flag             | Type   | Default       | Description                              |
| ---------------- | ------ | ------------- | ---------------------------------------- |
| `--output, -o`   | Path   | (from config) | Override output path                     |
| `--validate, -v` | Choice | strict        | Validation mode (strict\|warn)           |
| `--verbose`      | Flag   | False         | Print detailed progress                  |
| `--dry-run`      | Flag   | False         | Show what would be composed, don't write |
| `--help`         | Flag   | N/A           | Show help message                        |

**Exit codes**:

- `0` - Success
- `1` - Configuration error (invalid YAML, missing required fields)
- `2` - Fragment error (missing file in strict mode)
- `3` - Output error (cannot write file)
- `4` - Argument error (invalid options)

### 3.2.3 Usage Examples

**Basic usage**:

```bash
# Config specifies everything
claudeutils compose agents/compose.yaml

# Override output path
claudeutils compose agents/compose.yaml --output docs/AGENTS.md

# Warn mode (skip missing fragments)
claudeutils compose agents/compose.yaml --validate warn

# Verbose output
claudeutils compose agents/compose.yaml --verbose

# Dry-run (validate without writing)
claudeutils compose agents/compose.yaml --dry-run
```

**Verbose output example**:

```
Loading config: agents/compose.yaml
Config valid (5 fragments, output: CLAUDE.md)
Processing: docs/intro.md (2.3 KB)
Processing: docs/features.md (5.1 KB)
Processing: docs/rules.md (8.7 KB)
Processing: docs/footer.md (1.2 KB)
Composed 4 fragments to CLAUDE.md (17.3 KB)
```

**Dry-run output example**:

```
Dry-run: Would compose to CLAUDE.md
Fragments:
  1. docs/intro.md (2.3 KB)
  2. docs/features.md (5.1 KB)
  3. docs/rules.md (8.7 KB)
Output size estimate: ~9 KB (before separators)
```

### 3.2.4 pyproject.toml Integration

**Entry point definition**:

```toml
[project.scripts]
claudeutils = "claudeutils.cli:main"

[project]
dependencies = [
    "click>=8.0.0",  # CLI framework
    "PyYAML>=6.0",   # YAML parsing
]
```

**CLI module structure** (`src/claudeutils/cli.py`):

```python
"""CLI entry point for claudeutils."""

import click
from pathlib import Path
from claudeutils.compose import compose, load_config


@click.group()
@click.version_option()
def main():
    """Claudeutils: Markdown composition and generation toolkit."""
    pass


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Override output path from config')
@click.option('--validate', '-v', type=click.Choice(['strict', 'warn']),
              default='strict', help='Validation mode')
@click.option('--verbose', is_flag=True, help='Verbose output')
@click.option('--dry-run', is_flag=True, help='Show plan without writing')
def compose_command(config_file, output, validate, verbose, dry_run):
    """Compose markdown from YAML configuration."""
    try:
        config_path = Path(config_file)
        config = load_config(config_path)

        if verbose:
            click.echo(f"Loading config: {config_file}")
            click.echo(f"Fragments: {len(config['fragments'])}")

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
        raise SystemExit(2)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        raise SystemExit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(3)


if __name__ == '__main__':
    main()
```

### 3.2.5 Error Handling

**Configuration errors**:

```bash
$ claudeutils compose nonexistent.yaml
Error: Configuration file not found: nonexistent.yaml
Exit code: 4

$ claudeutils compose bad.yaml
Configuration error: Error parsing YAML: line 3, column 5
Exit code: 1
```

**Fragment errors**:

```bash
# Strict mode
$ claudeutils compose config.yaml
Error: Fragment not found: docs/intro.md
Exit code: 2

# Warn mode
$ claudeutils compose config.yaml --validate warn
WARNING: Skipping missing fragment: docs/intro.md
Composed 2 of 3 fragments to output.md
Exit code: 0
```

---

## 3.3 YAML Schema

### 3.3.1 Schema Definition

**Root level structure**:

```yaml
# Required
fragments:                   # List[str] - Ordered fragment paths
  - path/to/fragment1.md
  - path/to/fragment2.md

output:                      # str - Output file path (relative or absolute)
  path/to/output.md

# Optional: Path source deduplication
sources:                     # Dict[str, str] - Path prefix mappings
  core: agent-core/fragments
  local: src/fragments

# Optional: Composition behavior
title:                       # str | null - Prepended markdown header
  "Document Title"

adjust_headers:              # bool - Increase all fragment headers by 1 level
  true

separator:                   # str - Fragment separator style
  "---"                      # Options: "---", "blank", "none"

validate_mode:               # str - Error handling for missing fragments
  "strict"                   # Options: "strict", "warn"
```

**Type specification**:

```python
CompositionConfig = {
    # Required
    fragments: List[str],     # Non-empty list
    output: str,              # Non-empty string

    # Optional with defaults
    sources?: Dict[str, str],          # Default: {}
    title?: str | None,                # Default: None
    adjust_headers?: bool,             # Default: False
    separator?: "---" | "blank" | "none",  # Default: "---"
    validate_mode?: "strict" | "warn", # Default: "strict"
}
```

### 3.3.2 Field Specifications

#### `fragments` (Required)

**Type**: `List[str]`

**Purpose**: Ordered list of fragment file paths to compose.

**Constraints**:

- Must be non-empty list
- Paths can be relative (from config file directory) or absolute
- Paths can reference `sources` prefixes (e.g., `*core/file.md`)
- Order is preserved exactly (deterministic composition)
- Duplicate entries allowed (compose same file multiple times)

**Examples**:

```yaml
# Relative paths
fragments:
  - docs/intro.md
  - docs/features.md

# With anchors (see sources section)
fragments:
  - *core/communication.md
  - *local/rules.md
  - *core/footer.md
```

#### `output` (Required)

**Type**: `str`

**Purpose**: Path to output file generated by composition.

**Constraints**:

- Non-empty string
- Relative (resolved from config directory) or absolute
- Parent directory created automatically if needed
- Existing file overwritten without prompt

**Examples**:

```yaml
# Relative (common)
output: CLAUDE.md
output: docs/README.md

# Absolute
output: /Users/david/projects/my-project/AGENTS.md
```

#### `sources` (Optional)

**Type**: `Dict[str, str]`

**Purpose**: Path prefix mappings to reduce repetition in fragment list.

**Pattern (YAML anchors)**:

```yaml
sources:
  core: &core agent-core/fragments
  local: &local src/fragments/

fragments:
  - *core/file1.md      # Expands to agent-core/fragments/file1.md
  - *local/file2.md     # Expands to src/fragments/file2.md
```

**Benefits**:

- **DRY principle**: Define paths once, reference many times
- **Maintainability**: Update path in one place
- **Clarity**: Intent visible in `sources` section
- **No substitution logic needed**: Native YAML feature

#### `title` (Optional)

**Type**: `str | None`

**Default**: `None` (no title)

**Behavior**:

- If provided: written as `# {title}\n\n` at start of output
- If null or absent: skipped

**Examples**:

```yaml
# With title
title: "Project Documentation"

# Without title (common for CLAUDE.md)
# output file starts with first fragment content
```

#### `adjust_headers` (Optional)

**Type**: `bool`

**Default**: `False`

**Purpose**: Increase all fragment header levels by 1 (h1→h2, h2→h3, etc.)

**Use cases**:

- Role files: Increase headers to nest under document title
- Included documentation: Prevent header level conflicts
- **NOT used** for flat CLAUDE.md composition

**Example**:

Input fragment:

```markdown
# Purpose

Coordinate workflow between agents.

## Responsibilities

- Task delegation
```

With `adjust_headers: true`:

```markdown
## Purpose

Coordinate workflow between agents.

### Responsibilities

- Task delegation
```

#### `separator` (Optional)

**Type**: `"---" | "blank" | "none"`

**Default**: `"---"`

**Purpose**: Visual separator between fragments in output.

**Behavior**:

- `"---"`: Markdown horizontal rule: `\n---\n\n`
- `"blank"`: Blank line: `\n\n`
- `"none"`: No separator (fragments concatenated directly)
- Applied between each pair of consecutive fragments
- **Not applied** after last fragment

#### `validate_mode` (Optional)

**Type**: `"strict" | "warn"`

**Default**: `"strict"`

**Purpose**: Error handling strategy for missing fragments.

**Behavior**:

**strict mode**:

- Pre-validate all fragments before writing
- Fail immediately if any fragment missing
- No partial output created
- Exit code: 2 (fragment error)

**warn mode**:

- Log warnings for missing fragments
- Continue with available fragments
- Partial output created
- Print summary: "Composed X of Y fragments"
- Exit code: 0 (success with warnings)

### 3.3.3 YAML Anchor Pattern

**Purpose**: Reduce path duplication using YAML anchors.

**Syntax**:

```yaml
sources:
  core: &core agent-core/fragments      # Define anchor
  local: &local src/fragments

fragments:
  - *core/communication.md              # Use anchor
  - *local/project-rules.md
  - *core/footer.md
```

**How it works**:

1. `&core` creates an anchor pointing to string value `agent-core/fragments`
2. `*core` references that anchor, inserting the value
3. YAML expands `*core/communication.md` to `agent-core/fragments/communication.md`

### 3.3.4 Validation Rules

**Load-time validation** (Schema):

```
1. File exists and readable
2. Valid YAML syntax
3. Required fields present: fragments, output
4. Fragment list non-empty (fail if empty)
5. Output non-empty string
6. Field types correct
7. Unknown fields ignored (for forward compatibility)
```

**Compose-time validation** (Files):

Strict mode:

```
1. Check all fragments exist before writing
2. Fail if any missing (FileNotFoundError)
3. List all missing files in error message
4. No partial output
```

Warn mode:

```
1. Check each fragment as it's processed
2. Skip missing fragments with warning
3. Continue with available fragments
4. Summary: "Composed X of Y fragments"
```

---

## 4. Integration Notes

### 4.1 Component Interaction

**Data flow**:

```
YAML config file
    ↓
load_config() → Configuration dict
    ↓
CLI argument overrides (optional)
    ↓
compose() function with resolved parameters
    ↓
Fragment processing:
  - Load fragment
  - Apply transformations (header adjustment if enabled)
  - Normalize newlines
  - Write to output with separators
    ↓
Output file
```

**Component responsibilities**:

1. **YAML schema** - Declarative composition definition
2. **load\_config()** - Parse and validate configuration
3. **CLI layer** - Argument parsing, override application, error formatting
4. **compose()** - Core composition algorithm
5. **Text utilities** - Reusable transformation functions

### 4.2 CLI to Core Mapping

**CLI arguments map to compose() parameters**:

```
CONFIG_FILE → load_config(Path(CONFIG_FILE))
--output    → output parameter (overrides config['output'])
--validate  → validate_mode parameter (overrides config['validate_mode'])
--verbose   → logging configuration
--dry-run   → skip compose() call, print plan
```

### 4.3 YAML to Core Mapping

**Configuration fields map to compose() parameters**:

```yaml
fragments       → fragments parameter
output          → output parameter
title           → title parameter
adjust_headers  → adjust_headers parameter
separator       → separator parameter
validate_mode   → validate_mode parameter
sources         → (YAML anchor expansion, transparent to compose())
```

### 4.4 Error Handling Layers

**Three layers of error handling**:

1. **YAML validation** (load\_config)
   - Schema errors → ValueError
   - Missing required fields → ValueError
   - Invalid field types → ValueError

2. **Fragment validation** (compose)
   - Missing fragments (strict) → FileNotFoundError
   - Missing fragments (warn) → warnings to stderr

3. **Output errors** (compose)
   - Cannot create directory → PermissionError
   - Cannot write file → IOError

**CLI error mapping**:

```
ValueError → exit code 1 (configuration error)
FileNotFoundError → exit code 2 (fragment error)
PermissionError/IOError → exit code 3 (output error)
```

### 4.5 Integration with Build Systems

**Makefile integration**:

```makefile
CLAUDE.md: agents/compose.yaml agent-core/fragments/*.md
	claudeutils compose agents/compose.yaml
```

**justfile integration**:

```just
CLAUDE.md: agents/compose.yaml
    claudeutils compose agents/compose.yaml
```

**CI/CD integration**:

```bash
#!/bin/bash
set -e
echo "Validating configuration..."
claudeutils compose validate agents/compose.yaml
echo "Building CLAUDE.md..."
claudeutils compose agents/compose.yaml --verbose
```

---

## 5. Implementation Notes

### 5.1 Dependencies

**Standard library**:

- `pathlib` - Path handling
- `re` - Regular expressions for header manipulation
- `logging` - Status reporting

**External packages**:

- `PyYAML>=6.0` - YAML parsing
- `click>=8.0.0` - CLI framework

**Installation**:

```bash
pip install -e .
```

### 5.2 Performance Characteristics

- **Fragment reading**: O(n\*m) where n=fragments, m=avg fragment size
- **Header adjustment**: O(k\*lines) per fragment (regex operations)
- **File I/O**: Single sequential write, unbuffered per fragment
- **Memory**: Entire output file buffered in memory during write

Not optimized for large files (MB+), but adequate for typical markdown documentation.

### 5.3 Testing Strategy

**Unit tests**:

```python
# Test composition
test_compose_basic()
test_compose_with_title()
test_compose_adjust_headers()
test_compose_separators()

# Test text utilities
test_increase_header_levels()
test_normalize_newlines()
test_format_separator()
test_get_header_level()

# Test configuration
test_load_config_valid()
test_load_config_missing_fields()
test_load_config_invalid_yaml()

# Test error handling
test_missing_fragment_strict()
test_missing_fragment_warn()
test_output_permission_error()
```

**CLI tests**:

```python
# Test CLI commands
test_compose_basic(tmp_path)
test_compose_missing_config()
test_compose_missing_fragment()
test_compose_warn_mode()
test_compose_output_override()
test_compose_verbose()
test_compose_dry_run()
```

### 5.4 Key Design Decisions

**Why Click framework?**

- Simple, declarative command definition
- Built-in help and version support
- Exit code handling
- Type conversion (Path, Choice)

**Why config file first?**

- Reusable across multiple invocations
- Version-controllable composition definition
- Explicit over implicit (config is the contract)
- Supports complex setups without CLI arg explosion

**Why YAML over JSON?**

- Human-readable and editable
- Supports comments
- YAML anchors for path deduplication
- PyYAML is standard in Python ecosystem

**Why UTF-8 only?**

- Simplifies implementation
- Standard for markdown documents
- Adequate for target use cases

### 5.5 Future Extensibility

**Planned extensions** (not in this phase):

1. Fragment metadata preservation
2. Content validation (malformed markdown detection)
3. Table of contents generation
4. Custom transformations (per-fragment callbacks)
5. Batch composition (multiple outputs)

**Design allows extensions without breaking changes**:

- Additional optional parameters in `compose()`
- New utility functions in same module
- Configuration schema supports new fields
- Error handling framework supports new exception types

---

## 6. Examples

### 6.1 Simple CLAUDE.md Generation

**Configuration** (`agents/compose.yaml`):

```yaml
sources:
  core: &core agent-core/fragments

fragments:
  - *core/AGENTS-framework.md
  - *core/communication.md
  - *core/delegation.md
  - *core/tool-preferences.md
  - *core/hashtags.md

output: CLAUDE.md
```

**Command**:

```bash
claudeutils compose agents/compose.yaml
```

**Output** (`CLAUDE.md`):

```markdown
[AGENTS-framework.md content]

---

[communication.md content]

---

[delegation.md content]

---

[tool-preferences.md content]

---

[hashtags.md content]
```

### 6.2 Role File with Header Adjustment

**Configuration** (`agents/compose.yaml`):

```yaml
sources:
  core: &core agent-core/fragments
  roles: &roles src/fragments/roles

fragments:
  - *core/role-header.md
  - *roles/orchestrator-purpose.md
  - *roles/orchestrator-capabilities.md
  - *roles/orchestrator-constraints.md

output: agents/role-orchestrator.md
title: Orchestrator Agent
adjust_headers: true
separator: "---"
validate_mode: strict
```

**Command**:

```bash
claudeutils compose agents/compose.yaml
```

**Input fragment** (`src/fragments/roles/orchestrator-purpose.md`):

```markdown
# Purpose

Coordinate work between specialized agents.
```

**Output** (`agents/role-orchestrator.md`):

```markdown
# Orchestrator Agent

## Header Content
[role-header.md content with adjusted headers]

---

## Purpose

Coordinate work between specialized agents.

---

[rest of composition with adjusted headers]
```

### 6.3 Multi-project with Warn Mode

**Configuration** (`agents/compose.yaml`):

```yaml
sources:
  core: &core agent-core/fragments
  local: &local .
  project: &project src/fragments

fragments:
  - *core/AGENTS-framework.md
  - *core/communication.md
  - *local/project-communication-addendum.md  # Optional, may be missing
  - *core/delegation.md
  - *project/model-selection-local.md
  - *core/tool-preferences.md
  - *core/footer.md

output: CLAUDE.md
validate_mode: warn
```

**Command**:

```bash
claudeutils compose agents/compose.yaml
```

**Output** (if `project-communication-addendum.md` missing):

```
WARNING: Skipping missing fragment: ./project-communication-addendum.md
Composed 6 of 7 fragments to CLAUDE.md
```

### 6.4 Programmatic Usage

**Python script**:

```python
from pathlib import Path
from claudeutils.compose import compose

# Define fragments programmatically
fragments = [
    Path("docs/intro.md"),
    Path("docs/features.md"),
    Path("docs/api.md"),
    Path("docs/examples.md"),
]

# Compose with custom settings
compose(
    fragments=fragments,
    output=Path("dist/documentation.md"),
    title="Complete Documentation",
    adjust_headers=False,
    separator="---",
    validate_mode="strict",
)

print("Documentation built successfully")
```

### 6.5 Integration with justfile

**justfile**:

```just
# Generate CLAUDE.md from composition
compose-claude:
    claudeutils compose agents/compose.yaml --verbose

# Generate role file
compose-role:
    claudeutils compose agents/compose-role.yaml

# Full build
build-agents: compose-claude compose-role
    @echo "Agent configuration built"
```

**Usage**:

```bash
just compose-claude
just build-agents
```

---

## Summary

The composition API provides a unified, flexible system for markdown fragment assembly:

**Core capabilities**:

1. Programmatic API via `compose()` function
2. Configuration-driven composition via YAML
3. CLI interface for command-line usage
4. Text manipulation utilities (header adjustment, normalization)
5. Robust error handling (strict and warn modes)

**Key design strengths**:

- **Simple**: Minimal required fields, clear defaults
- **Flexible**: Optional features for advanced use cases
- **Maintainable**: YAML anchors reduce duplication
- **Extensible**: Schema supports future enhancements
- **Integrated**: Works with build systems, CI/CD

**Pattern consolidation**:

- Combines tuick's programmatic approach with emojipack's configuration pattern
- Balances simplicity (config-driven) with flexibility (CLI overrides)
- Supports both CLAUDE.md generation (flat) and role files (hierarchical)

This design provides sufficient specification for implementation in Phase 4.
