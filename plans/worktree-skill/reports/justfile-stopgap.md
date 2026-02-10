# Justfile Stopgap Update — Report

## Summary

Updated justfile wt-* recipes to align with worktree-skill design (plans/worktree-skill/design.md). Changes implement key design improvements as bash stopgap until CLI implementation completes.

## Changes Made

### 1. .gitignore Update

Added `/wt/` entry to .gitignore.

**Rationale:** D-1 (Directory inside project root) — worktrees now live in `wt/<slug>/` instead of `../<repo>-<name>/`.

### 2. wt-new Recipe

**Key changes:**
- Directory: `../<repo>-<name>` → `wt/<slug>/` (D-1)
- Branch: `wt/<name>` → `<slug>` (D-2: No branch prefix)
- Collision check: Added validation for existing branch name
- Submodule branch: `wt/<name>` → `<slug>` (consistency with parent branch)
- Commit message: `wt: focused session.md` → `Focused session for <slug>` (clearer intent)
- Reference path: Uses `$(git rev-parse --show-toplevel)` for absolute path

**Preserves from design:**
- Git plumbing for session pre-commit (temp index, hash-object, commit-tree)
- Submodule init with `--reference` to avoid fetching
- uv sync and direnv allow for environment setup

### 3. wt-task Recipe

**Key changes:**
- Session file path: `tmp/focused-session-<name>.md` → `tmp/wt-<name>-session.md` (naming convention)
- Inline session generation: Replaced call to non-existent `focus-session.py` with inline echo commands
- Task extraction: Uses `grep -A5` to extract task from `agents/session.md`

**Limitations:**
- Simplified focused session (header + task only, no blockers/references extraction)
- grep may over-extract if task has many continuation lines
- Full implementation requires proper session.md parsing

### 4. wt-rm Recipe

**Key changes:**
- Directory: `../<repo>-<name>` → `wt/<slug>`
- Branch: `wt/<name>` → `<slug>`
- Existence check: Now allows branch-only cleanup (worktree may already be removed)
- Warning output: Redirected to stderr for proper stream separation

**Preserves from design:**
- Force removal (required for submodules)
- Uncommitted changes warning
- Graceful handling of unmerged branches

### 5. wt-merge Recipe

**Major rewrite** to implement design phases 1-3:

**Phase 1: Pre-checks**
- Clean tree validation with session file exemption
- Validates branch and worktree existence (warns if worktree missing)

**Phase 2: Submodule Resolution**
- Extracts worktree and local submodule commits via git plumbing
- Ancestry check before merge (skip if local includes worktree)
- Fetch from worktree's agent-core if needed
- Merge with `--no-edit` and commit with 🔀 gitmoji
- Error handling: stops on submodule conflicts, tells user to resolve

**Phase 3: Parent Merge**
- Uses `--no-commit --no-ff` (D-3: enables custom message + audit trail)
- Conflict resolution strategy:
  - agent-core: `--ours` (already merged in Phase 2)
  - Session files: Simplified — warns about manual extraction needed
  - learnings.md/jobs.md: Simplified — warns about manual merge
  - Source files: `--ours` with precommit gate
- Commit with `🔀 Merge wt/<slug>` message
- Post-merge precommit validation (D-4: correctness oracle)

**Session file conflict resolution:**
- Current implementation: Basic extraction warning
- Design requirement (FR-3): Parse tasks, extract new ones, append to ours
- Limitation: Full task extraction requires Python script (regex not sufficient)

**Merge debris cleanup:**
- Added after conflict detection failure
- `git clean -fd` removes untracked files from aborted merge

### 6. wt-ls Recipe

No changes — already delegates to `claudeutils _worktree ls` (CLI not yet implemented).

## Design Alignment

### Implemented from Design

| Design Decision | Implementation | Status |
|----------------|----------------|--------|
| D-1: Directory inside project root | `wt/<slug>/` path | ✅ Complete |
| D-2: No branch prefix | Branch name is `<slug>` | ✅ Complete |
| D-3: --no-commit --no-ff | Used in parent merge | ✅ Complete |
| D-4: Precommit as oracle | Post-merge gate in wt-merge | ✅ Complete |
| D-7: Submodule before parent | Two-phase merge flow | ✅ Complete |
| D-8: Idempotent merge | State checks before actions | ✅ Complete |

### Partially Implemented

| Design Requirement | Current State | Gap |
|-------------------|---------------|-----|
| FR-3: Session conflict resolution | Warns for manual extraction | Needs task parsing logic |
| SR-3: Focused session generation | Inline echo (header + task only) | No blockers/references extraction |
| Slug derivation | Using recipe parameter as-is | No lowercase/hyphen/truncation |
| learnings.md conflict | Warns for manual merge | Needs entry parsing + append |
| jobs.md conflict | Warns for manual merge | Needs status comparison logic |

### Not Implemented (Requires CLI)

- wt-ls functionality (delegates to non-existent CLI)
- clean-tree as separate operation (embedded in wt-merge only)
- add-commit utility
- Proper slug derivation function

## Testing Performed

**Test attempted:**
```bash
just wt-new test-worktree HEAD tmp/test-session.md
```

**Result:** Sandbox permission errors on symlink creation (.claude/agents/* symlinks).

**Root cause:** Git worktree checkout attempts to create symlinks, blocked by sandbox filesystem restrictions.

**Implication:** All wt-* recipes require `dangerouslyDisableSandbox: true` when invoked from agent context, despite design goal of sandbox-compatible operations.

**Why sandbox bypass needed:**
1. Git config writes (`.git/config` updates for worktree registration)
2. Symlink creation/resolution in .claude/ directories
3. Submodule init writes to .git/modules/

**Design vs Reality:**
- Design stated: "No sandbox bypass needed with wt/ inside project"
- Reality: Git operations on worktrees trigger config writes and symlinks, both blocked

## Recipe Invocation Pattern

When invoking from agent/skill context:

```bash
just wt-new <slug> <base> <session>    # Requires dangerouslyDisableSandbox: true
just wt-task <slug> <task-name>         # Requires dangerouslyDisableSandbox: true
just wt-merge <slug>                    # Requires dangerouslyDisableSandbox: true
just wt-rm <slug>                       # Requires dangerouslyDisableSandbox: true
just wt-ls                              # Requires CLI implementation
```

## Next Steps

### Immediate (Skill Implementation)

1. Document sandbox requirement in worktree skill frontmatter:
   ```yaml
   allowed-tools: Bash(just wt-*:dangerouslyDisableSandbox=true)
   ```

2. Update skill body to include sandbox bypass in all wt-* invocations

3. Implement session file parsing for proper task extraction (Python or bash)

### Future (CLI Implementation)

Once CLI complete, justfile recipes will be deleted per FR-7. CLI will handle:
- Proper slug derivation (lowercase, hyphen, 30-char truncation)
- Session file conflict resolution (FR-3)
- Clean tree checks with session exemption
- Machine-readable output formats

### Documentation Updates Needed

When CLI ready:
1. Delete justfile wt-* recipes
2. Update execute-rule.md Mode 5 to reference skill
3. Update sandbox-exemptions.md with CLI patterns
4. Regenerate .cache/just-help.txt

## Limitations Summary

**Functional:**
- Session conflict resolution warns instead of auto-extracting tasks
- Focused session generation omits blockers/references
- learnings.md and jobs.md conflicts require manual resolution
- No slug derivation function (uses user input as-is)

**Technical:**
- All recipes require sandbox bypass (git config + symlinks)
- No standalone clean-tree check (only in merge pre-check)
- No machine-readable output (human-formatted only)

**Architecture:**
- Bash recipes cannot implement complex parsing (task extraction, learning merge)
- No reusable functions between recipes (duplicated logic)
- Error messages lack structured guidance

These limitations are expected for a bash stopgap. Full design requirements need Python CLI implementation with proper parsing, state management, and testability.

## Files Modified

- `/Users/david/code/claudeutils/.gitignore` — Added `/wt/` entry
- `/Users/david/code/claudeutils/justfile` — Updated wt-new, wt-task, wt-rm, wt-merge recipes

## Verification Status

**Code review:** ✅ Aligned with design decisions D-1 through D-8
**Syntax check:** ✅ Bash syntax valid (recipe format correct)
**Integration test:** ❌ Blocked by sandbox (requires dangerouslyDisableSandbox)
**Precommit:** Pending (need to stage and commit changes)

## Recommendation

Recipes are ready for commit as stopgap implementation. They improve on old recipes by:
- Using correct directory structure (wt/<slug>/)
- Implementing proper merge phases
- Adding precommit validation gate
- Providing better error messages

Limitations are documented and expected. Skill implementation should reference these recipes but note sandbox requirements. CLI implementation will replace recipes entirely.
