## Orchestrator Instructions

Execute steps sequentially using validator-consolidation-task agent. Phase boundaries (after Steps 4, 6, 8) are checkpoints — run test suite and escalate if failures. Steps 2-4 and Steps 5-6 could be parallelized within their phases if orchestrator supports it, but sequential execution is acceptable.

---