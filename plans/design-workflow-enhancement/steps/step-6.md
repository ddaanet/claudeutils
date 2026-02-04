# Step 6

**Plan**: `plans/design-workflow-enhancement/runbook.md`
**Execution Model**: sonnet
**Report Path**: `plans/design-workflow-enhancement/reports/step-6-requirements-validation.md`

---

## Step 6: Extend Plan Skills and Vet Agents for Requirements Validation

**Objective**: Add requirements passthrough to plan skills and conditional requirements validation to vet agents

**Execution Model**: Sonnet (interprets design guidance into skill/agent edits)

**Implementation**:

**6.1 - Update plan-adhoc skill** (`agent-core/skills/plan-adhoc/SKILL.md`):
- Extend Point 0.5 item 0 to read requirements from design
- Add requirements to Common Context template
- Update vet checkpoint prompt to include requirements validation

**6.2 - Update plan-tdd skill** (`agent-core/skills/plan-tdd/SKILL.md`):
- Same changes as plan-adhoc (Phase 1 intake, Common Context, checkpoints)

**6.3 - Update vet-agent** (`agent-core/agents/vet-agent.md`):
- Add conditional requirements validation section (triggers when context provided)
- Add "Requirements Validation" section to review report template

**6.4 - Update vet-fix-agent** (`agent-core/agents/vet-fix-agent.md`):
- Same changes as vet-agent

**Expected Outcome**: Plan skills passthrough requirements, vet agents conditionally validate against requirements

**Validation**:
- All 4 files modified
- Requirements reading in both plan skills
- Conditional requirements validation in both vet agents
- Backward compatible (no requirements context = no validation)
- YAML frontmatter valid

**Report Path**: `plans/design-workflow-enhancement/reports/step-6-requirements-validation.md`

---
