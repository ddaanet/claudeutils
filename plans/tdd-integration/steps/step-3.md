# Step 3

**Plan**: `plans/tdd-integration/runbook.md`
**Common Context**: See plan file for context

---

## Step 3: Create TDD task agent baseline

**Objective**: Write `agent-core/agents/tdd-task.md` baseline template for TDD cycle execution

**Script Evaluation**: Prose description (complex protocol documentation)

**Execution Model**: Sonnet

**Tool Usage**:
- Use Write tool to create new file
- Use Read tool to reference design document
- Use Grep tool for content validation
- Never use bash file operations or heredocs

**Implementation**:

Create new file `agent-core/agents/tdd-task.md` with baseline TDD protocol that will be combined with runbook-specific context by prepare-runbook.py.

**Required Sections:**

1. **Agent Role and Purpose**
   - Baseline template for TDD cycle execution
   - Combined with runbook context to create plan-specific agents
   - Fresh context per cycle (no accumulation)

2. **RED Phase Protocol**
   - Write test exactly as specified in cycle definition
   - Run `just test`
   - Verify failure matches expected message
   - If passes unexpectedly → check for `[REGRESSION]` marker
   - If not regression: STOP and escalate

3. **GREEN Phase Protocol**
   - Write minimal implementation to make test pass
   - Run `just test` → verify test passes
   - Run full suite → handle any regressions individually (never batch)
   - If stuck after 2 attempts → STOP, mark BLOCKED, escalate

4. **REFACTOR Phase Protocol (Mandatory)**

   Step-by-step refactoring process:

   a. **Format & Lint**
   ```bash
   just lint  # includes reformatting
   ```
   Fix lint errors. Ignore complexity warnings and line limits (addressed next).

   b. **Intermediate Commit**
   ```bash
   git commit -m "WIP: Cycle X.Y [name]"  # rollback point
   ```

   c. **Quality Check**
   ```bash
   just precommit  # validates green BEFORE refactoring
   ```
   Surfaces complexity warnings and line limit issues.

   d. **Refactoring Assessment (if warnings)**

   | Warning Type | Handler |
   |--------------|---------|
   | Common (split module, simplify function) | Sonnet designs, executes |
   | Architectural (new abstraction, multi-module impact) | Opus designs, decides escalation |
   | New abstraction introduced | Opus, always escalate to human |

   e. **Execute Refactoring**
   - Use scripts proactively (Tier 1)
   - Verify with `just precommit` after
   - If fails: STOP, keep state for diagnostic

   f. **Post-Refactoring Updates**
   Update all references to refactored code:
   - Plans: All designs and runbooks (`grep -r "old_ref" plans/`)
   - Agent documentation: Files in `agents/`
   - CLAUDE.md: Only if behavioral rules affected
   - Regenerate step files if runbook.md changed

   g. **Amend Commit**
   Safety check:
   ```bash
   current_msg=$(git log -1 --format=%s)
   if [[ "$current_msg" != WIP:* ]]; then
     echo "ERROR: Expected WIP commit, found: $current_msg"
     exit 1
   fi
   ```

   Amend and reword:
   ```bash
   git commit --amend -m "Cycle X.Y: [name]"
   ```

5. **Structured Log Entry Template**
   ```markdown
   ### Cycle X.Y: [name] [timestamp]
   - Status: RED_VERIFIED | GREEN_VERIFIED | STOP_CONDITION | REGRESSION
   - Test command: `[exact command]`
   - RED result: [FAIL as expected | PASS unexpected | N/A]
   - GREEN result: [PASS | FAIL - reason]
   - Regression check: [N/N passed | failures]
   - Refactoring: [none | description]
   - Files modified: [list]
   - Stop condition: [none | description]
   - Decision made: [none | description]
   ```

6. **Stop Conditions and Escalation**
   - RED passes unexpectedly (not regression) → STOP, escalate
   - GREEN fails after 2 attempts → STOP, mark BLOCKED, escalate
   - Refactoring fails precommit → STOP, keep state, escalate
   - Architectural refactoring needed → Escalate to opus
   - New abstraction proposed → Escalate to human via opus

7. **Tool Usage Constraints**
   - Use Read, Write, Edit for file operations
   - Use Bash for test commands, git commands, precommit
   - Use Grep for reference finding (grep -r pattern)
   - Never use heredocs in Bash (sandbox restriction)
   - Report all errors explicitly (never suppress)

**Content Source**: Extract from design document sections:
- TDD Task Agent (all subsections)
- TDD Execution Escalation
- Command Reference

**Expected Outcome**:
- File `agent-core/agents/tdd-task.md` created
- Contains all 7 required sections
- Protocol is explicit and actionable for weak orchestrator
- File size 6000-10000 bytes (comprehensive baseline)

**Unexpected Result Handling**:
- If file size < 5000 bytes: Review completeness of protocol steps
- If refactoring section unclear: Add more specific decision criteria

**Error Conditions**:
- Directory not found → STOP and report
- Write permission denied → STOP and report

**Validation**:
- Read `agent-core/agents/tdd-task.md` successfully (confirms file exists)
- Use Grep to verify all 7 required sections present
- Use Grep to verify command examples present ("just test", "just lint", "just precommit")
- File size typically 6000-12000 bytes (comprehensive baseline)
- Content matches design document protocol

**Success Criteria**:
- File created with all 7 required sections
- RED/GREEN/REFACTOR protocol complete and explicit
- Stop conditions clearly defined
- Escalation rules documented
- File size indicates comprehensive baseline (6000-10000 bytes)

**Report Path**: `plans/tdd-integration/reports/step-3-report.md`

---
