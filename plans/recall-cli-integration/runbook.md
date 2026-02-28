---
name: recall-cli-integration
model: sonnet
---

# Recall CLI Integration

**Context**: Production `_recall` Click group replacing prototype shell scripts. TDD.
**Design**: `plans/recall-cli-integration/outline.md`
**Requirements**: `plans/recall-cli-integration/requirements.md`
**Status**: Draft
**Created**: 2026-02-28

---

## Common Context

**Requirements (from requirements.md):**
- FR-1: `_recall check <job>` — structural validation of recall artifacts (Entry Keys section with ≥1 entry)
- FR-2: `_recall resolve` — two modes (artifact: strict, exit 1 on any failure; argument: best-effort, exit 0 if ≥1 resolves)
- FR-3: `_recall diff <job>` — files changed since artifact mtime via git log
- FR-4: Click group registration as hidden `_recall` on main CLI
- FR-5: LLM-native output — all stdout, exit codes, facts-only errors

**Scope boundaries:**
- IN: `_recall` group, artifact parser, tests, CLI registration, prototype deletion, doc updates
- OUT: `_recall generate`, resolution caching, replacing `when` CLI, hook/gate changes

**Key Constraints:**
- C-1: Delegate to `claudeutils.when.resolver.resolve()` — no independent resolution
- C-2: Project root via `CLAUDE_PROJECT_DIR` with `.` fallback
- C-3: No hardcoded `agents/memory-index.md` or `agents/decisions/` paths
- C-4: `## Entry Keys` is terminal section (parse to EOF)

**Recall (from artifact):**
- `_fail(msg, code=1) -> Never` pattern — consolidates display+exit, LLM-native (stdout not stderr). Define locally in `_recall/cli.py`.
- CliRunner for all CLI tests — in-process, isolated filesystem. No subprocess invocation.
- RED assertions must verify behavior, not structure — mock resolver and verify correct invocation, assert output content not just exit code.
- E2E with real git repos for `diff` subcommand — `tmp_path` fixtures, mocks only for error injection.
- GREEN verification is `just check && just test` — lint is a required gate.
- Error handling layering — context at failure site, display at top level.
- Boolean returns for expected program state checks — not exceptions.

**Project Paths:**
- Source: `src/claudeutils/recall_cli/` (new package)
- Tests: `tests/test_recall_artifact.py`, `tests/test_recall_cli_check.py`, `tests/test_recall_cli_resolve.py`, `tests/test_recall_cli_diff.py`
- Prototypes: `agent-core/bin/recall-{check,resolve,diff}.sh` (delete after CLI ships)
- Registration: `src/claudeutils/cli.py` (add_command)
- Existing resolver: `src/claudeutils/when/resolver.py` — `resolve(query, index_path, decisions_dir)`
- Existing when CLI: `src/claudeutils/when/cli.py` — reference for operator stripping, null handling, dedup pattern

---

### Phase 1: Artifact parser (type: tdd)

Shared parsing for `## Entry Keys` terminal section. Used by both `check` and `resolve`.

## Cycle 1.1: Parse Entry Keys section from artifact content

**Prerequisite:** Read `plans/recall-cli-integration/outline.md` — understand `artifact.py` component design. Read `agent-core/bin/recall-resolve.sh` — understand prototype parsing behavior (annotation stripping, operator detection, blank/comment skipping).

**RED Phase:**

**Test:** `test_parse_entry_keys_section_returns_entries` in `tests/test_recall_artifact.py`
**Assertions:**
- Given content with `## Entry Keys` heading followed by entry lines, returns list of raw entry strings
- Given content `"# Title\n\nPreamble\n\n## Entry Keys\n\nwhen foo — annotation\nhow bar\n"`, returns `["when foo — annotation", "how bar"]`
- Blank lines within section are excluded from result
- Content above `## Entry Keys` is not included

**Expected failure:** ImportError — `recall_cli.artifact` module doesn't exist

**Why it fails:** Package and module not yet created

**Verify RED:** `pytest tests/test_recall_artifact.py::test_parse_entry_keys_section_returns_entries -v`

**GREEN Phase:**

**Implementation:** Create `src/claudeutils/recall_cli/` package with `__init__.py` and `artifact.py`.

**Behavior:**
- `parse_entry_keys_section(content: str) -> list[str] | None` reads from `## Entry Keys` heading to EOF
- Returns `None` if heading not found
- Returns list of non-blank lines after the heading
- Skips blank lines

**Approach:** Split content on newlines, scan for `## Entry Keys` line, collect remaining non-blank lines.

**Changes:**
- File: `src/claudeutils/recall_cli/__init__.py`
  Action: Create empty init file
- File: `src/claudeutils/recall_cli/artifact.py`
  Action: Implement `parse_entry_keys_section`

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_artifact.py -v`
**Verify no regression:** `just test`

---

## Cycle 1.2: Section missing and comment line filtering

**RED Phase:**

**Test:** `test_parse_entry_keys_section_missing` and `test_parse_entry_keys_skips_comments` in `tests/test_recall_artifact.py`
**Assertions:**
- Content without `## Entry Keys` heading returns `None`
- Content with heading but only blank lines returns `[]` (empty list, not None)
- Lines starting with `#` within the section (comment lines) are excluded
- Entry `"# this is a comment"` is filtered, entry `"when foo"` is kept

**Expected failure:** Comment filtering not implemented (comments returned as entries)

**Why it fails:** Cycle 1.1 doesn't filter comment lines

**Verify RED:** `pytest tests/test_recall_artifact.py::test_parse_entry_keys_skips_comments -v`

**GREEN Phase:**

**Implementation:** Add comment line filtering to `parse_entry_keys_section`.

**Behavior:**
- Lines starting with `#` (after stripping) within the Entry Keys section are skipped
- Empty section (only blanks/comments after heading) returns `[]`

**Changes:**
- File: `src/claudeutils/recall_cli/artifact.py`
  Action: Add `line.startswith("#")` filter in the collection loop

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_artifact.py -v`
**Verify no regression:** `just test`

---

## Cycle 1.3: Parse trigger from entry line

**RED Phase:**

**Test:** `test_parse_trigger_strips_annotation` and `test_parse_trigger_detects_operator` in `tests/test_recall_artifact.py`
**Assertions:**
- `parse_trigger("when foo — some annotation")` returns `"when foo"`
- `parse_trigger("how bar — another note")` returns `"how bar"`
- `parse_trigger("bare trigger — note")` returns `"when bare trigger"` (prepends "when")
- `parse_trigger("when already prefixed")` returns `"when already prefixed"` (no change)
- `parse_trigger("how to do something")` returns `"how to do something"` (kept as-is)
- `parse_trigger("no annotation")` returns `"when no annotation"` (bare, no dash)

**Expected failure:** ImportError or AttributeError — `parse_trigger` doesn't exist

**Why it fails:** Function not yet implemented

**Verify RED:** `pytest tests/test_recall_artifact.py::test_parse_trigger_strips_annotation -v`

**GREEN Phase:**

**Implementation:** Add `parse_trigger(entry_line: str) -> str` to `artifact.py`.

**Behavior:**
- Strips annotation: split on first ` — ` (em dash with spaces), take left side, strip trailing whitespace
- Detects operator: if first word (lowercased) is "when" or "how", return as-is; else prepend "when "

**Approach:** String split on ` — `, then word-check first token against `{"when", "how"}`.

**Changes:**
- File: `src/claudeutils/recall_cli/artifact.py`
  Action: Add `parse_trigger` function

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_artifact.py -v`
**Verify no regression:** `just test`

---

### Phase 2: Check subcommand (type: tdd)

`_recall check <job>` — structural validation of recall artifacts.

## Cycle 2.1: Check succeeds on valid artifact

**Prerequisite:** Read `src/claudeutils/worktree/cli.py:38-41` — understand `_fail` pattern. Read `src/claudeutils/cli.py:144-150` — understand group registration.

**RED Phase:**

**Test:** `test_check_valid_artifact` in `tests/test_recall_cli_check.py`
**Assertions:**
- CliRunner invokes `cli` with `["_recall", "check", "test-job"]`
- With `plans/test-job/recall-artifact.md` containing valid Entry Keys section (≥1 entry), exit code is 0
- Use CliRunner isolated filesystem to create the artifact file

**Expected failure:** UsageError — `_recall` group not registered on CLI

**Why it fails:** Click group and subcommand not yet created

**Verify RED:** `pytest tests/test_recall_cli_check.py::test_check_valid_artifact -v`

**GREEN Phase:**

**Implementation:** Create `_recall` Click group in `recall_cli/cli.py`, register on main CLI, implement `check` subcommand.

**Behavior:**
- Click group `@click.group(name="_recall")`
- `check` subcommand takes `job` argument
- Derives artifact path from `CLAUDE_PROJECT_DIR` (or `.`) + `plans/<job>/recall-artifact.md`
- Reads file, calls `parse_entry_keys_section`, validates ≥1 entry
- Exit 0 on valid

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Create Click group and `check` subcommand with `_fail` helper
- File: `src/claudeutils/cli.py`
  Action: Import and register `recall_cmd` via `add_command`

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_check.py -v`
**Verify no regression:** `just test`

---

## Cycle 2.2: Check failure modes

**RED Phase:**

**Test:** `test_check_missing_artifact`, `test_check_no_entry_keys_section`, `test_check_empty_section` in `tests/test_recall_cli_check.py`
**Assertions:**
- Missing file: exit code 1, output contains `"recall-artifact.md missing for test-job"`
- No Entry Keys section: exit code 1, output contains `"recall-artifact.md has no Entry Keys section for test-job"`
- Empty section (heading present, no entries): exit code 1, output contains `"recall-artifact.md has no entries for test-job"`
- All error messages to stdout (not stderr) — FR-5

**Expected failure:** Check always exits 0 (no error handling yet)

**Why it fails:** Cycle 2.1 only implemented success path

**Verify RED:** `pytest tests/test_recall_cli_check.py::test_check_missing_artifact -v`

**GREEN Phase:**

**Implementation:** Add error handling to `check` subcommand.

**Behavior:**
- File missing: `_fail("recall-artifact.md missing for <job>")`
- Section missing (`parse_entry_keys_section` returns `None`): `_fail("recall-artifact.md has no Entry Keys section for <job>")`
- Empty entries (returns `[]`): `_fail("recall-artifact.md has no entries for <job>")`

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Add conditional checks after file read and parse calls

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_check.py -v`
**Verify no regression:** `just test`

---

## Cycle 2.3: Check accepts null entry as valid

**RED Phase:**

**Test:** `test_check_null_entry_valid` in `tests/test_recall_cli_check.py`
**Assertions:**
- Artifact with only `"null — no relevant entries found"` in Entry Keys section: exit code 0
- Null entry counts as a parseable entry (≥1 entry satisfied)

**Expected failure:** Depends on implementation — may already pass if null is treated as any other line. If RED passes, verify assertion would catch the defect (vacuous assertion check).

**Why it fails:** Null handling not explicitly tested

**Verify RED:** `pytest tests/test_recall_cli_check.py::test_check_null_entry_valid -v`

**GREEN Phase:**

**Implementation:** Verify null entry handling (may be a no-op if parser already treats null as a regular entry line).

**Behavior:**
- `"null — no relevant entries found"` is a non-blank, non-comment line → included in parsed entries → count ≥1 → valid

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py` or no changes needed
  Action: Verify behavior, add explicit comment if no code change needed

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_check.py -v`
**Verify no regression:** `just test`

---

### Phase 3: Resolve subcommand (type: tdd)

`_recall resolve` — two-mode resolution with different error semantics.

## Cycle 3.1: Resolve artifact mode — happy path

**Prerequisite:** Read `src/claudeutils/when/cli.py:38-60` — understand `_resolve_queries` pattern (resolve loop, dedup, error collection). Read `src/claudeutils/when/resolver.py:13-28` — understand `resolve()` signature.

**RED Phase:**

**Test:** `test_resolve_artifact_mode_happy_path` in `tests/test_recall_cli_resolve.py`
**Assertions:**
- CliRunner invokes `["_recall", "resolve", "<artifact-path>"]` where artifact-path is a real file in isolated filesystem
- Artifact contains two entries in Entry Keys section
- Mock `when.resolver.resolve` to return distinct content for each trigger
- Output contains both resolved contents separated by `---`
- Exit code 0
- `resolve` called with correct bare trigger strings (operator stripped by `parse_trigger`)

**Expected failure:** `resolve` subcommand doesn't exist

**Why it fails:** Only `check` implemented so far

**Verify RED:** `pytest tests/test_recall_cli_resolve.py::test_resolve_artifact_mode_happy_path -v`

**GREEN Phase:**

**Implementation:** Add `resolve` subcommand to `_recall` group.

**Behavior:**
- Takes variadic arguments (`nargs=-1`)
- Mode detection: `Path(args[0]).is_file()` → artifact mode
- Artifact mode: read file, parse Entry Keys section, `parse_trigger` each entry
- Call `when.resolver.resolve(trigger_query, index_path, decisions_dir)` per trigger
- `trigger_query` is the bare query (operator stripped by the `when` resolver's own `_strip_operator` — pass the full "when X" string, let resolver handle it). Actually: `resolve()` takes bare query, and internally the `_resolve_trigger` handles "to " prefix stripping. The `_recall` should strip operator prefix before calling, matching `when/cli.py` pattern.
- Collect results, dedup on content string, join with `\n---\n`
- Exit 0

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Add `resolve` subcommand with artifact mode implementation

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_resolve.py -v`
**Verify no regression:** `just test`

---

## Cycle 3.2: Resolve argument mode — happy path

**RED Phase:**

**Test:** `test_resolve_argument_mode_happy_path` in `tests/test_recall_cli_resolve.py`
**Assertions:**
- CliRunner invokes `["_recall", "resolve", "when writing mock tests", "how encode paths"]`
- First arg is NOT a file path → argument mode
- Mock `when.resolver.resolve` returns content per trigger
- Output contains both resolved contents separated by `---`
- Exit code 0
- Operator prefix stripped before calling resolver

**Expected failure:** Argument mode not implemented (all args treated as file path)

**Why it fails:** Mode detection falls through to artifact mode, file not found

**Verify RED:** `pytest tests/test_recall_cli_resolve.py::test_resolve_argument_mode_happy_path -v`

**GREEN Phase:**

**Implementation:** Add argument mode branch to `resolve` subcommand.

**Behavior:**
- First arg not a file → argument mode
- Each arg through `parse_trigger` (strips operator, annotation irrelevant for args)
- Same resolve loop, dedup, output as artifact mode

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Add argument mode branch in resolve subcommand

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_resolve.py -v`
**Verify no regression:** `just test`

---

## Cycle 3.3: Resolve artifact mode — strict error semantics

**RED Phase:**

**Test:** `test_resolve_artifact_mode_any_failure_exits_1` in `tests/test_recall_cli_resolve.py`
**Assertions:**
- Artifact with 3 entries, mock resolver raises `ResolveError` on second trigger
- Exit code 1 (ANY non-null failure → exit 1)
- Output still contains successfully resolved entries (resolve all, then fail)
- Error message in output contains the failed trigger info

**Expected failure:** Resolve exits 0 despite resolution failure

**Why it fails:** Error handling not implemented for artifact mode

**Verify RED:** `pytest tests/test_recall_cli_resolve.py::test_resolve_artifact_mode_any_failure_exits_1 -v`

**GREEN Phase:**

**Implementation:** Add error tracking to resolve loop, apply artifact-mode exit semantics.

**Behavior:**
- Track errors per trigger (list of error strings)
- After all triggers processed: if any errors and artifact mode → exit 1
- Output resolved content first, then error messages

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Add error collection and mode-specific exit code logic

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_resolve.py -v`
**Verify no regression:** `just test`

---

## Cycle 3.4: Resolve argument mode — best-effort error semantics

**RED Phase:**

**Test:** `test_resolve_argument_mode_partial_success_exits_0` and `test_resolve_argument_mode_total_failure_exits_1` in `tests/test_recall_cli_resolve.py`
**Assertions:**
- 3 args, resolver fails on 2 but succeeds on 1: exit code 0 (≥1 resolved)
- 3 args, resolver fails on all: exit code 1 (zero resolved)
- Successful content still in output for partial success case

**Expected failure:** Argument mode uses artifact mode's strict semantics (exit 1 on any failure)

**Why it fails:** Exit code logic doesn't differentiate modes

**Verify RED:** `pytest tests/test_recall_cli_resolve.py::test_resolve_argument_mode_partial_success_exits_0 -v`

**GREEN Phase:**

**Implementation:** Differentiate exit code logic by mode.

**Behavior:**
- Artifact mode: any error → exit 1
- Argument mode: exit 1 only if zero successes

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Branch exit code logic on mode flag

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_resolve.py -v`
**Verify no regression:** `just test`

---

## Cycle 3.5: Resolve null handling and dedup

**RED Phase:**

**Test:** `test_resolve_null_entries_silent` and `test_resolve_dedup_content` in `tests/test_recall_cli_resolve.py`
**Assertions:**
- Artifact with `"null — no relevant entries found"` entry: exit 0, no content in output for null
- Null entry failure does NOT count as resolution failure (artifact mode stays exit 0 if only nulls)
- Two entries resolving to same content: output contains content only once (dedup)
- Mock resolver returns same string for two different triggers → single occurrence in output

**Expected failure:** Null counted as resolution failure, or dedup not applied

**Why it fails:** Null handling not yet special-cased in resolve loop

**Verify RED:** `pytest tests/test_recall_cli_resolve.py::test_resolve_null_entries_silent -v`

**GREEN Phase:**

**Implementation:** Add null detection and content dedup to resolve loop.

**Behavior:**
- After `parse_trigger`, if bare query (operator-stripped) equals "null" → skip resolution, not counted as success or failure
- `seen: set[str]` tracks resolved content, skip duplicates
- All-null artifact → exit 0 (no failures, no successes needed)

**Approach:** Check if query after stripping operator prefix equals "null". Use `when/cli.py`'s `_strip_operator` pattern for this check. Dedup via set membership before appending to results.

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Add null detection before resolver call, add seen-set dedup

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_resolve.py -v`
**Verify no regression:** `just test`

---

### Phase 4: Diff subcommand (type: tdd)

`_recall diff <job>` — files changed since artifact mtime via git log.

## Cycle 4.1: Diff lists changed files

**Prerequisite:** Read `agent-core/bin/recall-diff.sh` — understand prototype behavior (mtime, git log, exclude artifact, sort, dedup).

**RED Phase:**

**Test:** `test_diff_lists_changed_files` in `tests/test_recall_cli_diff.py`
**Assertions:**
- Real git repo in `tmp_path`: init repo, create artifact file, commit, then create/commit another file in `plans/<job>/` after artifact
- CliRunner invokes `["_recall", "diff", "test-job"]` with `CLAUDE_PROJECT_DIR` env set to tmp_path
- Output contains the changed file path
- Output does NOT contain `plans/test-job/recall-artifact.md`
- Exit code 0

**Expected failure:** `diff` subcommand doesn't exist

**Why it fails:** Only `check` and `resolve` implemented

**Verify RED:** `pytest tests/test_recall_cli_diff.py::test_diff_lists_changed_files -v`

**GREEN Phase:**

**Implementation:** Add `diff` subcommand to `_recall` group.

**Behavior:**
- Takes `job` argument
- Derives artifact path from project root
- Gets artifact mtime via `os.path.getmtime()`, formats as ISO timestamp
- Runs `git log --since=<mtime> --name-only --pretty=format: -- plans/<job>/`
- Filters: remove blank lines, exclude artifact path, dedup, sort
- Output sorted file list to stdout
- Exit 0

**Approach:** `subprocess.run` for git commands. Parse stdout lines.

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Add `diff` subcommand

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_diff.py -v`
**Verify no regression:** `just test`

---

## Cycle 4.2: Diff precondition failures

**RED Phase:**

**Test:** `test_diff_not_git_repo` and `test_diff_artifact_missing` in `tests/test_recall_cli_diff.py`
**Assertions:**
- In non-git directory (isolated filesystem, no git init): exit code 1, output contains error about not being in git repo
- In git repo but artifact file missing: exit code 1, output contains artifact missing message
- Both errors to stdout (LLM-native)

**Expected failure:** Diff succeeds or crashes instead of clean error

**Why it fails:** Precondition checks not implemented

**Verify RED:** `pytest tests/test_recall_cli_diff.py::test_diff_not_git_repo -v`

**GREEN Phase:**

**Implementation:** Add precondition guards to `diff`.

**Behavior:**
- Check `git rev-parse --is-inside-work-tree` → `_fail` if not git repo
- Check artifact file exists → `_fail` if missing

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Add guards before git log execution

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_diff.py -v`
**Verify no regression:** `just test`

---

## Cycle 4.3: Diff empty output and sort/dedup

**RED Phase:**

**Test:** `test_diff_no_changes_empty_output` and `test_diff_sorted_deduped` in `tests/test_recall_cli_diff.py`
**Assertions:**
- Git repo where no files changed since artifact mtime: exit code 0, output is empty
- Git repo with same file modified in multiple commits: file appears once in output (dedup)
- Multiple files: output is sorted alphabetically

**Expected failure:** Dedup or sort not applied

**Why it fails:** Edge cases not handled

**Verify RED:** `pytest tests/test_recall_cli_diff.py::test_diff_sorted_deduped -v`

**GREEN Phase:**

**Implementation:** Verify sort/dedup behavior (may already work from Cycle 4.1).

**Behavior:**
- Dedup via `set()`, sort via `sorted()`
- Empty result → exit 0, no output

**Changes:**
- File: `src/claudeutils/recall_cli/cli.py`
  Action: Verify or fix sort/dedup in diff output processing

**Verify lint:** `just check`
**Verify GREEN:** `pytest tests/test_recall_cli_diff.py -v`
**Verify no regression:** `just test`

---

### Phase 5: Integration, cleanup, prototype deletion (type: general)

Registration verification, prototype deletion (Q-1), doc updates.

## Step 5.1: Integration test — full CLI invocation

**Objective:** Verify all three subcommands work through the main CLI entry point (`cli` group).

**Implementation:**
- Write `test_recall_cli_integration` in `tests/test_recall_cli_check.py` (or new file if space)
- Test `_recall` group is hidden from `--help` output
- Test all three subcommands accessible via `["_recall", "check", ...]`, `["_recall", "resolve", ...]`, `["_recall", "diff", ...]`
- Verify no conflict with existing `recall` command

**Expected Outcome:** All integration assertions pass, `_recall` hidden, `recall` still works.
**Validation:** `just test`

---

## Step 5.2: Delete prototype scripts and update references

**Objective:** Remove `agent-core/bin/recall-{check,resolve,diff}.sh` per Q-1. Update skills/docs that reference them.

**Implementation:**
- Delete `agent-core/bin/recall-check.sh`, `agent-core/bin/recall-resolve.sh`, `agent-core/bin/recall-diff.sh`
- Grep for references: `recall-check.sh`, `recall-resolve.sh`, `recall-diff.sh` across codebase
- Update each reference to point to `claudeutils _recall check`, `claudeutils _recall resolve`, `claudeutils _recall diff`

**Expected Outcome:** Prototypes deleted, no dangling references.
**Error Conditions:** If references exist in generated files, update the source (not the generated output).
**Validation:** `grep -r "recall-check\.sh\|recall-resolve\.sh\|recall-diff\.sh" --include="*.md" --include="*.sh" --include="*.py"` returns empty.

---

## Step 5.3: Final precommit validation

**Objective:** Full `just precommit` pass confirming everything is clean.

**Implementation:**
- Run `just precommit`
- Fix any issues found

**Expected Outcome:** Clean exit from precommit.
**Validation:** `just precommit` exits 0.
