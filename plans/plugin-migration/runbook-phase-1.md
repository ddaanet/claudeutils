# Phase 1: Plugin Manifest

**Purpose:** Create the minimal plugin manifest and version marker to enable plugin discovery.

**Dependencies:** None (first phase)

**Model:** Haiku (inline execution, no delegation)

**Prerequisites:**

Before starting Phase 1, verify documentation loaded:
- Design document: `plans/plugin-migration/design.md` (already read)
- Skills loaded: `plugin-dev:plugin-structure` and `plugin-dev:hook-development` (required by design "Documentation Perimeter")

If skills not loaded, invoke:
```
/skill plugin-dev:plugin-structure
/skill plugin-dev:hook-development
```

---

## Step 1.1: Create plugin manifest

**Objective:** Create minimal plugin manifest at `agent-core/.claude-plugin/plugin.json` with name, version, and description.

**Execution Model:** Haiku (inline execution)

**Implementation:**

Create directory and plugin manifest:

```bash
mkdir -p agent-core/.claude-plugin
cat > agent-core/.claude-plugin/plugin.json << 'EOF'

```json
{
  "name": "edify",
  "version": "1.0.0",
  "description": "Workflow infrastructure for Claude Code projects"
}
EOF
```

**Design Reference:**
- D-1: Plugin name = `edify` (Latin *aedificare* = "to build" + "to instruct")
- Design Component 1: Minimal manifest (auto-discovery handles skills/agents/hooks from conventional directories)

**Validation:**
- File exists at `agent-core/.claude-plugin/plugin.json`
- JSON parses correctly: `jq . agent-core/.claude-plugin/plugin.json`
- Contains required fields: `name`, `version`, `description`

**Expected Outcome:** Plugin manifest file created with valid JSON structure.

**Error Conditions:**
- `.claude-plugin/` directory creation fails → Check permissions on `agent-core/` directory
- JSON syntax error → Fix JSON structure
- `jq` not installed → Install with `brew install jq` or package manager

**Success Criteria:**
- File exists at correct path
- JSON is well-formed
- `jq` validation passes

---

## Step 1.2: Create fragment version marker

**Objective:** Create fragment version marker at `agent-core/.version` with initial version `1.0.0`.

**Execution Model:** Haiku (inline execution)

**Implementation:**

Create `.version` file using `printf` to avoid trailing newline:

```bash
printf '1.0.0' > agent-core/.version
```

**Design Reference:**
- Design Component 3: Fragment versioning system
- Version bump protocol: major = breaking CLAUDE.md structure, minor = new fragment, patch = content fix

**Validation:**
- File exists at `agent-core/.version`
- Contains exactly `1.0.0` with no trailing newline: `[ "$(cat agent-core/.version)" = "1.0.0" ]`
- Byte count is exactly 5: `[ "$(wc -c < agent-core/.version)" -eq 5 ]`

**Expected Outcome:** Version marker file created with initial version.

**Error Conditions:**
- File write fails → Check permissions
- Wrong content → Verify exact string `1.0.0`

**Success Criteria:**
- File exists at correct path
- Content is exactly `1.0.0` (5 bytes, no trailing newline)
- Byte count validation passes

---

## Phase 1 Checkpoint

**Verification:**

Run these commands to verify Phase 1 completion:

```bash
# Verify plugin.json exists and is valid JSON
test -f agent-core/.claude-plugin/plugin.json && jq . agent-core/.claude-plugin/plugin.json

# Verify .version exists with correct content
test -f agent-core/.version && [ "$(cat agent-core/.version)" = "1.0.0" ]
```

**Success:** Both commands exit 0

**On failure:** Review error messages, fix issues, re-run verification

**Next:** Proceed to Phase 2 (Skills and Agents)
