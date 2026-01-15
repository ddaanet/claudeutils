# Phase 1: Step 2

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 2: Extract justfile-base.just

**Objective**: Identify and extract shared justfile recipes used across projects.

**Source Analysis Required**:
- claudeutils/justfile
- scratch/emojipack/justfile (if exists)
- scratch/pytest-md/justfile (if exists)
- home repository justfile (mentioned in design)

**Shared Recipes to Extract** (common patterns):
- Development environment setup (venv, install)
- Testing commands (test, test-watch)
- Code quality (format, lint, type-check)
- Agent-related helpers (read-agents, sync-check)
- Build/packaging commands

**Technical Decisions**:
- Start with single file approach (justfile-base.just)
- Can split by concern in later phases if needed
- Include bash helper functions that are generally useful
- Preserve comments documenting recipe purpose

**Actions**:
1. Read all justfile sources to identify common recipes
2. Extract shared recipes to `agent-core/fragments/justfile-base.just`
3. Document recipe purpose and parameters in comments
4. Ensure recipes use variables for project-specific paths (e.g., `SRC_DIR`, `TEST_DIR`)
5. Test that extracted recipes are syntactically valid

**Validation**:
- [ ] Recipes compile with `just --check`
- [ ] All extracted recipes have documentation comments
- [ ] Project-specific hardcoded paths replaced with variables

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
