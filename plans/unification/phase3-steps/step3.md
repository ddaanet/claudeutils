# Step 3

**Context**: Read `execution-context.md` for full context before executing this step.

---

### Step 3: Design CLI Entry Point

**Objective**: Design the CLI interface for composition commands (claudeutils compose).

**Script Evaluation**: Medium design task - prose description

**Execution Model**: Sonnet (interface design)

**Implementation**:
1. Read core module design from Step 2
2. Design CLI subcommand structure:
   - `claudeutils compose <config-file>` for CLAUDE.md generation
   - `claudeutils compose role` for role file generation (tuick pattern)
   - Future extensibility for other modes
3. Design command-line arguments:
   - Config file path (required)
   - Output path (optional, default from config)
   - Verbosity flags (optional)
   - Validation flags (optional)
4. Design pyproject.toml integration:
   - Entry point definition
   - Subcommand routing
5. Create usage pattern examples:
   - Simple CLAUDE.md generation
   - Role file generation with arguments
   - Integration with justfile/Makefile
6. Write to: `scratch/consolidation/design/cli-design.md`
7. Write execution log to: `plans/unification/reports/phase3-step3-execution.md`

**Expected Outcome**: CLI design document with:
- Complete subcommand structure
- Argument specifications
- Usage examples
- Integration patterns

**Unexpected Result Handling**:
- If role mode requires significantly different CLI pattern: Propose alternatives, escalate if unclear
- If argument combinations create complexity: Simplify or propose phased approach

**Error Conditions**:
- Core module design not found → Escalate (Step 2 may have failed)
- Cannot determine appropriate CLI pattern → Document options, escalate for decision
- pyproject.toml integration unclear → Research existing patterns, escalate if needed

**Validation**:
- Design document exists at expected path
- Subcommand structure defined
- Arguments specified with types
- At least 3 usage examples provided
- pyproject.toml integration documented

**Success Criteria**:
- CLI design created at `scratch/consolidation/design/cli-design.md`
- Document includes:
  - Subcommand structure (compose, compose role, future modes)
  - Argument specifications (required/optional, types, defaults)
  - Usage examples (at least 3 complete examples)
  - pyproject.toml entry point definition
- Design matches patterns in design.md
- Execution report documents CLI decisions

**Report Path**: `plans/unification/reports/phase3-step-3.md`
**Artifact Path**: `scratch/consolidation/design/cli-design.md`

---


---

**Execution Instructions**:
1. Read execution-context.md for prerequisites, critical files, and execution notes
2. Execute this step following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
