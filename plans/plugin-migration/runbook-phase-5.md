# Phase 5: Cleanup and Validation

**Purpose:** Remove symlinks, clean up obsolete configuration and documentation, validate all plugin functionality

**Dependencies:** Phase 1-4 complete (all plugin components ready)

**Model:** Haiku for cleanup (steps 5.1-5.2), Sonnet for validation (step 5.3)

**Estimated Complexity:** Low for cleanup, High for validation

---

## Step 5.1: Remove symlinks

**Objective:** Remove all symlinks from `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` directories.

**Implementation:**

1. **Count symlinks before removal (baseline):**
```bash
echo "Symlinks before removal:"
find .claude -type l | wc -l
find .claude/skills -type l | wc -l
find .claude/agents -type l | wc -l
find .claude/hooks -type l | wc -l
```

**Expected counts (per design):**
- Total: ~32 symlinks
- `.claude/skills/`: 16 symlinks
- `.claude/agents/`: 12 symlinks (preserve `*-task.md` regular files)
- `.claude/hooks/`: 4 symlinks

2. **Remove symlinks from .claude/skills/:**
```bash
# Remove all symlinks (all skills/ entries are symlinks)
find .claude/skills -type l -delete
```

3. **Remove symlinks from .claude/agents/:**
```bash
# Remove only symlinks, preserve *-task.md regular files
find .claude/agents -type l -delete
```

**Preservation note:** Plan-specific agents (`*-task.md`) are regular files (type f), not symlinks. The `-type l` filter ensures only symlinks are removed.

4. **Remove symlinks from .claude/hooks/:**
```bash
# Remove all symlinks (all hooks/ entries are symlinks)
find .claude/hooks -type l -delete
```

5. **Verify counts after removal:**
```bash
echo "Symlinks after removal:"
find .claude -type l | wc -l  # Should be 0

echo "Regular files preserved:"
find .claude/agents -type f -name "*-task.md" | wc -l  # Should be 6+
```

**Expected Outcome:**
- All symlinks removed from `.claude/` subdirectories
- Plan-specific `*-task.md` agents preserved (regular files)
- 0 symlinks remain in `.claude/`

**Unexpected Result Handling:**
- If symlinks remain: check deletion command succeeded, verify no permission errors
- If *-task.md files deleted: ERROR - these should be regular files (type f), not symlinks
- If count mismatch from expected: investigate unexpected symlinks or missing entries

**Validation:**
- `find .claude -type l | wc -l` returns 0
- `find .claude/agents -type f -name "*-task.md"` shows 6+ files (plan-specific agents intact)
- `.claude/skills/`, `.claude/agents/`, `.claude/hooks/` directories exist but contain no symlinks

**Success Criteria:**
- All symlinks removed (0 remaining)
- Plan-specific agents preserved
- Directories intact (not deleted, just emptied of symlinks)

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

## Step 5.3: Validate all functionality

**Objective:** Comprehensive validation of plugin discovery, hook behavior, agent coexistence, and performance parity (NFR-1, NFR-2).

**Implementation:**

**PREREQUISITE: Restart required**

All validation requires restarting Claude Code session after Phase 1-4 changes:

```bash
# Exit current session, then restart with:
claude --plugin-dir ./edify-plugin
```

**Validation 1: Plugin discovery**

Verify skills appear in `/help` output:

```bash
# From Claude Code session:
/help

# Expected: /edify:init and /edify:update skills listed
```

Verify agents visible in Task tool:
- Create a simple task that delegates to a plugin agent
- Confirm agent selection shows both plugin agents (edify:*) and plan-specific agents (*-task.md)

**Expected:** All 14 plugin agents + 6+ plan-specific agents visible

**Validation 2: Hook testing**

Test each hook event type:

**PreToolUse (Write/Edit + pretooluse-block-tmp.sh):**
```bash
# Try writing to /tmp/ (should be blocked)
echo "test" > /tmp/test.txt
# Expected: Hook blocks operation, error message shown
```

**PreToolUse (Bash + submodule-safety.py):**
```bash
# Try running command when cwd != project root
cd tmp && ls
# Expected: Hook warns or blocks (depends on submodule-safety logic)
```

**PostToolUse (Bash + submodule-safety.py):**
```bash
# Run any Bash command
ls -la
# Expected: Hook runs after command (no visible output unless error)
```

**UserPromptSubmit (shortcuts):**
```bash
# Submit shortcut prompt
s
# Expected: Shortcut expands to #status
```

**UserPromptSubmit (version-check):**
```bash
# Create .edify-version with old version
echo "0.9.0" > .edify-version

# Restart session, submit any prompt
# Expected: Warning shown on first prompt only
# "⚠️ Fragments outdated (project: 0.9.0, plugin: 1.0.0). Run /edify:update."

# Clean up
rm .edify-version tmp/.edify-version-checked
```

**Validation 3: Agent coexistence (FR-8)**

Verify both plugin and plan-specific agents coexist:

```bash
# Create test plan-specific agent
cat > .claude/agents/test-task.md <<EOF
---
name: test-task
description: Test agent for validation
---
This is a test agent.
EOF

# Restart session, verify both types visible in Task tool
# Expected: Plugin agents (edify:*) AND plan-specific agents (*-task.md) both appear

# Clean up
rm .claude/agents/test-task.md
```

**Validation 4: NFR-1 - Performance parity (edit→restart cycle time)**

**Baseline (pre-migration, with symlinks):**

Record baseline cycle time:
1. Edit a skill file (e.g., add comment to `edify-plugin/skills/commit/SKILL.md`)
2. Restart Claude Code session
3. Verify change visible in `/help` output

Record elapsed time (use stopwatch or `time` command).

**After migration (plugin auto-discovery):**

Repeat same process:
1. Edit same skill file
2. Restart Claude Code session
3. Verify change visible

Compare times. **Expected:** Within 10% of baseline (dev mode with `--plugin-dir` should match symlink performance).

**Validation 5: NFR-2 - Token overhead parity (context size)**

**Baseline measurement:**

Create identical session state:
1. Start fresh session with specific CLAUDE.md
2. Submit specific prompt (e.g., "Explain the commit skill")
3. Count tokens in response context

Record token count.

**After migration:**

Repeat with same CLAUDE.md and prompt:
1. Fresh session: `claude --plugin-dir ./edify-plugin`
2. Same prompt
3. Count tokens

Compare token counts. **Expected:** Difference ≤ 5% (NFR-2 requirement).

**Tool for token counting:** Use Claude Code's built-in token counter or external tool.

**Expected Outcome:**
- All plugin discovery working (skills, agents visible)
- All hooks functional (tested across all event types)
- Agent coexistence verified (plugin + plan-specific)
- NFR-1 validated (edit→restart cycle time parity)
- NFR-2 validated (token overhead ≤ 5% difference)

**Unexpected Result Handling:**
- If skills not visible: check plugin.json exists, restart completed, `--plugin-dir` correct
- If hooks not firing: check hooks.json format (direct, not wrapper), scripts exist and executable
- If agents missing: check both `edify-plugin/agents/` and `.claude/agents/` directories
- If performance regression: investigate plugin loading overhead, check for errors
- If token overhead exceeds 5%: analyze context diff, check for duplicate content loading

**Validation:**
- Skills `/edify:init` and `/edify:update` appear in `/help`
- All 4 hook types tested and functional (PreToolUse Write/Edit, PreToolUse Bash, PostToolUse Bash, UserPromptSubmit)
- Both plugin and plan-specific agents visible in Task tool
- Edit→restart cycle time within 10% of baseline
- Token overhead ≤ 5% vs baseline

**Success Criteria:**
- Plugin discovery: ✓ (skills and agents visible)
- Hook testing: ✓ (all 4 hook event types functional, behavior matches current implementation)
- Agent coexistence: ✓ (FR-8 verified)
- NFR-1: ✓ (performance parity)
- NFR-2: ✓ (token overhead ≤ 5%)

**Report Path:** `plans/plugin-migration/reports/phase-5-execution.md`

---

## Common Context

**Affected Files:**

**Symlink removal:**
- `.claude/skills/` (16 symlinks deleted)
- `.claude/agents/` (12 symlinks deleted, 6+ regular files preserved)
- `.claude/hooks/` (4 symlinks deleted)

**Configuration cleanup:**
- `.claude/settings.json` (hooks section removed)
- `edify-plugin/justfile` (sync-to-parent recipe removed)

**Documentation cleanup:**
- `edify-plugin/fragments/claude-config-layout.md`
- `edify-plugin/fragments/sandbox-exemptions.md`
- `edify-plugin/fragments/project-tooling.md`
- `edify-plugin/fragments/delegation.md`

**Key Constraints:**
- Symlink removal is POINT OF NO RETURN (cannot easily restore without re-running `just sync-to-parent` from pre-migration state)
- Restart required after Phase 1-4 before validation
- NFR validation requires baseline measurements from pre-migration state
- Agent coexistence test verifies FR-8 requirement

**Stop Conditions:**
- If symlinks cannot be removed (permission errors)
- If settings.json becomes invalid after hooks removal
- If any validation fails (plugin discovery, hooks, agent coexistence, performance, token overhead)
- If NFR-1 or NFR-2 fails validation (regression from baseline)
