# Step 2.5

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Phase Context

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

---

## Step 2.5: Remove deprecated artifacts (FR-8, FR-9, FR-13)

**Objective**: Delete superseded agents and demote memory-index from always-loaded context.

**Implementation:**
- Delete `agent-core/agents/remember-task.md` (FR-8)
- Delete `agent-core/agents/memory-refactor.md` (FR-9)
- Remove `@agents/memory-index.md` reference from `CLAUDE.md` line 49 (~5000 tokens, 2.9% recall — FR-13)
- File `agents/memory-index.md` remains (used by when-resolve.py)
- Verify no other files reference deleted agents: `grep -r "remember-task\|memory-refactor" agent-core/ agents/ .claude/ --include="*.md"`

**Validation:** Grep returns no references (excluding plan files and git history).

**Phase 2 Checkpoint:** `just precommit` passes. Grep verification clean.

---
