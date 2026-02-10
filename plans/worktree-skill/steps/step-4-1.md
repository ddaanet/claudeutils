# Cycle 4.1

**Plan**: `plans/worktree-skill/runbook.md`
**Execution Model**: haiku
**Phase**: 4
**Report Path**: `plans/worktree-skill/reports/cycle-4-1-notes.md`

---

## Cycle 4.1: Frontmatter and file structure

**RED:**
Test YAML frontmatter validates with required fields. Create empty skill file `agent-core/skills/worktree/SKILL.md` with only frontmatter YAML. Run `python3 -c 'import yaml; yaml.safe_load(open("agent-core/skills/worktree/SKILL.md").read().split("---")[1])'` — should parse without errors.

Verify required fields exist and have correct structure:
- `name: worktree` exists as string
- `description:` exists as multi-line string mentioning invocation triggers: "create a worktree", "set up parallel work", "merge a worktree", "branch off a task", `wt` shortcut
- `allowed-tools:` exists as list including Read, Write, Edit, `Bash(claudeutils _worktree:*)`, `Bash(just precommit)`, `Bash(git status:*)`, `Bash(git worktree:*)`, Skill
- `user-invocable: true` exists as boolean
- `continuation:` exists as dict with `cooperative: true` and `default-exit: []` (empty array)

Read the file and assert each field's presence and type. The test should fail if any required field is missing or has wrong type.

**GREEN:**
Create `agent-core/skills/worktree/SKILL.md` with frontmatter block following YAML multi-line syntax for description. Use `>-` for folded scalar (preserves single newlines, folds long lines).

Describe the skill's purpose clearly: manages worktree lifecycle from creation through merge cleanup. Mention all invocation patterns user might say. Include behavioral triggers: "create", "set up", "merge", "branch off", plus literal shortcut `wt`.

Specify allowed-tools comprehensively. Use wildcard patterns where appropriate (`claudeutils _worktree:*` covers all subcommands). Include Skill tool for potential `/handoff --commit` invocation.

Set continuation cooperative mode with empty default-exit (skill completes inline, no tail calls by default).

After frontmatter, add H2 section headers for the three modes: `## Mode A: Single Task`, `## Mode B: Parallel Group`, `## Mode C: Merge Ceremony`. Leave sections empty for now.

---

**Expected Outcome**: GREEN verification, no regressions
**Stop/Error Conditions**: RED doesn't fail → STOP; GREEN doesn't pass → Debug; Regression → STOP
**Validation**: RED verified ✓, GREEN verified ✓, No regressions ✓
**Success Criteria**: Test fails during RED, passes during GREEN, no breaks
**Report Path**: plans/worktree-skill/reports/cycle-4-1-notes.md

---
