# Phase 1 Execution - Step 3

**Plan**: `plans/oneshot-workflow/phase1-execution-plan.md`
**Common Context**: See plan file for script specification, baseline rename info, and file structure

---

## Step 1.3: Implement prepare-runbook.py Script

**Objective**: Create prepare-runbook.py script with full functionality per specification

**Script Evaluation**: Large/complex (>100 lines, multiple functions, validation logic) - PROSE DESCRIPTION

**Execution Model**: Sonnet

**Implementation**:

Create `/Users/david/code/agent-core/bin/prepare-runbook.py` with the following structure:

### Main Components

**1. Argument Parsing**
- Accept single argument: runbook file path
- Validate file exists and is readable
- Derive output paths from runbook location and name

**2. Frontmatter Parsing**
- Use stdlib approach (no pyyaml dependency)
- Extract name and model from YAML frontmatter
- Default: name from filename, model = sonnet

**3. Section Extraction**
- Parse runbook content into sections:
  - Common Context (optional)
  - Steps (required, format: "## Step N:" or "## Step N.M:")
  - Orchestrator Instructions (optional)
- Validate step numbering (no duplicates)
- Preserve section content verbatim

**Section boundary detection**:
- Common Context: `## Common Context` (H2) to next H2 heading or Steps
- Steps: Each `## Step N:` or `## Step N.M:` (H2 heading with "Step" prefix)
- Orchestrator: `## Orchestrator Instructions` (H2) to end of file

**Content extraction**:
- Include the heading line in extracted content
- Preserve all content until next H2 heading
- Preserve blank lines and formatting within sections
- Strip leading/trailing blank lines from section content

**4. Plan-Specific Agent Generation**
- Read baseline from `agent-core/agents/quiet-task.md`
- Extract baseline content (skip frontmatter)
- Create new frontmatter with plan-specific values
- Append separator
- Append common context (if exists)
- Write to `.claude/agents/<runbook-name>-task.md`

**Frontmatter strategy**: Replace baseline frontmatter entirely
- name: `<runbook-name>-task`
- description: "Execute <runbook-name> steps from the plan with plan-specific context."
- model: From runbook frontmatter or "haiku" default
- color: "cyan"
- tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]

**Reference implementation**: See `/Users/david/code/claudeutils/plans/unification/build-plan-agent.sh` (lines 73-100) for existing agent composition approach. The prepare-runbook.py script extends this pattern with step extraction and validation.

**5. Step File Generation**
- Extract each step section
- Create individual files: `plans/<runbook-name>/steps/step-N.md` or `step-N-M.md`
- Include reference to plan and common context
- Format:
  ```markdown
  # Step N: [Title]

  **Plan**: [path to runbook]
  **Common Context**: [path to common context file or inline]

  [Step content from runbook]
  ```

**6. Orchestrator Plan Generation**
- Use Orchestrator Instructions section if present
- Otherwise generate default:
  ```markdown
  # Orchestrator Plan: [runbook-name]

  Execute steps sequentially using [runbook-name]-task agent.
  Stop on error and escalate to sonnet.
  ```
- Write to `plans/<runbook-name>/orchestrator-plan.md`

**7. Validation**
- Baseline agent exists (MUST fail if missing)
- At least one step section exists (MUST fail if missing)
- No duplicate step numbers (MUST fail if duplicates)
- Output directories writable (MUST fail if not writable)
- Warn if artifacts exist (overwriting is normal)
- Warn if optional sections missing

**8. Output**
- Print list of created/updated files
- Print summary (N steps, agent name, model)
- On error: Clear error message with context

**9. Make Executable**
- Add shebang line at top of file: `#!/usr/bin/env python3`
- Set executable permission: `chmod +x prepare-runbook.py`

### Path Derivation Logic

From input `plans/foo/runbook.md`:
- Runbook name: `foo` (from parent directory)
- Agent: `.claude/agents/foo-task.md`
- Steps: `plans/foo/steps/step-*.md`
- Orchestrator: `plans/foo/orchestrator-plan.md`

### Error Handling

- File not found → Exit with clear message
- Parse error → Exit with line number and context
- Write error → Exit with path and permission info
- Validation error → Exit with specific validation failure

**Expected Outcome**: Script created with all functionality, executable, well-structured

**Unexpected Result Handling**:
- If implementation reveals design issues: Document in report, escalate to user
- If stdlib frontmatter parsing insufficient: Document limitation, proceed with simple parsing

**Error Conditions**:
- Script syntax errors → Report error with details
- Missing imports → Report error, verify stdlib-only requirement
- Logic errors discovered during implementation → Document and escalate

**Validation**:
- Script is executable (`chmod +x`)
- No syntax errors (`python3 -m py_compile`)
- Uses only stdlib imports
- Follows specification sections

**Success Criteria**:
- Script exists at `agent-core/bin/prepare-runbook.py`
- Script is executable (has executable permission and shebang)
- No syntax errors
- All required functions implemented (9 components)
- Validation logic present
- Help message available

**Report Path**: `plans/oneshot-workflow/reports/phase1-step3-execution.md`

---

---

## Execution Instructions

1. Read `phase1-execution-plan.md` for:
   - Prerequisites and validation requirements
   - Error escalation triggers
   - Success criteria

2. Execute this step following the implementation section above

3. Perform all validation checks as specified

4. Write execution log to report path specified above with:
   - What was done
   - Results and artifacts created
   - Any errors or unexpected outcomes
   - Verification of success criteria

5. Return format:
   - Success: "done: <brief summary>"
   - Failure: "error: <description with diagnostic info>"

6. **Stop immediately** on any unexpected results per communication rules
