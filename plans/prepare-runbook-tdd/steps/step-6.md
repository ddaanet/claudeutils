# Step 6

**Plan**: `plans/prepare-runbook-tdd/runbook.md`
**Common Context**: See plan file for context

---

## Step 6: Implement Cycle File Generation

**Objective**: Create `generate_cycle_file()` function to generate cycle files with pattern `cycle-X-Y.md`.

**Script Evaluation**: Prose description (30-40 line modification)

**Execution Model**: Sonnet

**Implementation**:

1. Create `generate_cycle_file()` function modeled on `generate_step_file()`:
   - Parameters: cycle_data, runbook_name, steps_dir
   - File naming: `cycle-{major}-{minor}.md` (e.g., `cycle-1-1.md`)
   - Location: Same `plans/<runbook-name>/steps/` directory
2. Implement cycle file template:
   ```markdown
   # Cycle {major}.{minor}

   **Plan**: `plans/{runbook_name}/runbook.md`
   **Common Context**: See plan file for context

   ---

   ## Cycle {major}.{minor}: {name}

   {cycle_content}
   ```
3. Extract cycle content from parsed cycle data:
   - Include full cycle section
   - Preserve all subsections (RED/GREEN/REFACTOR/Stop Conditions)
   - Maintain markdown formatting
4. Modify main generation logic to route based on runbook type:
   - If TDD → use `generate_cycle_file()`
   - If general → use `generate_step_file()`
5. Update output messages:
   - "✓ Created cycle: plans/{runbook}/steps/cycle-{X}-{Y}.md"

**Expected Outcome**: Cycle files generated for TDD runbooks instead of step files.

**Unexpected Result Handling**:
- If cycle content malformed → Report and STOP

**Error Conditions**:
- File write failure → Report error and exit
- Invalid cycle data → Report and exit

**Validation**:
- Cycle files created in correct location
- File naming matches pattern `cycle-X-Y.md`
- File content includes cycle header and full content
- Output messages accurate

**Success Criteria**:
- `generate_cycle_file()` function implemented
- Function creates correctly formatted cycle files
- Main logic routes to appropriate generator
- Output messages updated
- Changes tested (documented in report)

**Report Path**: `plans/prepare-runbook-tdd/reports/step-6-report.md`

---
