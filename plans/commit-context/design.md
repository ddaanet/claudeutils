# /commit-context Skill Design

**Status**: Ready for implementation

## Goal

New skill `/commit-context` that skips git discovery (status/diff/log) when agent already has context from conversation.

## Implementation

**Path**: `.claude/skills/commit-context/SKILL.md`

**Frontmatter**:
```yaml
name: commit-context
description: Commit using conversation context. Use when you know what changed (just wrote/edited files). Skips git status/diff discovery.
```

**Protocol** (simplified from /commit):

1. **Caller provides context**: Skill assumes agent knows what files changed and why (from conversation)

2. **Draft commit message**: Same format as /commit (imperative, 50-72 chars, bullet details)

3. **Run pre-commit checks**: Same validation flags as /commit (none/--test/--lint)

4. **Stage and commit**: `git add <specific files>` (not -A), then commit

5. **Verify**: `git status` to confirm clean

**Key differences from /commit**:
- NO `git status` for discovery (caller knows changes)
- NO `git diff HEAD` for analysis (caller analyzed already)
- NO `git log` (already removed from /commit)
- Stage specific files (not `git add -A`) based on context
- Still runs pre-commit validation

**Copy from /commit skill**:
- Commit message format section
- Validation flags section
- Critical constraints section
- Multi-line quoted string format (not heredocs)

## Verification

- [ ] Skill created at correct path
- [ ] Skips discovery steps
- [ ] Retains pre-commit validation
- [ ] Documents when to use (agent has context)
