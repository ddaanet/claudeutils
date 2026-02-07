# Step 3.3

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 3.3: Create version check hook

Create `agent-core/hooks/userpromptsubmit-version-check.py` with once-per-session version mismatch detection.

**Implementation:** Python script that checks `.edify-version` vs `.version`, uses temp file `tmp/.edify-version-checked` for once-per-session gating, injects warning via `additionalContext` if versions differ.

---
