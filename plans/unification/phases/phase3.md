# Consolidation: Phase 3

**Context**: Read `consolidation-context.md` for full context before executing this phase.

---

## Phase 3: Design Unified Composition API

Create `scratch/consolidation/design/compose-api.md`:

### 3.1 Core Composition Module

Location: `src/claudeutils/compose.py`

**Features** (extracted from tuick/build.py):
- Fragment concatenation
- Header level manipulation (`increase_header_levels`)
- Decorator injection (title + separators)
- YAML config parsing (read compose.yaml)
- Multiple output modes:
  - `agents` mode: AGENTS.md generation
  - `role` mode: Role file generation with headers
  - `skill` mode: (future) Skill template generation

### 3.2 CLI Entry Point

Location: `src/claudeutils/cli_compose.py`

```toml
# pyproject.toml
[project.scripts]
claudeutils = "claudeutils.cli:main"

# Subcommand: claudeutils compose
```

**Usage patterns**:
```bash
# Simple AGENTS.md generation
claudeutils compose agents/compose.yaml

# Role generation (tuick pattern)
claudeutils compose role \
  --output agents/roles/commit-agent.md \
  --title "Commit Agent" \
  agents/src/role-definition-commit.md \
  agents/src/core.md \
  agents/src/git.md
```

### 3.3 YAML Schema

```yaml
# agents/compose.yaml
sources:
  core: agent-core/fragments

fragments:
  - core/AGENTS-framework.md
  - core/communication.md
  - core/delegation.md
  - src/project-specific.md

output: AGENTS.md
```

---


---

**Execution Instructions**:
1. Read consolidation-context.md for prerequisites, critical files, and execution notes
2. Execute this phase following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
