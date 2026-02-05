# Test Strategy

Testing conventions and patterns for claudeutils codebase.

## .Test Organization

### Test Module Split Strategy

**Decision:** Split test files to mirror source module structure + separate CLI test modules by subcommand

**Structure:**
```
tests/
├── test_models.py          # Pydantic validation
├── test_paths.py           # Path encoding
├── test_parsing.py         # Content extraction, filtering
├── test_discovery.py       # Session listing
├── test_agent_files.py     # Agent file discovery
├── test_extraction.py      # Recursive extraction
├── test_cli_list.py        # List command
├── test_cli_extract_basic.py   # Extract command, session matching
└── test_cli_extract_output.py  # JSON output, integration
```

**Rationale:** Maintain 400-line limit while keeping related tests together

## .Mock Patching

### Mock Patching Pattern

**Decision:** Patch where object is **used**, not where it's **defined**

**Example:**
```python
# If module A defines foo(), and module B imports and uses it:
# Patch at usage location:
monkeypatch.setattr("pkg.b.foo", mock)  # ✅ Correct
monkeypatch.setattr("pkg.a.foo", mock)  # ❌ Won't work
```

**Rationale:** Python imports create references in the importing module's namespace

**Applied:** Mock patches target `claudeutils.discovery.*` and `claudeutils.extraction.*` for functions used in those modules

## .TDD Approach

### Testing Strategy for Markdown Cleanup

**TDD approach:**
- Red test → minimal code → green test
- Each feature: 4-6 test cycles
- Integration tests verify no conflicts
- Edge cases documented and tested

**Test coverage:**
- Valid patterns (should convert)
- Invalid patterns (should skip or error)
- Edge cases (empty blocks, unclosed fences, etc.)
- Integration (multiple fixes together)

### Success Metrics

- All new tests pass
- All existing tests pass (no regressions)
- Code follows existing patterns
- Clear error messages for invalid input
- Documentation complete and accurate

## TDD RED Phase: Behavioral Verification

**TDD RED behavioral:**

**Decision Date:** 2026-01-31

**Decision:** RED phase tests must verify behavior, not just structure.

**Anti-pattern:** Tests checking only structure (AttributeError, exit_code == 0, key existence)

**Problem:** Minimal GREEN implementations pass structure tests without implementing actual functionality.

**Examples of structural tests (insufficient):**
- `assert result.exit_code == 0` → implementation returns 0 with hardcoded data
- `assert "KEY" in dict` → implementation returns `{"KEY": ""}` (empty string)
- Test checks class/method exists → implementation returns stub that does nothing

**Correct pattern:** RED tests verify behavior with mocking/fixtures
- Mock file I/O and verify reads/writes to actual paths
- Mock external calls (subprocess, API) and verify correct invocation
- Assert on output content, not just success/failure
- Use fixtures (tmp_path) to simulate real filesystem state

**Rationale:** TDD principle "write minimal code to pass test" works only if test requires real behavior.

**Example:** Test should mock ~/.claude/account-mode file and verify CLI reads it, not just check exit code.

**Impact:** Prevents trivial implementations that satisfy tests without implementing functionality.

## TDD: Presentation vs Behavior

**Decision Date:** 2026-01-31

**Decision:** Test behavior, defer presentation quality to vet checkpoints.

**Anti-pattern:** Writing RED-GREEN cycles for help text wording, error message phrasing.

**Rationale:** Presentation tests are brittle and self-evident.

**Impact:** Focus TDD cycles on functionality, handle presentation in batch during vet checkpoints.

## TDD Integration Test Gap

**Decision Date:** 2026-02-05

**Decision:** Add integration test requirement at phase boundaries for CLI/composition tasks.

**Anti-pattern:** Unit tests verify function calls (mock.assert_called) but not behavioral outcomes.

**Root cause:** Tests checked execution (function invoked) not integration (results consumed).

**Correct pattern:** For CLI/composition tasks, assert on critical content presence in output, not just structure.

**Example:** Cycle 5.4 test verified two-line output exists but didn't check usage data present.

**Implementation:** xfail integration test at phase start, pass at phase end.

**Impact:** Ensures behavioral outcomes are tested, not just execution paths.

## Conformance Validation for Migrations

**Decision Date:** 2026-02-05

**Decision:** Compare Python implementation against original shell spec at completion.

**Pattern:** Delegated to exploration agent, writes detailed conformance matrix.

**Benefits:** Catches presentation/visual gaps that unit tests miss.

**Example:** statusline-wiring found all 5 requirements met but missing emojis/bars/colors.

**Impact:** Behavioral equivalence verification beyond functional testing.
