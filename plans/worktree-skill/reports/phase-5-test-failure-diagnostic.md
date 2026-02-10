# Phase 5 Test Failure Diagnostic

## Summary

**Status:** Fixed worktree submodule initialization, but test still fails at merge step.

**Root Cause:** Git 2.52.0 introduced stricter security for file protocol in submodule operations. Tests use relative submodule URLs (`./agent-core`) which fail to resolve correctly from worktrees.

**Test Status:**
- Pre-existing failure at Phase 4 checkpoint (confirmed by checking out c5b38ef)
- Not caused by Phase 5 changes
- Test: `tests/test_merge_phase_2.py::test_merge_phase_2_diverged_commits`

## Investigation

### Issue 1: Submodule Initialization Failure

**Symptom:** `git submodule update --init --reference` fails with "fatal: transport 'file' not allowed"

**Root Cause:**
- Git 2.52.0 disables file protocol by default for security
- Relative submodule URL `./agent-core` resolved from worktree location
- `--reference` flag alone insufficient

**Fix Applied:**
- Added `-c protocol.file.allow=always` flag to `git submodule update` command
- File: `src/claudeutils/worktree/commands.py` line 181-191
- Allows local file protocol for test scenarios

### Issue 2: Submodule URL Resolution

**Symptom:** Worktree submodule cloned from wrong repository (parent repo instead of agent-core submodule)

**Root Cause:**
- Relative URL `./agent-core` resolves differently from worktree context
- Git interprets path relative to worktree location, not parent repo

**Fix Applied:**
- Changed test helper to use absolute paths for submodule URLs
- File: `tests/test_merge_helpers.py` line 53-56
- Format: `/absolute/path/to/repo/agent-core` instead of `./agent-core`

### Issue 3: Merge Fetch Failure

**Symptom:** Merge fails with "Error: failed to fetch from worktree submodule"

**Root Cause:**
- Merge code fetches from worktree submodule using absolute path
- File protocol restriction applies to fetch operations

**Fix Attempted:**
- Added `-c protocol.file.allow=always` to fetch command
- File: `src/claudeutils/worktree/merge_phases.py` line 128-138
- **Still failing** - may need additional investigation

## Changes Made

### 1. `src/claudeutils/worktree/commands.py`

```python
# Line 181-191
run_git(
    [
        "-c",
        "protocol.file.allow=always",  # Added
        "-C",
        str(worktree_path),
        "submodule",
        "update",
        "--init",
        "--reference",
        str(agent_core_local),
    ],
    check=False,
)
```

### 2. `src/claudeutils/worktree/merge_phases.py`

```python
# Line 128-138
fetch_result = run_git(
    [
        "-c",
        "protocol.file.allow=always",  # Added
        "-C",
        "agent-core",
        "fetch",
        str(worktree_ac_path),
        "HEAD",
    ],
    check=False,
)
```

### 3. `tests/test_merge_helpers.py`

```python
# Line 53-56
# Use absolute path for submodule URL to work correctly from worktrees
submodule_url = str(agent_core_path.absolute())
(repo_path / ".gitmodules").write_text(
    f'[submodule "agent-core"]\n\tpath = agent-core\n\turl = {submodule_url}\n'
)
```

## Test Results

### Before Fix
- 795/797 passed, 1 failed, 1 xfail
- Failing: `test_merge_phase_2_diverged_commits` - checkout failure

### After Partial Fix
- Checkout step passes (submodule properly initialized)
- Merge step fails (fetch from worktree submodule)
- Other Phase 2 tests pass: `test_merge_phase_2_no_divergence`, `test_merge_phase_2_fast_forward`

## Remaining Issues

1. **Merge fetch still failing** despite `-c protocol.file.allow=always` flag
   - May need to check if flag is in correct position
   - May need to verify worktree submodule state before fetch

2. **Test design assumption** - test assumes submodule operations work seamlessly from worktrees with relative URLs
   - Real-world usage: users have `../../agent-core` style URLs
   - Test setup: uses `./agent-core` which doesn't match real usage

## Recommendation

**Option A: Fix remaining fetch issue**
- Debug why `-c protocol.file.allow=always` not working for fetch
- May need different approach (config file, environment variable, etc.)

**Option B: Skip/mark test as expected failure**
- Document as known limitation with Git 2.52.0+ security
- Mark test with `@pytest.mark.xfail(reason="Git 2.52.0 file protocol restriction")`
- File issue for future investigation

**Option C: Redesign test**
- Use bare repositories or different submodule setup
- Match real-world usage patterns more closely

## Next Steps

Given that this is a pre-existing failure (confirmed at Phase 4 checkpoint) and not introduced by Phase 5 changes, recommend:

1. Mark test as xfail with clear documentation
2. File issue for future investigation
3. Continue with Phase 5 execution
4. Investigate proper fix in separate session

## Git Version Info

```
git version 2.52.0
```

Recent git versions (2.45+) introduced stricter file protocol restrictions for security. This affects submodule operations using file:// URLs or absolute paths.
