# Worktree RM Safety Gate

## Requirements

### Functional Requirements

**FR-1: Detect uncommitted changes in parent worktree**
`rm` checks parent worktree `git status --porcelain` before any destructive operations. If dirty files exist, exit non-zero with status output listing dirty files. Currently warns and proceeds (cli.py:373-376).

**FR-2: Detect uncommitted changes in submodule**
`rm` checks agent-core submodule `git status --porcelain` before any destructive operations. If dirty files exist, exit non-zero with status output. Currently no submodule check exists in `rm`.

**FR-3: Exit code convention**
Exit 2 on dirty tree detection (consistent with `_delete_branch` precedent). Status output describes what's dirty (parent, submodule, or both) with file list.

**FR-4: `--force` flag bypasses safety gate**
`rm --force <slug>` skips dirty tree check and proceeds with current warn-and-remove behavior. Required for automation, intentional abandonment of worktrees, and non-interactive callers.

**FR-5: Skill layer surfaces status and confirms**
Worktree skill Mode C (`wt-rm`) catches exit 2, surfaces dirty file list to user, asks for confirmation, retries with `--force` if confirmed.

### Constraints

**C-1: Layered design — CLI refuses, caller decides**
Established pattern from `_delete_branch` (exit 2). CLI detects problem and reports; skill/agent layer handles user interaction. CLI never prompts interactively.

**C-2: Reuse existing `clean-tree` patterns**
`clean-tree` command and `verify_clean_tree` (merge.py) already check parent + submodule with correct porcelain parsing. Extract shared logic or follow same pattern.

**C-3: Session context files exempt from dirty check**
`clean-tree` exempts `session.md`, `jobs.md`, `learnings.md` in `agents/`. Same exemption applies here — these are expected to change during worktree lifecycle.

### Out of Scope

- Changes to `merge` command dirty checks (already gates correctly via `verify_clean_tree`)
- Changes to `new` command
- Untracked file detection in submodule (current `--porcelain` covers tracked modifications only; match existing convention)

### References

- `src/claudeutils/worktree/cli.py:366-397` — current `rm` implementation
- `src/claudeutils/worktree/cli.py:227-245` — `clean-tree` command (parent + submodule pattern)
- `src/claudeutils/worktree/merge.py:23-61` — `verify_clean_tree` (merge dirty check with exemptions)
- `src/claudeutils/worktree/cli.py:336-346` — `_delete_branch` exit 2 precedent
- Session evidence: `wt rm` warned about 1 uncommitted file, proceeded, lost changes; agent-core had 3-file divergent branch silently dropped
