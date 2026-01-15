# Phase 1: Step 3

**Context**: Read `phase1-execution-context.md` for full context before executing this step.

---

### Step 3: Extract Python Tool Configurations

**Objective**: Extract shared ruff and mypy configurations.

**Source Files**:
- claudeutils/pyproject.toml
- Other scratch repo pyproject.toml files

**Configuration Sections**:
- `[tool.ruff]` and subsections (lint, format, lint.per-file-ignores)
- `[tool.mypy]`

**Technical Decisions**:
- Extract as standalone TOML files, not fragments with markers
- Include only truly shared settings
- Document extension points for local customization
- Note Python version handling as potential variable (design.md:342-346)

**Algorithm for "Common" Settings:**

1. Parse [tool.ruff] from all available pyproject.toml files
2. For each setting key:
   - If present in ALL files with IDENTICAL value → Include in shared fragment
   - If present in some files or values differ → Exclude, document in comment
3. For list settings (e.g., select, ignore):
   - Include only items present in ALL projects
   - Document: "# Local projects may add: E501, F401, etc."
4. Create ruff.toml with intersection of settings
5. Add header comment: "# Shared ruff configuration - extend locally as needed"

Repeat same algorithm for mypy.toml.

**Actions**:
1. Read pyproject.toml from multiple projects
2. Identify common ruff settings using algorithm above:
   - Target version
   - Line length
   - Common lint rules (enabled/disabled)
   - Format settings
3. Create `agent-core/fragments/ruff.toml` with shared settings
4. Identify common mypy settings using algorithm above:
   - Python version
   - Strictness flags
   - Plugin configuration
5. Create `agent-core/fragments/mypy.toml`
6. Document in comments: "Local projects can extend with project-specific rules"

**Open Decision Points**:
- **Python version**: Should fragments specify minimum version or use template variable?
  - Recommendation: Use `py312` as baseline, document override mechanism
- **Per-file ignores**: These are project-specific, exclude from shared fragment

**Validation**:
- [ ] TOML files parse correctly
- [ ] Settings represent intersection of current projects
- [ ] Extension mechanism documented

---


---

**Execution Instructions**:
1. Read phase1-execution-context.md for prerequisites and validation patterns
2. Execute this step following the actions listed above
3. Perform validation checks
4. Document results in execution report
5. Stop on any unexpected results per communication rules
