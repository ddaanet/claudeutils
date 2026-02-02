# Claude Tools Rewrite - Runbook Split Summary

**Date**: 2026-01-30
**Action**: Split single runbook into two repository-specific runbooks

## What Was Created

### 1. Transfer Package for claudeutils

**Directory**: `transfer-to-claudeutils/`

**Contents**:
- `design.md` - Complete design document (copy)
- `runbook.md` - Python implementation runbook (45 cycles)
- `README.md` - Transfer and execution instructions

**Purpose**: Everything needed to execute Python implementation in claudeutils repo

### 2. Home Repository Runbook

**File**: `home-runbook.md`

**Contents**:
- 6 cycles creating shell wrappers
- Integration tests for wrappers
- direnv integration verification

**Purpose**: Shell wrapper creation after Python modules complete

### 3. Orchestration Plan

**File**: `orchestration-plan.md`

**Contents**:
- Overall execution sequence (4 steps)
- Dependencies and prerequisites
- Migration and cutover procedures
- Rollback plan
- Success metrics

**Purpose**: Coordinate execution across both repositories

### 4. Original Runbook (Deprecated)

**File**: `runbook.md`

**Status**: Archived with deprecation notice pointing to split versions

**Reason**: Original combined all work in one runbook, making cross-repo execution unclear

## File Structure

```
plans/claude-tools-rewrite/
├── design.md                      # Original design (reference)
├── runbook.md                     # DEPRECATED - see split versions
├── SPLIT-SUMMARY.md              # This file
├── orchestration-plan.md          # Overall execution plan
├── home-runbook.md                # Home repo: shell wrappers (6 cycles)
├── transfer-to-claudeutils/       # Package for claudeutils repo
│   ├── README.md                  # Transfer instructions
│   ├── design.md                  # Design copy for claudeutils
│   └── runbook.md                 # Python implementation (45 cycles)
└── reports/                       # Will contain execution reports
    └── runbook-review.md          # TDD plan review (PASS)
```

## Execution Sequence

### Step 1: Transfer to claudeutils

```bash
# Copy transfer directory contents to claudeutils repo
cd /Users/david/code/home
mkdir -p /Users/david/code/claudeutils/plans/claude-tools-rewrite
cp transfer-to-claudeutils/* /Users/david/code/claudeutils/plans/claude-tools-rewrite/
```

### Step 2: Execute in claudeutils

```bash
cd /Users/david/code/claudeutils
python3 agent-core/bin/prepare-runbook.py plans/claude-tools-rewrite/runbook.md
# Then /orchestrate or manual execution (45 cycles)
```

### Step 3: Execute in home

```bash
cd /Users/david/code/home
python3 agent-core/bin/prepare-runbook.py plans/claude-tools-rewrite/home-runbook.md
# Then /orchestrate or manual execution (6 cycles)
```

### Step 4: Migration

Follow migration steps in `orchestration-plan.md`

## Review Status

Both runbooks passed tdd-plan-reviewer:
- ✅ **claudeutils runbook**: Zero violations, 45 cycles
- ✅ **home runbook**: Zero violations, 6 cycles

## Cycle Distribution

| Phase | Repository | Cycles | Focus |
|-------|------------|--------|-------|
| 1 | claudeutils | 13 | Account module (state, providers, keychain) |
| 2 | claudeutils | 9 | Model module (config parsing, overrides) |
| 3 | claudeutils | 23 | Statusline module + CLI integration |
| 4 | home | 6 | Shell wrappers + integration tests |
| **Total** | | **51** | |

## Benefits of Split

1. **Clear repository boundaries** - Work in correct context
2. **Independent execution** - Can run claudeutils work without home repo
3. **Clean transfer** - Transfer package is self-contained
4. **Easier tracking** - Reports directory per repo
5. **Better isolation** - Test paths, fixtures, conventions per repo

## Next Steps

1. Review `orchestration-plan.md` for overall strategy
2. Transfer design and runbook to claudeutils (Step 1)
3. Execute Python implementation in claudeutils (Step 2)
4. Execute shell wrappers in home (Step 3)
5. Migration and cutover (Step 4)

## Notes

- Original combined runbook preserved for reference
- All files reviewed and validated
- prepare-runbook.py ready for both runbooks
- Commit this split structure before execution
