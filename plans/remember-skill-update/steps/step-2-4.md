# Step 2.4

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Phase Context

Prose edits to skills, agents, and CLAUDE.md. All decisions pre-resolved.

**Note:** SKILL.md also edited in Phase 3 (agent routing). Phase 3 depends on Phase 2 completion.

**Platform prerequisite:** Load `/plugin-dev:skill-development` before editing skill files.

---

## Step 2.4: Update handoff skill Step 4 with trigger framing

**Objective**: Enforce trigger-compatible title format at creation time.

**Target:** `agent-core/skills/handoff/SKILL.md` (lines 101-107)

**Implementation:**
- Strengthen line 105: titles must start with "When" or "How to", min 2 content words after prefix
- Add: reject jargon/root-cause titles, suggest rephrasing to situation description
- Add examples: ❌ "transformation table" → ✅ "choosing review gate"; ❌ "prose gates" → ✅ "prevent skill steps from being skipped"

**Validation:** Read Step 4, verify format rules present and examples clear.

---
