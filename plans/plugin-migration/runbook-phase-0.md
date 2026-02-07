# Phase 0: Directory Rename

**Purpose:** Rename agent-core directory to edify-plugin across entire project (D-1)

**Dependencies:** None

**Model:** Haiku

**Estimated Complexity:** Trivial (git mv + path updates)

---

## Step 0.1: Rename agent-core → edify-plugin

**Objective:** Rename the submodule directory from `agent-core` to `edify-plugin` and update all references.

**Implementation:**

1. **Rename directory using git mv:**
```bash
git mv agent-core edify-plugin
```

2. **Update .gitmodules:**
   - Change `path = agent-core` to `path = edify-plugin`
   - Change `url` if needed (will change when repo published)

3. **Update root justfile:**
   - Search-replace: `agent-core/` → `edify-plugin/`
   - Affected recipes: `cache`, import path (future), recipe scripts referencing agent-core

4. **Update .claude/settings.json:**
   - Permissions.allow patterns: `Bash(agent-core/bin/...` → `Bash(edify-plugin/bin/...`
   - Hook commands: `$CLAUDE_PROJECT_DIR/agent-core/hooks/` → `$CLAUDE_PROJECT_DIR/edify-plugin/hooks/`

5. **Update CLAUDE.md:**
   - Fragment @ references: `@agent-core/fragments/` → `@edify-plugin/fragments/`
   - Cache @ references: `@.cache/just-help-agent-core.txt` → `@.cache/just-help-edify-plugin.txt`

6. **Update symlinks (relative paths auto-adjust):**
   - Symlinks use relative paths like `../../agent-core/skills/commit` → will become `../../edify-plugin/skills/commit`
   - Git mv handles this automatically for tracked symlinks
   - Verify symlinks still resolve after rename: `ls -la .claude/skills/commit`

7. **Update cache filenames:**
   - Rename `.cache/just-help-agent-core.txt` → `.cache/just-help-edify-plugin.txt`
   - Update agent-core/Makefile target names if needed

8. **Search for remaining references:**
```bash
# Find any remaining agent-core references (excluding git history)
grep -r "agent-core" --exclude-dir=.git --exclude-dir=edify-plugin .
```

9. **Test basic functionality:**
```bash
# Verify justfile still works
just --list

# Verify symlinks resolve
ls -la .claude/skills/commit

# Verify CLAUDE.md loads
# (manual: check that fragments load without errors on next session)
```

**Expected Outcome:**
- Directory renamed from `agent-core/` to `edify-plugin/`
- All references updated to use new name
- Symlinks still resolve correctly
- Justfile recipes work
- No broken @ references in CLAUDE.md

**Unexpected Result Handling:**
- If symlinks break: re-run `just sync-to-parent` from edify-plugin/ directory
- If grep finds additional references: update those files
- If justfile fails: check import paths and recipe scripts

**Validation:**
- `ls -d edify-plugin/` shows directory exists
- `ls -d agent-core/` returns "No such file or directory"
- `git status` shows renamed files, no deleted/added files
- `just --list` runs without error
- Symlink test: `readlink .claude/skills/commit` shows `../../edify-plugin/skills/commit`

**Success Criteria:**
- Directory renamed successfully
- All path references updated
- Symlinks resolve correctly
- No broken references found by grep
- Justfile and git status validate clean rename

**Report Path:** `plans/plugin-migration/reports/phase-0-execution.md`

---

## Common Context

**Affected Files:**
- `agent-core/` → `edify-plugin/` (directory rename)
- `.gitmodules` (submodule path)
- `justfile` (recipe paths)
- `.claude/settings.json` (permissions, hooks)
- `CLAUDE.md` (@ references)
- `.cache/just-help-agent-core.txt` → `.cache/just-help-edify-plugin.txt`
- Possibly: `edify-plugin/Makefile` (target names)

**Key Constraints:**
- Use `git mv` for directory rename (preserves history)
- Test symlink resolution after rename
- Grep for any remaining references before proceeding
- Directory rename is irreversible (commit point)

**Stop Conditions:**
- If grep finds unexpected references that cannot be updated
- If symlinks break and cannot be restored
- If justfile recipes fail after rename
