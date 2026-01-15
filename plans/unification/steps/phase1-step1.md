# Phase 1: Step 1

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 1: Create agent-core Repository Structure

**Objective**: Initialize the shared repository with proper directory structure.

**Technical Details**:
- Initialize as git repository locally first (GitHub remote can be added later)
- Location: `/Users/david/code/agent-core` (sibling to claudeutils)
- Structure based on design.md:64-68

**Actions**:
1. Create repository directory: `/Users/david/code/agent-core`
2. Initialize git: `git init`
3. Create directory structure:
   ```
   agent-core/
     fragments/
       justfile-base.just
       ruff.toml
       mypy.toml
       communication.md
       delegation.md
       tool-preferences.md
       hashtags.md
       AGENTS-framework.md
     agents/
       (reserved for Phase 2)
     composer/
       (reserved for future)
     README.md
   ```
4. Create initial README.md documenting purpose and structure
5. Initial commit: "Initialize agent-core repository structure"

**Validation**:
- [ ] Directory structure matches design
- [ ] Git repository initialized
- [ ] README.md explains purpose

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
