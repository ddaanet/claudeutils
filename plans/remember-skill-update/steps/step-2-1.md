# Step 2.1

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Phase Context

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

---

## Step 2.1: Update remember SKILL.md

**Objective**: Align skill documentation with new validation rules and inline execution model.

**Target:** `agent-core/skills/remember/SKILL.md`

**Implementation:**
- **Title guidance (FR-5):** Add section after "Learnings Quality Criteria" (line 76): titles must start with "When"/"How to", min 2 content words after prefix, anti-pattern/correct-pattern examples
- **Trigger derivation (FR-4):** Update Step 4a (line 59): trigger = operator prefix + learning title (mechanical, no rephrasing). Remove "Optimize for discovery" guidance (line 67) — title IS the trigger
- **Inline execution (FR-8):** Add prerequisite note: skill executes in calling session, requires clean session (fresh start). Remove any delegation references
- **Inline splitting (FR-9):** Add to Step 4: after Write/Edit to decision file, check line count; if >400, split by H2/H3 boundaries into 100-300 line sections; run `validate-memory-index.py --fix` after split
- **Fix "no hyphens" (KD-1):** Remove "no hyphens or special characters" from line 65 — contradicts practice (30+ triggers use hyphens)

**Validation:** Read updated file, verify all 5 changes applied, no conflicting instructions.

---
