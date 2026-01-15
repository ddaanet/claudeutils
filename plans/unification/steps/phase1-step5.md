# Phase 1: Step 5

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 5: Create AGENTS-framework.md Fragment

**Objective**: Extract the structural/framework parts of AGENTS.md that are consistent across projects.

**Content to Include**:
- Header explaining purpose of AGENTS.md
- Roles table (design.md:93-101)
- Rules table (design.md:105-107)
- Skills table (design.md:112-114)
- Loading mechanism explanation

**Technical Note**: This provides the "scaffold" that fragments will be composed into.

**Content Boundary:**

Include in AGENTS-framework.md:
- File header explaining AGENTS.md purpose (current AGENTS.md:1-7)
- Section structure (## Communication Rules, ## Delegation Principle, etc. headers only)
- Roles/Rules/Skills tables (AGENTS.md:91-114)
- Loading mechanism (AGENTS.md:116-120)

Exclude from AGENTS-framework.md:
- Specific communication rules (goes in communication.md)
- Delegation content (goes in delegation.md)
- Tool preferences content (goes in tool-preferences.md)
- Hashtag definitions (goes in hashtags.md)

Result: Framework provides structure and tables; fragments provide rule content.

**Actions**:
1. Create `agent-core/fragments/AGENTS-framework.md`
2. Extract structural content from existing AGENTS.md (headers, tables)
3. Structure as complete markdown document (no composition markers needed)
4. Will be concatenated with other fragments in Step 6

**Validation**:
- [ ] Framework is project-agnostic
- [ ] Framework contains structure/tables but not rule content
- [ ] Tables match current AGENTS.md format

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
