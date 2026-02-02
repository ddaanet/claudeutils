---
name: commit
description: Git commit standards
---

# Commit Skill

## BEFORE STARTING (Mandatory)

⚠️ **Do NOT use `/commit` or other built-in Claude Code skills.** Follow this file
instead.

**If not already loaded, read this file using the Read tool:**

1. `CLAUDE.md` - Project overview and user preferences

⚠️ **Do not proceed until this file is in context.**

## Commit Message Format

### Core Principles

- **Concise:** Focus on WHAT changed and WHY
- **No methodology details:** Don't mention "with TDD" or implementation approach
- **Design rationale:** Include reasoning for non-obvious changes

### Anti-Patterns - Never Include

🚫 **DON'T mention:**

- TDD/methodology in commit messages
- Vendor credits (don't mention Claude/Anthropic)
- Implementation details that are visible in the diff

✅ **DO include:**

- What changed at a high level
- Why the change was made (if not obvious)
- Design rationale for architectural decisions

---

## Examples

### ✅ Good Examples

```
Implement path encoding and session discovery

Add functions to encode project paths and list top-level sessions,
sorted by timestamp for easy discovery of recent conversations.
```

```
Add trivial message filter for feedback extraction

Filter out single-character responses and common continuation
keywords (y/n/ok/continue) to focus on substantive user feedback.
```

```
Extract feedback recursively from sub-agent sessions

Scan agent files by session ID to find all related sub-agents,
including interrupted or failed tasks that don't have completion
markers.
```

### ❌ Bad Examples

```
Implement Step 1 with TDD using pytest

Generated with Claude Code assistance
```

*Problems: Mentions TDD, mentions Claude, doesn't explain what Step 1 does*

```
Add tests and implementation
```

*Problem: Too vague, doesn't explain what was added or why*

```
Complete Step 2: trivial filter

Implemented with strict TDD methodology following the red-green-refactor
cycle. Thanks to Claude Code for assistance.
```

*Problems: Mentions methodology, vendor credit, doesn't explain what the trivial filter
does*

---

## Git Workflow

### Staging Files

🚫 **Never use `git add -A` or `git add .`** - these can stage unintended files.

✅ **Always add files explicitly:**

```bash
git add src/specific_file.py tests/test_specific.py
```

### Common Commands

```bash
git status            # Check staged changes
git diff HEAD         # Review all changes (staged + unstaged)
git add <file>...     # Stage specific files explicitly
git commit -m "..."   # Commit with concise message
```

### Multi-line Commit Messages

✅ **Use heredoc syntax for clean formatting:**

```bash
git commit -m "$(cat <<'EOF'
Short summary line

Longer explanation of why this change was made and what
design decisions were involved.
EOF
)"
```

**Alternative:** Literal newlines in double quotes also work:

```bash
git commit -m "Short summary line

Longer explanation of why this change was made and what
design decisions were involved."
```

### Message Body Structure

Structure the body using paragraphs or lists for clarity:

**Use paragraphs for related points:**

```
Add feedback analysis pipeline

Implements three stages: collect extracts all feedback from sessions,
analyze filters noise and categorizes by type, and rules identifies
actionable items for system prompts.

Each stage can work standalone or piped together for end-to-end
processing.
```

**Use lists for multiple distinct items:**

```
Fix markdown formatter edge cases

- Protect inline code spans with 1-2 backticks
- Escape fence marker sequences (3+ backticks)
- Implement CommonMark-compliant backtick matching
- Skip unmatched backtick strings per atomicity rules
```

🚫 **Avoid:** One big compact paragraph that's hard to scan.

---

## Error Recovery

### Git Lock File Errors

If commit fails with a lock file error (`.git/index.lock` exists):

1. Wait 2 seconds and retry
2. If still failing, wait 2 more seconds and retry once more
3. Only ask the user after two failed retries

This handles transient lock issues from concurrent git operations.
