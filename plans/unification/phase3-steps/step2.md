# Step 2

**Context**: Read `execution-context.md` for full context before executing this step.

---

### Step 2: Design Core Composition Module

**Objective**: Design the composition engine module (src/claudeutils/compose.py) based on extracted features.

**Script Evaluation**: Large design task - prose description

**Execution Model**: Sonnet (architectural design)

**Implementation**:
1. Read feature extraction from Step 1
2. Design module structure:
   - Define main composition function signature
   - Define helper functions (header manipulation, decorator injection, etc.)
   - Define data structures for configuration
   - Define error handling approach
3. Design composition algorithm:
   - Fragment loading (from file paths)
   - Fragment concatenation (order preservation)
   - Header level adjustment (increase_header_levels)
   - Decorator injection (title, separators)
   - Output generation
4. Design text manipulation utilities:
   - Header level detection and manipulation
   - Markdown structure preservation
   - Whitespace handling
5. Create design document section:
   - Module overview (purpose, scope)
   - API surface (public functions and signatures)
   - Algorithm description (step-by-step composition process)
   - Examples (code usage examples)
6. Write to: `scratch/consolidation/design/core-module-design.md`
7. Write execution log to: `plans/unification/reports/phase3-step2-execution.md`

**Expected Outcome**: Core module design document with:
- Clear module structure (functions, classes if needed)
- Detailed composition algorithm
- API signatures with type hints
- Usage examples

**Unexpected Result Handling**:
- If feature extraction reveals conflicting requirements: Propose resolution, escalate if unclear
- If complexity exceeds single-module scope: Propose multi-module structure, escalate for approval

**Error Conditions**:
- Feature extraction not found → Escalate (Step 1 may have failed)
- Design decisions unclear → Document alternatives, escalate for architectural choice
- Cannot reconcile tuick vs emojipack approaches → Document trade-offs, escalate for decision

**Validation**:
- Design document exists at expected path
- Module structure clearly defined
- API signatures specified
- Composition algorithm documented
- At least 2 usage examples provided

**Success Criteria**:
- Core module design created at `scratch/consolidation/design/core-module-design.md`
- Document includes:
  - Module structure (functions, parameters, return types)
  - Composition algorithm (detailed steps)
  - Text manipulation utilities (header levels, decorators)
  - API examples (at least 2)
- Design is implementable (sufficient detail for coding)
- Execution report documents design decisions

**Report Path**: `plans/unification/reports/phase3-step-2.md`
**Artifact Path**: `scratch/consolidation/design/core-module-design.md`

---


---

**Execution Instructions**:
1. Read execution-context.md for prerequisites, critical files, and execution notes
2. Execute this step following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
