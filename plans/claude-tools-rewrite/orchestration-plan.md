---
name: claude-tools-rewrite-orchestration
status: draft
created: 2026-01-30
---

# Claude Tools Rewrite - Orchestration Plan

**Goal**: Replace ~2000 lines of untested shell scripts with Python modules in claudeutils, then integrate via thin shell wrappers in home repo

## Overview

This project spans two repositories:
1. **claudeutils** (/Users/david/code/claudeutils/) - Python implementation with tests
2. **home** (/Users/david/code/home/) - Shell wrapper integration

## Execution Sequence

### Step 1: Transfer Design and Runbook to claudeutils

**Action**: Copy transfer directory to claudeutils repo

```bash
# In claudeutils repo
mkdir -p plans/claude-tools-rewrite
cp -r /Users/david/code/home/plans/claude-tools-rewrite/transfer-to-claudeutils/* \
      plans/claude-tools-rewrite/
```

**Deliverables**:
- plans/claude-tools-rewrite/design.md (in claudeutils)
- plans/claude-tools-rewrite/runbook.md (in claudeutils)

### Step 2: Execute Python Implementation (claudeutils repo)

**Runbook**: `plans/claude-tools-rewrite/runbook.md` (in claudeutils)
**Working Directory**: /Users/david/code/claudeutils/
**Cycles**: 45 cycles across 3 phases
**Execution**:

```bash
cd /Users/david/code/claudeutils
python3 agent-core/bin/prepare-runbook.py plans/claude-tools-rewrite/runbook.md
# Then run /orchestrate or manual execution
```

**Output**:
- src/claudeutils/account/ module (state, mode, keychain, providers, usage, switchback, cli)
- src/claudeutils/model/ module (config, overrides, cli)
- src/claudeutils/statusline/ module (display, cli)
- tests/ with full coverage
- claudeutils CLI with account/model/statusline commands

**Success Criteria**:
- All 45 cycles GREEN
- `just dev` passes (tests, mypy, ruff)
- CLI commands functional: `claudeutils account status`, `claudeutils model list`, etc.

### Step 3: Execute Shell Wrapper Integration (home repo)

**Runbook**: `plans/claude-tools-rewrite/home-runbook.md` (in home)
**Working Directory**: /Users/david/code/home/
**Cycles**: 6 cycles in 1 phase
**Execution**:

```bash
cd /Users/david/code/home
python3 agent-core/bin/prepare-runbook.py plans/claude-tools-rewrite/home-runbook.md
# Then run /orchestrate or manual execution
```

**Output**:
- claude/claude-account (wrapper with direnv integration)
- claude/claude-model (simple delegation wrapper)
- claude/statusline-command (stdin passthrough wrapper)

**Success Criteria**:
- All 6 cycles GREEN
- Wrappers call claudeutils correctly
- direnv integration works for mode switches
- Statusline produces correct 2-line output

### Step 4: Migration and Cutover

**Actions**:

1. **Backup existing scripts**:
   ```bash
   cd ~/code/home/claude
   mkdir -p .backup-$(date +%Y%m%d)
   mv claude-account.sh claude-model.sh statusline-command.sh .backup-*/
   ```

2. **Verify wrappers**:
   ```bash
   claude/claude-account status
   claude/claude-model list
   echo '{}' | claude/statusline-command
   ```

3. **Update justfile** (if needed):
   - No changes needed if wrappers use same names

4. **Test integration**:
   - Run `claude-account plan` → verify direnv reloads
   - Run `claude-model set <model>` → verify override written
   - Start Claude Code → verify statusline renders

5. **Remove old scripts** (after successful verification):
   ```bash
   rm -rf claude/.backup-* claude/lib/account-validation.sh
   ```

## Dependencies

```
Step 1 (Transfer)
    ↓
Step 2 (claudeutils implementation)
    ↓
Step 3 (home wrappers)
    ↓
Step 4 (migration)
```

**Critical**: Steps must execute in sequence. Step 3 requires Step 2 complete.

## Rollback Plan

If issues arise during Step 4:

1. **Restore old scripts**:
   ```bash
   mv claude/.backup-*/*.sh claude/
   ```

2. **Investigate issue** in isolated environment

3. **Fix and retest** before attempting cutover again

## Runbook Locations

| Component | Runbook | Repository | Status |
|-----------|---------|------------|--------|
| Python implementation | `plans/claude-tools-rewrite/runbook.md` | claudeutils | Ready for prepare-runbook.py |
| Shell wrappers | `plans/claude-tools-rewrite/home-runbook.md` | home | Ready for prepare-runbook.py |
| Design (original) | `plans/claude-tools-rewrite/design.md` | home | Reference |
| Design (transferred) | `plans/claude-tools-rewrite/design.md` | claudeutils | For implementation |

## Transfer Package

**Directory**: `plans/claude-tools-rewrite/transfer-to-claudeutils/`

**Contents**:
- design.md - Complete design document
- runbook.md - 45-cycle TDD runbook for Python implementation

**Transfer Command**:
```bash
# From home repo
tar -czf claude-tools-rewrite-transfer.tar.gz \
  plans/claude-tools-rewrite/transfer-to-claudeutils/

# Copy to claudeutils repo and extract
cd /Users/david/code/claudeutils
tar -xzf ~/code/home/claude-tools-rewrite-transfer.tar.gz
mv transfer-to-claudeutils/* plans/claude-tools-rewrite/
rmdir transfer-to-claudeutils
```

## Success Metrics

**Technical**:
- Python modules: 100% test coverage on validation logic
- All CLI commands functional
- Zero regressions from shell scripts
- plistlib fixes heredoc bug
- Statusline startup <100ms

**Process**:
- Design → Two runbooks → Execution → Integration
- Clear separation of concerns (Python vs shell)
- Testability (mocked subprocess, tmp_path fixtures)

## Timeline Estimate

**Not providing estimates per CLAUDE.md** - User will gauge based on cycle execution.

## Notes

- **Review**: Both runbooks passed tdd-plan-reviewer (zero violations)
- **Testing approach**: Pure TDD - RED/GREEN/REFACTOR for all cycles
- **Migration strategy**: Three phases in design (account+model → statusline → cutover)
- **Zero new dependencies**: Uses stdlib + existing pydantic/click
