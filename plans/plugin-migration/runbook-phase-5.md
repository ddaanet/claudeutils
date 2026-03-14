### Phase 5: Version coordination and precommit (type: general, model: sonnet)

Wire version consistency and release coordination. Runs early — creates `.edify.yaml` before Phase 2's setup hook needs it.

---

## Step 5.1: Create .edify.yaml schema and initial file

**Objective**: Create `.edify.yaml` in project root with version from `pyproject.toml` and default sync policy.

**Prerequisites**:
- Read `pyproject.toml` (current version — `0.0.2`)

**Implementation**:
1. Create `.edify.yaml` in project root:
   ```yaml
   # Edify plugin version marker
   # Written by /edify:init, updated by edify-setup.sh on session start
   version: "0.0.2"
   sync_policy: nag  # nag | auto-with-report (future)
   ```
2. Version must match `pyproject.toml` version exactly
3. `sync_policy: nag` is the default — setup hook compares versions and nags if stale

**Expected Outcome**:
- `.edify.yaml` exists in project root with valid YAML
- `version` field matches `pyproject.toml`
- `sync_policy` is `nag`

**Error Conditions**:
- If `.edify.yaml` already exists → read and verify, do not overwrite without checking

**Validation**:
- `python3 -c "import yaml; d=yaml.safe_load(open('.edify.yaml')); assert d['version']=='0.0.2'; assert d['sync_policy']=='nag'; print('OK')"`

---

## Step 5.2: Add version consistency precommit check

**Objective**: Add a check that `plugin.json` version == `pyproject.toml` version, integrated into `just precommit` and `just release`.

**Prerequisites**:
- Read `justfile` (understand current precommit recipe structure)
- Read `agent-core/.claude-plugin/plugin.json` (created in Step 1.1)
- Step 1.1 complete (plugin.json exists)

**Implementation**:
1. Create version consistency check script at `agent-core/bin/check-version-consistency.py`:
   - Read `pyproject.toml` version
   - Read `agent-core/.claude-plugin/plugin.json` version
   - Compare — exit 0 if match, exit 1 with message if mismatch
2. Add to `just precommit` recipe (after lint, before test):
   - `python3 agent-core/bin/check-version-consistency.py`
3. Update `just release` recipe to bump both files together:
   - Accept version argument
   - Update `pyproject.toml` version
   - Update `plugin.json` version
   - Run consistency check to verify

**Expected Outcome**:
- `agent-core/bin/check-version-consistency.py` exists and is executable
- `just precommit` includes version consistency check
- Mismatched versions cause precommit failure

**Error Conditions**:
- If `just release` recipe doesn't exist → create it or add version bump to existing release workflow
- If `plugin.json` path changes → update script accordingly

**Validation**:
1. Run `just precommit` — should pass (versions match)
2. Temporarily change `plugin.json` version → `just precommit` should fail
3. Restore `plugin.json` version
