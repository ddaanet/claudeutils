## Orchestrator Instructions

**CRITICAL: Each step MUST be executed by a separate agent invocation.** Do not execute multiple steps in a single agent call.

Use tdd-integration-task agent for all step executions.

**Execution Order:**

**Phase 1 - Parallel execution (Steps 1-3):**
- Launch 3 agents in parallel (single message with 3 Task tool calls):
  - Agent 1: Execute Step 1 (create oneshot-workflow.md)
  - Agent 2: Execute Step 2 (create tdd-workflow.md)
  - Agent 3: Execute Step 3 (create tdd-task.md)
- Wait for all 3 agents to complete before proceeding

**Phase 2 - Parallel execution (Steps 4-5):**
- Launch 2 agents in parallel (single message with 2 Task tool calls):
  - Agent 4: Execute Step 4 (update /design skill)
  - Agent 5: Execute Step 5 (update /oneshot skill)
- Wait for both agents to complete before proceeding

**Phase 3 - Sequential execution (Steps 6-8):**
- Agent 6: Execute Step 6 (create planning request for prepare-runbook.py)
- Agent 7: Execute Step 7 (create planning request for /plan-tdd) - after Step 6 completes
- Agent 8: Execute Step 8 (pytest-md integration) - can run independently

**Agent Invocation Pattern:**
```
For parallel steps: Single message with multiple Task tool calls
For sequential steps: One Task tool call per message, wait for completion
```

**Error Handling:**

- File not found errors → Verify prerequisites, escalate to user
- Permission denied → Escalate to user immediately
- Unexpected file structure → Stop and escalate to sonnet for review
- Parse errors in modified files → Stop and escalate to sonnet for fix

**Escalation Rules:**

- Haiku → Sonnet: Complex modifications, unexpected structures
- Sonnet → User: Missing prerequisites, blocked tasks, architectural decisions

**Success Criteria:**

- Steps 1-5 completed successfully (files created/modified)
- Steps 6-7 completed successfully (planning requests created)
- Step 8 completed successfully (pytest-md integrated)
- All validation criteria met for all steps
- No syntax errors in any modified files
- Planning requests ready for separate planning sessions

---