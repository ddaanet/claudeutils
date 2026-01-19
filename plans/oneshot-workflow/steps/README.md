# Phase 1 Execution Steps

This directory contains individual step files for Phase 1 execution.

## Files

- `step-1-1.md` - Create Directory Structure
- `step-1-2.md` - Move and Rename Baseline Agent
- `step-1-3.md` - Implement prepare-runbook.py Script
- `step-1-4.md` - Test Script with Phase 2 Runbook

## Execution Pattern

Each step should be executed using the plan-specific agent (to be created):

```bash
# After plan-specific agent is created
# Use Task tool with phase1-task agent for each step
```

## Full Context

For complete execution context, metadata, and design decisions, see:
- Main plan: `plans/oneshot-workflow/phase1-execution-plan.md`
- Design: `plans/oneshot-workflow/design.md`
- Review: `plans/oneshot-workflow/reports/phase1-plan-review.md`
