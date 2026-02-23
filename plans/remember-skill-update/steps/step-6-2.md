# Step 6.2

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 6

---

## Phase Context

Mechanical rename — grep-and-replace across codebase. Sonnet sufficient (no architectural judgment, purely mechanical substitution despite touching skill files). Advisory: artifact-type override rule recommends opus for skill file edits, but this phase is pure text substitution with no semantic content changes — sonnet assignment is appropriate exception.

---

## Step 6.2: Sync symlinks and verify completeness

**Objective**: Ensure skill discovery works after rename.

**Implementation:**
- Run `just sync-to-parent`
- Verify symlinks: `.claude/skills/codify` exists, `.claude/skills/remember` removed
- Grep verification: `grep -r "/remember" agent-core/ agents/ .claude/ --include="*.md"` — only historical references remain
- Note: requires session restart (skill directory change)

**Validation:** Symlinks correct, grep clean.

**Phase 6 Checkpoint:** `just precommit` passes. Grep clean.

---
