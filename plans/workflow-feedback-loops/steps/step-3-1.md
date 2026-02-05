# Step 3.1

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Step 3.1: Update /design skill

**Objective:** Add outline file output and FP-1 checkpoint

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/skills/design/SKILL.md`:

1. Modify Phase A.5 (BEHAVIORAL CHANGE):
   - Current: Outline presented inline in conversation
   - New: Write outline to `plans/<job>/outline.md`
   - Add instruction to create plans/<job>/ directory if needed

2. Add FP-1 checkpoint after A.5:
   - Delegate to `outline-review-agent`
   - Agent applies all fixes to outline
   - Agent writes review to `plans/<job>/reports/outline-review.md`

3. Modify Phase B:
   - After FP-1 review: `open plans/<job>/outline.md` (presents to user in editor)
   - User reads outline in editor, provides feedback in chat
   - Designer applies deltas to outline file
   - Re-review via outline-review-agent if significant changes

**Reference:** Design Section "Skill Changes - /design Skill" lines 405-419

**Expected Outcome:** Outline written to file, reviewed before user sees it

**Success Criteria:**
- Phase A.5 writes to file, not inline
- FP-1 checkpoint delegated to outline-review-agent
- Phase B uses `open` command to present outline

---
