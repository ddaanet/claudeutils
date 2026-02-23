# Step 2.3

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Phase Context

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

---

## Step 2.3: Update consolidation-patterns.md derivation protocol

**Objective**: Make trigger derivation mechanical — title IS the trigger.

**Target:** `agent-core/skills/remember/references/consolidation-patterns.md`

**Implementation:**
- Update Memory Index Maintenance section (line 64): trigger derived mechanically from title — `## When X Y` → `/when x y` (lowercase, no rephrasing)
- Remove "Trigger naming" optimization guidance that implies agent judgment

**Validation:** Read updated section, verify no language suggesting rephrasing or "optimize for discovery".

---
