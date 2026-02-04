## Orchestrator Instructions

Execute all phases sequentially:

1. Read each phase header to understand objective and complexity
2. Execute all steps in phase order
3. After each phase: check reports directory for review results
4. If review identifies blockers: fix and re-run phase
5. Continue to next phase

**Stop on:** Any failure in step execution, blocker in review, or missing artifact.