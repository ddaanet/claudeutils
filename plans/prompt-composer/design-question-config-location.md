# Design Question: Role Configuration File Location

- **Status**: ✅ RESOLVED by Opus
- **Created**: 2025-12-26
- **Resolved**: 2025-12-26
- **Context**: Module system directory structure refinement

---

## DECISION: Option 3 (Modified) - `agents/roles/`

**Rationale**: Role configs are specifications that define composition recipes. They
belong alongside role outputs, not buried in module hierarchy.

**Naming Strategy**: Use `.next.md` suffix during development to avoid overwriting
existing files.

**See**: Opus agent output (agentId: a8ddc9f) for complete analysis.

**Key Points**:

- Config location: `agents/roles/{role}.yaml`
- Development output: `agents/role-{role}.next.md`
- Production output: `agents/role-{role}.md` (after cutover)
- Archive old files: `agents/archive/` during migration

---

## ORIGINAL QUESTION

---

## Updated Directory Structure

**Confirmed changes**:

```
agents/
├── modules/              # Relocated from root modules/
│   ├── src/             # Semantic sources (14 modules)
│   ├── gen/             # Generated variants
│   └── MODULE_INVENTORY.md
├── role-planning.md     # Generated roles live directly in agents/
├── role-code.md
├── role-lint.md
├── role-execute.md
├── role-refactor.md
├── role-review.md
├── role-remember.md
├── rules-commit.md      # Skills also in agents/
├── rules-handoff.md
└── AGENTS.md
```

---

## Open Question: Role Config Location

**Role configs** are YAML files that specify:

- Which modules to include
- Target model class (strong/standard/weak)
- Rule budget
- Section structure

**Example**: `planning.yaml`, `code.yaml`, etc.

### Option 1: `agents/configs/`

```
agents/
├── configs/
│   ├── planning.yaml
│   ├── code.yaml
│   ├── lint.yaml
│   ├── execute.yaml
│   ├── refactor.yaml
│   ├── review.yaml
│   └── remember.yaml
├── modules/
├── role-planning.md
└── ...
```

**Pros**:

- Clear separation: configs vs generated files
- Keeps agents/ root clean
- Parallel to modules/ structure

**Cons**:

- Generic name "configs" - what kind of configs?
- Not immediately obvious these are role configs

---

### Option 2: `agents/modules/configs/`

```
agents/
├── modules/
│   ├── src/
│   ├── gen/
│   ├── configs/        # Role configs under modules
│   │   ├── planning.yaml
│   │   └── ...
│   └── MODULE_INVENTORY.md
├── role-planning.md
└── ...
```

**Pros**:

- Role configs are module composition specs
- Everything module-related in one place
- Clear hierarchy: modules → configs

**Cons**:

- Configs are not modules themselves
- Might be confusing (configs alongside src/gen)
- Longer path

---

### Option 3: `agents/roles/`

```
agents/
├── roles/              # Role-specific files
│   ├── planning.yaml
│   ├── code.yaml
│   └── ...
├── modules/
├── role-planning.md
└── ...
```

**Pros**:

- Clear purpose: role-related files
- Short path
- Parallel to modules/ for discoverability

**Cons**:

- Could be confused with generated role files
- Generated files in root, configs in subdirectory (asymmetric)

---

### Option 4: Root `roles/`

```
roles/
├── planning.yaml
├── code.yaml
└── ...

agents/
├── modules/
├── role-planning.md
└── ...
```

**Pros**:

- Clear separation: source (roles/) vs output (agents/)
- Conceptually: configs → generation pipeline → output

**Cons**:

- Creates another top-level directory
- Breaks agents/ as single location for all agent files
- Less discoverable

---

### Option 5: Co-located with generated files

```
agents/
├── modules/
├── role-planning.md
├── role-planning.yaml  # Config next to output
├── role-code.md
├── role-code.yaml
└── ...
```

**Pros**:

- Immediate association: config → output
- No extra directories
- Easy to find related files

**Cons**:

- Clutters agents/ root with 14+ files
- Config and output mixed (could be confusing)
- Harder to see all configs at once

---

## Considerations for Opus

1. **Discoverability**: How easy to find configs when editing?
2. **Clarity**: Does location make purpose obvious?
3. **Maintainability**: Will structure make sense in 6 months?
4. **Pipeline flow**: Does location reflect generation flow?
5. **Precedent**: Any similar patterns in the project?

---

## Current Project Structure Context

```
.
├── agents/              # Agent instruction files
│   ├── AGENTS.md
│   ├── design-decisions.md
│   ├── role-*.md
│   └── rules-*.md
├── plans/               # Planning documents
├── src/                 # Python source code
│   └── claudeutils/
├── tests/               # Test files
├── pyproject.toml       # Project config
├── justfile             # Task definitions
└── README.md
```

**Pattern**: Configuration files generally at project root (`pyproject.toml`) or
co-located with what they configure.

---

## Recommendation Request

**Opus**: Please evaluate options and recommend:

1. **Preferred location** for role config YAML files
2. **Rationale** based on considerations above
3. **Any alternative** not listed that would be superior
4. **Naming convention** if directory name should differ

Consider:

- This is a permanent structure decision
- Configs will be edited when adding/removing modules
- Pipeline: `config.yaml` → variant generation → role composition → `role-{name}.md`
- 7 role configs total (planning, code, lint, execute, refactor, review, remember)

---

**END OF QUESTION**
