# Step 5.2

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 5.2: Cleanup configuration and documentation

**Objective:** Remove `hooks` section from settings.json, remove `sync-to-parent` recipe from edify-plugin justfile, update fragment documentation to remove sync-to-parent references.

**Implementation:**

1. **Remove hooks section from .claude/settings.json:**

Delete the entire `hooks` key and its contents. Result should be:

```json
{
  "permissions": { ... },
  "attribution": { ... },
  "plansDirectory": "plans/claude/",
  "sandbox": { ... }
}
```

**Verification:** `jq '.hooks' .claude/settings.json` should return `null` (key removed entirely)

2. **Remove sync-to-parent recipe from edify-plugin/justfile:**

Delete the `sync-to-parent` recipe definition from `edify-plugin/justfile`.

**Verification:** `grep -q sync-to-parent edify-plugin/justfile` should exit 1 (not found)

3. **Update fragment documentation:**

Remove or update references to `sync-to-parent` in these files:

- `edify-plugin/fragments/claude-config-layout.md`:
  - Remove "Symlinks in .claude/" section
  - Remove `just sync-to-parent` references in hook configuration section

- `edify-plugin/fragments/sandbox-exemptions.md`:
  - Remove `just sync-to-parent` subsection

- `edify-plugin/fragments/project-tooling.md`:
  - Remove example: "Symlink management → `just sync-to-parent`"

- `edify-plugin/fragments/delegation.md`:
  - Update example showing `just sync-to-parent` to use plugin auto-discovery instead

**Update strategy:**
- Replace symlink workflow examples with plugin auto-discovery examples
- Remove sections that only apply to symlink-based distribution
- Preserve sections that remain relevant (hook configuration patterns, permission patterns)

**Expected Outcome:**
- `hooks` key removed from settings.json
- `sync-to-parent` recipe removed from edify-plugin justfile
- Fragment documentation updated to reflect plugin-based workflow

**Unexpected Result Handling:**
- If settings.json becomes invalid JSON: restore `hooks` key and try manual edit
- If fragments have additional sync-to-parent references: search with `grep -r "sync-to-parent" edify-plugin/fragments/`

**Validation:**
- `jq . .claude/settings.json` succeeds (valid JSON) and `jq '.hooks' .claude/settings.json` returns `null`
- `! grep -q sync-to-parent edify-plugin/justfile` (recipe removed)
- `grep -r "sync-to-parent" edify-plugin/fragments/` returns 0 results (all references removed)

**Success Criteria:**
- settings.json valid with no `hooks` section
- edify-plugin justfile has no sync-to-parent recipe
- Fragment documentation updated (no sync-to-parent references)

---
