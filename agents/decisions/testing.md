# Test Strategy

Testing conventions and patterns for claudeutils codebase.

## Test Organization

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

## Mock Patching

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

## TDD Approach

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
