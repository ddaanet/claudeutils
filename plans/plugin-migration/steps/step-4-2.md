# Step 4.2

**Plan**: `plans/plugin-migration/runbook.md`
**Execution Model**: haiku
**Phase**: 3

---

## Step 4.2: Update root justfile with import

**Objective:** Add import statement to root justfile, remove migrated recipes, keep project-specific recipes.

**Implementation:**

1. **Add import at top of root justfile (after prolog):**

Add this line after the `bash_prolog` definition:

```just
import 'edify-plugin/just/portable.just'
```

2. **Remove migrated recipes from root justfile:**

Delete these recipe definitions (now provided by import):
- `claude`
- `claude0`
- `wt-new`
- `wt-ls`
- `wt-rm`
- `wt-merge`
- Remove `precommit-base` subset from `precommit` recipe (validators are now called via import)

3. **Update precommit recipe to call precommit-base:**

Change `precommit` recipe to use dependency pattern (base validators run first, then project-specific):

```just
precommit: precommit-base
    # Add language-specific checks after base validators
    ruff check
    mypy
    pytest
```

Note: The dependency `precommit: precommit-base` ensures base validators run before project-specific checks.

4. **Keep project-specific recipes:**

These remain in root justfile:
- `help`
- `dev`
- `cache`
- `test`
- `line-limits`
- `lint`
- `check`
- `format`
- `release`

5. **Keep full bash_prolog:**

Root justfile retains full bash prolog with project-specific helpers (sync, run-checks, pytest-quiet) — not just the minimal fail/visible/colors subset used by portable.just.

**Design References:**
- D-5: justfile import mechanism
- Component 5: Root justfile changes table
- Outline expansion guidance: portable.just bash prolog scope (fail, visible, colors only)

**Validation:**
- Import line added: `grep "import 'edify-plugin/just/portable.just'" justfile`
- Migrated recipes removed: `! grep -E "^(claude|claude0|wt-new|wt-ls|wt-rm|wt-merge):" justfile`
- Project recipes remain: `grep -E "^(help|dev|cache|test):" justfile`
- Justfile parses: `just --list` runs without error
- End-to-end test: `just --list` shows both imported and local recipes, `just claude` invokes imported recipe

**Expected Outcome:**
- Root justfile imports portable.just
- Migrated recipes removed from root
- Project-specific recipes and full prolog remain
- `just --list` shows both imported and local recipes

**Unexpected Result Handling:**
- If import fails: verify path `edify-plugin/just/portable.just` exists and is valid Just syntax
- If `just --list` fails: check for syntax errors, duplicate recipe definitions
- If recipes missing: ensure import added before removing local definitions

**Success Criteria:**
- Import statement present in root justfile
- All 7 migrated recipes removed from root
- Project-specific recipes remain intact
- `just --list` succeeds and shows combined recipes
- `just claude` works (calls imported recipe)

**Report Path:** `plans/plugin-migration/reports/phase-4-execution.md`

---
