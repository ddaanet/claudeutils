# Code Review: handoff-cli-tool (RC10 Layer 1)

## RC9 Fix Verification

**M-1 VERIFIED** — commit_gate.py:164-165 — `root = Path(cwd or ".")` and `matched_paths = [root / f for f in matched if (root / f).exists()]`. Path resolution now correctly threads `cwd` parameter.

**m-7 VERIFIED** — handoff/pipeline.py:15-19 — `HandoffState` dataclass has only `input_markdown` and `timestamp` fields. No trace of `step_reached` in any `grep` across src/tests.

**m-8 CARRIED** (by design) — commit_gate.py:143 — `_AGENT_CORE_PATTERNS` hardcoded. Deferred per outline C-1.

**m-9 VERIFIED** — commit_gate.py:34-39 — `_git_output` docstring now includes: "Warning: `.strip()` destroys leading spaces in porcelain XY format. Do not use for ``git status --porcelain`` output — use raw ``result.stdout.splitlines()`` instead."

**m-10 VERIFIED** — commit_pipeline.py:234 — `if parent_output:` guard prevents appending empty string.

## Findings

[M] handoff/pipeline.py:44-45 — robustness — `load_state()` uses `HandoffState(**data)` to deserialize state files. After m-7 removed the `step_reached` field from `HandoffState`, any pre-existing state file written before the fix (containing `step_reached`) will crash with `TypeError: HandoffState.__init__() got an unexpected keyword argument 'step_reached'`. State files persist across sessions in `tmp/.handoff-state.json`. Fix: filter `data` to known fields before unpacking, or use a try/except that clears corrupt state.

[m] commit_pipeline.py:269-273 — error signaling — When `validate_files` raises `CleanFileError` for submodule files (line 273), the error message contains paths relative to the submodule root (e.g., `fragments/foo.md` instead of `agent-core/fragments/foo.md`). The `_partition_by_submodule` function strips the submodule prefix at line 107. The calling agent sees clean-file paths without context about which repo they belong to.

[m] handoff/pipeline.py:75 — robustness — `overwrite_status` builds a regex replacement string: `r"\g<1>\n**Status:** " + status_text + r"\n\g<3>"`. If `status_text` contains regex backreference patterns (e.g., `\g<1>` or `\1`), `re.subn` would interpret them during substitution. While unlikely in practice, status text originates from user-written handoff input. Fix: use a function replacement callback instead of string replacement to avoid interpretation.

[m] git_cli.py:32 — functional correctness — `_build_repo_section` concatenates `header + "\n\n".join(parts)`. When only one part exists (status without diff, or diff without status), the output has no `\n\n` separator — correct. But when `header` is `"## Parent\n"` and both status and diff exist, the output is `"## Parent\nstatus...\n\ndiff..."`. The heading's trailing `\n` runs directly into status text with no blank line between heading and content. Minor formatting inconsistency — markdown renderers may not separate them clearly.

[m] session/status/render.py:118 — robustness — `_build_dependency_edges` joins all blocker groups into one string and checks whether two task names both appear anywhere in it. Two tasks mentioned in completely unrelated blocker entries would be falsely marked as dependent. Per ST-1 the spec says "no logical dependency (Blockers/Gotchas)" — the current check is overly conservative but functionally safe (prevents parallel execution that might be safe, never allows parallel execution that isn't).

[m] session/status/cli.py:67 — robustness — `list_plans(Path("plans"))` uses a relative path. If the process cwd differs from the project root, this resolves to the wrong directory. The session file path uses `CLAUDEUTILS_SESSION_FILE` env var (line 51) and `_is_dirty()` uses no `cwd` parameter (line 76). All three assume process cwd equals project root — consistent assumption but not defensively coded.

## Summary

0 critical, 1 major, 5 minor
