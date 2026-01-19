# Execution Plan - Split Files

**Generated from**: phase3-execution-plan.md
**Step count**: 5
**Format**: STEP

## Files

- **execution-context.md** - Common context for all steps (prerequisites, critical files, execution notes, success criteria)

### Steps
- **step1.md** - Step 1 execution instructions
- **step2.md** - Step 2 execution instructions
- **step3.md** - Step 3 execution instructions
- **step4.md** - Step 4 execution instructions
- **step5.md** - Step 5 execution instructions

## Usage

For each step execution:
1. Provide both `execution-context.md` and `step{N}.md` to the executor
2. Executor reads context first, then executes step
3. Executor writes results to execution report
4. Review before proceeding to next step

## Orchestration Pattern

```
Executor:
  Input: execution-context.md + step{N}.md
  Output: Terse return ("done: <summary>" or "blocked: <reason>")
  Reports: Written to execution report file

Review Agent (if needed):
  Input: context + execution report
  Output: Review findings
```
