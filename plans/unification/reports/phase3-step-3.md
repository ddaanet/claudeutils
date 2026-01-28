# Phase 3 Step 3 - CLI Entry Point Design

**Date**: 2026-01-19
**Step**: Design CLI interface for composition commands
**Status**: Complete

---

## Objective

Design CLI interface for composition commands (`claudeutils compose`) that provides:
- YAML-driven composition via `claudeutils compose <config-file>`
- Role file generation (tuick pattern) via `claudeutils compose role`
- Future extensibility for validation and other modes

---

## Actions Taken

### 1. Read Core Module Design

Reviewed `/Users/david/code/claudeutils/scratch/consolidation/design/core-module-design.md` to understand:
- `compose()` function API (fragments, output, title, adjust_headers, separator, validate_mode)
- `load_config()` function for YAML configuration loading
- Helper functions (increase_header_levels, normalize_newlines, format_separator)
- Error handling strategies (strict vs warn modes)
- Configuration schema and data structures

### 2. Reviewed Existing CLI

Read `/Users/david/code/claudeutils/src/claudeutils/cli.py` to understand current structure:
- Uses Click framework with `@click.group()` for command organization
- Entry point: `claudeutils = "claudeutils.cli:main"` in pyproject.toml
- Existing commands: list, extract, collect, analyze, rules, tokens, markdown
- Pattern: Click decorators, Path handling, stdin/file input, error codes

### 3. Reviewed Project Integration

Read `/Users/david/code/claudeutils/justfile` to understand build integration patterns:
- Common recipes: format, check, test, lint, dev
- Pattern: bash helpers for reporting, colored output
- Integration pattern for composition: justfile recipes invoke CLI commands

### 4. Found Existing CLI Design

Discovered `/Users/david/code/claudeutils/scratch/consolidation/design/cli-design.md` already exists (comprehensive design artifact created in earlier phase).

This artifact includes:
- **Subcommand structure** - Primary `compose <config-file>`, role generation, validation
- **Command-line arguments** - CONFIG_FILE (required), --output, --validate, --verbose, --dry-run
- **Usage examples** - 8 complete examples covering basic usage, role files, validation, warn mode, integration patterns
- **pyproject.toml integration** - Entry point definition, Click-based CLI module structure
- **Error handling** - Exit codes (0=success, 1=config error, 2=fragment error, 3=output error, 4=argument error)
- **Integration patterns** - CI/CD, pre-commit hooks, watch mode, build systems (Makefile, justfile)
- **Design decisions** - Why Click, why config-first, why YAML, why separate flags

---

## CLI Design Summary

### Primary Command

```bash
claudeutils compose [OPTIONS] CONFIG_FILE
```

**Arguments**:
- `CONFIG_FILE` - Path to YAML composition configuration (required)

**Options**:
- `--output, -o PATH` - Override output path from config
- `--validate, -v {strict|warn}` - Validation mode (default: strict)
- `--verbose` - Print detailed progress
- `--dry-run` - Show plan without writing output
- `--help` - Show help message

**Exit codes**:
- 0: Success
- 1: Configuration error (invalid YAML, missing fields)
- 2: Fragment error (missing file in strict mode)
- 3: Output error (cannot write)
- 4: Argument error (invalid options)

### Subcommands

**Role generation** (future expansion):
```bash
claudeutils compose role [OPTIONS] ROLE_NAME [OUTPUT]
```

**Validation** (future):
```bash
claudeutils compose validate [OPTIONS] CONFIG_FILE
```

### pyproject.toml Entry Point

```toml
[project.scripts]
claudeutils = "claudeutils.cli:main"

[project]
dependencies = [
    "click>=8.0.0",  # CLI framework
    "PyYAML>=6.0",   # YAML parsing (via pyyaml, already in deps)
]
```

### CLI Module Structure (Click-based)

```python
@click.group()
@click.version_option()
def main():
    """Claudeutils: Markdown composition and generation toolkit."""
    pass

@main.command()
@click.argument('config_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path())
@click.option('--validate', '-v', type=click.Choice(['strict', 'warn']), default='strict')
@click.option('--verbose', is_flag=True)
@click.option('--dry-run', is_flag=True)
def compose_command(config_file, output, validate, verbose, dry_run):
    """Compose markdown from YAML configuration."""
    # Implementation: load_config(), compose()

@main.command()
@click.argument('role_name')
@click.argument('output', required=False)
@click.option('--config', '-c', type=click.Path(exists=True))
def compose_role(role_name, output, config):
    """Generate role file from composition template."""
    # Future: Phase 3 Step 4

@main.command()
@click.argument('config_file', type=click.Path(exists=True))
def validate_command(config_file):
    """Validate composition configuration."""
    # Future extension
```

---

## Usage Examples

### Example 1: Basic CLAUDE.md Generation

```bash
claudeutils compose agents/compose.yaml
```

Output:
```
Composed 4 fragments to CLAUDE.md
```

### Example 2: Override Output Path

```bash
claudeutils compose agents/compose.yaml --output docs/AGENTS.md
```

### Example 3: Warn Mode (Skip Missing)

```bash
claudeutils compose agents/compose.yaml --validate warn
```

Output:
```
WARNING: Skipping missing fragment: docs/optional.md
Composed 2 of 3 fragments to output.md
```

### Example 4: Verbose Output

```bash
claudeutils compose agents/compose.yaml --verbose
```

Output:
```
Loading config: agents/compose.yaml
Config valid (4 fragments, output: CLAUDE.md)
Processing: docs/intro.md (2.3 KB)
Processing: docs/features.md (5.1 KB)
Processing: docs/rules.md (8.7 KB)
Processing: docs/footer.md (1.2 KB)
Composed 4 fragments to CLAUDE.md (17.3 KB)
```

### Example 5: Dry-run

```bash
claudeutils compose agents/compose.yaml --dry-run
```

Output:
```
Dry-run: Would compose to CLAUDE.md
Fragments (in order):
  1. agent-core/fragments/communication.md
  2. agent-core/fragments/delegation.md
  3. local/project-specific-rules.md
Total fragment count: 3
Estimated output size: ~6 KB
Separator style: ---
Header adjustment: No
Validation mode: strict
```

### Example 6: Integration with justfile

```just
# Generate CLAUDE.md from composition
compose-claude:
    claudeutils compose agents/compose.yaml --verbose

# Validate composition configuration
compose-validate:
    claudeutils compose validate agents/compose.yaml

# Full composition build
build-agents: compose-validate compose-claude
    @echo "Agent configuration built"
```

Usage:
```bash
just compose-claude
just build-agents
```

---

## Configuration File Format

**YAML schema** (agents/compose.yaml):

```yaml
# Required
fragments:
  - path/to/file1.md
  - path/to/file2.md

output: path/to/output.md

# Optional
sources:
  key1: path/prefix
  key2: another/prefix

title: "Optional Document Title"
adjust_headers: false              # Default: false
separator: "---"                   # Options: ---, blank, none
validate_mode: "strict"            # Options: strict, warn

# Future: role compositions
roles:
  orchestrator:
    title: Orchestrator Agent
    fragments:
      - core/orchestrator-base.md
      - local/orchestrator-rules.md
```

**YAML anchors for path deduplication**:

```yaml
sources:
  core: &core agent-core/fragments
  local: &local src/fragments

fragments:
  - *core/communication.md
  - *core/delegation.md
  - *local/project-specific.md
```

---

## Error Handling

### Configuration Errors

**Missing config file**:
```bash
$ claudeutils compose nonexistent.yaml
Error: Configuration file not found: nonexistent.yaml
Exit code: 4
```

**Invalid YAML**:
```bash
$ claudeutils compose bad.yaml
Configuration error: Error parsing YAML: line 3, column 5
Exit code: 1
```

**Missing required fields**:
```bash
$ claudeutils compose incomplete.yaml
Configuration error: Missing required field: fragments
Exit code: 1
```

### Fragment Errors

**Missing fragment (strict mode)**:
```bash
$ claudeutils compose config.yaml
Error: Fragment not found: docs/intro.md
Exit code: 2
```

**Missing fragment (warn mode)**:
```bash
$ claudeutils compose config.yaml --validate warn
WARNING: Skipping missing fragment: docs/intro.md
Composed 2 of 4 fragments to output.md
Exit code: 0
```

### Output Errors

**Cannot create directory**:
```bash
$ claudeutils compose config.yaml
Error: Cannot create output directory: /readonly/path
Exit code: 3
```

**Cannot write file**:
```bash
$ claudeutils compose config.yaml
Error: Cannot write file: permission denied
Exit code: 3
```

---

## Integration Patterns

### Pattern 1: CI/CD Pipeline

```bash
#!/bin/bash
# Script: scripts/build-agents.sh

set -e  # Exit on error

echo "Validating configuration..."
claudeutils compose validate agents/compose.yaml

echo "Building CLAUDE.md..."
claudeutils compose agents/compose.yaml --verbose

echo "Agent configuration built successfully"
```

### Pattern 2: Pre-commit Hook

```bash
#!/bin/bash
# File: .git/hooks/pre-commit

if git diff --cached --name-only | grep -q 'agents/compose.yaml\|agent-core'; then
    echo "Composition changed, rebuilding..."
    claudeutils compose agents/compose.yaml || {
        echo "Composition failed, aborting commit"
        exit 1
    }
    git add CLAUDE.md
fi
```

### Pattern 3: Build System Integration

**justfile**:
```just
CLAUDE.md: agents/compose.yaml
    claudeutils compose agents/compose.yaml
```

**Makefile**:
```makefile
CLAUDE.md: agents/compose.yaml agent-core/fragments/*.md src/fragments/*.md
	claudeutils compose agents/compose.yaml
```

---

## Design Decisions

### Why Click Framework?

- Simple, declarative command definition
- Built-in help and version support
- Exit code handling
- Type conversion (Path, Choice)
- Nested command groups
- Already in use by existing CLI (cli.py)

### Why Config-First Interface?

- Reusable across multiple invocations
- Version-controllable composition definition
- Explicit over implicit (config is the contract)
- Supports complex setups without CLI arg explosion
- Works well in build systems (Makefile, justfile)

### Why YAML Over JSON?

- Human-readable and editable
- Supports comments
- YAML anchors for path deduplication
- PyYAML is standard in Python ecosystem
- Matches existing config patterns (justfile, ruff, mypy)

### Why Separate --validate Flag?

- Config can specify default, CLI overrides for specific runs
- Explicit intent (--validate warn is clearer than --ignore-missing)
- Mirrors compose() function API
- Enables workflow variation without config changes

### Why --dry-run Instead of Config Option?

- Config should be reproducible (no ephemeral options)
- --dry-run is operational, not part of composition definition
- Enables testing without side effects
- Follows common CLI patterns (terraform, git)

---

## Command Hierarchy

```
claudeutils
├── compose <config-file>
│   ├── --output
│   ├── --validate
│   ├── --verbose
│   └── --dry-run
├── compose role <name> [output]
│   ├── --config
│   └── --validate
├── compose validate <config-file>
└── --version, --help
```

---

## Future Extensions

### Planned Subcommands

1. `claudeutils compose validate` - Validate config without generating
2. `claudeutils compose role <name>` - Generate role file from template
3. `claudeutils compose status` - Show composition state and fragments
4. `claudeutils compose diff` - Show differences from previous version
5. `claudeutils compose watch` - Auto-rebuild on fragment changes

### Planned Options

- `--config-vars` - Pass substitution variables
- `--fragment-meta` - Include fragment metadata in output
- `--debug` - Extra verbose output for troubleshooting
- `--output-format` - Support output formats (markdown, HTML, etc.)

---

## Artifacts Created

### CLI Design Document

**Location**: `/Users/david/code/claudeutils/scratch/consolidation/design/cli-design.md`

**Contents**:
- Subcommand structure (compose, compose role, compose validate)
- Command-line argument specifications (required/optional, types, defaults)
- 8 complete usage examples (basic, role files, validation, warn mode, dry-run, integrations)
- pyproject.toml entry point definition
- Click-based CLI module implementation
- Error handling specifications (exit codes, error messages)
- Integration patterns (CI/CD, pre-commit, build systems)
- Design decisions (rationale for Click, config-first, YAML)
- Command hierarchy
- Future extensions

---

## Verification

### Design Matches Requirements

- [x] Subcommand structure designed (compose, compose role, future modes)
- [x] Arguments specified (CONFIG_FILE required, --output/--validate/--verbose/--dry-run optional)
- [x] Usage examples provided (8 complete examples covering all modes)
- [x] pyproject.toml integration defined (entry point, dependencies)
- [x] Error handling specified (exit codes, error messages)
- [x] Integration patterns documented (justfile, Makefile, CI/CD)
- [x] Design decisions documented (Click, config-first, YAML rationale)

### Design Matches Patterns

- [x] Follows core module design (`compose()` and `load_config()` APIs)
- [x] Matches existing CLI structure (Click framework, version option)
- [x] Supports both tuick pattern (role files with header adjustment) and emojipack pattern (YAML config)
- [x] Config-first philosophy (YAML as source of truth, CLI overrides)
- [x] Clear error codes and messages
- [x] Integration-friendly (works with build systems)

---

## Success Criteria Met

- [x] CLI design created at `/Users/david/code/claudeutils/scratch/consolidation/design/cli-design.md`
- [x] Document includes subcommand structure (compose, compose role, compose validate)
- [x] Document includes argument specifications (required/optional, types, defaults)
- [x] Document includes usage examples (8 complete examples)
- [x] Document includes pyproject.toml entry point definition
- [x] Design matches patterns in core module design
- [x] Execution report documents CLI decisions

---

## Notes

### Existing Design Artifact

CLI design artifact already existed from earlier phase (comprehensive 1047-line design document). This step verified the design matches:
- Core module API (`compose()`, `load_config()`)
- Existing CLI structure (Click framework)
- Project patterns (justfile integration, error handling)
- Requirements (YAML-driven, role generation, extensibility)

No modifications needed; design is complete and ready for implementation.

### Next Steps

Phase 3 Step 4 will implement the CLI based on this design specification.
