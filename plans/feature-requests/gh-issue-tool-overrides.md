## Problem

The Bash tool description includes ~1600 tokens of hardcoded content that cannot be disabled or replaced:

- **Git commit/PR instructions** (`GIT_COMMIT_AND_PR_CREATION_INSTRUCTION`, ~800 tokens) — step-by-step commit and PR workflow with repeated "call multiple tools in parallel" boilerplate (4x)
- **Sandbox behavioral note** (~450 tokens) — tells the model how to handle sandbox failures, includes auto-retry guidance that promotes ask-by-default behavior (see related issue below)
- **"Use specialized tools over bash"** guidance (~350 tokens) — "Avoid using Bash with find, grep, cat, head, tail, sed, awk, echo"

For users who have custom commit workflows (skills, hooks, scripts), enforce tool usage via PreToolUse hooks, and manage sandbox behavior through `permissions.allow` + project CLAUDE.md, this is pure token waste on every conversation.

## Evidence of demand

- [tweakcc](https://github.com/Piebald-AI/tweakcc) by Piebald AI already patches these exact strings in local Claude Code installations — proving users want per-component control
- `--system-prompt` flag overrides the main system prompt but not tool descriptions — the override surface is incomplete
- #8245 reports 20k+ tokens of git status context that can't be disabled — same class of problem (unavoidable git-related prompt overhead)

## Proposed solution

A setting to override individual tool description components, complementing `--system-prompt`:

```json
{
  "toolPrompts": {
    "bash.gitInstructions": false,
    "bash.sandboxNote": "path/to/custom-sandbox-note.md",
    "bash.main": "path/to/custom-bash-description.md"
  }
}
```

Or more broadly, expose tool descriptions as overridable markdown files (similar to how CLAUDE.md overrides behavior), allowing users to replace any component with their own version or disable it entirely.

## Use case

Power users building LLM environments on top of Claude Code CLI who:
- Run with `--system-prompt` to replace the main system prompt
- Have custom commit/git workflows via skills and scripts
- Enforce tool usage patterns via PreToolUse hooks
- Need to redirect temporary file usage to project-local directories (conflicting with builtin `/tmp/claude` TMPDIR guidance)

## Related

- #8245 — Git status context wastes >20k tokens, cannot be disabled
- #6825 — Subagent context inheritance configurability (closed as completed — precedent for this type of configurability)
