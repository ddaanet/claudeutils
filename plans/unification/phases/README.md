# Out-of-Tree Consolidation - Split Plan Files

**Generated from**: consolidation-plan.md
**Phase count**: 7

## Files

- **consolidation-context.md** - Common context for all phases (architecture decisions, critical files, execution notes, success criteria)

### Phases
- **phase1.md** - Phase 1 execution instructions
- **phase2.md** - Phase 2 execution instructions
- **phase3.md** - Phase 3 execution instructions
- **phase4.md** - Phase 4 execution instructions
- **phase5.md** - Phase 5 execution instructions
- **phase6.md** - Phase 6 execution instructions
- **phase7.md** - Phase 7 execution instructions

## Usage

For each phase execution:
1. Provide both `consolidation-context.md` and `phase{N}.md` to the executor
2. Executor reads context first, then executes phase
3. Executor writes results to execution report (scratch/consolidation/reports/)
4. Review before proceeding to next phase

## Orchestration Pattern

```
Haiku Executor:
  Input: consolidation-context.md + phase{N}.md
  Output: Terse return ("done: <summary>" or "blocked: <reason>")
  Reports: Written to scratch/consolidation/reports/phase{N}-execution.md

Review Agent (if needed):
  Input: context + execution report
  Output: Review findings (diff-based)
```
