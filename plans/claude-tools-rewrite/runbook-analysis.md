# Runbook Analysis: Why Deliverables Are Not Functional

**Date**: 2026-01-30
**Issue**: All 37 TDD cycles complete, tests pass, but features don't work

## Problems Identified

### 1. Metadata Mismatch

**Runbook line 18:**
```
**Total Steps**: 45 cycles across 3 phases
```

**Reality:** Only 37 cycles defined (1.1-1.13, 2.1-2.9, 3.1-3.15)

**Missing:** 8 cycles (likely integration/wiring cycles)

---

### 2. Tests Are Too Weak - Don't Validate Actual Functionality

The runbook GREEN phases describe full implementations, but the tests only verify structure/existence.

#### Example 1: account status (Cycle 3.9)

**Runbook says (line 1676):**
> "Create Click command group 'account' with 'status' command **reading state** and calling validate_consistency()"

**Test actually checks:**
```python
def test_account_status() -> None:
    """Test that account status command returns account state."""
    runner = CliRunner()
    result = runner.invoke(cli, ["account", "status"])
    # The command should exist and return exit code 0
    assert result.exit_code == 0
```

**What's missing:**
- ❌ No verification that it reads ~/.claude/account-mode file
- ❌ No verification that it detects OAuth in keychain
- ❌ No verification that it calls validate_consistency()
- ❌ No verification of actual output content

**Actual implementation (src/claudeutils/account/cli.py:48-65):**
```python
def status() -> None:
    """Display current account status."""
    # Minimal implementation: create a simple state and display it
    state = AccountState(
        mode="plan",
        provider="anthropic",
        oauth_in_keychain=True,
        api_in_claude_env=False,
        has_api_key_helper=False,
        litellm_proxy_running=False,
    )
    issues = state.validate_consistency()
    click.echo(f"Mode: {state.mode}")
    click.echo(f"Provider: {state.provider}")
    # ...
```

**Problem:** HARDCODED state! Doesn't read any files. But test passes because it only checks exit code.

---

#### Example 2: Providers return empty strings (Cycles 1.9, 1.10)

**Runbook Cycle 1.9 says:**
> "OpenRouterProvider.claude_env_vars() returns both API key and base URL"

**Test checks:**
```python
def test_openrouter_provider_env_vars() -> None:
    provider = OpenRouterProvider()
    env_vars = provider.claude_env_vars()

    # Verify both OPENROUTER_API_KEY and ANTHROPIC_BASE_URL are present
    assert "OPENROUTER_API_KEY" in env_vars
    assert "ANTHROPIC_BASE_URL" in env_vars
```

**What's missing:**
- ❌ No check that values are non-empty
- ❌ No check that values are actually retrieved from keychain/config

**Actual implementation:**
```python
def claude_env_vars(self) -> dict[str, str]:
    """Get environment variables needed for this provider."""
    return {
        "OPENROUTER_API_KEY": "",  # EMPTY!
        "ANTHROPIC_BASE_URL": "",  # EMPTY!
    }
```

**Test passes** because it only checks key existence, not values!

---

#### Example 3: statusline just prints "OK" (Cycle 3.15)

**Runbook says:**
> "Create Click command 'statusline' reading stdin JSON"

**Test checks:**
```python
def test_statusline_reads_stdin() -> None:
    runner = CliRunner()
    result = runner.invoke(cli, ["statusline"], input='{"test": "data"}')
    assert result.exit_code == 0
```

**Actual implementation:**
```python
def statusline() -> None:
    """Display statusline reading JSON from stdin."""
    input_data = sys.stdin.read()
    if input_data.strip():
        json.loads(input_data)  # Validate JSON
    click.echo("OK")  # Just prints OK!
```

**Doesn't actually format or display a statusline!** But test passes.

---

### 3. Missing Integration Cycles

The runbook ends at Cycle 3.15 with basic CLI structure. **Missing cycles for:**

1. **Account status reading real state** - Read ~/.claude/ files, detect keychain entries
2. **Account plan/api integration** - Wire up providers, generate real claude-env
3. **Provider credential retrieval** - Connect keychain to providers
4. **Statusline formatting integration** - Use StatuslineFormatter to format output
5. **Model list filtering** - Actually filter by tier (load_litellm_config implemented but not wired to CLI)
6. **Usage cache integration** - Wire UsageCache to actual API calls
7. **End-to-end testing** - Integration tests with real ~/.claude/ files
8. **Error handling** - Keychain not found, config missing, etc.

**These 8 missing cycles explain the metadata mismatch (45 - 37 = 8)**

---

## Root Cause

**TDD cycles tested STRUCTURE, not BEHAVIOR:**

- ✅ "Does the command exist?"
- ✅ "Does it return exit code 0?"
- ✅ "Does the class have this method?"
- ❌ "Does it read actual files?"
- ❌ "Does it return correct values?"
- ❌ "Does it integrate with other components?"

**Why this happened:**

The runbook GREEN phase descriptions say what SHOULD be implemented, but the RED phase tests only check minimal structure. Since TDD follows "write minimal code to pass the test," implementers wrote stubs that pass exit-code checks but don't do real work.

---

## What Should Have Happened

### Example: Proper account status test (Cycle 3.9)

**RED Phase test should be:**
```python
def test_account_status(tmp_path: Path) -> None:
    """Test that account status reads state files and validates."""
    # Setup: create ~/.claude/ files
    claude_dir = tmp_path / ".claude"
    claude_dir.mkdir()
    (claude_dir / "account-mode").write_text("plan")
    (claude_dir / "account-provider").write_text("anthropic")

    # Mock keychain to return OAuth present
    with patch("pathlib.Path.home", return_value=tmp_path):
        with patch("claudeutils.account.Keychain.find", return_value="oauth-token"):
            runner = CliRunner()
            result = runner.invoke(cli, ["account", "status"])

    # Verify reads actual state (not hardcoded)
    assert result.exit_code == 0
    assert "Mode: plan" in result.output
    assert "Provider: anthropic" in result.output
    assert "OAuth: present" in result.output or "No issues found" in result.output
```

**This would FORCE the implementation to:**
1. Read ~/.claude/account-mode file
2. Read ~/.claude/account-provider file
3. Check keychain for OAuth
4. Display actual state (not hardcoded)

---

## Recommendations

### Option 1: Write Missing Integration Cycles

Create 8 additional cycles (3.16-3.23) that:
1. Wire up real file reading for account status
2. Connect providers to keychain
3. Integrate StatuslineFormatter with CLI
4. Add error handling
5. Integration tests

### Option 2: Fix Existing Cycles

Go back and strengthen the tests in Cycles 3.9-3.15:
- Add assertions for actual behavior, not just exit codes
- Add file mocking/setup in tests
- Verify output content, not just success

### Option 3: Manual Implementation

Since all structure is in place, manually implement the missing wiring:
1. Update account status to read ~/.claude/ files
2. Update providers to fetch from keychain/config
3. Update statusline to use StatuslineFormatter
4. Add integration tests

---

## Impact

**Current state:**
- ✅ All classes and methods exist
- ✅ All tests pass
- ✅ Type checking passes
- ✅ Code is well-structured
- ❌ **Features don't actually work**

**To complete:**
- Need ~8 more cycles OR manual implementation
- Need stronger integration tests
- Need to wire up existing components

---

## Lesson Learned

**When writing TDD runbooks:**
1. RED phase tests must verify BEHAVIOR, not just structure
2. Tests should force real integration, not stubs
3. Use mocking/fixtures to test real file I/O, not just exit codes
4. Metadata (cycle count) must match actual cycles defined
