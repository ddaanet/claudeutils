# Phase 1: Execution Plan - Split Files

**Generated from**: phase1-execution-plan.md
**Step count**: 10

## Files

- **phase1-execution-context.md** - Common context for all steps (prerequisites, technical decisions, success criteria, execution notes)

### Steps
- **phase1-step1.md** - Step 1 execution instructions
- **phase1-step2.md** - Step 2 execution instructions
- **phase1-step3.md** - Step 3 execution instructions
- **phase1-step4.md** - Step 4 execution instructions
- **phase1-step5.md** - Step 5 execution instructions
- **phase1-step6.md** - Step 6 execution instructions
- **phase1-step7.md** - Step 7 execution instructions
- **phase1-step8.md** - Step 8 execution instructions
- **phase1-step9.md** - Step 9 execution instructions
- **phase1-step10.md** - Step 10 execution instructions

## Usage

**Agent Reuse Pattern** (for cache efficiency):

1. **Executor Agent** (haiku):
   - First step: Spawn new executor with context + step1
   - Subsequent steps: Resume executor with step{N} (leverages cache from previous context)
   - Each invocation writes results to execution report

2. **Reviewer Agents**:
   - First review: Spawn new haiku reviewer with execution report
   - Subsequent reviews: Resume same reviewer (maintains review context)
   - Final approval: Spawn sonnet reviewer after all haiku reviews pass

3. **Workflow**:
   ```
   Step 1: Task(executor, context+step1) → output file → Task(reviewer, report1)
   Step 2: Task(resume=executor_id, step2) → append to file → Task(resume=reviewer_id, report2)
   Step 3: Task(resume=executor_id, step3) → append to file → Task(resume=reviewer_id, report3)
   ...
   Step 10: Task(resume=executor_id, step10) → append to file → Task(resume=reviewer_id, report10)
   Final: Task(sonnet-reviewer, all reports)
   ```

## Orchestration Pattern

**Initial spawn** (Step 1):
```
Haiku Executor Agent (new):
  Input: phase1-execution-context.md + phase1-step1.md
  Output: plans/unification/reports/phase1-step1-execution.md
  Returns: agent_id (save for reuse)

Haiku Reviewer Agent (new):
  Input: plans/unification/reports/phase1-step1-execution.md
  Output: plans/unification/reports/phase1-step1-review.md
  Returns: agent_id (save for reuse)
```

**Resumed execution** (Steps 2-10):
```
Haiku Executor Agent (resumed):
  resume: <executor_agent_id>
  Input: phase1-step{N}.md (context already in cache)
  Output: plans/unification/reports/phase1-step{N}-execution.md

Haiku Reviewer Agent (resumed):
  resume: <reviewer_agent_id>
  Input: phase1-step{N}-execution.md
  Output: plans/unification/reports/phase1-step{N}-review.md
```

**Final approval** (after all steps reviewed):
```
Sonnet Reviewer Agent (new):
  Input: All execution + review reports
  Output: Final approval or change requests
```
