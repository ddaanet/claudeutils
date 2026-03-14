### Phase 4: Justfile modularization (type: general, model: sonnet)

Extract portable recipes and update root justfile.

**Depends on D-5 redesign:** Current D-5 specifies a single `portable.just`. Thematic modules are the better design — consumers import only what they need. Module boundaries need design work before this phase executes. If D-5 redesign has not occurred by execution time, proceed with single `portable.just` as originally designed.

---

## Step 4.1: Create portable justfile module(s)

**Objective**: Extract portable recipe stack from current `justfile` into plugin-distributed module(s).

**Prerequisites**:
- Read `justfile` (current recipe definitions — identify which recipes are portable vs project-specific)
- Read outline.md §Key Decisions D-5 (full list of portable recipes)
- Read outline.md §Component 5 (import boundary constraints, variable merging)
- Check if D-5 redesign has occurred (thematic modules vs single file)

**Implementation**:
1. **If D-5 redesign completed** (thematic modules): create separate module files per design
2. **If D-5 not redesigned** (default): create single `agent-core/portable.just`
3. Extract these recipes (per D-5):
   - `claude` / `claude0` — opinionated launch wrapper (system prompt replacement, plugin config)
   - `lint` / `format` / `check` — ruff, mypy, docformatter
   - `red` — permissive TDD variant
   - `precommit` — full lint with complexity
   - `precommit-base` — edify-plugin validators only
   - `test` — pytest with framework flags
   - `wt-*` — manual worktree fallbacks
4. Do NOT include: `release`, `line-limits`, project-specific helpers
5. Each module needs its own minimal bash prolog:
   ```just
   # Minimal prolog for portable recipes (cannot rely on root justfile's bash_prolog)
   fail := 'echo "FAIL:" && exit 1'
   visible := 'echo'
   red := '\033[0;31m'
   green := '\033[0;32m'
   reset := '\033[0m'
   ```
6. Update `claude` recipe to use `--plugin-dir ./agent-core` flag

**Expected Outcome**:
- Portable justfile module(s) exist in `agent-core/`
- All portable recipes present with correct bash prolog
- `release` and project-specific recipes NOT included

**Error Conditions**:
- If recipe depends on project-specific variables not in prolog → add to prolog or restructure
- If `just` import syntax doesn't support the module structure → simplify to single file

**Validation**:
- `just --justfile agent-core/portable.just --list` shows all expected recipes (single-file case)
- No project-specific recipes present

---

## Step 4.2: Update root justfile to import portable modules

**Objective**: Replace extracted recipes with import statement(s) and verify all recipes work.

**Prerequisites**:
- Step 4.1 complete (portable module(s) exist)
- Read `justfile` (current state)

**Implementation**:
1. Add import statement(s) at top of `justfile`:
   - Single file: `import 'agent-core/portable.just'`
   - Thematic: `import 'agent-core/lint.just'` etc.
2. If using single `portable.just` with potential overrides: add `set allow-duplicate-recipes`
3. Remove recipes that moved to portable module(s):
   - `claude`, `claude0`, `lint`, `format`, `check`, `red`, `precommit-base`, `test`, `wt-*`
4. Keep in root justfile:
   - `release` (project-specific)
   - `line-limits` (project-specific)
   - `bash_prolog` for project-specific helper functions
   - `precommit` (may need project-specific additions beyond base)
   - Project-specific worktree helpers
5. Regenerate cached help files:
   - `.cache/just-help.txt`
   - `.cache/just-help-edify-plugin.txt` (if applicable)

**Expected Outcome**:
- Root `justfile` imports portable module(s)
- Extracted recipes removed from root (no duplication unless `allow-duplicate-recipes` for intentional overrides)
- All recipes functional

**Error Conditions**:
- If `just claude` fails → check import path, portable module syntax
- If recipe override doesn't work → verify `set allow-duplicate-recipes` or restructure imports
- If `just --list` missing recipes → check import path resolution

**Validation**:
- `just --list` shows both imported and project-specific recipes
- `just lint` works (imported recipe)
- `just release --help` works (project-specific recipe, if exists)
- `just precommit` passes (end-to-end validation)
- Regenerated `.cache/just-help*.txt` files match `just --list` output
