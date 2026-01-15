# Phase 1: Step 9

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 9: Test pyproject.toml Section Usage

**Objective**: Verify that extracted config fragments work when included in project pyproject.toml.

**Approach**: Manual copy for Phase 1 (automated composition is future work).

**Actions**:
1. Read `agent-core/fragments/ruff.toml`
2. In test repo `pyproject.toml`, update `[tool.ruff]` section
3. Add comment: `# Base configuration from agent-core/fragments/ruff.toml`
4. Test: `ruff check .` to verify config loads
5. Repeat for mypy configuration
6. Test: `mypy .` to verify config loads

**Validation**:
- [ ] Ruff configuration loads without errors
- [ ] Mypy configuration loads without errors
- [ ] Local extensions work (e.g., adding project-specific ignore rules)

**Note**: Full composition automation deferred to Phase 3 or prompt-composer integration.

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
