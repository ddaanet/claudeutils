# Plan: Gitmoji Integration & Commit Skill Improvements

## Problem Statement

1. **Commits from agents don't include gitmoji** - Commit skills don't integrate gitmoji selection; agents don't follow manual `/gitmoji` then `/commit` workflow
2. **Custom gitmojis not loaded reliably** - Separate `custom-gitmojis.md` file requires explicit read
3. **Commit skill issues:**
   - Precommit checks run too late (after drafting message)
   - Uses `git add -A` instead of selecting specific files
   - Doesn't preserve already-staged changes
   - Missing token-efficient bash pattern

## Decisions

- Gitmoji integration: Reference gitmoji skill from commit skills (modular)
- Duplication: Accept duplication between commit/commit-context (self-contained)
- Custom gitmojis: Append during cache generation (not manual merge)
- Rule scope: Add "discussing skills" trigger to CLAUDE.md

---

## Changes

### 1. Update gitmoji cache generation script

**File:** `agent-core/skills/gitmoji/scripts/update-gitmoji-index.sh`

After downloading official gitmojis, append custom gitmojis:

```bash
# After curl | jq > "$INDEX_FILE"

# Append custom gitmojis
cat >> "$INDEX_FILE" << 'EOF'
🗜️ - compress - Reducing file size, condensing content, or optimizing for brevity
🤖 - robot - Add or update agent skills, instructions, or guidance
EOF
```

**File:** `agent-core/skills/gitmoji/custom-gitmojis.md` → DELETE

**File:** `agent-core/skills/gitmoji/SKILL.md`
- Remove references to `custom-gitmojis.md`
- Update "Read Gitmoji Indices" to reference single cache file
- Remove "Lookup order" multi-step (just read cache)

### 2. Restructure commit skill execution steps

**File:** `agent-core/skills/commit/SKILL.md`

Reorder and simplify execution steps:

```markdown
## Execution Steps

1. **Pre-commit + discovery** (single bash block, fail fast)
   ```bash
   exec 2>&1
   set -xeuo pipefail
   just precommit  # or: just test (--test) / just lint (--lint)
   git status -vv
   ```
   - Precommit first: if it fails, no verbose output bloat
   - Shows: file status + staged diffs + unstaged diffs
   - Note what's already staged vs unstaged (preserve staging state)
   - ERROR if working tree is clean

2. **Perform handoff**
   - Run `/handoff` skill to update session.md

3. **Draft commit message**
   - Based on discovery output, follow "short, dense, structured" format

4. **Select gitmoji**
   - Invoke `/gitmoji` skill to select appropriate emoji
   - Prefix commit message title with selected gitmoji
   - Skip if `--no-gitmoji` flag provided

5. **Stage, commit, verify** (single bash block)
   ```bash
   exec 2>&1
   set -xeuo pipefail
   git add file1.txt file2.txt
   git commit -m "🐛 Fix authentication bug

   - Detail 1
   - Detail 2"
   git status
   ```
   - Stage specific files only (not `git add -A`)
   - Preserve already-staged files
   - Do NOT commit secrets (.env, credentials.json, etc.)
```

### 3. Restructure commit-context skill

**File:** `agent-core/skills/commit-context/SKILL.md`

Key differences from /commit:
- Skips discovery (uses conversation context)
- Skip precommit IF context shows: last edit → precommit passed
- For safety: include precommit in commit bash block

```markdown
## Execution Steps

1. **Perform handoff**
   - Run `/handoff` skill to update session.md

2. **Draft commit message**
   - Based on conversation context, follow "short, dense, structured" format

3. **Select gitmoji**
   - Invoke `/gitmoji` skill
   - Skip if `--no-gitmoji` flag provided

4. **Stage, commit, verify** (single bash block)
   ```bash
   exec 2>&1
   set -xeuo pipefail
   just precommit  # safety check (or just test/just lint per flag)
   git add file1.txt file2.txt
   git commit -m "🐛 Fix bug

   - Detail 1"
   git status
   ```
   - Precommit in bash block catches any issues
   - Stage specific files only
```

### 4. Update skill-development rule

**File:** `CLAUDE.md` (line 267)

```markdown
**Rule:** When creating, editing, or discussing skills, start by loading the `plugin-dev:skill-development` skill.
```

---

## Files Modified

- `agent-core/skills/gitmoji/scripts/update-gitmoji-index.sh` (append custom gitmojis)
- `agent-core/skills/gitmoji/custom-gitmojis.md` (delete)
- `agent-core/skills/gitmoji/SKILL.md` (simplify to single cache file)
- `agent-core/skills/commit/SKILL.md` (reorder steps, add gitmoji, fix staging, add token-efficient pattern)
- `agent-core/skills/commit-context/SKILL.md` (add gitmoji step, token-efficient pattern)
- `CLAUDE.md` (update Skill Development rule)

---

## Verification

1. **Run update script:** `./agent-core/skills/gitmoji/scripts/update-gitmoji-index.sh`
2. **Check cache:** `tail -5 agent-core/skills/gitmoji/cache/gitmojis.txt` (should show custom gitmojis)
3. **Gitmoji skill:** Read SKILL.md, confirm no custom-gitmojis.md references
4. **Commit skill:** Read SKILL.md, verify:
   - Precommit + discovery in step 1 (precommit first to avoid bloat on failure)
   - Gitmoji step present (step 4)
   - Stage/commit/verify in single bash block (step 5)
   - No blank line after strict mode in examples
5. **Commit-context skill:** Read SKILL.md, verify:
   - Precommit included in commit bash block (safety)
   - Gitmoji step present
6. **Test manually:** Make a change, run `/commit`, verify gitmoji selection and proper staging

---

## Future Work (out of scope)

**Optimize test execution:** Skip tests if no changes since last successful run.
- Approach: Script optimization, not agent behavior change
- Research: pytest caching docs

**split-plan.py:** Lightweight script for efficient plan dispatch.
- Split ad-hoc plans by `### N.` headers into step files
- Pattern: `split-plan.py plans/foo.md` → `plans/foo/steps/step-*.md`
- Enables lean orchestrator dispatch without context bloat
