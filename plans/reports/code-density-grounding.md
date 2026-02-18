# Code Density and Exception Handling — Grounded Reference

Date: 2026-02-18

## Research Foundation

**Internal branch:** Opus analysis of `src/claudeutils/worktree/` module — 19 raw subprocess calls, 18 SystemExit raises, 6 exception-as-control-flow sites. Full applicability audit across cli.py, merge.py, utils.py.

**External branch:** EAFP/LBYL principles (Real Python, Python glossary, mathspp), subprocess best practices (Python docs, sqlpey), Click exception hierarchy (Click docs), Black formatting mechanics (Black docs, trailing comma spec).

**User feedback:** Annotated `src/claudeutils/cli.py` with 12 anti-pattern markers across exception handling, Black density, and architecture.

## Adapted Methodology

### Principle 1: Git State Queries Return Booleans

**Problem:** Two inconsistent idioms for "does branch exist?" — raw subprocess LBYL (5-6 lines under Black) and EAFP try/except (5 lines, treats expected condition as exceptional).

**Grounding:** EAFP is idiomatic for IO operations where failure is uncommon (Real Python, Python glossary). But "branch doesn't exist" in worktree operations is a *normal program state*, not an exceptional event (charlax/antipatterns: "Exception handling is for unexpected or exceptional events"). Neither EAFP nor verbose LBYL is correct here.

**Solution:** `_git_ok(*args) -> bool` — boolean wrapper returning `returncode == 0`. Covers 13 of 15 raw subprocess sites. Two outliers needing stderr remain as raw calls.

**Evidence:** Internal audit found `_git()` already eliminates 20+ raw stdout calls. `_git_ok()` eliminates the remaining 13 returncode-only calls. Together they eliminate all raw `subprocess.run(["git", ...])` from cli.py and merge.py.

### Principle 2: Error Exits Are Single Calls

**Problem:** 18 instances of `click.echo(msg, err=True)` + `raise SystemExit(N)` across worktree module. 3-6 lines each under Black.

**Grounding:** Click's own exception hierarchy (`ClickException`, `UsageError`) consolidates display+exit into a single raise (Click docs). But Click's built-in exceptions have hardcoded exit codes (UsageError→2, Abort→1) and require `@click.pass_context`. A module-level helper is more flexible.

**Solution:** `_fail(msg, code=1) -> Never` in utils.py. Preserves exit code semantics (1=error, 2=safety gate). Type annotation `Never` informs type checkers that control flow terminates.

**Alternative considered:** Click's `ClickException` subclass with custom exit code. Rejected: adds class hierarchy overhead for what is a 3-line function. The project's exit code semantics (1 vs 2) don't map to Click's exception types.

### Principle 3: Black Expansion Signals Abstraction Need

**Problem:** Raw `subprocess.run()` with keyword args expands to 5-6 lines under Black. The `_git()` helper collapses these to 1 line, but callers bypass it when they need returncode instead of stdout.

**Grounding:** Black's formatting algorithm tries to fit calls on one line, falling back to one-arg-per-line (Black docs). Keyword arguments expand aggressively. Wrapper functions that encode default kwargs as policy reduce expansion (Black trailing comma spec).

**Generalized rule:** When a call site consistently takes 5+ lines after Black formatting, the call has too many parameters for inline use. Extract a helper whose defaults encode the common kwargs.

### Principle 4: Exceptions for Exceptional Events Only

**Problem:** `try: _git("rev-parse"...) except CalledProcessError:` used to check branch existence. `ValueError` raised for expected conditions (no session found, multiple matches).

**Grounding:** Exception handling is for unexpected/exceptional events (charlax/antipatterns, Medium anti-pattern article). If a condition is a normal program state, LBYL or return values are cleaner. Raising `ValueError` for expected conditions allows `except ValueError` to catch legitimate bugs.

**Solution for subprocess:** `_git_ok()` returns boolean instead of raising.
**Solution for domain errors:** Custom exception classes (e.g., `SessionNotFoundError`) instead of `ValueError`. Lint rule about "no hardcoded exception messages" is properly satisfied by custom classes, not circumvented by intermediate `msg` variables.

### Principle 5: Error Handling Layers Don't Overlap

**Problem (from user feedback on cli.py):** Double error handling where exceptions are caught and messages printed at multiple levels — both at the failure site AND at a top-level handler.

**Grounding:** Error handling should follow a single-responsibility model. Failure site: collect context, raise typed exception. Top level: display, exit. When both layers print, you get duplicate output or conflicting messages. The "raise from" chain preserves the causal chain without duplicating display logic.

**Rule:** Context collection at the failure site. Display at the top level. Never both.

## Grounding Quality: Moderate

**Strong grounding:** EAFP/LBYL boundaries, subprocess patterns, Click exception hierarchy, Black expansion mechanics — all from authoritative sources with clear applicability.

**Thin grounding:** The `_git_ok()` pattern is a project-specific synthesis (no external source describes this exact helper design). But it follows directly from the grounded principle that state queries should return booleans when the condition is expected.

**Not grounded (standard practice):** Custom exception classes, `Never` return type, pydantic models vs ad-hoc casting. These are established Python patterns not requiring external validation.

## Sources

- [Real Python — LBYL vs EAFP](https://realpython.com/python-lbyl-vs-eafp/)
- [mathspp — EAFP and LBYL coding styles](https://mathspp.com/blog/pydonts/eafp-and-lbyl-coding-styles)
- [Medium — Exception as Control Flow Anti-Pattern](https://medium.com/@samanwayghatak/exception-as-control-flow-anti-pattern-e3b46b079cdd)
- [charlax/antipatterns — Error Handling](https://github.com/charlax/antipatterns/blob/master/error-handling-antipatterns.md)
- [Python subprocess docs](https://docs.python.org/3/library/subprocess.html)
- [sqlpey — subprocess best practices](https://www.sqlpey.com/python/python-subprocess-best-practices/)
- [Click docs — Exception Handling](https://click.palletsprojects.com/en/stable/exceptions/)
- [Black docs — The Black Code Style](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)
- [Black GitHub Issue #1288 — Magic Trailing Comma](https://github.com/psf/black/issues/1288)
