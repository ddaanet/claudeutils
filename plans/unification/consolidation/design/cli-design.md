# CLI Design: Composition Commands (claudeutils compose)

**Date**: 2026-01-19
**Based on**: Core module design (core-module-design.md), Pattern analysis (design.md)
**Status**: Design artifact for Phase 3 Step 3
**Integration**: pyproject.toml entry points, CLI routing via Click or Typer

---

## Overview

The CLI provides entry points for composition operations, transforming the programmatic API (`compose.py`) into command-line accessible actions. The design follows the composition module's architecture, supporting both CLAUDE.md generation (flat composition) and role file generation (with header adjustment).

### Supported Commands

```
claudeutils compose <config-file>          # Generate from YAML config
claudeutils compose role <name> <output>   # Generate role file (future expansion)
claudeutils compose validate <config-file> # Validate configuration (future)
```

### Design Principles

1. **Config-first interface** - Primary mode reads YAML composition definition
2. **Minimal flags** - CLI args for path/output overrides only (config is source of truth)
3. **Fail-safe by default** - strict validation mode is default
4. **Progressive disclosure** - Basic usage simple, advanced options available via config
5. **Integration-friendly** - Works with justfile recipes, Makefile targets, shell scripts

---

## Subcommand Structure

### Primary Command: `claudeutils compose <config-file>`

**Purpose**: Generate composed markdown from YAML configuration file.

**Signature**:

```bash
claudeutils compose [OPTIONS] CONFIG_FILE
```

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

**Usage example**:

```bash
# Basic usage (config specifies everything)
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

---

### Subcommand: `claudeutils compose role`

**Purpose**: Generate role file from fragments with header adjustment (future expansion).

**Signature**:

```bash
claudeutils compose role [OPTIONS] ROLE_NAME [OUTPUT]
```

**Arguments**:

| Argument    | Type   | Required | Description                                              |
| ----------- | ------ | -------- | -------------------------------------------------------- |
| `ROLE_NAME` | String | Yes      | Role identifier (e.g., 'orchestrator', 'quiet-explore')  |
| `OUTPUT`    | Path   | No       | Output file path (default: `agents/role-{ROLE_NAME}.md`) |

**Options**:

| Flag             | Type   | Default             | Description                    |
| ---------------- | ------ | ------------------- | ------------------------------ |
| `--config, -c`   | Path   | agents/compose.yaml | Role composition template file |
| `--validate, -v` | Choice | strict              | Validation mode                |
| `--verbose`      | Flag   | False               | Print progress                 |

**Algorithm**:

1. Load role template from config (maps role names to fragment lists)
2. Look up `ROLE_NAME` in template
3. Resolve all fragments
4. Compose with `adjust_headers=true` (unless overridden in template)
5. Write to `OUTPUT` (or default path)

**Usage example**:

```bash
# Generate orchestrator role file
claudeutils compose role orchestrator

# Generate with specific output
claudeutils compose role quiet-explore agents/roles/quiet-explore.md

# Use alternate template
claudeutils compose role quiet-task --config agents/alt-compose.yaml
```

---

### Subcommand: `claudeutils compose validate`

**Purpose**: Validate composition configuration without generating output (future).

**Signature**:

```bash
claudeutils compose validate [OPTIONS] CONFIG_FILE
```

**Arguments**:

| Argument      | Type | Required | Description                     |
| ------------- | ---- | -------- | ------------------------------- |
| `CONFIG_FILE` | Path | Yes      | Path to YAML configuration file |

**Behavior**:

1. Load and parse configuration
2. Check all required fields present
3. Validate field types
4. Check all fragments exist
5. Print validation report

**Exit codes**:

- `0` - Valid
- `1` - Configuration error
- `2` - Fragment error

**Usage example**:

```bash
claudeutils compose validate agents/compose.yaml
```

---

## Command-Line Arguments Specification

### Global Flags (All Commands)

| Flag        | Type | Description              |
| ----------- | ---- | ------------------------ |
| `--help`    | Flag | Show command help        |
| `--version` | Flag | Show claudeutils version |

### Config Argument

**Purpose**: Path to YAML composition configuration file.

**Behavior**:

- Relative paths resolved from current working directory
- Absolute paths used as-is
- File must exist (error if missing)
- File must be valid YAML (error if malformed)

**Example paths**:

- `agents/compose.yaml` (relative)
- `./compose.yaml` (relative, explicit)
- `/path/to/agents/compose.yaml` (absolute)
- `~/projects/agents/compose.yaml` (home-relative)

### --output / -o

**Purpose**: Override output path specified in config.

**Behavior**:

- Relative paths resolved from CWD
- Absolute paths used as-is
- Parent directory created if needed
- Existing file overwritten without prompt
- If not provided, output from config used

**Example**:

```bash
claudeutils compose config.yaml --output dist/output.md
```

### --validate / -v

**Purpose**: Control error handling for missing fragments.

**Options**:

- `strict` (default) - Fail if any fragment missing
- `warn` - Log warnings, skip missing fragments

**Behavior**:

- Passed to compose() function's `validate_mode` parameter
- Strict mode: all fragments validated before writing
- Warn mode: missing fragments skipped with warnings

**Example**:

```bash
# Strict (fail on missing)
claudeutils compose config.yaml --validate strict

# Warn (skip missing, print warnings)
claudeutils compose config.yaml --validate warn
```

### --verbose

**Purpose**: Enable detailed progress output.

**Behavior**:

- Prints configuration loaded
- Prints each fragment being processed
- Prints fragment sizes and paths
- Prints final output summary
- Useful for debugging composition

**Example**:

```bash
claudeutils compose config.yaml --verbose
```

Output:

```
Loading config: agents/compose.yaml
Config valid (5 fragments, output: CLAUDE.md)
Processing: docs/intro.md (2.3 KB)
Processing: docs/features.md (5.1 KB)
Processing: docs/rules.md (8.7 KB)
Processing: docs/footer.md (1.2 KB)
Composed 4 fragments to CLAUDE.md (17.3 KB)
```

### --dry-run

**Purpose**: Validate configuration and show plan without writing.

**Behavior**:

- Load and validate configuration
- Check all fragments exist (strict mode only)
- Show composition plan
- Do not create output file
- Useful for testing configurations

**Example**:

```bash
claudeutils compose config.yaml --dry-run
```

Output:

```
Dry-run: Would compose to CLAUDE.md
Fragments:
  1. docs/intro.md (2.3 KB)
  2. docs/features.md (5.1 KB)
  3. docs/rules.md (8.7 KB)
Output size estimate: ~9 KB (before separators)
```

---

## Configuration File Format

### Composition Config (agents/compose.yaml)

**Schema**:

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
  quiet-explore:
    title: Quiet Explore Agent
    adjust_headers: true
    fragments:
      - core/quiet-explore-base.md
      - core/tool-preferences.md
```

**YAML Anchors for Path Deduplication**:

```yaml
sources:
  core: &core agent-core/fragments
  local: &local src/fragments

fragments:
  - *core/communication.md
  - *core/delegation.md
  - *local/project-specific.md
  - *core/footer.md
```

**Variables** (optional, for future template support):

```yaml
title: "Documentation for ${PROJECT_NAME}"
# Expanded via environment or config-specific substitution
```

---

## pyproject.toml Integration

### Entry Point Definition

**Location**: `pyproject.toml [project.scripts]`

```toml
[project.scripts]
claudeutils = "claudeutils.cli:main"
```

### CLI Module Structure

**File**: `src/claudeutils/cli.py`

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


@main.command()
@click.argument('role_name')
@click.argument('output', required=False)
@click.option('--config', '-c', type=click.Path(exists=True),
              default='agents/compose.yaml',
              help='Role composition template file')
@click.option('--validate', '-v', type=click.Choice(['strict', 'warn']),
              default='strict', help='Validation mode')
def compose_role(role_name, output, config, validate):
    """Generate role file from composition template."""
    # Implementation delegated to Phase 3 Step 4
    click.echo("Role composition coming in Phase 3 Step 4")


@main.command()
@click.argument('config_file', type=click.Path(exists=True))
def validate_command(config_file):
    """Validate composition configuration."""
    try:
        config_path = Path(config_file)
        config = load_config(config_path)
        click.echo(f"Valid configuration: {len(config['fragments'])} fragments")
    except Exception as e:
        click.echo(f"Validation error: {e}", err=True)
        raise SystemExit(1)


if __name__ == '__main__':
    main()
```

### Dependencies in pyproject.toml

```toml
[project]
dependencies = [
    "click>=8.0.0",  # CLI framework
    "PyYAML>=6.0",   # YAML parsing
]
```

### Installation

```bash
# Development install with CLI entry point
pip install -e .

# Usage after install
claudeutils compose agents/compose.yaml
```

---

## Usage Examples

### Example 1: Simple CLAUDE.md Generation

**Configuration** (`agents/compose.yaml`):

```yaml
fragments:
  - agent-core/fragments/communication.md
  - agent-core/fragments/delegation.md
  - agent-core/fragments/tool-preferences.md
  - local/project-specific-rules.md

output: CLAUDE.md
separator: "---"
validate_mode: strict
```

**Command**:

```bash
claudeutils compose agents/compose.yaml
```

**Output**:

```
Composed 4 fragments to CLAUDE.md
```

**CLAUDE.md structure**:

```markdown
[communication.md content]

---

[delegation.md content]

---

[tool-preferences.md content]

---

[project-specific-rules.md content]
```

---

### Example 2: Role File Generation with Header Adjustment

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
adjust_headers: true          # Increase headers by 1 level
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

[header content]

---

## Purpose

Coordinate work between specialized agents.

---

[rest of composition with adjusted headers]
```

---

### Example 3: Validation with Verbose Output

**Configuration** (`agents/compose.yaml`):

```yaml
fragments:
  - docs/intro.md
  - docs/features.md
  - docs/advanced.md
  - docs/footer.md

output: docs/README.md
```

**Command**:

```bash
claudeutils compose agents/compose.yaml --verbose
```

**Output**:

```
Loading config: agents/compose.yaml
Config valid (4 fragments, output: docs/README.md)
Processing: docs/intro.md (2.3 KB)
Processing: docs/features.md (5.1 KB)
Processing: docs/advanced.md (8.7 KB)
Processing: docs/footer.md (1.2 KB)
Composed 4 fragments to docs/README.md (17.3 KB)
```

---

### Example 4: Warn Mode (Skip Missing Fragments)

**Configuration** (`agents/compose.yaml`):

```yaml
fragments:
  - docs/intro.md
  - docs/optional-feature.md        # This file doesn't exist
  - docs/main-content.md

output: docs/output.md
validate_mode: warn                 # Won't fail on missing
```

**Command**:

```bash
claudeutils compose agents/compose.yaml
```

**Output**:

```
WARNING: Skipping missing fragment: docs/optional-feature.md
Composed 2 of 3 fragments to docs/output.md
```

**Generated file** (`docs/output.md`):

```markdown
[intro.md content]

---

[main-content.md content]
```

---

### Example 5: Integration with Makefile

**Makefile**:

```makefile
.PHONY: compose
compose:
	claudeutils compose agents/compose.yaml --verbose

.PHONY: validate
validate:
	claudeutils compose validate agents/compose.yaml

.PHONY: compose-role
compose-role:
	claudeutils compose role $(ROLE) --config agents/compose.yaml

.PHONY: compose-all
compose-all: compose compose-role
	@echo "All compositions complete"
```

**Usage**:

```bash
# Generate CLAUDE.md
make compose

# Validate configuration
make validate

# Generate specific role
make compose-role ROLE=orchestrator

# Generate all
make compose-all
```

---

### Example 6: Integration with justfile

**justfile**:

```just
# Generate CLAUDE.md from composition
compose-claude:
    claudeutils compose agents/compose.yaml --verbose

# Validate composition configuration
compose-validate:
    claudeutils compose validate agents/compose.yaml

# Generate role file
compose-role role:
    claudeutils compose role {{ role }} --config agents/compose.yaml

# Full composition build
build-agents: compose-validate compose-claude
    @echo "Agent configuration built"
```

**Usage**:

```bash
# Build CLAUDE.md
just compose-claude

# Validate
just compose-validate

# Generate role
just compose-role orchestrator

# Full build
just build-agents
```

---

### Example 7: Dry-run for Testing

**Command**:

```bash
claudeutils compose agents/compose.yaml --dry-run
```

**Output**:

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

---

### Example 8: Multiple Configurations

**Directory structure**:

```
agents/
  compose.yaml              # Default CLAUDE.md
  compose-expanded.yaml     # Extended version with more rules
  compose-minimal.yaml      # Minimal version for distribution
```

**Commands**:

```bash
# Standard composition
claudeutils compose agents/compose.yaml

# Expanded version
claudeutils compose agents/compose-expanded.yaml --output CLAUDE-expanded.md

# Minimal version for distribution
claudeutils compose agents/compose-minimal.yaml --output dist/CLAUDE.md
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
WARNING: Skipping missing fragment: docs/features.md
Composed 2 of 4 fragments to output.md
Exit code: 0
```

### Output Errors

**Cannot create output directory**:

```bash
$ claudeutils compose config.yaml
Error: Cannot create output directory: /readonly/path
Exit code: 3
```

**Cannot write output file**:

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

### Pattern 3: Watch Mode (with entr)

```bash
#!/bin/bash
# Rebuild CLAUDE.md when any fragment changes

ls agents/compose.yaml agent-core/fragments/*.md src/fragments/*.md | \
    entr claudeutils compose agents/compose.yaml --verbose
```

### Pattern 4: Build System Integration

**Makefile target**:

```makefile
CLAUDE.md: agents/compose.yaml agent-core/fragments/*.md src/fragments/*.md
	claudeutils compose agents/compose.yaml
```

**justfile target**:

```just
CLAUDE.md: agents/compose.yaml
    claudeutils compose agents/compose.yaml
```

---

## Future Extensions

### Planned Subcommands

1. **`claudeutils compose validate`** - Validate config without generating
2. **`claudeutils compose role <name>`** - Generate role file from template
3. **`claudeutils compose status`** - Show composition state and fragments
4. **`claudeutils compose diff`** - Show differences from previous version
5. **`claudeutils compose watch`** - Auto-rebuild on fragment changes

### Planned Options

- **`--config-vars`** - Pass substitution variables
- **`--fragment-meta`** - Include fragment metadata in output
- **`--debug`** - Extra verbose output for troubleshooting
- **`--output-format`** - Support output formats (markdown, HTML, etc.)

### Planned Features

- Configuration templates and inheritance
- Fragment discovery from directory patterns
- Per-fragment include/exclude conditions
- Output validation (check for required sections)

---

## Design Decisions

### Why Click Framework?

- Simple, declarative command definition
- Built-in help and version support
- Exit code handling
- Type conversion (Path, Choice)
- Nested command groups
- No external dependencies beyond PyYAML

### Why Config File First?

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
- \--dry-run is operational, not part of composition definition
- Enables testing without side effects
- Follows common CLI patterns (terraform, git)

---

## CLI Entry Point Routing

### Command Hierarchy

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

### Click Group Structure

```python
@click.group()
def main():
    """Root command group"""

@main.command()
def compose_command():
    """Subcommand: compose"""

@main.group()
def compose_group():
    """Group: compose subcommands"""

@compose_group.command()
def role():
    """Subcommand: compose role"""

@compose_group.command()
def validate():
    """Subcommand: compose validate"""
```

**Alternative: Single Command with Subcommands**

```bash
# If composition is the only CLI feature
claudeutils compose agents/compose.yaml
claudeutils role orchestrator
claudeutils validate agents/compose.yaml
```

**Current design uses group structure for future extensibility**.

---

## Testing Strategy

### CLI Testing

```python
# tests/test_cli.py

def test_compose_basic(tmp_path):
    """Test basic compose command"""
    config = create_test_config(tmp_path)
    result = runner.invoke(main, ['compose', str(config)])
    assert result.exit_code == 0

def test_compose_missing_config():
    """Test error on missing config"""
    result = runner.invoke(main, ['compose', 'nonexistent.yaml'])
    assert result.exit_code == 4

def test_compose_missing_fragment():
    """Test strict mode error"""
    result = runner.invoke(main, ['compose', 'config.yaml'])
    assert result.exit_code == 2
    assert "not found" in result.output

def test_compose_warn_mode():
    """Test warn mode continues on missing"""
    result = runner.invoke(main, ['compose', 'config.yaml', '--validate', 'warn'])
    assert result.exit_code == 0
    assert "WARNING" in result.output
```

---

## Summary

The CLI design provides:

1. **Primary command** - `claudeutils compose <config-file>` for YAML-driven composition
2. **Flexible options** - --output, --validate, --verbose, --dry-run for run-time control
3. **Clear subcommands** - Role generation and validation (future)
4. **Integration patterns** - Works with make, justfile, CI/CD, build systems
5. **Robust error handling** - Exit codes, clear error messages
6. **Config-first philosophy** - YAML configuration is source of truth
7. **pyproject.toml integration** - Standard Python entry point pattern

The design balances simplicity (config-driven default) with flexibility (CLI overrides) and provides clear upgrade path for future subcommands (role generation, validation, status, diff).
