# Session: Workflow Infrastructure Improvements

**Status:** Infrastructure improvement tasks identified from plugin migration vetting RCAs.

## Completed This Session

**Extracted infrastructure improvements from plugin migration vetting session:**

Two RCAs identified workflow infrastructure gaps that apply across all future work:

**RCA #1: Sequential Task Launch**
- Issue: Tool batching documentation doesn't explicitly cover Task tool parallelization
- Impact: ~14 min wall-clock delay when launching agents sequentially vs in parallel
- Learning: Sequential Task launch breaks parallelism

**RCA #2: Vet-Fix-Agent Context-Blind Validation**
- Issue: No execution context provided to vet-fix-agent, no UNFIXABLE escalation protocol
- Impact: Agent validates against current state instead of execution-time state, causing incorrect "fixes"
- Learning: Vet-fix-agent context-blind validation

**Branch created:** Separated infrastructure tasks from plugin migration work for independent merge to main.

## Pending Tasks

- [ ] **Strengthen commit Gate B coverage check** — Gate B is boolean (any report?) not coverage ratio (artifacts:reports 1:1) | sonnet
  - Commit skill Step 1 Gate B: count new/modified production artifacts, verify each has vet report
- [ ] **Review reflect skill: task output for skill/fragment fixes** — RCA should produce pending tasks for skill/fragment updates, not inline fixes, for context economy | sonnet
  - Current: reflect skill applies fixes in-session (Exit Path 1) consuming context budget
  - Better: produce tasks in session.md for separate session execution
- [ ] **Strengthen vet-fix-agent delegation pattern** — Add execution context provision and UNFIXABLE detection | sonnet
  - Sub-tasks:
    1. Add execution context to vet-fix-agent prompts (include phase dependencies, state transitions)
    2. Add UNFIXABLE detection to orchestrator (read report, grep for markers, escalate if found)
    3. Document vet-fix-agent limitations in memory-index.md (context-blind by default)
    4. Evaluate meta-review necessity (when should vet output be vetted?)
  - Analysis: plans/reflect-rca-sequential-task-launch/rca.md
- [ ] **Update tool-batching.md for Task tool parallelization** — Add explicit Task tool guidance with examples | sonnet
  - Add "Task Tool Parallelization" section to agent-core/fragments/tool-batching.md
  - Include example: vet 6 phase files in parallel (6 Task calls in single message)
  - Show anti-pattern (sequential launch) vs correct pattern (batched launch)

## Blockers / Gotchas

**Vet-fix-agent temporal reasoning limitation:**
- Agent validates against current filesystem state, not execution-time state
- Mitigation: Provide execution context in delegation prompts (dependencies, state transitions)
- See pending task: "Strengthen vet-fix-agent delegation pattern"

**UNFIXABLE detection is manual:**
- Vet reports mark issues as UNFIXABLE but don't escalate
- Orchestrator must read report and grep for markers
- See pending task: "Strengthen vet-fix-agent delegation pattern" (sub-task 2)

## Reference Files

- **plans/reflect-rca-sequential-task-launch/rca.md** — RCA covering both deviations (Task parallelization + vet context issues)
- **agent-core/fragments/tool-batching.md** — Current tool batching guidance (needs Task tool section)
- **agents/learnings.md** — Contains learnings from both RCAs
