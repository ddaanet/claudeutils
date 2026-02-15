# Step 2.2

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: opus
**Phase**: 2

---

## Step 2.2: Expand review-plan Section 11 with general detection

**Objective**: Add `**General:**` detection bullets to Sections 11.1-11.3 (vacuity, ordering, density).

**Prerequisites**:
- Read `agent-core/skills/review-plan/SKILL.md` (current Section 11)
- Step 2.1 committed (runbook-review.md has General detection criteria as reference)

**Implementation**:

Expand Section 11 (LLM Failure Mode Detection):

1. **Section 11.1 (Vacuity Detection)**:
   - Preserve existing TDD content
   - Add `**General:**` subsection with:
     - Scaffolding-only steps (file creation without behavioral change)
     - Steps producing outcomes achievable by extending prior step
     - Heuristic: steps > LOC/20

2. **Section 11.2 (Ordering Defects)**:
   - Preserve existing TDD content
   - Add `**General:**` subsection with:
     - Steps referencing structures from later steps
     - Prerequisites not validated before use
     - Foundation-after-behavior inversions

3. **Section 11.3 (Density Issues)**:
   - Preserve existing TDD content
   - Add `**General:**` subsection with:
     - Adjacent steps on same artifact with <20 LOC delta
     - Multi-step sequences collapsible to single step
     - Over-granular decomposition without clear boundary

4. **Add restart-reason verification** (metadata validation):
   - For each phase claiming "Restart required: Yes", verify the stated reason matches restart trigger rules
   - Restart triggers: agent definitions (.claude/agents/), hooks, plugins, MCP only
   - NOT restart triggers: decision documents, skills, fragments loaded on-demand via /when recall
   - Distinction: @-referenced files have content loaded at startup; indexed-but-recalled files do not
   - Detection: grep phase headers for "Restart required: Yes", cross-reference artifact type against trigger rules

**Expected Outcome**: Section 11 expanded with General detection criteria mirroring runbook-review.md's new axes. Restart-reason verification added to metadata validation.

**Error Conditions**:
- If General criteria duplicate TDD → differentiate by artifact type (tests vs implementations)
- If criteria too abstract → add concrete detection heuristics
- If section numbering breaks → preserve 11.1, 11.2, 11.3 structure

**Validation**:
1. Commit changes
2. Delegate to skill-reviewer: "Review review-plan Section 11 expansion. Verify General subsections added to 11.1-11.3, criteria are concrete and distinct from TDD, and structure preserved."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-2.2-skill-review.md

---
