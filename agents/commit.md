---
name: commit
description: Git commit standards
---

# Commit Skill

> **Context:** Load `@AGENTS.md` for project overview and user preferences.

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
*Problems: Mentions methodology, vendor credit, doesn't explain what the trivial filter does*

---

## Git Workflow

### Common Commands

```bash
git status            # Check staged changes
git diff              # Review changes
git commit -m "..."   # Commit with concise message
```

### Multi-line Commit Messages

For longer messages, use a heredoc:

```bash
git commit -m "$(cat <<'EOF'
Short summary line

Longer explanation of why this change was made and what
design decisions were involved.
EOF
)"
```
