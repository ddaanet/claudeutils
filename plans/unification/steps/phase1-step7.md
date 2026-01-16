# Phase 1: Step 7

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 7: Add agent-core as Submodule to Test Repository

**Objective**: Test the submodule integration in a scratch repository.

**Test Repository Options**:
- scratch/emojipack (simpler codebase)
- scratch/pytest-md (more representative)

**Recommendation**: Start with emojipack for simpler validation.

**Technical Details**:
- Submodule location: project root (`emojipack/agent-core/`)
- Submodule URL: Local path works for testing (`/Users/david/code/agent-core`)

**Actions**:
1. Navigate to test repository (e.g., `scratch/emojipack`)
2. Add submodule: `git submodule add /Users/david/code/agent-core agent-core`
3. Create `agents/` directory if it doesn't exist
4. Copy composition script and compose.yaml from claudeutils
5. Update paths in compose.yaml to reference `agent-core/fragments/`
6. Run generation: `agents/compose.sh`
7. Review generated CLAUDE.md
8. Commit: "Add agent-core submodule and generate CLAUDE.md"

**Validation**:
- [ ] Submodule added successfully
- [ ] `.gitmodules` file created
- [ ] Generation script works with submodule paths
- [ ] Generated CLAUDE.md is usable

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
