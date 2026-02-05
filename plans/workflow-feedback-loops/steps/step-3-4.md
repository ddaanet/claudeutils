# Step 3.4

**Plan**: `plans/workflow-feedback-loops/runbook.md`
**Execution Model**: sonnet
**Phase**: 3

---

## Step 3.4: Update /orchestrate skill

**Objective:** Enhance phase boundary checkpoints with requirements context

**Execution Model:** Sonnet

**Implementation:**

Edit `agent-core/skills/orchestrate/SKILL.md`:

1. Add requirements context to vet-fix-agent prompts:
   - Include requirements summary in checkpoint prompt
   - Format: List of FR-* items relevant to completed phase

2. Add explicit instruction for changed files:
   - Run: `git diff --name-only <last-checkpoint-commit>..HEAD`
   - Pass changed file list to vet-fix-agent (not git diff text)
   - Agent reviews each file using Read tool

3. Add runbook exclusion instruction:
   - Explicitly state: "Do NOT read runbook.md"
   - Scope: Implementation changes only

4. Add phase boundary detection guidance:
   - Parse step file frontmatter for `Phase: N`
   - When phase number changes → phase boundary checkpoint

**Reference:** Design Section "FP-5: Phase Boundary Review (ENHANCED)" and "/orchestrate Skill" lines 485-489

**Expected Outcome:** Checkpoints include requirements context, use file list not diff text

**Success Criteria:**
- Requirements context in vet-fix-agent prompt
- Changed files list pattern documented
- Runbook exclusion explicit
- Phase boundary detection documented
