# Session Handoff: 2026-01-19

**Status:** TDD integration design complete - ready for sonnet planning

## Completed This Session

- Analyzed pytest-md skills vs agent-core skills
- Designed TDD workflow integration (Option A: TDD as specialized workflow)
- Wrote design document: `plans/tdd-integration/design.md`

**Key design decisions:**
- Merge /design and /plan-design (TDD mode support)
- Merge /execute-tdd and /orchestrate (unified runbook execution)
- TDD task agent as baseline template (not standalone)
- Agent-per-cycle pattern with prepare-runbook.py integration
- WIP commit + amend pattern for clean history
- Separate workflow docs (oneshot + tdd)

## Pending Tasks

### Immediate: Create Implementation Runbook
- [ ] Run `/plan-adhoc` on `plans/tdd-integration/design.md`

### TDD Integration Implementation (from runbook)
- [ ] Write `agent-core/agents/tdd-workflow.md`
- [ ] Write `agent-core/agents/tdd-task.md` (baseline template)
- [ ] Move `claudeutils/agents/workflow.md` → `agent-core/agents/oneshot-workflow.md`
- [ ] Update `/design` skill with TDD mode
- [ ] Update `/oneshot` skill with TDD methodology detection
- [ ] Update `/orchestrate` skill with TDD runbook support
- [ ] Update `prepare-runbook.py` for TDD cycle format
- [ ] Create `/plan-tdd` skill
- [ ] pytest-md integration: submodule + sync + remove project skills

### After TDD Integration
- [ ] Fix precommit checks in markdown branch
- [ ] Return to unification branch for Phase 4

## Next Steps

1. Start new session with sonnet
2. Type `#execute` → runs `/plan-adhoc` on `plans/tdd-integration/design.md`
