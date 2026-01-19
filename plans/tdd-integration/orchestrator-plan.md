## Orchestrator Instructions

Execute steps sequentially using tdd-integration-task agent.

**Execution Order:**

1. Execute steps 1-3 in parallel (independent file creation)
2. Execute steps 4-5 in parallel after steps 1-3 complete (for reference consistency)
3. Execute step 6 after steps 1-5 complete (creates planning request)
4. Execute step 7 after step 6 completes (creates planning request)
5. Execute step 8 (can proceed independently, not blocked by steps 6-7)

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