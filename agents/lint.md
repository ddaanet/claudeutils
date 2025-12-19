---
name: lint
description: Fix linting and type checking errors
---

# Lint Skill

**Agent:** Weak models (haiku).

## Role

Fix errors reported by `just check` (ruff + mypy).

---

## Workflow (Critical)

**Always run `just format check`** (not just `just check`). The format step auto-fixes many issues.

1. Run `just format check`
2. If format modified files, **re-read them before editing** - your cached version is stale
3. Fix remaining errors reported by check
4. Repeat until clean

⚠️ **Never edit a file without re-reading it first after format runs.** Format changes line numbers and content.

---

## Core Principles

### No Complexity Refactoring

⚠️ **Do NOT fix complexity issues (e.g., C901 "too complex").** Complexity fixes require refactoring, which needs planning from a strong agent. If you see complexity errors:

1. Skip them
2. Report them to the user
3. Continue with other lint errors

### No Suppression Shortcuts

If linter or type checker complains, fix the underlying issue properly.

- Prefer architectural fixes over `# noqa` suppressions
- Refactor code to satisfy type checker rather than using `type: ignore`
- Address the root cause, not just the symptom

### Explain All Ignores

Any suppression comment must include an explanation:

```python
# GOOD: Explains why ignore is intentional
value = cast(str, data)  # type: ignore[arg-type] - API returns untyped dict

# BAD: No explanation
value = cast(str, data)  # type: ignore
```

### Use Correct Directives

- Use `# noqa: <code>` for ruff suppressions (NOT pyright directives)
- Ruff handles both linting and formatting in this project
- Example: `# noqa: E501` not `# pyright: ignore`

---

## Quick Reference

```bash
just format check   # Preferred: format then check (re-read files after)
just check          # Run ruff + mypy only
just format         # Auto-format only
just dev            # Full cycle: format, check, test
```

---

## Common Fixes

### Ruff Errors

| Code | Issue | Fix |
|------|-------|-----|
| F401 | Unused import | Remove the import |
| F841 | Unused variable | Remove or prefix with `_` |
| E501 | Line too long | Break into multiple lines |
| I001 | Import order | Run `just format` |

### Mypy Errors

| Error | Issue | Fix |
|-------|-------|-----|
| `arg-type` | Wrong argument type | Fix the type or add proper cast with comment |
| `return-value` | Wrong return type | Fix function signature or return statement |
| `assignment` | Type mismatch | Fix variable type annotation |
| `no-untyped-def` | Missing annotations | Add parameter and return type annotations |

---

## When Ignores Are Acceptable

Use suppressions only after exhausting alternatives:

### Missing Types in Third-Party Libraries

1. Search for a stubs package (e.g., `types-requests`, `types-PyYAML`)
2. Install with `uv add --dev types-<package>`
3. Only suppress if no stubs exist

### Incorrect or Insufficiently Specific Types

1. Search the library's bug tracker for the issue
2. Search the web for known workarounds
3. **Do not conclude it's a library limitation without evidence**
4. If confirmed as library issue: report that `agents/lint.md` must be updated to document the issue, providing the most authoritative source (GitHub issue, documentation, etc.)
5. **Rules files are only updated by a strong agent** - do not edit lint.md yourself

### Python Type System Limitations

If the type system cannot express a valid pattern:

1. Report the issue to the user
2. **Do not make changes** - wait for user guidance

Always document the reason in the ignore comment with a reference to the source.
