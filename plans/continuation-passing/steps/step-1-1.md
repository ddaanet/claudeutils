# Step 1.1

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.1: Implement Cooperative Skill Registry Builder

**Objective:** Build registry of cooperative skills from 3 sources with frontmatter metadata extraction.

**Execution Model:** Sonnet

**Implementation:**

Create registry builder function that scans for cooperative skills:

**Three discovery sources:**

1. **Project-local skills:**
   - Glob: `$CLAUDE_PROJECT_DIR/.claude/skills/**/SKILL.md`
   - Direct frontmatter scan

2. **Enabled plugins:**
   - Read `~/.claude/settings.json` → `enabledPlugins` list
     ```json
     {
       "enabledPlugins": ["plugin-dev", "my-custom-plugin"]
     }
     ```
   - Read `~/.claude/plugins/installed_plugins.json` → resolve install paths
     ```json
     {
       "plugin-dev": {
         "installPath": "/Users/user/.claude/plugins/cache/claude-plugins-official/plugin-dev/abc123",
         "scope": "user"
       },
       "my-custom-plugin": {
         "installPath": "/path/to/custom/plugin",
         "scope": "project",
         "projectPath": "/Users/user/code/myproject"
       }
     }
     ```
   - Check plugin scope filtering:
     - `scope: "user"` → include for all projects
     - `scope: "project"` → include only if `projectPath` matches `$CLAUDE_PROJECT_DIR`
   - Glob each enabled plugin: `<installPath>/skills/**/SKILL.md`

3. **Built-in skills (fallback list):**
   ```python
   BUILTIN_SKILLS = {
       # Empty initially — all cooperative skills are project-local or plugin-based
       # Add entries here if built-in skills need continuation support
   }
   ```

**Frontmatter extraction:**

For each SKILL.md file found:
- Parse YAML frontmatter
- Check `continuation.cooperative: true`
- Extract `continuation.default-exit` list (array of skill references)
- Skip if `cooperative` is missing or false

**Registry structure:**
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

**Error handling:**
- Skip malformed YAML (log warning, continue)
- Skip skills without continuation block
- Handle missing files gracefully (plugin uninstalled but in settings)

**Expected Outcome:**

Function returns dictionary mapping skill names to metadata. Calling `build_registry()` discovers all cooperative skills and their default exits.

**Validation:**
- Verify project-local skills discovered (agent-core/skills/*/SKILL.md)
- Verify enabled plugins scanned correctly
- Verify non-cooperative skills excluded

**Success Criteria:**
- Registry contains all 6 cooperative skills from design:
  - `/design`, `/plan-adhoc`, `/plan-tdd`, `/orchestrate` → `default_exit: ["/handoff --commit", "/commit"]`
  - `/handoff` → `default_exit: ["/commit"]` (only when `--commit` flag present)
  - `/commit` → `default_exit: []` (terminal)
- Each entry has `cooperative: True` and `default_exit` list
- Non-cooperative skills excluded from registry

**Report Path:** `plans/continuation-passing/reports/step-1-1-execution.md`

---
