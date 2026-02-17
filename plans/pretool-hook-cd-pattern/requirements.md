# Pretool Hook cd Pattern

## Requirements

### Functional Requirements

**FR-1: Allow `cd <project_root> && <command>` pattern**
The `submodule-safety.py` PreToolUse hook must allow Bash commands that begin with `cd <project_dir>` followed by `&&` and subsequent commands, when cwd ≠ project root. Currently only bare `cd <project_dir>` (exact match) is allowed, blocking the compound pattern sub-agents need.

Acceptance criteria:
- `cd /project/root && git status` → allowed (cwd restored before command runs)
- `cd /project/root && pytest tests/` → allowed
- `cd "/project/root" && some_cmd` → allowed (quoted variants)
- Bare `cd /project/root` → still allowed (existing behavior preserved)
- `git status` (without cd prefix, wrong cwd) → still blocked

**FR-2: Security analysis of the `cd && command` pattern**
Document the security implications of relaxing the exact-match constraint. Analysis must cover:
- Shell operator chaining after `&&` (`;`, `||`, pipes, subshells)
- Whether `cd <root> &&` prefix provides equivalent safety to "already at project root"
- Command injection surface (agent-generated vs external input)
- Comparison with current threat model (what does the hook actually prevent?)

Acceptance criteria:
- Written analysis in requirements or design artifact
- Each attack vector explicitly evaluated with verdict (safe/risk/mitigated)
- Recommendation: proceed, proceed with constraints, or reject

**FR-3: Handle quoting and whitespace variants**
The cd prefix check must handle the quoting variants that agents actually produce:
- `cd /path && cmd` (unquoted)
- `cd "/path" && cmd` (double-quoted)
- `cd '/path' && cmd` (single-quoted)
- Whitespace around `&&` (e.g., `cd /path&&cmd`, `cd /path  &&  cmd`)

Acceptance criteria:
- All quoting variants pass through when path matches project root
- Mismatched paths still blocked regardless of quoting

### Constraints

**C-1: No weakening of wrong-cwd blocking**
Commands without a `cd <project_root>` prefix must remain blocked when cwd ≠ project root. The relaxation is strictly for commands that restore cwd as their first action.

**C-2: Exact path matching only**
The cd target must be exactly `$CLAUDE_PROJECT_DIR` — no path traversal (`../`), symlink resolution, or partial matching. The current exact-match security property must extend to the compound pattern.

**C-3: PostToolUse behavior unchanged**
The PostToolUse cwd-drift warning is independent and must not be affected.

### Out of Scope

- Allowing commands from arbitrary directories (hook's core invariant)
- Allowing `cd <other_path> && cmd` where path ≠ project root
- Changes to PostToolUse handler
- Changes to other hooks (pretooluse-block-tmp.sh, pretooluse-symlink-redirect.sh)
- Sub-agent hook execution (hooks don't fire in sub-agents — separate concern)

### Security Analysis

#### Threat Model: What does the hook prevent?

The hook enforces: **all Bash commands execute from project root**. This prevents:
1. **Context confusion** — agent reads files from wrong directory, makes decisions based on wrong codebase
2. **Cross-project contamination** — edits applied to wrong project when in worktree/monorepo setup
3. **Stale state** — agent operates on a checkout that doesn't match its mental model

The hook does NOT prevent:
- Agent running `cd /elsewhere` from project root (allowed, caught by PostToolUse)
- Malicious commands from project root (not in scope — the hook is a cwd guard, not a command filter)

#### Analysis: Is `cd <root> && <cmd>` equivalent to "already at root"?

**Yes, with caveats.**

Shell semantics of `cd /path && cmd`:
- If `cd` fails → `cmd` does not execute (short-circuit `&&`)
- If `cd` succeeds → `cmd` executes from `/path`
- Equivalent to: subprocess with cwd=/path running cmd

**Attack vectors evaluated:**

| Vector | Verdict | Reasoning |
|--------|---------|-----------|
| `cd /root && cd /evil && bad_cmd` | **Safe** | Same as running `cd /evil` from project root — already possible, caught by PostToolUse |
| `cd /root && cmd; evil_cmd` | **Safe** | Both commands execute from /root. `;` doesn't change cwd |
| `cd /root && cmd \|\| evil_cmd` | **Safe** | Fallback runs from /root |
| `cd /root && $(evil)` | **Safe** | Subshell inherits /root as cwd |
| Path traversal: `cd /root/../evil &&` | **Mitigated by C-2** | Exact string match rejects traversal |
| Newline injection: `cd /root\n evil` | **Investigate** | Hook receives command as string from Claude — no user-controlled injection point. Agent-generated only. |

**Conclusion: Proceed.** The `cd <root> &&` prefix guarantees subsequent commands start from project root — identical security posture to the current "cwd is already correct" case. The hook's value is preventing *accidental* wrong-cwd execution, not preventing an adversarial agent (which could bypass hooks entirely).

#### Residual Risk

The relaxation slightly increases the "allowed command surface" — previously only bare `cd` was allowed from wrong cwd, now compound commands are too. But the compound commands execute from project root, so the security invariant (commands run from correct directory) is preserved.

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (hook modification in FR-1)
