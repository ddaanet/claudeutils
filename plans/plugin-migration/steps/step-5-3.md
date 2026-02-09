# Step 5.3

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

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
