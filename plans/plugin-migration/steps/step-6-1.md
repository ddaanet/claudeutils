# Step 6.1

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 6.1: Regenerate cache files

**Objective:** Regenerate `.cache/just-help.txt` and `.cache/just-help-edify-plugin.txt` to reflect updated justfile content.

**Implementation:**

1. **Regenerate root justfile cache:**
```bash
just cache
```

This regenerates:
- `.cache/just-help.txt` (includes imported recipes from portable.just)
- `.cache/just-help-edify-plugin.txt` (sync-to-parent removed)

**How `just cache` works:**
- Runs root justfile `cache` recipe
- Calls `make -C edify-plugin cache` which regenerates edify-plugin cache
- Both cache files updated in single command

2. **Verify cache content changes:**

**Root cache (should show imported recipes):**
```bash
cat .cache/just-help.txt | grep -E "^[[:space:]]+(claude|wt-new|wt-ls|wt-rm|wt-merge|precommit-base)"
```

**Expected:** All imported recipes appear (claude, claude0, wt-new, wt-ls, wt-rm, wt-merge, precommit-base)

**Edify-plugin cache (should NOT show sync-to-parent):**
```bash
! grep -q sync-to-parent .cache/just-help-edify-plugin.txt
```

**Expected:** sync-to-parent recipe NOT present (recipe removed in Phase 5.2)

**Expected Outcome:**
- `.cache/just-help.txt` updated with imported recipes
- `.cache/just-help-edify-plugin.txt` updated without sync-to-parent
- Both cache files reflect current justfile state

**Unexpected Result Handling:**
- If `just cache` fails: check justfile syntax, verify edify-plugin/Makefile cache target exists
- If imported recipes missing from root cache: verify import line in root justfile
- If sync-to-parent still in edify-plugin cache: verify recipe removed in Phase 5.2

**Validation:**
- `.cache/just-help.txt` contains imported recipe names (claude, wt-new, etc.)
- `.cache/just-help-edify-plugin.txt` does NOT contain sync-to-parent
- Both files have recent modification timestamp (after `just cache` run)

**Success Criteria:**
- Both cache files regenerated successfully
- Root cache includes imported recipes from portable.just
- Edify-plugin cache excludes removed sync-to-parent recipe
- CLAUDE.md @ references resolve (no broken cache file references)

**Report Path:** `plans/plugin-migration/reports/phase-6-execution.md`

---
