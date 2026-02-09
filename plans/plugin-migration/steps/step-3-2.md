# Step 3.2

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 2

---

## Step 3.2: Delete obsolete hook script

**Objective:** Delete `edify-plugin/hooks/pretooluse-symlink-redirect.sh` (purpose eliminated by plugin auto-discovery).

**Execution Model:** Haiku (inline execution)

**Implementation:**

Remove symlink-redirect hook:

```bash
rm edify-plugin/hooks/pretooluse-symlink-redirect.sh
```

**Design Reference:**
- Design Component 2 table: "pretooluse-symlink-redirect.sh: Delete — Purpose eliminated — no symlinks to protect"
- Design "Affected Files (Delete)" section: Lists this file for deletion

**Rationale:**
This hook prevented editing edify-plugin files via symlinks. With plugin auto-discovery, skills/agents/hooks load directly from edify-plugin (no symlinks), so the hook's purpose is eliminated.

**Validation:**
- File no longer exists: `[ ! -f edify-plugin/hooks/pretooluse-symlink-redirect.sh ]`
- Remaining hooks present: `pretooluse-block-tmp.sh`, `submodule-safety.py`, `userpromptsubmit-shortcuts.py`, `userpromptsubmit-version-check.py`

**Expected Outcome:** Symlink-redirect hook script deleted.

**Error Conditions:**
- File doesn't exist (already deleted) → Success (idempotent)
- Permission denied → Check write permissions on `edify-plugin/hooks/`

**Success Criteria:**
- `pretooluse-symlink-redirect.sh` no longer exists
- Other hook scripts remain intact

---
