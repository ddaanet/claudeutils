# Code Deliverable Review (RC5)

**Reviewer:** Opus 4.6 [1M]
**Design reference:** `plans/handoff-cli-tool/outline.md`
**Scope:** 26 code files per review manifest. Full conformance review, independent of prior rounds.

## RC4 Fix Verification

| RC4 Finding | Fix Status | Evidence |
|-------------|-----------|----------|
| M-2: `init_repo_minimal` helper | VERIFIED | `tests/pytest_helpers.py:79-89` — cwd-style git init with user config, `check=False` with assert on returncode |
| m-1: `HandoffState.step_reached` | VERIFIED | `session/handoff/pipeline.py:20` — `step_reached: str = "write_session"` field present with correct default |
| m-2: ANSI color in `render_pending` | VERIFIED | `session/status/render.py:30,49-50` — `color: bool = False` kwarg, `click.style(header_line, bold=True, fg="green")` when enabled |
| m-3: Two-line format | VERIFIED | `session/status/render.py:48,52` — `▶ {name} ({model}) \| Restart: {restart}` on line 1, `  \`{cmd}\`` on line 2 |
| m-4: `_strip_hints` stateful loop | VERIFIED (partial) | `session/commit_pipeline.py:187-207` — stateful `prev_was_hint` variable tracks hint context; but see M-1 below |
| m-3 (RC4 two-line format) | VERIFIED | Format now matches design spec: `▶ {name} ({model}) \| Restart: {Yes/No}` + indented `\`{cmd}\`` |

All five RC4 fixes are present. One has a residual logic issue (M-1).

## New Findings

### Critical

1. **C-1: `_split_sections` does not treat `## Message` as terminal section** (session/commit.py:56-74)
   - Design spec line 162: "Everything from `## Message` to EOF is message body -- safe for content containing `## ` lines."
   - Implementation: `_split_sections` splits on every `## ` heading unconditionally. A commit message containing `## ` (e.g., blockquoted markdown section headings) would be truncated, with the remainder parsed as an unknown section and silently discarded.
   - **Axis:** Conformance, functional correctness
   - **Impact:** Commit messages with `## ` content would be silently truncated. The spec explicitly calls out this case as requiring safe handling.

### Major

1. **M-1: `_strip_hints` resets state after first continuation, misses subsequent continuation lines** (session/commit_pipeline.py:187-207)
   - Both branches that handle indented continuation lines (tab at line 198, double-space at line 198) set `prev_was_hint = False`. Multi-line hint blocks (hint + 2+ continuation lines) only filter the first continuation; remaining continuations are kept in output.
   - Example: `"hint: foo\n  line1\n  line2\nnormal"` keeps `"  line2"` because `prev_was_hint` is reset to False after filtering `"  line1"`.
   - **Axis:** Functional correctness
   - **Fix:** Set `prev_was_hint = True` (not False) when filtering a continuation line, so the next line continues the hint context check.

2. **M-2: `step_reached` field is defined but never used in resume path** (session/handoff/cli.py:46-52, session/handoff/pipeline.py:20)
   - Design H-4 specifies `step_reached` values `"write_session"` | `"diagnostics"` and states "re-execute from `step_reached`." The field is persisted to state file and roundtrips through JSON, but `handoff_cmd` always re-executes the full pipeline regardless of `step_reached` value. The field is write-only.
   - **Axis:** Conformance (H-4 spec), vacuity (field exists but does nothing)
   - **Mitigation:** Operations are idempotent, so full replay is safe. But the field is vestigial and misleading -- it implies resume granularity that doesn't exist.

3. **M-3: `vet_check` ignores `cwd` parameter** (session/commit_gate.py:108-129,141)
   - `_load_review_patterns()` reads `Path("pyproject.toml")` relative to process CWD. `_find_reports()` globs `Path("plans")` relative to process CWD. The rest of `commit_gate.py` accepts and propagates `cwd`. `vet_check()` itself has no `cwd` parameter, and `commit_pipeline._validate` cannot pass its `cwd` through.
   - **Axis:** Robustness, API consistency
   - **Note:** No production impact (CLI always runs from project root). Latent defect for test environments using `tmp_path`.

4. **M-4: Hardcoded `"agent-core"` in `worktree/cli.py:311`** (`_check_not_dirty`)
   - Design S-2: "Replaces `-C agent-core` literals with iteration over discovered submodules." `_is_submodule_dirty("agent-core")` reintroduces a hardcoded name instead of iterating `discover_submodules()`.
   - **Axis:** Conformance (S-2)
   - **Note:** Pre-existing from RC4 (was M-2 in RC4 review). Single submodule today, so functionally correct.

### Minor

1. **m-1: Commit pipeline ordering differs from design** (session/commit_pipeline.py:279-342)
   - Design: "validate -> vet check -> precommit -> stage -> submodule commit -> parent commit"
   - Implementation: validate_inputs -> stage parent files -> precommit/vet -> commit submodules -> commit parent
   - Staging before precommit is technically necessary (`just precommit` needs staged state). The deviation has a valid technical reason but the spec should be updated to match.
   - **Axis:** Conformance

2. **m-2: `worktree/cli.py:104,176` — except tuple without parentheses** (pre-existing)
   - `except FileNotFoundError, subprocess.CalledProcessError:` (line 104) and same pattern at line 176. Valid Python 3.14+ (PEP 758) but unconventional. Parenthesized form is the universal Python idiom.
   - **Axis:** Readability

3. **m-3: `commit_pipeline.py:34,49` — stderr discarded from precommit/lint**
   - `_run_precommit` and `_run_lint` return `result.stdout.strip()` only. Some tools write diagnostics to stderr. Design says failure output should include gate-specific diagnostics.
   - **Axis:** Functional completeness

4. **m-4: `handoff/cli.py:57-59` — diagnostic output conditionally suppressed**
   - H-3 specifies diagnostics emitted "Always" after session.md writes. Implementation guards with `if git_output:`. After session.md writes there will always be changes, so this is practically always true, but the condition contradicts the spec's "Always" language.
   - **Axis:** Conformance (H-3)

5. **m-5: `git.py:24` — `_git()` strips stdout, hazardous for porcelain callers**
   - `_git()` returns `r.stdout.strip()`. Per the learnings entry on porcelain format parsing, `strip()` destroys leading-space XY format. Current callers that need porcelain avoid `_git()` (using raw subprocess), but a docstring warning about this hazard would prevent regression.
   - **Axis:** Robustness (defensive documentation)

6. **m-6: `commit_gate.py:91` — ternary precedence in `allowed` expression**
   - `dirty | _head_files(cwd) if amend else dirty` parses as `dirty | (_head_files(cwd) if amend else dirty)`. Both branches produce correct results, but the intent is `(dirty | _head_files(cwd)) if amend else dirty`. Parenthesizing would prevent future modification errors.
   - **Axis:** Readability

## Conformance Summary

| Design Section | Status | Notes |
|---------------|--------|-------|
| S-1: Package structure | Conforms | Sub-packages for handoff and status (deviation from flat) but clean separation |
| S-2: `_git()` extraction + submodule discovery | Partial | Extraction done; one hardcoded `"agent-core"` remains (M-4) |
| S-3: Output/error conventions | Conforms | stdout-only, exit codes 0/1/2, `**Header:**` format |
| S-4: Session.md parser | Conforms | Composes existing functions from worktree/session.py |
| S-5: Git changes utility | Conforms | Submodule-aware, structured markdown output |
| H-1: Domain boundaries | Conforms | CLI handles writes + diagnostics only |
| H-2: Committed detection | Conforms | `write_completed` overwrites section content |
| H-3: Diagnostic output | Conforms (m-4) | Conditional guard, but practically always true |
| H-4: State caching | Partial | `step_reached` field exists but unused in resume (M-2) |
| C-1: Scripted vet check | Partial | Missing `cwd` propagation (M-3) |
| C-2: Submodule coordination | Conforms | Partitioning, per-submodule commit, pointer staging |
| C-3: Input validation | Conforms | Clean-file detection with amend awareness |
| C-4: Validation levels | Conforms | `just-lint`, `no-vet` orthogonal options |
| C-5: Amend semantics | Conforms | `--amend`, `--no-edit`, message requirements |
| C-Message: EOF semantics | **Non-conformant** | `## ` inside message body incorrectly splits (C-1) |
| ST-0: Worktree-destined tasks | Conforms | `worktree_marker` check in ▶ selection |
| ST-1: Parallel group detection | Conforms | Consecutive windows, blocker edges, cap at 5 |
| ST-2: Preconditions/degradation | Conforms | Fatal errors for missing file, old format, old section name |

## Summary

| Severity | Count | Delta from RC4 |
|----------|-------|----------------|
| Critical | 1 | +1 (new: `## Message` EOF handling) |
| Major | 4 | +2 (new M-1 strip_hints, M-2 step_reached; carried M-3 vet cwd, M-4 agent-core) |
| Minor | 6 | 0 (net: some carried, some new) |

**RC4 fixes verified:** All 5 fixes confirmed present and correctly implemented.

**New critical finding:** C-1 (`## Message` section does not capture through EOF) is the highest-priority item. The spec explicitly requires `## Message` to consume everything to EOF, protecting commit messages that contain `## ` headings. The current parser would silently truncate such messages.

**New major finding:** M-1 (`_strip_hints` continuation logic) only filters the first continuation line of multi-line hint blocks due to premature state reset.

**Carried findings:** M-3 (vet check cwd) and M-4 (hardcoded agent-core) are pre-existing from RC4.
