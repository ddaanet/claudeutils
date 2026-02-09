## Problem

The Bash tool sandbox has a hardcoded write allowlist that includes `/tmp/claude/` (and sets `TMPDIR` to it). This path cannot be removed from the allowlist via any user-facing configuration.

For projects that enforce project-local temporary file usage (e.g., `<project-root>/tmp/`), this creates an unblockable escape hatch:

- **Write/Edit tools** can be blocked via `permissions.deny` rules (e.g., `Write(/tmp/*)`) and PreToolUse hooks
- **Bash tool** bypasses both — it writes at the OS level, and `/tmp/claude/` is sandbox-allowlisted

No combination of hooks, permissions, or CLAUDE.md instructions can prevent `echo "x" > /tmp/claude/foo` from succeeding.

## Why project-local tmp/ matters

- **Sandbox isolation:** Project files stay within project boundaries
- **Cleanup control:** `git clean` or project-level cleanup handles temp files
- **Cross-session persistence:** Project-local tmp/ can be gitignored but survives session restarts; `/tmp/claude/` may not
- **Consistency:** All file writes (tools + bash) go through the same enforcement path

## Current workarounds (incomplete)

| Mechanism | Write/Edit | Bash | Coverage |
|-----------|-----------|------|----------|
| `permissions.deny: Write(/tmp/*)` | Blocks | No effect | Partial |
| PreToolUse hook (exit 2) | Blocks | Can block whole command, can't inspect writes | Partial |
| CLAUDE.md instructions | Behavioral | Behavioral | Unreliable |
| Sandbox allowlist | N/A | `/tmp/claude` allowed | **Gap** |

## Proposed solution

A setting to customize the sandbox write allowlist:

```json
{
  "sandbox": {
    "writeAllowlist": {
      "remove": ["/tmp/claude"],
      "add": ["./tmp"]
    }
  }
}
```

Or more conservatively, a single flag to remove `/tmp/claude` from the allowlist:

```json
{
  "sandbox": {
    "disableTmpClaude": true
  }
}
```

## Relationship to other requests

This is the OS-level enforcement complement to tool description overrides. Overriding the sandbox note's TMPDIR guidance (prompt level) removes the model's *motivation* to write to `/tmp/claude`. This request removes the model's *ability* to do so.
