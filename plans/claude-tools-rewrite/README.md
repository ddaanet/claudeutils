# Transfer Package: Claude Tools Rewrite

**Purpose**: This directory contains all materials needed to execute the Python implementation phase in the claudeutils repository.

## Contents

- **design.md** - Complete design document with architecture, decisions, and module layout
- **runbook.md** - 45-cycle TDD runbook for implementing account, model, and statusline modules

## Transfer Instructions

### Copy to claudeutils Repository

```bash
# From home repo root
cd /Users/david/code/home

# Create plans directory in claudeutils if it doesn't exist
mkdir -p /Users/david/code/claudeutils/plans/claude-tools-rewrite

# Copy design and runbook
cp plans/claude-tools-rewrite/transfer-to-claudeutils/design.md \
   /Users/david/code/claudeutils/plans/claude-tools-rewrite/

cp plans/claude-tools-rewrite/transfer-to-claudeutils/runbook.md \
   /Users/david/code/claudeutils/plans/claude-tools-rewrite/
```

### Execute in claudeutils Repository

```bash
cd /Users/david/code/claudeutils

# Prepare runbook for execution
python3 agent-core/bin/prepare-runbook.py plans/claude-tools-rewrite/runbook.md

# Execute (via /orchestrate or manually)
# This will create:
#   - src/claudeutils/account/ (state, mode, keychain, providers, usage, switchback, cli)
#   - src/claudeutils/model/ (config, overrides, cli)
#   - src/claudeutils/statusline/ (display, cli)
#   - tests/ for all modules
```

## What This Implements

### Phase 1: Account Module Foundation (13 cycles)
- AccountState Pydantic model with validation
- Provider Protocol with Anthropic/OpenRouter/LiteLLM implementations
- Keychain wrapper for macOS security commands
- LaunchAgent plist generation (fixes heredoc bug)
- Usage API caching

### Phase 2: Model Module and Configuration (9 cycles)
- LiteLLM config parsing with tier/pricing metadata
- Model override file read/write
- Tier filtering

### Phase 3: Statusline Module and CLI Integration (23 cycles)
- StatuslineFormatter (ANSI colors, token bars, vertical bars)
- CLI commands: account {status,plan,api,provider}
- CLI commands: model {list,set,reset,show}
- CLI command: statusline

## After Execution

When all 45 cycles are GREEN in claudeutils:

1. Return to home repo
2. Execute `plans/claude-tools-rewrite/home-runbook.md` (6 cycles for shell wrappers)
3. Follow migration steps in `plans/claude-tools-rewrite/orchestration-plan.md`

## Review Status

✅ **Passed tdd-plan-reviewer**: Zero violations
- All cycles use behavioral descriptions (not prescriptive code)
- Perfect RED/GREEN sequencing
- Incremental implementation pattern

## Dependencies

**Before starting**:
- claudeutils package in development mode
- pytest, mypy, ruff configured
- Access to ~/.claude/ for integration tests

**After completion**:
- Python modules ready for shell wrapper integration
- All functionality testable and tested
- Ready to replace ~2000 lines of shell scripts

## Related Files

In home repo:
- `plans/claude-tools-rewrite/design.md` - Original design (same as this copy)
- `plans/claude-tools-rewrite/home-runbook.md` - Shell wrapper runbook (6 cycles)
- `plans/claude-tools-rewrite/orchestration-plan.md` - Overall execution plan
- `plans/claude-tools-rewrite/runbook.md` - Combined runbook (deprecated - use split versions)

## Notes

- **Execution context**: Work happens in claudeutils repo, not home
- **Report location**: Use `plans/claude-tools-rewrite/reports/` in claudeutils
- **Test fixtures**: Use tmp_path for ~/.claude/ state file simulation
- **Mock patterns**: subprocess.run patches for keychain/security/launchctl/curl/git/pgrep
