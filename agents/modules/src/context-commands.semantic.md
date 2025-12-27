# Context Commands Module

---
author_model: claude-opus-4-5-20251101
semantic_type: project_context
expansion_sensitivity: explicit
target_rules:
  strong: 4-5
  standard: 5-7
  weak: 7-10
---

## Semantic Intent

Reference for development commands. Agents should use these exact commands rather than
inventing alternatives.

---

## Development Commands

### Primary Workflow

```bash
just dev              # Format, check, and test (full validation)
just test             # Run pytest only
just check            # Run ruff + mypy only
just format           # Auto-format code with ruff
```

### Role-Specific Commands

```bash
just role-code        # Run tests only (for code role - no linting)
just role-code -k X   # Run specific test matching pattern X
just lint             # Run linting only (for lint role)
```

### Tool Commands

```bash
uv run claudeutils list                    # List all sessions
uv run claudeutils extract <prefix>        # Extract feedback by session prefix
uv run claudeutils extract <prefix> -o X   # Extract to file X
```

### Dependency Management

```bash
uv add <package>           # Add runtime dependency
uv add --dev <package>     # Add development dependency
uv sync                    # Sync dependencies from lockfile
```

---

## Command Selection by Role

| Role    | Primary Command   | Never Run        |
|---------|-------------------|------------------|
| code    | `just role-code`  | `just check`     |
| lint    | `just lint`       | -                |
| execute | `just role-code`  | `just check`     |
| review  | `just dev`        | -                |
