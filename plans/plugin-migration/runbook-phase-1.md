# Phase 1: Plugin Manifest

**Purpose:** Create plugin manifest and version marker to enable Claude Code plugin discovery

**Dependencies:** Phase 0 (edify-plugin directory exists)

**Model:** Haiku

**Estimated Complexity:** Trivial (2 simple files, ~15 lines total)

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
# Verify plugin.json exists and parses as valid JSON
test -f edify-plugin/.claude-plugin/plugin.json && jq . edify-plugin/.claude-plugin/plugin.json

# Verify .version exists with correct content (5 bytes, no trailing newline)
test -f edify-plugin/.version && [ "$(cat edify-plugin/.version)" = "1.0.0" ] && [ "$(wc -c < edify-plugin/.version)" -eq 5 ]
```

**Expected Outcome:**
- `edify-plugin/.claude-plugin/plugin.json` created with valid JSON
- `edify-plugin/.version` created with `1.0.0` content (exactly 5 bytes)
- Both validation commands exit 0
- Files ready for plugin auto-discovery after Phase 2-3 (skills/agents/hooks)

**Unexpected Result Handling:**
- If `.claude-plugin/` creation fails: check permissions on edify-plugin/ directory
- If JSON validation fails: check syntax (trailing commas, quotes, malformed JSON)
- If .version validation fails: verify exact string `1.0.0` with no trailing newline
- If `jq` not installed: install with `brew install jq` or use `python3 -m json.tool` instead

**Validation:**
- `[ -f edify-plugin/.claude-plugin/plugin.json ]` returns true
- `[ -f edify-plugin/.version ]` returns true
- `jq . edify-plugin/.claude-plugin/plugin.json` succeeds (valid JSON)
- `cat edify-plugin/.version` outputs exactly `1.0.0`
- `wc -c < edify-plugin/.version` outputs `5` (no trailing newline)

**Success Criteria:**
- Both files created successfully
- plugin.json parses as valid JSON with required fields (name, version, description)
- .version contains semver string with exact byte count
- Ready for plugin discovery components (Phase 2-3)

**Report Path:** `plans/plugin-migration/reports/phase-1-execution.md`

---

## Common Context

**Affected Files:**
- `edify-plugin/.claude-plugin/` (directory creation)
- `edify-plugin/.claude-plugin/plugin.json` (new file)
- `edify-plugin/.version` (new file)

**Key Constraints:**
- plugin.json must be valid JSON (Claude Code plugin loader requirement)
- .version must contain semver string for version-check hook comparison
- Minimal plugin.json per D-1 (name + version + description only)
- Auto-discovery from conventional directories (no path overrides in manifest)

**Stop Conditions:**
- If edify-plugin/ directory doesn't exist (Phase 0 not complete)
- If JSON validation fails repeatedly (syntax error in manifest)
