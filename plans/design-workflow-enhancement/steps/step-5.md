# Step 5

**Plan**: `plans/design-workflow-enhancement/runbook.md`
**Execution Model**: sonnet
**Report Path**: `plans/design-workflow-enhancement/reports/step-5-requirements-design.md`

---

## Step 5: Extend Design Skill and Design-Vet-Agent for Requirements

**Objective**: Add requirements checkpoint (A.0) to design skill and requirements alignment checks to design-vet-agent

**Execution Model**: Sonnet (interprets design guidance into skill/agent edits)

**Implementation**:

**5.1 - Update design skill** (`agent-core/skills/design/SKILL.md`):
- Add Phase A.0 (Requirements Checkpoint) before A.1
- Update Phase C.1 to include requirements section guidance with traceability format

**5.2 - Update design-vet-agent** (`agent-core/agents/design-vet-agent.md`):
- Add requirements alignment checks to "Analyze Design" section
- Add section 4.5 "Validate Requirements Alignment"
- Update review report template with "Requirements Alignment" section

**Expected Outcome**: Design skill has A.0 requirements checkpoint, design-vet-agent validates requirements alignment

**Validation**:
- Both files modified
- Phase A.0 appears before A.1
- design-vet-agent has section 4.5
- YAML frontmatter valid

**Report Path**: `plans/design-workflow-enhancement/reports/step-5-requirements-design.md`

---
