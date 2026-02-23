# Worktree Error Output — Outline

## Problem

`_worktree` is an LLM-native command group (underscore prefix) but uses stderr for error output. The Bash tool's error envelope duplicates stderr content on non-zero exit — agents see every error message twice. Additionally, `derive_slug` raises unhandled `ValueError`, producing a raw Python traceback instead of a clean message.

## Approach

Align `_worktree` error output with the existing LLM-native convention (cli.md: "When CLI Commands Are LLM-Native"): all output to stdout, exit code as signal, no stderr.

This is already the pattern in `merge.py`, `merge_state.py`, `resolve.py` — only `cli.py` uses `err=True`.

## Key Decisions

1. **All error output to stdout** — Drop `err=True` from all `click.echo()` calls in `cli.py`. Matches the LLM-native decision and eliminates Bash tool duplication.

2. **Catch `derive_slug` ValueError in `new()`** — Convert to clean one-line error with constraint context (allowed chars: `[a-zA-Z0-9 .-]`, max 25 chars). Exit code 2 (validation failure).

3. **Introduce `_fail()` helper** — Per cli.md "When Writing Error Exit Code" decision: consolidate `click.echo()` + `raise SystemExit(N)` into `_fail(msg, code=1) -> Never`. The decision documents this as already planned but `_fail` doesn't exist yet. All 8 `err=True` + `SystemExit` pairs in cli.py become `_fail()` calls.

4. **Warning output stays as `click.echo()` (stdout, no exit)** — Lines 77, 110, 309, 363 are warnings that don't exit. Drop `err=True` but keep as plain `click.echo()`.

## Scope

**IN:**
- `src/claudeutils/worktree/cli.py` — all `err=True` sites (8 error, 4 warning)
- `_fail()` helper (in cli.py or new utils module)
- Catch `derive_slug` ValueError in `new()`
- Tests for new error path

**OUT:**
- `merge.py`, `merge_state.py`, `resolve.py` — already use stdout
- User-facing commands (`analyze`, `rules`, `tokens`) — different convention
- Error message content changes beyond `derive_slug` (existing messages are fine)

## Open Questions

None. All decisions pre-resolved by existing cli.md conventions.
