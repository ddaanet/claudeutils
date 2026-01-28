# Feature Extraction: Existing Composition Implementations

**Date**: 2026-01-19
**Source Files Analyzed**:

- /Users/david/code/tuick/agents/build.py (73 lines)
- /Users/david/code/emojipack/agents/compose.sh (31 lines)
- /Users/david/code/emojipack/agents/compose.yaml (13 lines)

---

## Executive Summary

Two distinct composition patterns were identified in existing implementations:

1. **Tuick pattern** (Python-based): Programmatic composition with metadata injection and header manipulation
2. **Emojipack pattern** (Shell+YAML-based): Configuration-driven composition with path mapping and declarative fragment lists

Both patterns solve the same problem (composing markdown fragments) but with different architectural approaches. Key differences: tuick operates via CLI arguments, emojipack uses YAML configuration; tuick auto-adjusts headers, emojipack preserves original structure.

---

## Complete Feature List: Tuick Implementation

### Core Composition Features

1. **Fragment Concatenation**: Combines multiple source files in specified order
   - File: build.py lines 37-50
   - Implementation: Sequential file reading and writing
   - Pattern: For-loop over source\_files paths
   - Key detail: Maintains fragment order exactly as provided

2. **Fragment Validation**: Checks file existence before processing
   - File: build.py lines 38-40
   - Implementation: `if not src_file.exists()` with warning to stderr
   - Behavior: Continues processing on missing files (graceful degradation)
   - Note: Logs warning but doesn't fail build

3. **Separator Injection**: Inserts markdown horizontal rules between fragments
   - File: build.py lines 44-46
   - Implementation: `out.write("\n---\n\n")` between sections
   - Pattern: No separator before first fragment
   - Purpose: Visual demarcation of fragment boundaries

### Text Manipulation Features

4. **Header Level Adjustment**: Increases markdown header levels by one
   - File: build.py lines 9-18 (increase\_header\_levels function)
   - Implementation: Regex substitution `^(#+) ` to `#\1 `
   - Pattern: `re.sub(r'^(#+) ', r'#\1 ', content, flags=re.MULTILINE)`
   - Scope: Applied to all fragment content automatically
   - Purpose: Ensures proper hierarchy when composing (prevents section depth conflicts)

5. **Newline Normalization**: Ensures proper line endings
   - File: build.py lines 52-54
   - Implementation: Checks content ends with newline, adds if missing
   - Pattern: `if not content.endswith("\n"): out.write("\n")`
   - Purpose: Prevents markdown parsing issues from missing newlines

### Decorator/Metadata Features

6. **Title Injection**: Prepends a title to composed output
   - File: build.py lines 32-34
   - Implementation: `out.write(f"# {role_title}\n\n")`
   - Pattern: Single markdown header at document start
   - Purpose: Names the composed document (e.g., role name)

7. **Output Path Handling**: Creates parent directories automatically
   - File: build.py line 29
   - Implementation: `output_path.parent.mkdir(parents=True, exist_ok=True)`
   - Pattern: Recursive directory creation with idempotency
   - Purpose: Ensures output directory structure exists

### Configuration Features

8. **CLI Argument Parsing**: Command-line interface for composition
   - File: build.py lines 57-68 (main function)
   - Signature: `build.py OUTPUT TITLE SOURCE...`
   - Pattern: Positional arguments, variadic source list
   - Validation: Requires at least 4 arguments (program, output, title, 1 source)

### Output Features

9. **File Output Generation**: Writes composed content to specified path
   - File: build.py lines 31-54
   - Pattern: Context manager `with output_path.open("w")`
   - Behavior: Overwrites existing file
   - Confirmation: Prints status message to stdout

10. **Status Reporting**: Provides feedback on completion
    - File: build.py line 68
    - Implementation: `print(f"Built {output_path}")`
    - Purpose: User feedback on success

---

## Emojipack Implementation Analysis

### Configuration Features (YAML-based)

**Configuration Structure**:

```yaml
sources:
  core: &core agent-core/fragments

fragments:
  - *core/AGENTS-framework.md
  - [... more fragments ...]

output: AGENTS.md
```

Features:

- **YAML Anchors & Aliases**: `&core` / `*core` for DRY path references
- **Ordered Fragment List**: Direct list of files to compose in order
- **Output Declaration**: Single field specifies destination file

### Composition Algorithm (Shell-based)

**Process**:

1. Fragment list iteration
2. File existence check for each fragment
3. Concatenation with blank line separator
4. Status reporting

**Key Differences from Tuick**:

- No automatic header level adjustment
- No title/metadata injection
- Preserves original markdown structure
- Error handling: Exits on missing file (fail-fast)
- Simpler, single-purpose implementation

---

## Feature Comparison Matrix

| Feature                 | Tuick       | Emojipack        | Notes                                                       |
| ----------------------- | ----------- | ---------------- | ----------------------------------------------------------- |
| Fragment concatenation  | ✓           | ✓                | Both support ordered composition                            |
| Fragment validation     | ✓ (warning) | ✓ (fail-fast)    | Different error strategies                                  |
| Separator injection     | ✓           | ✓                | Both add blank lines (emojipack automatic)                  |
| Header adjustment       | ✓           | ✗                | Only tuick manipulates header levels                        |
| Newline normalization   | ✓           | ✗                | Not explicit in shell script                                |
| Title injection         | ✓           | ✗                | Only tuick adds document title                              |
| Output path auto-create | ✓           | ✗                | Tuick handles nested dirs, shell relies on emojipack layout |
| CLI interface           | ✓ (args)    | ✓ (script)       | Tuick args, emojipack script (reads YAML)                   |
| YAML config             | ✗           | ✓                | Only emojipack uses YAML for fragment lists                 |
| Path deduplication      | ✗           | ✓ (YAML anchors) | Emojipack leverages YAML features                           |

---

## Feature Categorization

### Core Composition Features (Essential)

- Fragment concatenation (both implementations must support)
- Fragment validation (both implementations have it)
- Separator injection (both do this, style differs)
- Ordered fragment processing (fundamental requirement)
- File output generation (foundational)

### Text Manipulation Features (Important)

- Header level adjustment (tuick does this; needed for role files)
- Newline normalization (tuick handles explicitly)

### Configuration Features (Important)

- YAML schema support (emojipack pattern, required for unified API)
- Path deduplication via YAML anchors (emojipack feature; reduces duplication)
- Fragment ordering (both support; YAML makes it declarative)

### Metadata/Decoration Features (Optional but Useful)

- Title injection (tuick feature; useful for role files, probably not for CLAUDE.md)
- Separator style customization (could be optional)

### CLI/Integration Features (Important)

- CLI argument parsing (tuick pattern)
- Status reporting (both have it)
- Output directory auto-creation (tuick feature; useful for nested outputs)

### Error Handling Features (Important)

- Graceful degradation on missing files (tuick warning mode)
- Fail-fast on missing files (emojipack mode)
- Permission error handling (neither explicitly handles)

---

## Patterns to Preserve

1. **Markdown-aware composition**: Both implementations understand markdown structure
2. **Ordered fragment processing**: Order matters; must be deterministic
3. **Fragment validation**: Check files exist before processing
4. **Declarative YAML config**: emojipack's YAML approach is cleaner than CLI args
5. **Path deduplication**: YAML anchors pattern reduces repetition in large compositions
6. **Simple, focused algorithm**: Both implementations are straightforward, not over-engineered

---

## Patterns to Improve

1. **Header manipulation**: Tuick's automatic header increment is good for role files, but CLAUDE.md often mixes different content types. Make this configurable.

2. **Error handling strategy**:
   - Tuick warns on missing files and continues (loose)
   - Emojipack fails on missing files (strict)
   - Recommendation: Support both via config flag (default strict for reliability)

3. **Configuration verbosity**:
   - Tuick forces CLI args for every composition (repetitive for repeated use)
   - Emojipack YAML approach scales better
   - Recommendation: YAML as primary config method

4. **Fragment separation**:
   - Both use simple newlines/rules
   - Recommendation: Support configurable separator (comment, rule, none)

5. **Markdown preservation**:
   - Tuick transforms all headers (potential side effect)
   - Recommendation: Make header adjustment optional per-fragment or global

---

## Design Recommendations for Unified API

### 1. Composition Algorithm Design

**Recommended approach** (hybrid tuick+emojipack):

```
Core algorithm:
  1. Load YAML config (emojipack pattern)
  2. Validate all fragments exist (fail-fast, emojipack pattern)
  3. For each fragment in order:
     a. Read file content
     b. Apply transformations (conditional header adjustment)
     c. Write to output with separator
  4. Report status
```

**Rationale**: YAML provides better DRY through anchors; fail-fast is safer; conditional header adjustment provides flexibility.

### 2. Configuration Schema Design

**Structure** (based on emojipack with enhancements):

```yaml
sources:
  core: &core agent-core/fragments
  lib: &lib src/fragments

fragments:
  - *core/section-1.md
  - *lib/section-2.md

output: AGENTS.md
mode: agents|role|skill          # Optional: affects decoration
adjust_headers: true|false       # Optional: header level adjustment
separator: rule|blank|comment    # Optional: how to separate fragments
validate_mode: strict|warn       # Optional: behavior on missing files
```

**Rationale**:

- `sources` + `fragments`: Leverage YAML anchors for DRY
- `output`: Clear output specification
- `mode`: Enables different composition styles (role files vs CLAUDE.md)
- `adjust_headers`: Make header adjustment conditional (tuick feature)
- `separator`: Configurable fragment boundaries
- `validate_mode`: Support both error strategies

### 3. Core Module API Design

**Recommended signatures** (based on tuick):

```python
def compose(
    fragments: list[Path] | list[str],
    output: Path,
    title: str | None = None,
    adjust_headers: bool = False,
    separator: str = "---",
    validate_mode: str = "strict",
) -> None:
    """Compose fragments into single markdown file."""

def load_config(config_path: Path) -> dict:
    """Load and parse YAML composition config."""

def increase_header_levels(content: str, levels: int = 1) -> str:
    """Adjust markdown header levels."""
```

**Rationale**:

- Simple, focused functions
- Reusable components
- Clear parameter contracts
- Matches tuick's straightforward approach

### 4. CLI Interface Design

**Recommended subcommands**:

```bash
claudeutils compose <config-file>              # Primary: YAML-driven
claudeutils compose role <output> <title> <fragments...>  # Secondary: tuick-compat
```

**Rationale**:

- Primary mode: YAML config (emojipack pattern, scales better)
- Secondary mode: CLI args (tuick compatibility, simple one-offs)
- Supports both use cases

### 5. Key Implementation Notes

- **Dependencies**: Only stdlib needed (pathlib, re, yaml)
- **Testing strategy**: Test each feature independently (concatenation, header adjustment, YAML parsing)
- **Error handling**: Structured exceptions for different failure modes
- **Performance**: Not a concern (fragment composition is lightweight)
- **Extensibility**: Design for future composition modes (role, skill, custom)

---

## Gaps and Questions

1. **Fragment path resolution**: Relative to config file or CWD? Both implementations use relative paths, but unclear if this is consistent. Recommendation: Document clearly, probably relative to config file for better portability.

2. **Large file handling**: Neither implementation shows handling of large (MB+) files. Assumption: Not a concern for typical markdown compositions.

3. **Encoding**: Both assume UTF-8. Should we support other encodings? Recommendation: UTF-8 only, document assumption.

4. **Fragment comments/metadata**: Neither implementation preserves per-fragment metadata. Might be useful for authoring/maintenance. Could add as future feature.

5. **Validation schemas**: Neither implementation validates fragment content. Should we reject malformed markdown? Recommendation: No validation of content, only file existence.

---

## Conclusion

**Tuick** provides a solid programmatic foundation with metadata injection and header manipulation. **Emojipack** demonstrates the benefits of YAML-driven configuration and path deduplication.

The unified API should:

1. Adopt emojipack's YAML configuration as primary interface
2. Implement tuick's composition algorithm with conditional header adjustment
3. Support both error handling strategies
4. Provide clean Python API for programmatic use
5. Design for extensibility (role files, skill compositions, etc.)

This hybrid approach preserves the strengths of both implementations while simplifying the user experience through declarative configuration.
