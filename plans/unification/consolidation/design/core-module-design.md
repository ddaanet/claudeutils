# Core Composition Module Design

**Date**: 2026-01-19
**Module**: `src/claudeutils/compose.py`
**Purpose**: Markdown fragment composition engine with configurable transformations

---

## 1. Module Overview

### Purpose

The composition module provides programmatic and configuration-driven capabilities to compose multiple markdown fragments into a single unified markdown document. It serves as the core engine for the unification project, enabling:

1. **Flexible fragment assembly** - Combine markdown files in specified order
2. **Markdown-aware transformations** - Adjust header levels, normalize formatting
3. **Configurable composition** - Support YAML-based configuration for repeatability
4. **Metadata injection** - Add titles and decorators to composed output
5. **Robust error handling** - Graceful and strict validation modes

### Scope

**In scope**:

- Fragment loading and validation
- Content concatenation with separators
- Header level manipulation
- YAML configuration parsing
- Output file generation
- Error handling strategies

**Out of scope**:

- Content validation (malformed markdown detection)
- Large file optimization (MB+ files)
- Non-UTF-8 encoding support
- Per-fragment metadata preservation
- Markdown linting or reformatting

### Key Design Principles

1. **Simple, focused functions** - Each function does one thing well
2. **Markdown-aware** - Understands header syntax, preserves structure
3. **Configuration-first** - YAML as primary interface, CLI args as secondary
4. **Fail-safe** - Explicit error handling, no silent failures
5. **Reusable components** - Text utilities available independently

---

## API Surface

### Primary Functions

#### 1. `compose()`

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

**Algorithm** (step-by-step):

1. Validate output path and create parent directory
2. If validate\_mode="strict": check all fragments exist (fail-fast)
3. Open output file for writing
4. If title provided: write `# {title}\n\n`
5. For each fragment in order:
   a. Read fragment file content
   b. If validate\_mode="warn" and file missing: log warning and skip
   c. Apply transformations: adjust\_headers if enabled
   d. Normalize newlines (ensure ends with `\n`)
   e. Write content to output
   f. If not last fragment: write separator
6. Close output file
7. Log success message to stdout

**Error handling**:

- Missing file + strict mode: raise FileNotFoundError with path
- Missing file + warn mode: log to stderr, continue
- Cannot create output dir: raise PermissionError
- Cannot write output: raise IOError (filesystem error)

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

---

#### 2. `load_config()`

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

**Schema validation**:

- Required fields: `fragments`, `output`
- Optional fields: `sources`, `title`, `adjust_headers`, `separator`, `validate_mode`
- `fragments` must be non-empty list
- `output` must be string
- `sources` (if present) must be dict with string values

**Algorithm**:

1. Load YAML from config\_path
2. Validate required fields present
3. Validate field types
4. Return parsed dict

**Usage example**:

```python
from pathlib import Path
from claudeutils.compose import load_config, compose

config = load_config(Path("composition.yaml"))
# config = {
#     'sources': {'core': 'agent-core/fragments'},
#     'fragments': ['core/intro.md', 'core/features.md'],
#     'output': 'AGENTS.md',
#     'adjust_headers': True,
# }

# Resolve fragment paths and compose
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

---

### Helper Functions (Text Manipulation)

#### 3. `increase_header_levels()`

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

    Behavior:
        - Matches lines starting with 1+ `#` followed by space
        - Prepends additional `#` characters
        - Preserves indentation and formatting
        - Case-insensitive (works with any header syntax)
        - No effect on code blocks or inline `#` not used as headers

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

**Algorithm**:

1. Use regex to find lines matching `^#+\s` (header lines)
2. For each match, prepend `levels` number of `#` characters
3. Preserve spacing and content
4. Return modified content

**Use cases**:

- Composing role files (increase fragment headers to prevent conflicts)
- Adjusting included documentation to fit hierarchy
- Not used for CLAUDE.md compositions (flat structure)

---

#### 4. `normalize_newlines()`

**Signature**:

```python
def normalize_newlines(content: str) -> str:
    """
    Ensure content ends with single newline.

    Args:
        content: String content.

    Returns:
        Content with single trailing newline.

    Behavior:
        - If content is empty: return single newline
        - If content ends with newline: return unchanged
        - If content missing newline: append single newline
        - Does NOT normalize internal line endings (no CRLF -> LF conversion)

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

**Purpose**:

- Prevent markdown parsing issues from missing final newlines
- Ensures proper separator placement
- Required before file write

---

#### 5. `get_header_level()`

**Signature**:

```python
def get_header_level(line: str) -> int | None:
    """
    Detect markdown header level from a line.

    Args:
        line: Single line of text.

    Returns:
        Header level (1-6) if line is header, None otherwise.

    Behavior:
        - Matches `^#+\s` pattern (one or more # followed by space)
        - Returns count of # characters
        - Returns None if not a header line

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

**Use cases**:

- Analyzing fragment header structure
- Detecting conflicts in hierarchies
- Future: validation and reporting

---

#### 6. `format_separator()`

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

**Purpose**:

- Consistent separator formatting
- Configurable visual demarcation
- Encapsulates formatting logic

---

## Data Structures

### Configuration Dictionary

**Loaded from YAML, used throughout composition**:

```python
{
    'sources': {
        'str': 'str',  # Path prefix mapping (e.g., 'core': 'agent-core/fragments')
        ...
    },
    'fragments': [
        'str',  # Fragment paths in order (may use sources prefix)
        ...
    ],
    'output': 'str',  # Output file path
    'title': 'str | None',  # Optional document title
    'adjust_headers': bool,  # Default False
    'separator': str,  # Default "---"
    'validate_mode': str,  # Default "strict"
}
```

### Fragment Metadata (Internal)

**Tracked during composition for error reporting**:

```python
{
    'path': Path,
    'exists': bool,
    'size_bytes': int | None,
    'error': str | None,
}
```

Not persisted, used only for reporting in strict mode validation.

---

## Error Handling Approach

### Exception Hierarchy

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

### Error Handling Strategies

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

### Logging

- Use Python's `logging` module (INFO/WARNING/ERROR levels)
- Configure via standard logging setup
- Messages to stderr for errors/warnings
- Success message to stdout

---

## Composition Algorithm (Detailed)

### Pseudo-code

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

### Algorithm Properties

- **Deterministic**: Same input always produces same output
- **Fail-fast (strict)**: Detects problems before writing
- **Order-preserving**: Fragments processed in exact order
- **Idempotent**: Running twice produces identical result
- **Reversible**: Can trace output back to inputs

---

## Text Manipulation Utilities

### Purpose

Encapsulate markdown-specific text operations that are reused across composition pipeline.

### Utility Functions Summary

| Function                                  | Input  | Output    | Purpose                        |
| ----------------------------------------- | ------ | --------- | ------------------------------ |
| `increase_header_levels(content, levels)` | String | String    | Adjust markdown header depth   |
| `normalize_newlines(content)`             | String | String    | Ensure single trailing newline |
| `get_header_level(line)`                  | String | Int\|None | Detect header level from line  |
| `format_separator(style)`                 | String | String    | Format fragment separator      |

### Design Notes

- All utilities are **pure functions** (no side effects)
- All utilities are **stateless** (no internal state)
- All utilities handle **edge cases** (empty strings, None values)
- All utilities are **independently testable**

---

## Module Structure (File Layout)

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

### Type Hints

All functions include full type hints using `typing` module:

- `Path` from `pathlib`
- `Optional[T]` for nullable values
- `Union[A, B]` for multiple types
- `List[T]` for sequences
- `Dict[str, Any]` for config dicts

---

## Usage Examples

### Example 1: Simple Composition from Fragment List

**Scenario**: Compose a documentation README from multiple markdown files.

```python
from pathlib import Path
from claudeutils.compose import compose

# List of fragments to compose in order
fragments = [
    Path("docs/01-introduction.md"),
    Path("docs/02-features.md"),
    Path("docs/03-installation.md"),
    Path("docs/04-usage.md"),
    Path("docs/05-troubleshooting.md"),
]

# Compose into single file
compose(
    fragments=fragments,
    output=Path("docs/README.md"),
    title="Project Documentation",
    adjust_headers=False,  # Preserve original structure
    separator="---",       # Visual separation between sections
    validate_mode="strict", # Fail if any fragment missing
)
```

**Expected output**: `/Users/david/code/claudeutils/docs/README.md`

**Output structure**:

```markdown
# Project Documentation

[content of 01-introduction.md]

---

[content of 02-features.md]

---

[content of 03-installation.md]

... etc ...
```

---

### Example 2: YAML-Driven Role File Composition

**Scenario**: Compose a role documentation file from YAML configuration with header level adjustment.

**Configuration file** (`roles/agent-config.yaml`):

```yaml
sources:
  core: &core agent-core/fragments
  roles: &roles src/fragments/roles

fragments:
  - *core/HEADER.md
  - *roles/agent-purpose.md
  - *roles/agent-capabilities.md
  - *roles/agent-constraints.md
  - *core/FOOTER.md

output: AGENTS.md
adjust_headers: true    # Increase headers by 1 level
separator: "---"
validate_mode: strict
```

**Python code**:

```python
from pathlib import Path
from claudeutils.compose import load_config, compose

# Load configuration
config = load_config(Path("roles/agent-config.yaml"))

# Extract and resolve fragment paths
fragments = [Path(f) for f in config['fragments']]

# Compose with all configuration options
compose(
    fragments=fragments,
    output=Path(config['output']),
    title=config.get('title'),
    adjust_headers=config['adjust_headers'],
    separator=config['separator'],
    validate_mode=config['validate_mode'],
)
```

**Processing notes**:

- All fragment headers increased by 1 level (# → ##, ## → ###, etc.)
- Enables proper hierarchy when role file is included in larger document
- YAML `sources` and `&core`/`&roles` anchors reduce path duplication
- Configuration reusable across multiple compositions

**Output structure**:

```markdown
[header.md content with ## instead of #]

---

[agent-purpose.md with adjusted headers]

---

[agent-capabilities.md with adjusted headers]

---

[agent-constraints.md with adjusted headers]

---

[footer.md content with adjusted headers]
```

---

### Example 3: Error Handling - Warn Mode

**Scenario**: Compose document while tolerating missing optional fragments.

```python
from pathlib import Path
from claudeutils.compose import compose
import logging

# Configure logging to see warnings
logging.basicConfig(level=logging.WARNING)

fragments = [
    Path("docs/intro.md"),          # exists
    Path("docs/missing-optional.md"), # missing (will be warned, not failed)
    Path("docs/main.md"),            # exists
]

try:
    compose(
        fragments=fragments,
        output=Path("docs/output.md"),
        validate_mode="warn",  # Don't fail on missing
    )
except FileNotFoundError:
    print("This won't be raised in warn mode")

# Output:
# WARNING: Skipping missing fragment: docs/missing-optional.md
# Built docs/output.md
```

**Output contains only**:

- Content from `docs/intro.md`
- Separator
- Content from `docs/main.md`

Missing fragment is skipped silently (with warning).

---

## Implementation Notes

### Dependencies

**Standard library only** (no external packages required):

- `pathlib` - Path handling
- `re` - Regular expressions for header manipulation
- `yaml` - YAML parsing (from stdlib starting Python 3.11 via external package, or use PyYAML)
- `logging` - Status reporting

### Performance Characteristics

- **Fragment reading**: O(n\*m) where n=fragments, m=avg fragment size
- **Header adjustment**: O(k\*lines) per fragment (regex operations)
- **File I/O**: Single sequential write, unbuffered per fragment
- **Memory**: Entire output file buffered in memory during write

Not optimized for large files (MB+), but adequate for typical markdown documentation.

### UTF-8 Assumption

All operations assume UTF-8 encoding:

- `Path.read_text()` defaults to UTF-8
- `Path.write_text()` defaults to UTF-8
- No support for other encodings

### Backward Compatibility

Design maintains compatibility with tuick's CLI pattern:

```python
# CLI adapter (CLI layer responsibility)
# Converts: compose.py ROLE TITLE SOURCE1 SOURCE2...
# To: compose(fragments=[SOURCE1, SOURCE2, ...], output=...)
```

---

## Future Extensibility

### Planned Extensions (not in this phase)

1. **Fragment metadata preservation** - Track per-fragment authorship/version
2. **Content validation** - Detect malformed markdown before composition
3. **Table of contents generation** - Auto-generate TOC from headers
4. **Custom transformations** - Per-fragment callback functions
5. **Batch composition** - Single operation for multiple outputs

### Design for Extension

Current design allows these extensions without breaking changes:

- Additional optional parameters in `compose()`
- New utility functions in same module
- Configuration schema supports new fields
- Error handling framework supports new exception types

---

## API Reference (Quick Summary)

```python
# Main functions
compose(fragments, output, title=None, adjust_headers=False,
        separator="---", validate_mode="strict") -> None
load_config(config_path) -> dict

# Text utilities
increase_header_levels(content, levels=1) -> str
normalize_newlines(content) -> str
get_header_level(line) -> int | None
format_separator(style="---") -> str

# Exceptions
CompositionError (base)
FragmentNotFoundError
ConfigurationError

# Constants
SEPARATOR_STYLES = {"---", "blank", "none"}
VALIDATE_MODES = {"strict", "warn"}
```

---

## Summary

The core composition module provides:

1. **Flexible composition** via `compose()` function with configurable options
2. **YAML support** via `load_config()` for configuration-driven composition
3. **Text utilities** for markdown manipulation (header adjustment, newline normalization)
4. **Robust error handling** with strict and warn modes
5. **Simple, testable design** with pure functions and clear responsibilities

This design balances the strengths of both tuick (programmatic, metadata) and emojipack (configuration-driven, DRY) patterns while providing a clean, extensible API for the unification project.
