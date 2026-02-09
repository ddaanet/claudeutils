# Step 1.1 Execution Report: Cooperative Skill Registry Builder

## Objective

Implement registry builder function that scans for cooperative skills from 3 sources with frontmatter metadata extraction.

## Implementation Summary

Added the following functions to `agent-core/hooks/userpromptsubmit-shortcuts.py`:

### Core Functions

1. **`build_registry() -> Dict[str, Dict[str, Any]]`**
   - Main entry point for registry building
   - Scans all three discovery sources
   - Returns dictionary mapping skill names to continuation metadata
   - Structure: `{"skill-name": {"cooperative": True, "default_exit": [...]}}`

2. **`extract_frontmatter(skill_path: Path) -> Optional[Dict[str, Any]]`**
   - Parses YAML frontmatter from SKILL.md files
   - Handles malformed files gracefully (returns None)
   - Requires yaml library (gracefully degrades if unavailable)

3. **`get_enabled_plugins() -> List[str]`**
   - Reads `~/.claude/settings.json` → `enabledPlugins` list
   - Returns empty list if settings missing or malformed

4. **`get_plugin_install_path(plugin_name: str, project_dir: str) -> Optional[str]`**
   - Resolves plugin install path from `~/.claude/plugins/installed_plugins.json`
   - Implements scope filtering:
     - `scope: "user"` → include for all projects
     - `scope: "project"` → include only if `projectPath` matches `$CLAUDE_PROJECT_DIR`
   - Returns None if plugin not found or scope doesn't match

5. **`scan_skill_files(base_path: Path) -> List[Path]`**
   - Recursive glob for `**/SKILL.md` under base path
   - Returns empty list if base path doesn't exist

### Discovery Sources

**1. Project-local skills:**
- Scans: `$CLAUDE_PROJECT_DIR/.claude/skills/**/SKILL.md`
- Extracts frontmatter with YAML parser
- Checks `continuation.cooperative: true`
- Extracts `continuation.default-exit` list

**2. Enabled plugin skills:**
- Reads `~/.claude/settings.json` → `enabledPlugins`
- For each enabled plugin, resolves install path from `installed_plugins.json`
- Applies scope filtering (user vs project)
- Scans `<installPath>/skills/**/SKILL.md`
- Same frontmatter extraction as project-local

**3. Built-in skills:**
- `BUILTIN_SKILLS` dictionary (empty initially)
- Fallback for built-in skills that need continuation support
- Updated via `registry.update(BUILTIN_SKILLS)` after scanning

### Error Handling

- **Missing YAML library:** `try/except ImportError` sets `yaml = None`, `extract_frontmatter` returns None
- **Malformed YAML:** `extract_frontmatter` returns None, skill skipped
- **Missing frontmatter:** Skills without `---` markers skipped
- **Missing continuation block:** Skills without `continuation` key skipped
- **Non-cooperative skills:** Skills with `cooperative: false` or missing excluded
- **Missing files:** `scan_skill_files` returns empty list for non-existent paths
- **Plugin uninstalled:** `get_plugin_install_path` returns None, plugin skipped

All errors logged silently (no output) to maintain hook's pass-through semantics for non-skill input.

## Registry Structure

```python
{
    "design": {
        "cooperative": True,
        "default_exit": ["/handoff --commit", "/commit"]
    },
    "plan-adhoc": {
        "cooperative": True,
        "default_exit": ["/handoff --commit", "/commit"]
    },
    # ... etc
}
```

**Key extraction:**
- Skill name from frontmatter `name` field
- Fallback to parent directory name if `name` missing

**Metadata extracted:**
- `cooperative: True` (skills with `cooperative: false` excluded)
- `default_exit: [...]` (list of skill invocations)

## Validation Status

**Implementation complete.** Validation deferred to Phase 3 integration tests:

- [ ] Verify project-local skills discovered (6 skills from `agent-core/skills/*/SKILL.md`)
- [ ] Verify enabled plugins scanned correctly
- [ ] Verify non-cooperative skills excluded
- [ ] Registry contains expected 6 cooperative skills with correct metadata

**Note:** Current skills do NOT have continuation frontmatter yet. Phase 2 will add frontmatter to skills. Phase 3 integration tests will verify complete end-to-end flow.

## Files Modified

- `agent-core/hooks/userpromptsubmit-shortcuts.py`:
  - Added imports: `glob`, `os`, `Path`, `typing` types, `yaml` (optional)
  - Added `BUILTIN_SKILLS` constant
  - Added 6 new functions (165 lines)

## Next Steps

Phase 1 continues with:
- Step 1.2: Implement continuation parser with 3 modes
- Step 1.3: Add Tier 3 processing to hook main()
- Step 1.4: Implement caching with mtime-based invalidation

After Phase 1 complete:
- Phase 2: Add continuation frontmatter to 6 cooperative skills
- Phase 3: Tests + validation of registry builder

## Success Criteria Status

**Pending validation in Phase 3:**

- [ ] Registry contains all 6 cooperative skills from design
- [ ] Each entry has `cooperative: True` and `default_exit` list
- [ ] Non-cooperative skills excluded from registry
- [ ] Function returns dictionary mapping skill names to metadata

**Implementation complete, validation deferred per runbook phasing.**
