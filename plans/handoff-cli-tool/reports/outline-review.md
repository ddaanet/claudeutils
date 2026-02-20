# Outline Review: handoff-cli-tool

**Artifact**: plans/handoff-cli-tool/outline.md
**Date**: 2026-02-19T00:00:00Z
**Mode**: review + fix-all

## Summary

The outline is structurally sound — the worktree CLI pattern is correctly applied, the mechanical/judgment split is well-defined, and the gitmoji embedding approach is technically feasible. Two issues required fixes: FR-1 input handling was ambiguous (status line / completed text appeared in the state cache but the CLI never receives them), and FR-2 git status output was missing from the commit command response. All other issues were clarity or minor gaps addressed inline. The outline is ready for user discussion.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements derived from session.md task description:

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| FR-1: Inputs (status line, completed text, optional files, optional commit message w/ gitmoji) | Approach (added), `_handoff commit`, D-2 | Complete | Fixed: Added explicit clarification that status line / completed text stay in agent Edit/Write domain; CLI receives message + files + gitmoji only |
| FR-2: Outputs (conditional) — learnings age, precommit result, git status+diff, worktree ls | `_handoff info`, `_handoff commit` | Complete | Fixed: Added `git_status` to commit JSON output; was missing from original |
| FR-3: Cache on failure — inputs to state file, rerun without re-entering skill | D-2, `_handoff resume` | Complete | Minor fix: Added `step_reached` value enumeration |
| FR-4: Gitmoji — embeddings + cosine similarity over 78 pre-computed vectors | D-1, `_handoff gitmoji` | Complete | Minor fix: Noted 77 vs 78 count discrepancy; added default fallback for no-match case |
| FR-5: Worktree CLI pattern — mechanical ops in CLI, judgment in agent | Approach, D-3, D-4, D-5 | Complete | Fixed: D-3 now has explicit per-command output format table clarifying mixed JSON/tab-sep |

**Traceability Assessment**: All requirements covered after fixes.

## Review Findings

### Critical Issues

1. **FR-1 input handling ambiguity**
   - Location: D-2 state caching, Approach section
   - Problem: D-2 lists `status_line` and `completed_text` in the state cache struct, but D-4 says CLI does NOT write session.md. These two fields are never accepted as CLI arguments in any command signature. The agent writes session.md directly — so what serializes these to the state file? The outline left the pipeline input contract undefined.
   - Fix: Added explicit "Inputs to the CLI pipeline (FR-1)" paragraph in Approach section clarifying that status line / completed text are session.md content written by the agent directly, not CLI inputs. The CLI receives only: message, files, gitmoji.
   - **Status**: FIXED

### Major Issues

1. **FR-2 git status missing from commit output**
   - Location: `_handoff commit` command output spec
   - Problem: Original output was `{hash, precommit_passed, precommit_output}`. FR-2 lists "git status+diff" as a conditional output. After commit, the agent needs to confirm the tree is clean — but this required a separate `_handoff info` call. The commit result should include post-commit git status.
   - Fix: Added `git_status` to commit JSON output. Added explanatory note that this satisfies FR-2.
   - **Status**: FIXED

2. **D-3 output format inconsistency undocumented**
   - Location: D-3 Output format
   - Problem: Original D-3 said "All commands return JSON to stdout" then immediately listed `gitmoji` as tab-separated — a contradiction. The worktree CLI uses tab-separated for simple machine-parseable values, but the outline didn't establish clear rules for when each applies.
   - Fix: Rewrote D-3 with explicit rule (structured → JSON, simple single-value → tab-separated) and a per-command table.
   - **Status**: FIXED

3. **Open Questions left unresolved**
   - Location: Open Questions 1, 2, 3
   - Problem: All three questions have clear answers available from exploration data (package has no numpy, package data location is well-established practice, submodule handling requires judgment). Leaving them open delays design sign-off without need.
   - Fix: Converted all three to recommendations/decisions with reasoning grounded in exploration findings. Flagged Q1 for user confirmation on one remaining trade-off.
   - **Status**: FIXED

### Minor Issues

1. **`step_reached` values not enumerated in D-2**
   - Location: D-2 state caching
   - Problem: `resume` replays from `step_reached` but the valid values were not defined, leaving ambiguity about the commit pipeline's resumable points.
   - Fix: Added explicit values: `"precommit"`, `"stage"`, `"commit"`, `"verify"`.
   - **Status**: FIXED

2. **Gitmoji count discrepancy (78 vs 77)**
   - Location: D-1, `_handoff gitmoji` command
   - Problem: Task spec says "78 pre-computed vectors"; exploration confirms 77 entries in both gitmoji files. Perpetuating "78" without noting the discrepancy could cause off-by-one in implementation.
   - Fix: Added note in D-1 to verify count before generating embeddings cache.
   - **Status**: FIXED

3. **No-match fallback behavior undefined for gitmoji**
   - Location: `_handoff gitmoji` command, D-1
   - Problem: Keyword fallback described but no behavior defined if neither embedding nor keyword matches.
   - Fix: Added default fallback to `✨ - sparkles` (most general gitmoji) rather than failing.
   - **Status**: FIXED

4. **`generate-gitmoji-embeddings.py` scope and runtime ambiguity**
   - Location: D-5 package structure
   - Problem: Script listed alongside package files without clarifying it is dev-only and not shipped.
   - Fix: Added "(dev-only, not shipped)" annotation and explanatory paragraph.
   - **Status**: FIXED

5. **`src/claudeutils/cli.py` modification not in D-5**
   - Location: D-5 package structure
   - Problem: Scope IN lists "Registration in main `cli.py`" but D-5 only lists the new `handoff/` files — the file to modify was absent from the structure diagram.
   - Fix: Added `src/claudeutils/cli.py # MODIFIED` line to D-5.
   - **Status**: FIXED

## Fixes Applied

- Approach section — Added FR-1 and FR-2 explicit summaries mapping task inputs/outputs to CLI commands
- `_handoff commit` — Added step 1 "cache inputs before attempting"; added `git_status` to output JSON; added success/failure state file behavior
- `_handoff commit` — Added note explaining `git_status` satisfies FR-2
- D-1 — Noted 77 vs 78 gitmoji count discrepancy; added default fallback for no-keyword-match case
- D-2 — Added `step_reached` valid value enumeration
- D-3 — Rewrote with explicit format rule and per-command output table
- D-5 — Added `src/claudeutils/cli.py # MODIFIED` line; added dev-only annotation to script; added explanatory paragraph for generate script
- Open Questions 1, 2, 3 — Converted to recommendations/decisions with reasoning

## Positive Observations

- The mechanical/judgment split is precisely and consistently applied across all four commands. D-4 is explicit and not hedged.
- Choosing pure Python cosine similarity (no numpy) keeps the dependency footprint consistent with the existing package philosophy.
- The `_handoff info` single-call design (all diagnostics in one response) is the right pattern — avoids multiple round-trips for what the agent needs before making judgment decisions.
- The `resume` command design is clean: state file existence is the signal, not a separate status endpoint.
- D-1's two-tier approach (pre-computed + runtime fallback) is well-reasoned with explicit rationale for rejecting alternatives.

## Recommendations

- **User decision needed (Open Question 1):** Confirm whether runtime OpenAI embedding quality matters in practice, or whether the shipped pre-computed cache + keyword fallback is sufficient for this project's commit message patterns. If runtime embedding is critical, the `openai` optional dep path is correct. If offline-only is preferred, document the pre-computed-cache-only design.
- **Testing approach:** Outline mentions "CliRunner pattern, mock git repos" but does not specify whether gitmoji embedding tests mock the OpenAI call or use the keyword fallback path. Implementation should test both paths.
- **State file cleanup on abandon:** D-2 specifies success deletes the state file but does not address the case where a user abandons the retry (old state file lingers). Consider adding a TTL check or `_handoff reset` command — or document that stale state files are ignored if timestamp is old.

---

**Ready for user presentation**: Yes
