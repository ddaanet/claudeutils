# Step 1.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.1: Create Plugin Infrastructure

**Objective:** Create plugin.json manifest and .version marker for plugin discovery and fragment version tracking.

**Implementation:**

1. **Create plugin manifest directory and file:**
```bash
mkdir -p edify-plugin/.claude-plugin
cat > edify-plugin/.claude-plugin/plugin.json <<'EOF'
{
  "name": "edify",
  "version": "1.0.0",
  "description": "Workflow infrastructure for Claude Code projects"
}
EOF
```

**Manifest design notes:**
- Minimal structure per D-1 (name + version + description only)
- Plugin name = `edify` (Latin *aedificare* = "to build" + "to instruct")
- Auto-discovery handles skills/agents/hooks from conventional directories
- No custom path overrides needed (edify-plugin already uses standard layout)

2. **Create version marker:**
```bash
printf '1.0.0' > edify-plugin/.version
```

**Version marker purpose:**
- Source version for fragment staleness detection (Component 7)
- Compared against project's `.edify-version` by version-check hook
- Semantic versioning: major = breaking CLAUDE.md structure, minor = new fragment, patch = content fix

3. **Validate file creation:**
```bash
# Verify plugin.json exists
test -f edify-plugin/.claude-plugin/plugin.json

# Verify plugin.json parses as valid JSON (fallback to python if jq unavailable)
if command -v jq >/dev/null 2>&1; then
  jq . edify-plugin/.claude-plugin/plugin.json >/dev/null
else
  python3 -m json.tool edify-plugin/.claude-plugin/plugin.json >/dev/null
fi

# Verify .version exists
test -f edify-plugin/.version

# Verify .version contains exact string "1.0.0"
[ "$(cat edify-plugin/.version)" = "1.0.0" ]

# Verify .version has exactly 5 bytes (no trailing newline)
[ "$(wc -c < edify-plugin/.version)" -eq 5 ]
```

**Expected Outcome:**
- `edify-plugin/.claude-plugin/plugin.json` created with valid JSON
- `edify-plugin/.version` created with `1.0.0` content (exactly 5 bytes)
- Both validation commands exit 0
- Files ready for plugin auto-discovery after Phase 2-3 (skills/agents/hooks)

**Unexpected Result Handling:**
- If `.claude-plugin/` creation fails: check permissions on edify-plugin/ directory
- If plugin.json file test fails: verify directory creation succeeded, check write permissions
- If JSON validation fails: check syntax (trailing commas, quotes, malformed JSON)
- If .version file test fails: verify write permissions on edify-plugin/ directory
- If .version content test fails: verify exact string `1.0.0` with no trailing newline (use `printf` not `echo`)
- If .version byte count fails: check for trailing newline, spaces, or other hidden characters

**Validation:**
- `test -f edify-plugin/.claude-plugin/plugin.json` returns true
- `test -f edify-plugin/.version` returns true
- JSON validation succeeds (jq or python3 -m json.tool exit 0)
- `[ "$(cat edify-plugin/.version)" = "1.0.0" ]` returns true
- `[ "$(wc -c < edify-plugin/.version)" -eq 5 ]` returns true (no trailing newline)

**Success Criteria:**
- Both files created successfully
- plugin.json parses as valid JSON with required fields (name, version, description)
- .version contains semver string with exact byte count
- Ready for plugin discovery components (Phase 2-3)

**Report Path:** `plans/plugin-migration/reports/phase-1-execution.md`

---
