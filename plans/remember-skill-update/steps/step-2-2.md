# Step 2.2

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Phase Context

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

---

## Step 2.2: Update consolidation-flow.md

**Objective**: Remove delegation flow, replace with inline invocation.

**Target:** `agent-core/skills/handoff/references/consolidation-flow.md`

**Implementation:**
- Replace delegation flow (lines 7-10: filter → batch check → delegate to remember-task → read report) with inline flow: invoke `/remember` skill in clean session
- Replace refactor flow (lines 16-19: delegate to memory-refactor) with inline instructions matching FR-9 (check line count, split by H2/H3, run validate-memory-index.py)
- Preserve error handling section (lines 24-27)

**Validation:** Read updated file, verify no references to remember-task or memory-refactor agents remain.

---
