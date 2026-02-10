# Cycle 5.3: sandbox-exemptions.md Worktree Patterns

**Timestamp:** 2026-02-10

**Status:** GREEN_VERIFIED

**Test command:** `just test`

**RED result:** PASS as expected (section did not exist)

**GREEN result:** PASS (section added successfully)

**Regression check:** 795/797 passed, 1 failed (pre-existing), 1 xfail (pre-existing) — no new failures

**Refactoring:** none

**Files modified:**
- `agent-core/fragments/sandbox-exemptions.md`

**Stop condition:** none

**Decision made:** none

## Summary

Added new "### Worktree Operations" section to `sandbox-exemptions.md` documenting:
- Location advantage: worktrees inside project root eliminate most sandbox bypass needs
- Remaining exceptions: `uv sync` (network + package downloads) and `direnv allow` (external writes)
- Skill implementation: worktree skill invokes with `dangerouslyDisableSandbox: true` automatically
- Updated "Commands Requiring dangerouslyDisableSandbox: true" list to reference environment initialization

This completes Cycle 5.3. The documentation now guides agents on sandbox requirements for worktree operations.
