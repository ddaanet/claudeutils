# Handoff Entry Point

## Current Task: CLI Migration to Click

**Status:** Test suite optimized, ready for migration

**Goal:** Migrate argparse-based CLI to click framework for cleaner code, better maintainability, and improved test harness.

### What's Done

- ✅ **Test suite optimization** - Converted 11 subprocess tests to direct `main()` calls (2.76s → 0.94s, 66% faster)
- ✅ **Performance analysis** - Identified subprocess overhead as primary slowness factor
- ✅ **Smoke test coverage** - Retained 3 subprocess tests to validate entry point
- ✅ **Test quality** - Improved stack traces and debugging experience

### What's Next

**NEXT:** Migrate CLI from argparse to click

Benefits of click migration:
- **Cleaner code:** Reduce `cli.py` from 152 lines of boilerplate to ~60 lines
- **Better testing:** Use `click.testing.CliRunner` for elegant test harness
- **Industry standard:** More maintainable, familiar to Python developers
- **Decorator-based:** More Pythonic than argparse's imperative style

Implementation approach:
1. Install click: `uv add click`
2. Convert `cli.py` to click decorators (command groups, options, arguments)
3. Update tests to use `CliRunner` instead of monkeypatch pattern
4. Run test suite to verify (expect ~0.94s performance maintained)
5. Optional: Consider `rich-click` for pretty help (low priority for pipeline CLI)

Estimated effort: 2-3 hours

Current CLI structure to migrate:
- Main parser with subparsers (list, extract, collect, analyze, rules, tokens, markdown)
- 7 command handlers in `cli.py`
- 1 command handler in `tokens_cli.py`
- Argparse custom help formatting and epilogs

Key files:
- `src/claudeutils/cli.py` - Main CLI entry point (399 lines)
- `src/claudeutils/tokens_cli.py` - Tokens command handler (80 lines)
- `tests/test_cli_*.py` - CLI test suite (58 tests)

---

## Previous Task: Module System Implementation

**Status:** Paused (design complete, ready for Phase 1)

**Goal:** Transform monolithic agent role files into composable module system with semantic sources and generated variants (strong/standard/weak). Target: ≤150 total rules.

### What's Done

- ✅ **Design decisions** - All Opus reviews complete (tier markers, config location, dev workflow)
- ✅ **Module extraction** - 14 semantic sources in `agents/modules/src/*.semantic.md`
- ✅ **Module inventory** - `agents/modules/MODULE_INVENTORY.md`
- ✅ **Directory structure** - `agents/roles/` for configs, `.next.md` pattern for safe development
- ✅ **Implementation plan** - Detailed Phase 1 plan ready for Haiku execution

### What's Next (When Resuming)

**NEXT:** Phase 1.1 - Test expansion quality (Sonnet vs Opus comparison)

Then:
1. **Phase 1.2: Rule Counter** - Build script to count `[RULE:Tn]` markers in module variants
2. **Phase 2: Variant Generator** - Generate variants from semantic sources
3. **Phase 3: Role Composer** - Compose role files from module variants
4. **Phase 7: Testing & Cutover** - A/B test, then atomic rename via `make cutover`

### Key Files to Read

| File                                                       | Purpose                                            |
| ---------------------------------------------------------- | -------------------------------------------------- |
| `plans/prompt-composer/plan-phase1.md`                     | Detailed Phase 1 plan for Haiku (ready to execute) |
| `plans/prompt-composer/plan-outline.md`                    | Full 8-phase implementation plan                   |
| `plans/prompt-composer/opus-review-tiering.md`             | Tier marker design decisions                       |
| `plans/prompt-composer/design-question-config-location.md` | Config location decision (agents/roles/)           |
| `plans/prompt-composer/design.md`                          | Complete design specification                      |
| `agents/modules/MODULE_INVENTORY.md`                       | Summary of 14 extracted modules                    |

---

## Core Context

1. `AGENTS.md` - Project overview, user preferences, role/rule definitions
2. `agents/DESIGN_DECISIONS.md` - Architectural and implementation decisions
3. `agents/TEST_DATA.md` - Data types and sample entries

## Roles (Load at Session Start)

- `agents/role-planning.md` - Design test specifications (opus/sonnet)
- `agents/role-code.md` - TDD implementation (haiku)
- `agents/role-lint.md` - Fix lint/type errors (haiku)
- `agents/role-refactor.md` - Plan refactoring (sonnet)
- `agents/role-execute.md` - Execute planned changes (haiku)
- `agents/role-review.md` - Code review and cleanup (sonnet)
- `agents/role-remember.md` - Update agent documentation (opus)

## Rules (Load Before Action)

- `agents/rules-commit.md` - **Read before any `git commit`**
- `agents/rules-handoff.md` - Read before ending a session

## Quick Reference

See `README.md` for usage examples and development commands.

Run `just dev` to verify all tests pass.
