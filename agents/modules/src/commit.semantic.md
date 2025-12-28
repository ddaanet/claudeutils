# Commit Skill Module

---
author_model: claude-opus-4-5-20251101
semantic_type: skill
expansion_sensitivity: explicit
target_rules:
  weak: 12-16
note: Skills only generate weak variant (loaded on-demand at session end)
---

## Semantic Intent

Git commits should have clear, concise messages that explain what changed and why. Avoid
methodology details, vendor credits, and obvious implementation details. Stage files
explicitly to avoid committing unintended changes.

---

## Critical (Tier 1)

### No Built-in Commit Commands

Do NOT use `/commit` or other built-in Claude Code skills. Follow this skill file
instead.

### Explicit File Staging

Never use `git add -A` or `git add .` - these can stage unintended files. Always add
files explicitly: `git add src/specific.py tests/test_specific.py`

### Message Content

Commit messages include:

- What changed at a high level
- Why the change was made (if not obvious)
- Design rationale for architectural decisions

Commit messages NEVER include:

- TDD or methodology mentions
- Vendor credits (Claude, Anthropic)
- Implementation details visible in the diff

---

## Important (Tier 2)

### Message Format

Short summary line (imperative mood), blank line, longer explanation if needed.

For multi-line messages, use heredoc:

```bash
git commit -m "$(cat <<'EOF'
Short summary line

Longer explanation of why this change was made.
EOF
)"
```

### Pre-Commit Verification

Before committing:

- `git status` - check what will be staged
- `git diff HEAD` - review all changes

---

## Preferred (Tier 3)

### Error Recovery

If commit fails with lock file error (.git/index.lock):

1. Wait 2 seconds, retry
2. If still failing, wait 2 more seconds, retry
3. Only ask user after two failed retries
