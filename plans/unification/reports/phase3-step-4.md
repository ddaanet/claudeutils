# Phase 3 Step 4 Execution Report: YAML Configuration Schema Design

**Date**: 2026-01-19
**Step**: Phase 3 Step 4 - Design YAML Configuration Schema
**Status**: Complete
**Artifacts**: `/Users/david/code/claudeutils/scratch/consolidation/design/yaml-schema.md`

---

## Objective

Design the YAML configuration format for composition definitions, supporting both agents mode (CLAUDE.md generation) and role mode (role-*.md generation) with path deduplication via YAML anchors.

---

## Execution Summary

### Documents Reviewed

1. **Core Module Design** (`scratch/consolidation/design/core-module-design.md`)
   - Reviewed compose() function signature and parameters
   - Confirmed configuration dictionary structure
   - Identified validation modes (strict/warn)
   - Noted optional fields (title, adjust_headers, separator)

2. **CLI Design** (`scratch/consolidation/design/cli-design.md`)
   - Reviewed command-line interface to YAML mapping
   - Confirmed CLI override behavior (output, validate flags)
   - Noted exit code patterns for different error types
   - Identified integration patterns (Makefile, justfile)

3. **Reference Implementation** (`/Users/david/code/emojipack/agents/compose.yaml`)
   - Analyzed YAML anchor usage pattern
   - Confirmed sources section structure
   - Validated fragment list ordering approach
   - Noted simplicity of configuration (minimal required fields)

### Schema Design Decisions

#### Required Fields

**`fragments`** (List[str])
- Ordered list of fragment file paths
- Non-empty list required
- Order preserved exactly in output
- Paths can be absolute, relative, or use YAML anchors

**`output`** (str)
- Output file path
- Parent directory created automatically
- Overwrites existing file without prompt

**Rationale**: Minimal required fields keep simple use cases simple while enabling complex compositions through optional fields.

#### Optional Fields

**`sources`** (Dict[str, str])
- Path prefix mappings for YAML anchor deduplication
- Pattern: `core: &core agent-core/fragments`
- Used with `*core/file.md` syntax in fragments list
- Not for variable substitution (YAML anchors handle expansion)

**`mode`** (str: "agents" | "role" | "skill")
- Composition mode determines default behaviors
- `agents`: Default, flat composition (CLAUDE.md)
- `role`: Header adjustment enabled by default
- `skill`: Future expansion, similar to agents
- Default: "agents"

**`title`** (str | null)
- Optional markdown header prepended as `# {title}\n\n`
- Used for role files: "Orchestrator Agent"
- Typically omitted for CLAUDE.md (fragments have headers)
- Default: None

**`adjust_headers`** (bool)
- Increase all headers by 1 level (# → ##)
- Enables proper hierarchy when composing role files
- Not used for flat CLAUDE.md compositions
- Default: false (agents mode), true (role mode)

**`separator`** (str: "---" | "blank" | "none")
- Visual separator between fragments
- `"---"`: Markdown horizontal rule (default)
- `"blank"`: Single blank line
- `"none"`: No separator
- Default: "---"

**`validate_mode`** (str: "strict" | "warn")
- Fragment validation strategy
- `"strict"`: Fail-fast on missing fragment (default)
- `"warn"`: Skip missing, log warnings
- Default: "strict"

#### YAML Anchor Pattern

**Pattern**:
```yaml
sources:
  core: &core agent-core/fragments
  local: &local src/fragments

fragments:
  - *core/communication.md
  - *local/project-rules.md
```

**How it works**:
1. `&core` defines anchor pointing to `agent-core/fragments`
2. `*core` references anchor, YAML expands to full path
3. `*core/communication.md` → `agent-core/fragments/communication.md`
4. Expansion happens during YAML parsing (before Python sees config)

**Benefits**:
- DRY: Define path once, reference many times
- Maintainability: Update path in one location
- Clarity: Intent visible in sources section
- No custom substitution logic needed (native YAML)

### Validation Rules Defined

#### Load-time Validation (Schema)

Performed by `load_config()` function:

1. Valid YAML syntax
2. Required fields present: `fragments`, `output`
3. `fragments` is non-empty list
4. `output` is non-empty string
5. Optional field types correct (sources: dict, adjust_headers: bool, etc.)
6. Enum validation (mode, separator, validate_mode)
7. Unknown fields ignored (forward compatibility)

**Errors**: ConfigurationError with descriptive message

#### Compose-time Validation (Files)

Performed by `compose()` function:

**Strict mode**:
- Pre-validate all fragments exist
- Collect all missing paths
- Raise FileNotFoundError with complete list
- No partial output created

**Warn mode**:
- Check each fragment during processing
- Log warning for missing fragments
- Skip missing, continue with available
- Create partial output
- Print summary: "Composed X of Y fragments"

**Errors**: FileNotFoundError (strict), warnings to stderr (warn)

### Examples Created

Five complete examples provided in schema document:

1. **Simple CLAUDE.md (agents mode)**
   - Minimal config with YAML anchors
   - Default behaviors (no header adjustment)
   - Horizontal rule separators
   - Strict validation

2. **Role File (role mode)**
   - Document title prepended
   - Header adjustment enabled
   - Demonstrates hierarchy creation
   - Multiple source paths (core + roles)

3. **Multi-project with Anchors**
   - Three source paths (core, local, project)
   - Mixed fragment sources
   - Warn mode for optional fragments
   - Complex composition pattern

4. **Simple Without Anchors**
   - Minimal configuration
   - Direct path specification
   - Good for simple cases
   - Easy to upgrade to anchors later

5. **Multiple Configurations**
   - Different configs for different purposes
   - Minimal (distribution), expanded (development)
   - CLI override examples

### Schema Documentation Structure

Created comprehensive schema document with:

1. **Overview** - Design principles, file location
2. **Complete Schema Definition** - Root level fields, type specification
3. **Detailed Field Specifications** - Each field with type, purpose, constraints, examples
4. **Validation Rules** - Load-time and compose-time validation approaches
5. **YAML Anchor Usage Pattern** - Syntax, benefits, examples
6. **Complete Schema Examples** - Five realistic examples with explanations
7. **Schema Validation Approach** - Two-phase validation with implementation guidance
8. **CLI Integration** - How config maps to CLI commands
9. **Forward Compatibility** - Unknown fields allowed, planned extensions
10. **Summary** - Key features and design balance

---

## Design Decisions

### 1. YAML Anchors vs Variable Substitution

**Decision**: Use YAML anchors for path deduplication, not custom variable substitution.

**Rationale**:
- YAML anchors are native YAML feature (no custom parsing needed)
- Expansion happens during YAML parsing (transparent to Python)
- Simpler implementation (no substitution logic in compose.py)
- Matches emojipack pattern (proven approach)
- Standard YAML pattern familiar to developers

**Alternative rejected**: Custom variable substitution (`${VAR}` style) would require:
- Custom parsing logic
- Variable resolution order rules
- Error handling for undefined variables
- More complex implementation

### 2. Minimal Required Fields

**Decision**: Only `fragments` and `output` required, all else optional.

**Rationale**:
- Simple use cases remain simple (2-field config works)
- Progressive disclosure (add options as needed)
- Clear separation: required vs optional
- Reduces learning curve for basic usage
- Enables complex compositions without forcing complexity

**Alternative rejected**: More required fields (title, mode, separator) would:
- Force configuration of features not always needed
- Increase verbosity for simple cases
- Reduce flexibility

### 3. Mode-Specific Defaults

**Decision**: Different modes (agents, role, skill) have different default behaviors.

**Rationale**:
- `adjust_headers: true` makes sense for role files, not CLAUDE.md
- Mode encapsulates intent (role vs agents vs skill)
- Reduces configuration boilerplate
- Explicit override available when needed
- Enables future mode-specific behaviors

**Alternative rejected**: Same defaults for all modes would:
- Require explicit configuration every time
- Lose semantic meaning of mode
- Miss opportunity to encode best practices

### 4. Two-Phase Validation

**Decision**: Schema validation at load time, file validation at compose time.

**Rationale**:
- Fail-fast on configuration errors (before any I/O)
- Separate concerns: structure vs content
- Clear error messages for each phase
- Strict mode: all-or-nothing (no partial output)
- Warn mode: graceful degradation

**Alternative rejected**: Single-phase validation would:
- Mix schema and file errors in single message
- Reduce clarity of error reporting
- Make strict/warn mode harder to implement

### 5. Strict Mode as Default

**Decision**: `validate_mode: "strict"` is default, warn mode opt-in.

**Rationale**:
- Fail-fast prevents silent errors
- Explicit intent for optional fragments (warn mode)
- Better for CI/CD (catch missing files early)
- Matches principle: errors should not pass silently
- Warn mode available when needed (environment-specific content)

**Alternative rejected**: Warn as default would:
- Allow silent failures (missing fragments unnoticed)
- Reduce confidence in compositions
- Violate error handling principle

---

## Artifacts Created

### Primary Artifact

**File**: `/Users/david/code/claudeutils/scratch/consolidation/design/yaml-schema.md`

**Content**:
- 920 lines of comprehensive schema documentation
- Complete field specifications with types, defaults, examples
- Validation rules (load-time and compose-time)
- YAML anchor usage patterns with detailed examples
- 5 complete configuration examples
- CLI integration guidance
- Forward compatibility notes
- Implementation guidance for load_config() and compose()

**Sections**:
1. Overview and design principles
2. Complete schema definition (root level + types)
3. Detailed field specifications (each field documented)
4. Validation rules (two-phase approach)
5. YAML anchor usage pattern (syntax + benefits)
6. Complete schema examples (5 realistic examples)
7. Schema validation approach (implementation guidance)
8. CLI integration (how config maps to commands)
9. Forward compatibility (unknown fields, extensions)
10. Summary (key features, design balance)

### Secondary Artifact

**File**: `/Users/david/code/claudeutils/plans/unification/reports/phase3-step-4.md` (this document)

**Content**:
- Execution summary and process
- Design decisions with rationale
- Schema structure overview
- Validation approach
- Examples summary
- Success criteria verification

---

## Success Criteria Verification

### ✓ YAML schema design created at scratch/consolidation/design/yaml-schema.md

**Status**: Complete

The schema document exists and contains comprehensive design.

### ✓ Document includes complete schema definition (all fields, types, structure)

**Status**: Complete

Schema definition includes:
- Required fields: `fragments`, `output`
- Optional fields: `sources`, `mode`, `title`, `adjust_headers`, `separator`, `validate_mode`
- Full type specifications (List[str], str, bool, enum types)
- Root level structure with TypeScript-like notation for clarity

### ✓ Document includes validation rules (required fields, types, path checks)

**Status**: Complete

Validation rules documented:
- **Load-time**: Schema validation (required fields, types, enums)
- **Compose-time**: File validation (strict vs warn modes)
- **Path checks**: Fragment existence, output writeability
- **Implementation guidance**: Example code for load_config() validation

### ✓ Document includes examples (at least 3: simple, role mode, multi-project)

**Status**: Complete (5 examples provided)

Examples included:
1. Simple CLAUDE.md (agents mode) - minimal config with anchors
2. Role File (role mode) - title + header adjustment
3. Multi-project with Anchors - 3 source paths, complex composition
4. Simple Without Anchors - basic case without deduplication
5. Multiple Configurations - different configs for different purposes

### ✓ Schema matches emojipack pattern from design.md

**Status**: Complete

Matches emojipack reference:
- YAML anchors for path deduplication (`sources` with `&anchor`)
- Fragment list is ordered sequence
- Minimal required fields (fragments, output)
- Same anchor syntax (`*core/file.md`)
- Configuration-driven approach (YAML as source of truth)

### ✓ Execution report documents schema decisions

**Status**: Complete (this document)

Report documents:
- Design decisions with rationale (5 key decisions)
- Alternative approaches considered and rejected
- Schema structure and validation approach
- Examples summary
- Success criteria verification

---

## Next Steps

**Phase 3 Step 5**: Implement Core Composition Module
- Implement compose.py based on core-module-design.md
- Implement load_config() with schema validation
- Implement text utilities (increase_header_levels, normalize_newlines, etc.)
- Write unit tests for composition functions
- Verify against YAML schema design

**Phase 3 Step 6**: Implement CLI Commands
- Implement cli.py based on cli-design.md
- Wire compose command to compose() function
- Add CLI option handling (--output, --validate, --verbose, --dry-run)
- Add exit code handling
- Write CLI integration tests

---

## Summary

Successfully designed comprehensive YAML configuration schema for composition definitions. Schema provides minimal required fields (fragments, output) with rich optional configuration (sources, mode, title, adjust_headers, separator, validate_mode). YAML anchor pattern enables path deduplication without custom parsing logic. Two-phase validation (schema + files) with strict/warn modes provides clear error handling. Five complete examples demonstrate simple to complex use cases. Schema documentation provides implementation guidance for compose.py and cli.py. All success criteria verified.
