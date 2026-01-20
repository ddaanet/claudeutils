# Step 3 Report: Create TDD Task Agent Baseline

**Step**: `plans/tdd-integration/steps/step-3.md`
**Timestamp**: 2026-01-19

## Summary

Created baseline TDD task agent template at `/Users/david/code/claudeutils/agent-core/agents/tdd-task.md` with complete RED/GREEN/REFACTOR protocol. File contains all 7 required sections and will be combined with runbook-specific context by `prepare-runbook.py` to create plan-specific agents.

## Actions Taken

1. Read design document to extract TDD protocol details
2. Created `agent-core/agents/tdd-task.md` with comprehensive baseline template
3. Verified file creation and content completeness

## File Created

**Path**: `/Users/david/code/claudeutils/agent-core/agents/tdd-task.md`
**Size**: 10,835 bytes
**Purpose**: Baseline template for TDD cycle execution (combined with runbook context)

## Sections Included

All 7 required sections present:

1. **Role and Purpose** - Agent role, context handling, fresh context per cycle
2. **RED Phase Protocol** - Write test, run suite, verify failure, handle unexpected pass
3. **GREEN Phase Protocol** - Minimal implementation, verify pass, regression check
4. **REFACTOR Phase Protocol** - 7-step mandatory refactoring process:
   - Step 1: Format & Lint (`just lint`)
   - Step 2: Intermediate Commit (WIP rollback point)
   - Step 3: Quality Check (`just precommit`)
   - Step 4: Refactoring Assessment (handler selection, tiers)
   - Step 5: Execute Refactoring (script-first principle)
   - Step 6: Post-Refactoring Updates (plans, agents, CLAUDE.md)
   - Step 7: Amend Commit (safety check, reword)
5. **Structured Log Entry** - Template with all required fields
6. **Stop Conditions and Escalation** - 5 stop conditions with escalation rules
7. **Tool Usage Constraints** - File operations, command execution, critical constraints

## Key Protocol Elements

**RED Phase:**
- Exact test specification from cycle definition
- Verify failure matches expected message
- Handle unexpected pass with regression check
- Stop and escalate if not regression

**GREEN Phase:**
- Minimal implementation approach
- Individual regression handling (never batch)
- 2-attempt limit with blocked escalation

**REFACTOR Phase:**
- Mandatory for every cycle
- WIP commit as rollback point
- Precommit validation before refactoring
- Tiered refactoring approach (script-first)
- Documentation updates (plans, agents, CLAUDE.md)
- Safety check before commit amend

**Command Examples:**
- `just test` - RED/GREEN verification
- `just lint` - Format & lint
- `just precommit` - Quality check and validation

## Validation Results

✓ File created successfully
✓ All 7 required sections present
✓ Command examples present (`just test`, `just lint`, `just precommit`)
✓ File size 10,835 bytes (within expected 6,000-12,000 byte range)
✓ Protocol matches design document specifications
✓ Stop conditions clearly defined (5 escalation scenarios)
✓ Escalation rules documented with status codes

## Expected Outcome Achieved

- [x] File `agent-core/agents/tdd-task.md` created
- [x] Contains all 7 required sections
- [x] Protocol is explicit and actionable for weak orchestrator
- [x] File size 10,835 bytes (comprehensive baseline within expected range)
- [x] RED/GREEN/REFACTOR protocol complete and explicit
- [x] Stop conditions clearly defined
- [x] Escalation rules documented
- [x] Tool usage constraints specified

## Success Criteria Met

All success criteria from step definition satisfied:

✓ File created with all 7 required sections
✓ RED/GREEN/REFACTOR protocol complete and explicit
✓ Stop conditions clearly defined (5 scenarios)
✓ Escalation rules documented (status codes and handlers)
✓ File size indicates comprehensive baseline (10,835 bytes)

---

**Status**: SUCCESS
**Next Step**: Step 4 (Move oneshot workflow documentation)
