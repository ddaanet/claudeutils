### Phase 5: Integration and Documentation (~4 cycles)

**Model:** haiku (mechanical wiring)
**Checkpoint:** light (vet-fix-agent)
**Depends on:** Phases 0-4 (CLI + SKILL.md implementation)

**Overview:** Wire worktree CLI into main command interface, update project configuration and documentation to reflect the new skill, and remove obsolete justfile recipes.

---

## Cycle 5.1: CLI Registration and .gitignore

**RED — Specify the behavior to verify:**

The main `claudeutils` CLI does not yet expose the `_worktree` subcommand. Running `claudeutils _worktree --help` should display the worktree command group with all six subcommands (new, rm, merge, ls, clean-tree, add-commit).

The project `.gitignore` does not yet exclude the `wt/` directory. Git status should not show untracked `wt/` worktree directories.

**Test expectations:**
- `claudeutils _worktree --help` exits 0 and displays Click group help with six subcommands listed
- `.gitignore` contains `wt/` entry
- Creating a test worktree `wt/test-slug/` results in git status showing no untracked directory warning

**GREEN — Implement to make tests pass:**

Import the worktree command group from `claudeutils.worktree.cli` and register it with the main CLI using `cli.add_command(worktree, "_worktree")`. The underscore prefix indicates this is an internal subcommand (invoked by skill, not users directly).

Add `wt/` entry to `.gitignore` to exclude worktree directories from version control.

**Approach:**
- Edit `src/claudeutils/cli.py`: add import statement for worktree command group, register with main CLI
- Edit `.gitignore`: append `wt/` entry (one line)
- Verify with manual test: `claudeutils _worktree --help` displays expected output

---

## Cycle 5.2: execute-rule.md Mode 5 Update

**RED — Specify the behavior to verify:**

The `agent-core/fragments/execute-rule.md` file still contains inline prose for Mode 5 (worktree setup) behavior. It should instead reference the `/worktree` skill as the canonical implementation.

**Test expectations:**
- Mode 5 section header remains: "### MODE 5: WORKTREE SETUP"
- Triggers section references `wt` commands
- Body text directs reader to `/worktree` skill documentation
- No inline implementation prose (slug derivation, session generation, merge ceremony)

**GREEN — Implement to make tests pass:**

Replace the inline worktree implementation prose with a reference to the `/worktree` skill. Preserve the trigger documentation (`wt` and `wt <task-name>`) but delegate behavior description to the skill.

**Approach:**
- Edit `agent-core/fragments/execute-rule.md` Mode 5 section
- Remove detailed implementation steps (slug derivation, focused session generation, worktree creation flow)
- Add: "See `agent-core/skills/worktree/SKILL.md` for implementation details"
- Keep trigger documentation intact for reference

---

## Cycle 5.3: sandbox-exemptions.md Worktree Patterns

**RED — Specify the behavior to verify:**

The `agent-core/fragments/sandbox-exemptions.md` file does not yet document worktree-specific sandbox bypass requirements. Agents invoking `_worktree new` need guidance on when sandbox bypass is required.

**Test expectations:**
- Section exists documenting worktree sandbox requirements
- Explains that `wt/` inside project root eliminates most sandbox bypass needs
- Documents exceptions: `uv sync` (network + filesystem for package downloads) and `direnv allow` (writes outside project)
- Notes that skill invokes these with `dangerouslyDisableSandbox: true`

**GREEN — Implement to make tests pass:**

Add a worktree-specific section to `sandbox-exemptions.md` documenting the directory location change (inside project root) and the remaining operations that require sandbox bypass (environment setup: `uv sync` and `direnv allow`).

**Approach:**
- Add new section: "### Worktree Operations"
- Explain directory location eliminates most bypass needs
- List exceptions: environment initialization steps in new worktrees
- Clarify that skill handles sandbox bypass, CLI itself is agnostic

---

## Cycle 5.4: Justfile Recipe Deletion

**RED — Specify the behavior to verify:**

The justfile still contains five obsolete recipes: `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, `wt-merge`. These are superseded by the `_worktree` CLI subcommand. Running `just --list` should not display these recipes.

The cached help text `.cache/just-help.txt` still references the old recipes. Running `just cache` should regenerate this file without the obsolete entries.

**Test expectations:**
- Justfile does not contain `wt-new`, `wt-task`, `wt-ls`, `wt-rm`, or `wt-merge` recipe definitions
- `just --list` output does not include these five recipes
- `.cache/just-help.txt` does not reference obsolete worktree recipes
- `just cache` completes successfully and updates cached help

**GREEN — Implement to make tests pass:**

Delete the five worktree recipe definitions from the justfile. Run `just cache` to regenerate `.cache/just-help.txt` with the updated recipe list.

**Approach:**
- Edit `justfile`: remove all five `wt-*` recipe blocks (likely contiguous section)
- Run `just cache` to regenerate cached help text
- Verify with `just --list`: no worktree recipes shown
- Verify `.cache/just-help.txt`: no references to `wt-new`, `wt-task`, etc.

**Note:** Recipe deletion may affect line count significantly. The justfile is tracked in version control, so git diff will show exact removals.
