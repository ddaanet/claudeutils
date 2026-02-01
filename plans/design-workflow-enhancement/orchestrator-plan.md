## Orchestrator Instructions

**Parallelization**:
- Steps 1-2: Must run sequentially (review depends on agent creation)
- Step 3: Can run in parallel with Steps 1-2 (no dependency on agent file)
- Step 4: Must run after all previous steps complete (needs all files + fixes applied)

**Stop conditions**:
- Any step reports error → stop, escalate to user
- Step 2 review identifies UNFIXABLE critical issues → stop, escalate

---