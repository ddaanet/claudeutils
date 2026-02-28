# Recall CLI Integration — Implementation Outline

## Module Structure

New package `src/claudeutils/recall_cli/` — separate from existing `recall/` (effectiveness analysis). Different domain, different consumers.

```
src/claudeutils/recall_cli/
├── __init__.py          # empty
├── cli.py               # Click group + check/resolve/diff subcommands
└── artifact.py          # Entry Keys section parsing (shared by check + resolve)
```

**Why not add to `recall/`:** The existing `recall/` package is effectiveness analysis (tool call extraction, topic detection, relevance scoring). `_recall` is artifact validation and resolution — different purpose, different consumers (LLM agents vs humans). Mixing them conflates two domains that share only the word "recall."

**Why a package, not single file:** `artifact.py` parsing is shared by `check` and `resolve`. Extracting it enables unit testing the parser independently from CLI wiring.

## Key Components

### `artifact.py` — Artifact Parser

Shared parser for `## Entry Keys` terminal section (C-4).

```
parse_entry_keys_section(content: str) -> list[str] | None
```

- Returns `None` if `## Entry Keys` heading not found (distinct from empty list = section exists but no entries)
- Returns list of raw entry lines (post-filtering: blank lines, comment lines removed)
- Does NOT strip annotations or detect operators — that's the caller's concern (check only needs count, resolve needs full processing)

```
parse_trigger(entry_line: str) -> str
```

- Strips annotation on first ` — ` separator
- Detects operator prefix: starts with "when"/"how" → use as-is, else prepend "when"
- Returns trigger string ready for `resolver.resolve()`

**Separation rationale:** `check` needs "are there entries?" (calls `parse_entry_keys_section`, checks length). `resolve` needs "what are the triggers?" (calls both functions). Keeping raw parsing separate from trigger normalization avoids `check` paying for normalization it doesn't need.

### `cli.py` — Click Group + Subcommands

**Group:** `@click.group(name="_recall")` — hidden by underscore convention.

**`_fail` pattern:** Local `_fail(msg, code=1) -> Never` — same 3-line pattern as `worktree/cli.py:38`. LLM-native: `click.echo(msg)` to stdout, `raise SystemExit(code)`. Not extracted to shared utils — `_fail` is private convention, not shared API.

**Project root:** `Path(os.getenv("CLAUDE_PROJECT_DIR", "."))` per C-2.

**`check` subcommand:**
- Derives artifact path: `project_root / "plans" / job / "recall-artifact.md"`
- Reads file, calls `parse_entry_keys_section(content)`
- Three failure modes: file missing, section missing (`None`), no entries (empty list)
- Exit 0 on valid (≥1 entry, including null entry)

**`resolve` subcommand:**
- Mode detection: `Path(args[0]).is_file()` → artifact mode, else argument mode
- Artifact mode: read file, `parse_entry_keys_section` + `parse_trigger` per entry
- Argument mode: each arg through `parse_trigger`
- Resolve loop: call `when.resolver.resolve(trigger, index_path, decisions_dir)` per trigger
- Null handling: triggers normalizing to "null" (after operator strip) pass through to resolver (silent exit, recall-null delivered)
- Dedup: `seen: set[str]` on resolved content strings (resolver is deterministic)
- Output: `---`-separated resolved content to stdout
- Exit code: artifact mode → exit 1 if any non-null fails; argument mode → exit 1 only if zero resolve

**`diff` subcommand:**
- Derives artifact path from project root + job name
- `git rev-parse --is-inside-work-tree` guard
- Artifact mtime via `os.path.getmtime()`, formatted for `git log --since`
- `git log --since=<mtime> --name-only --pretty=format: -- plans/<job>/`
- Filter: exclude artifact path, dedup, sort
- Always exit 0 (empty = no changes), exit 1 only for precondition failures (no git, no artifact)

### Registration

`cli.py` (main): `from claudeutils.recall_cli.cli import recall_cmd` → `cli.add_command(recall_cmd)`

No conflict with existing `recall` command — different group name (`_recall` vs `recall`).

## Test Organization

```
tests/
├── test_recall_artifact.py       # artifact.py unit tests (parser)
├── test_recall_cli_check.py      # check subcommand via CliRunner
├── test_recall_cli_resolve.py    # resolve subcommand, both modes
└── test_recall_cli_diff.py       # diff subcommand (real git repos, tmp_path)
```

**Test strategy per subcommand:**
- `check`: isolated filesystem (CliRunner), artifact fixtures with varying validity
- `resolve` artifact mode: mock `when.resolver.resolve()` for unit tests, real resolver for integration
- `resolve` argument mode: same mock/real split
- `diff`: real git repos in `tmp_path` (per "When Preferring E2E Over Mocked Subprocess" — git with tmp_path is fast, mocks are implementation-coupled)

## Scope Boundaries

**IN:** `_recall` group with check/resolve/diff, artifact parser, tests, CLI registration, prototype deletion (Q-1), referencing doc updates

**OUT:** `_recall generate`, resolution caching, replacing `when` CLI or `when-resolve.py`, recall effectiveness analysis changes, hook/gate changes

## Open Questions

None — all structural decisions resolved above.
