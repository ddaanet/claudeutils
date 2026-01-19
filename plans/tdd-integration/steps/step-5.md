# Step 5

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 5: Update /oneshot skill for methodology detection

**Objective**: Add TDD methodology detection to `/oneshot` skill entry point

**Script Evaluation**: Prose description (semantic modifications)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read tool to read existing skill file
- Use Edit tool to modify skill file
- Use Grep tool for validation
- Never use bash sed/awk or heredocs

**Implementation**:

Modify `agent-core/skills/oneshot/skill.md` to add methodology detection logic that routes to TDD or general workflow.

**Modifications Required:**

1. **Add Methodology Detection Section** (after "When to Use" section)
   ```markdown
   ## Methodology Detection

   The oneshot skill detects appropriate workflow based on these signals:

   **TDD Methodology Signals:**
   - Project has test-first culture
   - User mentions "test", "TDD", "red/green"
   - Feature requires behavioral verification
   - Project is pytest-md or similar

   **General Methodology Signals:**
   - Infrastructure/migration work
   - Refactoring without behavior change
   - Prototype/exploration
   - Default if TDD signals absent

   **Workflow Routing:**
   - TDD path: `/design` (TDD mode) → `/plan-tdd` → `/orchestrate` → `/vet` → `/review-analysis`
   - General path: `/design` → `/plan-adhoc` → `/orchestrate` → `/vet`
   ```

2. **Update Workflow Description**
   Add after methodology detection:
   ```markdown
   ## Workflow Selection

   Based on methodology detection, oneshot routes to:

   **TDD Workflow** (feature development):
   - Design with spike test section
   - Plan as TDD cycles (RED/GREEN/REFACTOR)
   - Execute via tdd-task agent
   - Review process compliance

   **General Workflow** (oneshot work):
   - Design with implementation details
   - Plan as sequential steps
   - Execute via quiet-task agent
   - Review code quality
   ```

3. **Add Workflow Documentation References**
   ```markdown
   ## Workflow Documentation

   - TDD workflow: See `agent-core/agents/tdd-workflow.md`
   - General workflow: See `agent-core/agents/oneshot-workflow.md`
   ```

**Expected Outcome**:
- skill.md modified with methodology detection
- Workflow routing documented
- References to workflow docs added
- File size increase of ~300-500 bytes

**Unexpected Result Handling**:
- If skill structure differs from expected: Adapt section placement
- If methodology detection already exists: Merge updates

**Error Conditions**:
- File not found → STOP and report
- Write permission denied → STOP and report

**Validation**:
- Use Grep to verify "Methodology Detection" in `agent-core/skills/oneshot/skill.md`
- Use Grep to verify TDD signals documented
- Use Grep to verify workflow routing present
- File size increased by ~300-500 bytes

**Success Criteria**:
- skill.md contains methodology detection
- Workflow routing documented
- References to workflow docs added
- No syntax errors
- File size increase 300-500 bytes

**Report Path**: `plans/tdd-integration/reports/step-5-report.md`

---
