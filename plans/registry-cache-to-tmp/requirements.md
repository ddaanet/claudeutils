**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Registry Cache to Tmp

Move continuation registry cache from system TMPDIR to project-local `tmp/`.

## Requirements

### Functional Requirements

**FR-1: Relocate registry cache**
Move the continuation registry cache storage from `$TMPDIR` (system temp) to `<project-root>/tmp/` (project-local, gitignored).
- Acceptance: Registry cache files created in `tmp/`, not in system temp
- Acceptance: Existing cache entries migrated or gracefully abandoned (no crash on missing old cache)
- Acceptance: Cache works across worktrees (shared `tmp/` in parent directory)

### Constraints

**C-1: Consistent with tmp-directory convention**
All temporary/cache files use project-local `tmp/` per `agent-core/fragments/tmp-directory.md`.

### Out of Scope

- Changing cache format or eviction policy
- Moving other caches (token cache already uses sqlite in project)
