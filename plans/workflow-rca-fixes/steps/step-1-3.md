# Step 1.3

**Plan**: `plans/workflow-rca-fixes/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Step 1.3: Update agent frontmatters (batch)

**Objective**: Inject skills frontmatter into 5 agent definitions.

**Prerequisites**:
- Steps 1.1-1.2 committed (skills exist on disk)
- Read all 5 target agent files to verify current state
- plugin-dev:agent-development loaded

**Implementation**:

Update frontmatter for 5 agents in single edit session:

1. `agent-core/agents/vet-fix-agent.md`:
   - Add `skills: [project-conventions, error-handling, memory-index]`

2. `agent-core/agents/design-vet-agent.md`:
   - Verify `skills: [project-conventions]` present (early bootstrap)
   - Add if missing

3. `agent-core/agents/outline-review-agent.md`:
   - Add `skills: [project-conventions]`

4. `agent-core/agents/plan-reviewer.md`:
   - Add `skills: [project-conventions]`
   - Note: already has review-plan skill reference

5. `agent-core/agents/refactor.md`:
   - Add `skills: [project-conventions, error-handling]`

**Expected Outcome**: All 5 agent definitions have `skills:` frontmatter referencing appropriate skills. Single commit with all changes.

**Error Conditions**:
- If skills field malformed → verify YAML array syntax
- If skills don't exist → check Steps 1.1-1.2 completed
- If agent files not found → verify paths with Glob

**Validation**:
1. Commit all frontmatter changes together
2. Delegate to agent-creator (plugin-dev): "Review and validate batch frontmatter updates for 5 agents at agent-core/agents/. Check skills references are valid and appropriate for each agent."
3. Read review report
4. If UNFIXABLE: STOP, escalate
5. If all fixed: proceed

**Report location**: plans/workflow-rca-fixes/reports/step-1.3-agent-batch-review.md

---

**Phase 1 Checkpoint**:
1. Run `just sync-to-parent` with dangerouslyDisableSandbox: true (creates symlinks in .claude/skills/)
2. Verify symlinks created: `ls -la .claude/skills/` should show error-handling and memory-index
3. Commit checkpoint if needed
4. Restart session (agent frontmatter changes require discovery)
5. Proceed to Phase 2

---


**Complexity:** High (3 steps, ~200 lines)
**Model:** Sonnet
**Restart required:** No (runbook-review.md accessed via /when recall, skills loaded on demand — none require restart)
**Diagnostic review:** Yes (improving review logic)
**FRs addressed:** FR-1, FR-2, FR-3

---
