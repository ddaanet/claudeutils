# Step 4

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 4: Update /design skill for TDD mode

**Objective**: Modify `/design` skill to support both general and TDD modes

**Script Evaluation**: Prose description (semantic modifications to skill)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Read tool to read existing skill file
- Use Edit tool to modify skill file
- Use Grep tool for validation
- Never use bash sed/awk or heredocs

**Implementation**:

Modify `agent-core/skills/design/skill.md` to add TDD mode support while preserving existing general mode functionality.

**Modifications Required:**

1. **Add Mode Selection Section** (near top of skill)
   ```markdown
   ## Design Mode Selection

   The design skill supports two modes based on methodology detection:

   **TDD Mode** - Triggered when:
   - Project has test-first culture
   - User mentions "test", "TDD", "red/green"
   - Feature requires behavioral verification
   - Project is pytest-md or similar

   **General Mode** - Triggered when:
   - Infrastructure/migration work
   - Refactoring without behavior change
   - Prototype/exploration work
   - Default if TDD signals absent
   ```

2. **Document Shared Sections** (both modes)
   - Problem statement
   - Requirements (functional, non-functional, out of scope)
   - Key design decisions with rationale
   - High-level phases

3. **Document TDD Mode Additions**
   ```markdown
   ### TDD Mode Specific Sections

   **Spike Test Section**:
   - Verify current behavior
   - Document framework defaults
   - Identify what might already work

   **Confirmation Markers**:
   - Use `(REQUIRES CONFIRMATION)` for decisions needing user input

   **Flag Reference Table** (if adding CLI options):
   - Document new flags and their behavior

   **"What Might Already Work" Analysis**:
   - Identify existing functionality to leverage
   ```

4. **Document General Mode Additions**
   ```markdown
   ### General Mode Specific Sections

   - Integration points
   - Edge cases
   - Risks and mitigations
   - Detailed implementation notes
   ```

5. **Update Output Section**
   ```markdown
   ## Output

   **TDD Mode**: Design document consumed by `/plan-tdd`
   **General Mode**: Design document consumed by `/plan-adhoc`
   ```

**Integration Points:**
- Preserve existing skill structure
- Add new sections without breaking existing usage
- Maintain backward compatibility with general mode
- Reference tdd-workflow.md and oneshot-workflow.md for details

**Expected Outcome**:
- skill.md modified with TDD mode support
- Mode selection documented
- TDD-specific sections added
- General mode sections preserved
- File size increase of ~500-1000 bytes

**Unexpected Result Handling**:
- If skill.md structure differs from expected: Review and adapt modifications
- If existing mode selection already present: Merge rather than duplicate

**Error Conditions**:
- File not found → STOP and report
- Parse error in existing content → STOP and report
- Write permission denied → STOP and report

**Validation**:
- Use Grep to verify "TDD Mode" present in `agent-core/skills/design/skill.md`
- Use Grep to verify mode selection section added
- Use Read to confirm original content preserved
- File size increased by ~800-1500 bytes

**Success Criteria**:
- skill.md contains mode selection logic
- TDD mode additions documented
- General mode preserved
- No syntax errors introduced
- File size increase 500-1000 bytes

**Report Path**: `plans/tdd-integration/reports/step-4-report.md`

---
