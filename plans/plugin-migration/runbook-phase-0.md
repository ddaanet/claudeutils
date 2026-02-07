# Phase 0: Directory Rename

**Purpose:** Rename agent-core directory to edify-plugin across entire project (D-1)

**Dependencies:** None

**Model:** Haiku

**Estimated Complexity:** Moderate (git mv + comprehensive path updates across 6 file categories)

---

## Step 0.1: Rename agent-core → edify-plugin

**Objective:** Rename the submodule directory from `agent-core` to `edify-plugin` and update all references across config files, rules, agents, documentation, and cache.

**Implementation:**

1. **Baseline inventory (pre-rename grep):**
```bash
# Find all agent-core references before rename (for comparison)
grep -r "agent-core" --exclude-dir=.git . > tmp/phase-0-baseline.txt
echo "Baseline references: $(wc -l < tmp/phase-0-baseline.txt)"
```

2. **Rename directory using git mv:**
```bash
git mv agent-core edify-plugin
```

3. **Update .gitmodules:**
   - Change `path = agent-core` to `path = edify-plugin`
   - URL stays unchanged (internal path only)

4. **Update root justfile:**
   - Search-replace: `agent-core/` → `edify-plugin/`
   - Affected recipes: `cache` (line ~25), `wt-new` (line ~65: `--reference "$main_dir/agent-core"`)
   - Critical: wt-new submodule reference must update or worktree creation fails

5. **Update .claude/settings.json:**
   - Permissions.allow patterns: `Bash(agent-core/bin/...` → `Bash(edify-plugin/bin/...`
   - Hook commands: `$CLAUDE_PROJECT_DIR/agent-core/hooks/` → `$CLAUDE_PROJECT_DIR/edify-plugin/hooks/`

6. **Update .claude/rules/*.md files:**
   - `skill-development.md` line 4: `paths: ["agent-core/skills/**/*"]` → `paths: ["edify-plugin/skills/**/*"]`
   - `commit-work.md`: `@agent-core/fragments/commit-delegation.md` → `@edify-plugin/fragments/commit-delegation.md`
   - `planning-work.md`: `@agent-core/fragments/` references → `@edify-plugin/fragments/`

7. **Update plan-specific agent files in .claude/agents/:**
   - `.claude/agents/plugin-migration-task.md` (this plan's agent)
   - `.claude/agents/claude-tools-rewrite-task.md`
   - `.claude/agents/consolidation-task.md`
   - `.claude/agents/learnings-consolidation-task.md`
   - `.claude/agents/workflow-controls-task.md`
   - `.claude/agents/design-workflow-enhancement-task.md`
   - Update all `agent-core/` references to `edify-plugin/`

8. **Update agents/session.md:**
   - Search-replace: `agent-core` → `edify-plugin` in Reference Files and other sections

9. **Rename cache file (BEFORE updating CLAUDE.md @ references):**
   - `mv .cache/just-help-agent-core.txt .cache/just-help-edify-plugin.txt`

10. **Update CLAUDE.md:**
    - Fragment @ references: `@agent-core/fragments/` → `@edify-plugin/fragments/`
    - Cache @ reference: `@.cache/just-help-agent-core.txt` → `@.cache/just-help-edify-plugin.txt`

11. **Update edify-plugin/Makefile:**
    - Line 4 comment: "agent-core includes" → "edify-plugin includes"
    - Line 10 target: `just-help-agent-core.txt:` → `just-help-edify-plugin.txt:`
    - Line 30 output: `.cache/just-help-agent-core.txt` → `.cache/just-help-edify-plugin.txt`

12. **Update plans/ historical documentation (DECISION REQUIRED):**
    - 41 references found in plans/ subdirectories:
      - `plans/reflect-rca-prose-gates/` (13 refs across outline, design, report)
      - `plans/validator-consolidation/requirements.md` (9 refs)
      - `plans/commit-unification/` (11 refs across design, report)
      - `plans/workflow-skills-audit/audit.md` (8 refs)
    - **Decision:** Update all historical docs for consistency (non-breaking but reduces confusion)
    - Execute: `find plans/ -type f -name '*.md' -exec sed -i '' 's/agent-core/edify-plugin/g' {} +`

13. **Post-rename verification grep:**
```bash
# Find remaining agent-core references (excluding git history)
grep -r "agent-core" --exclude-dir=.git . > tmp/phase-0-remaining.txt
echo "Remaining references: $(wc -l < tmp/phase-0-remaining.txt)"
# Compare: baseline should be ~100+ refs, remaining should be 0
```

14. **Validate ALL symlinks (not just one):**
```bash
# Verify all 31 symlinks in .claude/ resolve correctly
find .claude -type l | while read link; do
  readlink -f "$link" >/dev/null || echo "BROKEN: $link"
done
# Expected: no output (all symlinks resolve)
```

15. **Validate @ references resolve:**
```bash
# Check that all CLAUDE.md @ references point to existing files
grep '^@edify-plugin/' CLAUDE.md | sed 's/@//' | while read path; do
  [ -f "$path" ] || echo "MISSING: $path"
done
# Expected: no output (all @ paths exist)
```

16. **Test justfile functionality:**
```bash
just --list  # Should run without error
just cache   # Should regenerate cache files in .cache/
```

**Expected Outcome:**
- Directory renamed from `agent-core/` to `edify-plugin/`
- All references updated across 6 file categories (config, rules, agents, session, cache, historical docs)
- All 31 symlinks resolve correctly
- Justfile recipes work (including wt-new submodule reference)
- All @ references in CLAUDE.md resolve to existing files
- Post-rename grep shows 0 remaining references

**Unexpected Result Handling:**
- If symlinks break: identify which symlinks failed validation (step 14), check git mv handling
- If grep finds unexpected references: categorize by file type, add explicit update step for that category
- If justfile fails: verify import paths and wt-new `--reference` update
- If @ references missing: check cache file rename timing (must happen before CLAUDE.md update)

**Validation:**
- `ls -d edify-plugin/` shows directory exists
- `ls -d agent-core/` returns "No such file or directory"
- `git status` shows `renamed: agent-core/ -> edify-plugin/` plus modified files (.gitmodules, justfile, settings.json, CLAUDE.md, etc.)
- Post-rename grep shows 0 remaining references (compared to ~100+ baseline)
- All 31 symlinks resolve (step 14 produces no BROKEN output)
- All @ references resolve (step 15 produces no MISSING output)
- `just --list` and `just cache` run without error

**Success Criteria:**
- Directory renamed successfully with git mv
- All 6 file categories updated (config, rules, agents, session, cache, historical)
- All symlinks validate (comprehensive check, not single sample)
- All @ references validate (scripted check, not deferred to next session)
- Grep baseline vs remaining comparison shows complete coverage
- Git status shows clean rename (R status, not D+A)

**Report Path:** `plans/plugin-migration/reports/phase-0-execution.md`

---

## Common Context

**Affected Files (6 categories):**

**Core config:**
- `agent-core/` → `edify-plugin/` (directory rename)
- `.gitmodules` (submodule path)
- `justfile` (cache recipe + wt-new submodule reference)
- `.claude/settings.json` (permissions.allow, hooks)
- `CLAUDE.md` (@ references to fragments and cache)

**Rules files:**
- `.claude/rules/skill-development.md` (paths frontmatter)
- `.claude/rules/commit-work.md` (@ fragment reference)
- `.claude/rules/planning-work.md` (@ fragment references)

**Plan-specific agents:**
- `.claude/agents/plugin-migration-task.md`
- `.claude/agents/claude-tools-rewrite-task.md`
- `.claude/agents/consolidation-task.md`
- `.claude/agents/learnings-consolidation-task.md`
- `.claude/agents/workflow-controls-task.md`
- `.claude/agents/design-workflow-enhancement-task.md`

**Session state:**
- `agents/session.md` (Reference Files section)

**Cache:**
- `.cache/just-help-agent-core.txt` → `.cache/just-help-edify-plugin.txt`
- `edify-plugin/Makefile` lines 4, 10, 30 (target name + comment)

**Historical documentation (41 files in plans/):**
- `plans/reflect-rca-prose-gates/` (outline, design, report)
- `plans/validator-consolidation/requirements.md`
- `plans/commit-unification/` (design, report)
- `plans/workflow-skills-audit/audit.md`

**Key Constraints:**
- Use `git mv` for directory rename (preserves history)
- Perform baseline grep BEFORE rename for reference count comparison
- Rename cache file BEFORE updating CLAUDE.md @ references (timing dependency)
- Test ALL 31 symlinks, not single sample
- Validate @ references with script BEFORE manual session check
- Update all 6 file categories (config, rules, agents, session, cache, historical)
- Directory rename is irreversible once committed

**Stop Conditions:**
- If post-rename grep shows unexpected references that cannot be categorized/updated
- If symlink comprehensive validation (step 14) shows BROKEN symlinks that cannot be resolved
- If @ reference validation (step 15) shows MISSING files
- If justfile recipes fail after wt-new reference update
