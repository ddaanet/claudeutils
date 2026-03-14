### Phase 2: Hook migration and setup hook (type: general, model: sonnet)

Migrate all hooks to plugin, create consolidated setup hook, audit scripts for env var usage.
Phase 5 must complete first (`.edify.yaml` exists for setup hook to read/update).

---

## Step 2.1: Audit hook scripts for env var usage

**Objective**: Audit 4 hook scripts for `$CLAUDE_PROJECT_DIR` usage and hardcoded paths that may not resolve correctly under plugin context.

**Prerequisites**:
- Read outline.md Component 2 hook script changes table (authoritative list of which scripts need audit)
- Read each of the 4 scripts:
  - `agent-core/hooks/pretooluse-recipe-redirect.py`
  - `agent-core/hooks/pretooluse-recall-check.py`
  - `agent-core/hooks/sessionstart-health.sh`
  - `agent-core/hooks/stop-health-fallback.sh`

**Implementation**:
1. For each script, check:
   - Uses of `$CLAUDE_PROJECT_DIR` — these are correct (available in all hook types, resolves to project root)
   - Hardcoded `agent-core/` paths — these need `$CLAUDE_PLUGIN_ROOT` substitution (or `$EDIFY_PLUGIN_ROOT` after setup hook runs)
   - Relative path references — must use absolute paths via env vars
2. Record findings per script in a report at `plans/plugin-migration/reports/hook-audit.md`:
   - Script name
   - Finding: no-change-needed OR specific edits required (with line numbers)
   - Rationale

**Expected Outcome**:
- `plans/plugin-migration/reports/hook-audit.md` exists with per-script findings
- Each script classified as no-change or with specific edits listed

**Error Conditions**:
- If a script uses env vars not available in plugin context → escalate (design assumption violated)
- If a script has complex path resolution logic → document and escalate for careful review

**Validation**:
- Audit report exists with entries for all 4 scripts
- No scripts left unaudited

---

## Step 2.2: Apply hook script fixes from audit

**Objective**: Apply env var fixes identified in Step 2.1 audit. Delete `pretooluse-symlink-redirect.sh`.

**Prerequisites**:
- Step 2.1 complete (audit report exists)
- Read `plans/plugin-migration/reports/hook-audit.md` (audit findings)

**Implementation**:
1. Apply edits to each script per audit findings:
   - Replace hardcoded `agent-core/` paths with `$CLAUDE_PLUGIN_ROOT` or `$EDIFY_PLUGIN_ROOT`
   - Fix any relative path references to use absolute resolution
2. Delete `agent-core/hooks/pretooluse-symlink-redirect.sh` — purpose eliminated by plugin migration
3. Verify remaining scripts:
   - Grep all hook scripts for bare `agent-core/` references (should be zero after fixes)
   - Grep for relative path patterns (`./`, `../`) that don't use env var resolution

**Expected Outcome**:
- Audit fixes applied to affected scripts
- `pretooluse-symlink-redirect.sh` deleted
- No remaining bare `agent-core/` references or relative paths in hook scripts

**Error Conditions**:
- If audit found no changes needed → this step is a no-op except for the deletion
- If grep finds unexpected references → investigate and fix or escalate

**Validation**:
- `grep -r 'agent-core/' agent-core/hooks/*.py agent-core/hooks/*.sh` returns no matches (except comments)
- `ls agent-core/hooks/pretooluse-symlink-redirect.sh` returns "No such file"

---

## Step 2.3: Create consolidated edify-setup.sh

**Objective**: Create the SessionStart setup hook that exports env vars, installs edify CLI, writes version provenance, and checks for stale fragments.

**Script Evaluation**: Large (>100 lines, new code with multiple responsibilities)
**Execution Model**: Sonnet (may escalate to opus for UPS fallback design)

**Prerequisites**:
- Read outline.md Component 2 "Consolidated setup hook" section
- Read outline.md §Key Decisions D-7 (python deps mechanism)
- Step 5.1 complete (`.edify.yaml` exists)
- Recall: "when using session start hooks" — SessionStart output discarded for new interactive sessions (#10373). UPS fallback must account for this.

**Implementation**:
1. Create `agent-core/hooks/edify-setup.sh`
2. Script responsibilities (in order):
   a. **Export `EDIFY_PLUGIN_ROOT`** via `$CLAUDE_ENV_FILE`:
      ```bash
      echo "EDIFY_PLUGIN_ROOT=$CLAUDE_PLUGIN_ROOT" >> "$CLAUDE_ENV_FILE"
      ```
   b. **Install edify CLI** into plugin-local venv:
      - Check for `uv` availability: `command -v uv`
      - If available: create plugin-local venv (`uv venv "$CLAUDE_PLUGIN_ROOT/.venv"` if not already present), then install into it (`uv pip install --python "$CLAUDE_PLUGIN_ROOT/.venv/bin/python" claudeutils==X.Y.Z`)
      - If not: fall back to `pip install --target "$CLAUDE_PLUGIN_ROOT/.venv/lib"` or warn (R-3 mitigation)
      - Package name is `claudeutils` (current PyPI name; rename to `edify` is separate work)
      - Version pinned in script, updated with each plugin release
   c. **Write version provenance** to `.edify.yaml` (FR-10):
      - Read plugin version from `$CLAUDE_PLUGIN_ROOT/.claude-plugin/plugin.json`
      - Update `version` field in `.edify.yaml`
   d. **Compare versions and nag if stale** (FR-5):
      - Compare `.edify.yaml` `version` with plugin version
      - If mismatch: output nag message "Fragments may be stale. Run `/edify:update`"
      - Nag via `additionalContext` mechanism if available, else stdout
3. **UPS fallback** for SessionStart discard (#10373):
   - Check `$CLAUDE_TRANSCRIPT_PATH` for setup marker (if transcript exists)
   - If marker absent: run setup
   - If marker present: skip (already ran this session)
   - Write marker to transcript or temp file after successful setup
4. Script must be **idempotent** — safe to run multiple times in same session

**Expected Outcome**:
- `agent-core/hooks/edify-setup.sh` exists, is executable
- Script handles: env var export, CLI install with fallback, version write, staleness nag
- Script is idempotent and handles SessionStart discard scenario

**Error Conditions**:
- If `$CLAUDE_ENV_FILE` is not set → skip env var export (not in Claude Code context)
- If `$CLAUDE_PLUGIN_ROOT` is not set → skip all plugin-specific operations
- If `uv` and `pip` both unavailable → warn but don't fail (graceful degradation)
- If `.edify.yaml` doesn't exist → create it (first run scenario)

**Validation**:
- Script runs without error from project root: `bash agent-core/hooks/edify-setup.sh`
- After run: `.edify.yaml` version matches `plugin.json` version
- Script is idempotent: running twice produces same result

---

## Step 2.4: Wire setup hook into hooks.json (checkpoint)

**Objective**: Add `edify-setup.sh` as a SessionStart hook in `hooks.json`, ensuring it runs before `sessionstart-health.sh`.

**Prerequisites**:
- Steps 2.2, 2.3 complete
- Post-phase state: `agent-core/hooks/hooks.json` (rewritten in Step 1.2) contains all 9 surviving hooks in wrapper format

**Implementation**:
1. Edit `agent-core/hooks/hooks.json` SessionStart section (file is in wrapper format after Phase 1 rewrites it: `{"hooks": {"SessionStart": [...], ...}}` — edit within the existing wrapper)
2. Add `edify-setup.sh` entry BEFORE `sessionstart-health.sh`:
   ```json
   "SessionStart": [
     {
       "matcher": "*",
       "hooks": [
         {
           "type": "command",
           "command": "bash $CLAUDE_PLUGIN_ROOT/hooks/edify-setup.sh"
         },
         {
           "type": "command",
           "command": "bash $CLAUDE_PLUGIN_ROOT/hooks/sessionstart-health.sh"
         }
       ]
     }
   ]
   ```
   (This shows the value of the `"SessionStart"` key within `"hooks"` — not a standalone JSON document)
3. Ordering matters: setup provides env vars that health check may need

**Expected Outcome**:
- `hooks.json` SessionStart has `edify-setup.sh` before `sessionstart-health.sh`
- Total hook count is now 10 (9 original + 1 new setup hook)
- JSON validates

**Error Conditions**:
- If SessionStart section structure differs from expected → adapt insertion point
- If JSON validation fails after edit → fix syntax

**Validation**:
- JSON validates: `python3 -c "import json; json.load(open('agent-core/hooks/hooks.json')); print('OK')"`
- Verify session restart → setup hook fires → env vars available (same tmux verification mechanism as Step 1.3)
- Validation checkpoint — STOP and report Phase 2 results before proceeding
