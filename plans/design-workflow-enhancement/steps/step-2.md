# Step 2

**Plan**: `/Users/david/code/claudeutils/plans/design-workflow-enhancement/runbook.md`
**Common Context**: See plan file for context

---

## Step 2: Review quiet-explore Agent

**Objective**: Review and fix agent file using vet-agent

**Execution Model**: Sonnet (vet-agent review)

**Implementation**:

Delegate review to vet-agent:
```
Review agent-core/agents/quiet-explore.md for:
- YAML syntax correctness (frontmatter fields, multi-line description format)
- Description quality and clarity
- System prompt structure and completeness (all 7 directives from design)
- Tool list appropriateness
- Consistency with quiet-task baseline pattern

Write review report to plans/design-workflow-enhancement/reports/step-2-agent-review.md.
Return filepath only on success.
```

After receiving review, read report and apply all critical/major priority fixes to agent file.

**Expected Outcome**: Agent file reviewed and improved, report written

**Unexpected Result Handling**:
- If review identifies contradictory requirements in spec: Report to user with specific conflicts
- If git diff shows no changes after review but report lists issues: Verify report explains why no changes needed

**Error Conditions**:
- Agent file missing → Error: "Agent file not found, Step 1 may have failed"
- Review report not created → Escalate with error message from vet-agent

**Validation**:
- Review report exists at expected path
- Agent file still valid YAML after fixes
- All critical/major issues from report addressed
- Compare before/after using git diff (verify improvements made or report explains no-change rationale)

**Success Criteria**:
- Review complete with report written
- All critical/major issues fixed
- Agent file passes YAML parse
- Improvements documented in git diff or review report

**Report Path**: `plans/design-workflow-enhancement/reports/step-2-agent-review.md` (created by vet-agent)

---
