# Fragment Redundancy Analysis

Comparison of project CLAUDE.md fragments against Claude Code builtin prompts.
Source: [claude-code-system-prompts](https://github.com/Piebald-AI/claude-code-system-prompts) v2.0.76.

## Purpose

Identify fragments that duplicate builtin prompt content. These fragments:
- Waste tokens (loaded every session via CLAUDE.md, on top of builtin equivalents)
- May conflict with builtin wording, causing competing directives
- Are candidates for removal once builtin prompts can be overridden via tweakcc

## Redundancy Map

### Fully redundant (builtin covers same ground)

| Fragment | Builtin source | Overlap |
|----------|---------------|---------|
| `commit-skill-usage.md` | `tool-description-bash-git-commit-and-pr-creation-instructions.md` (~1615 tks) | Fragment says "use /commit skill." Builtin provides full git commit/PR workflow. Both compete for commit behavior. Fragment wins via skill invocation, but builtin tokens still loaded. |
| `tmp-directory.md` | `tool-description-bash-sandbox-note.md` — TMPDIR=/tmp/claude guidance; `system-prompt-scratchpad-directory.md` (~172 tks) | Fragment says "use project tmp/, never /tmp/claude." Builtin says "TMPDIR is /tmp/claude." Direct contradiction. Hook enforces fragment's rule for Write/Edit but not Bash. |

### Partially redundant (fragment extends or conflicts)

| Fragment | Builtin source | Overlap | Fragment adds |
|----------|---------------|---------|---------------|
| `tool-batching.md` | Bash tool: "When issuing multiple commands" (parallel vs sequential, && vs ;). Main system prompt: "call multiple tools in a single response." Git instructions: same phrase 4x. | Parallel/sequential tool call guidance | File-level edit planning (same-file sequential, different-file parallel, bottom-to-top insertion). Builtin has no edit-level batching. |
| `delegation.md` "Task Agent Tool Usage" | Bash tool: "Avoid using Bash with find, grep, cat, head, tail, sed, awk, echo" + tool mapping list | Identical tool mapping (Grep not grep, Read not cat, etc.) | Delegation framing (remind agents in task prompts). Builtin only tells main agent. |
| `sandbox-exemptions.md` | `tool-description-bash-sandbox-note.md` (~454 tks) | Both explain dangerouslyDisableSandbox, sandbox failure analysis | Project-specific bypass patterns (prepare-runbook.py, just sync-to-parent), prefix matching rule, excludedCommands bugs |
| `no-estimates.md` | Main system prompt: "Planning without timelines" section | Both say don't give time estimates | Fragment is 1 line. Builtin is a paragraph. |
| `error-handling.md` | Sandbox note: failure analysis guidance | Both discuss handling errors | Fragment is broader (all errors, not just sandbox). Sandbox note is specific to sandbox failures. |

### No redundancy (fragment-only knowledge)

| Fragment | Notes |
|----------|-------|
| `workflows-terminology.md` | Project-specific workflow definitions |
| `communication.md` | Agent behavioral rules |
| `execute-rule.md` | Session modes, shortcuts, task notation |
| `vet-requirement.md` | Vet-fix-agent requirement |
| `token-economy.md` | Token conservation rules |
| `code-removal.md` | Delete-don't-archive policy |
| `bash-strict-mode.md` | set -xeuo pipefail pattern |
| `claude-config-layout.md` | Hook/agent/bash config reference |
| `design-decisions.md` | /opus-design-question routing |
| `project-tooling.md` | Recipe-first evaluation |

## Token cost of redundancy

| Fragment | Tokens | Builtin equivalent tokens | Combined waste |
|----------|--------|--------------------------|----------------|
| `commit-skill-usage.md` | ~30 | ~1615 | ~1615 (builtin loaded regardless) |
| `tmp-directory.md` | ~80 | ~454 + ~172 | ~626 (builtin loaded regardless) |
| `tool-batching.md` | ~120 | ~200 (bash) + ~100 (main) | ~200 (partial overlap) |
| `delegation.md` tool section | ~100 | ~150 (bash tool list) | ~150 (near-identical) |
| `sandbox-exemptions.md` | ~300 | ~454 | ~454 (builtin loaded regardless) |
| `no-estimates.md` | ~20 | ~50 | ~50 (builtin loaded regardless) |
| **Total fragment tokens** | ~650 | | |
| **Total builtin overlap** | | ~3095 | |

The fragments cost ~650 tokens. The builtin equivalents cost ~3095 tokens that load regardless. Combined, ~3745 tokens of redundant or competing content per session.

## Plan: tweakcc integration

**Forward strategy:** Keep fragments as the authoritative source. Use tweakcc to replace builtin equivalents with minimal stubs or remove them entirely.

### Phase 1: Override builtin prompts via tweakcc

For each fully/partially redundant builtin:

| Builtin to override | Action | Fragment remains |
|---------------------|--------|-----------------|
| `tool-description-bash-git-commit-and-pr-creation-instructions.md` | Remove entirely (tweakcc patch to empty) | `commit-skill-usage.md` — already minimal |
| `tool-description-bash-sandbox-note.md` | Replace with project-specific sandbox guidance | `sandbox-exemptions.md` — keeps project patterns |
| `system-prompt-scratchpad-directory.md` | Remove entirely | `tmp-directory.md` — evaluate removal (see below) |
| Bash tool "Avoid using Bash with..." section | Remove (enforced by hook instead) | `delegation.md` tool section — keeps delegation framing |
| Bash tool "When issuing multiple commands" | Keep or thin | `tool-batching.md` — keeps edit-level batching |
| Main system prompt "Planning without timelines" | Keep (low token cost) | `no-estimates.md` — evaluate removal |

### Phase 2: Fragment cleanup (post-tweakcc)

After builtins are overridden, evaluate removing fragments that existed only to counter builtin behavior:

| Fragment | Remove? | Condition |
|----------|---------|-----------|
| `tmp-directory.md` | Yes | After sandbox note overridden + sandbox allowlist configurable (feature request) |
| `commit-skill-usage.md` | Yes | After git instructions removed via tweakcc |
| `no-estimates.md` | Maybe | 20 tokens, low cost. Keep if builtin "Planning without timelines" also removed. |
| `tool-batching.md` | Keep | Edit-level batching is fragment-only knowledge |
| `delegation.md` tool section | Keep | Delegation framing for sub-agents is fragment-only |
| `sandbox-exemptions.md` | Keep | Project-specific patterns not in any builtin |

### Phase 3: PreToolUse hook for bash tool usage

Replace prompt-level "use specialized tools over bash" with runtime enforcement:
- Hook matches Bash tool calls
- Filter: trivial one-liner commands (no pipes, no redirects, no complex logic)
- Check if command maps to a specialized tool (cat → Read, grep → Grep, find → Glob)
- Block with guidance: "Use Read tool instead of cat"
- Pass through: complex commands, pipes, redirects, multi-command chains

This eliminates the need for both the builtin bash guidance AND the delegation.md tool section for the main agent. Fragment keeps the reminder for sub-agent task prompts (hooks don't fire in sub-agents).
