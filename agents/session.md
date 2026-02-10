# Session: Worktree — Fix preprocessor idempotency

**Status:** Focused worktree for parallel execution.

## Pending Tasks

- [ ] **Fix preprocessor idempotency for inline backticks** — Route through `/design`, `/plan-adhoc`, or `/plan-tdd` as appropriate
  - Failing test: `tests/test_markdown_fixtures.py::test_preprocessor_idempotency[02-inline-backticks]`
  - Bug: Triple/quadruple backtick code spans gain extra `` `` `` delimiters on re-processing
  - Diff at index 25: re-processed output wraps backtick sequences with additional delimiters
  - Preprocessor source: `src/claudeutils/markdown/` (check preprocessor module)
  - Corpus defines correct behavior — the fixture is correct, the preprocessor needs fixing

## Blockers / Gotchas

- Corpus defines correct behavior (learning) — do NOT modify fixtures to make tests pass
- Pipeline idempotency principle: `(preprocessor)²` must produce same result as single pass

## Reference Files

- `tests/test_markdown_fixtures.py` — Test file with idempotency parametrized tests
- `tests/fixtures/markdown/02-inline-backticks/` — Fixture directory (input + expected)
