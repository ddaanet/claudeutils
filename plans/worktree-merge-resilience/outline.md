# Merge Artifact Resilience — Outline

## Approach

Segment-level diff3 merge for learnings.md on every merge — replaces git's line-oriented 3-way merge for this file. Structural validation in precommit as defense-in-depth for manual edits.

## Segment-level diff3 resolver (FR-1, FR-2, FR-4)

Current `resolve_learnings_md()` does line-set dedup — each line compared independently. Heading lines shared by both sides are "not theirs-only" so they're dropped, but their bullet children may differ and get appended headingless. Also uses ours-wins implicitly, silently dropping branch modifications.

### Fix: diff3 at segment granularity, every merge

Parse learnings content into segments keyed by heading text. Each segment = heading line + body lines (until next heading or EOF). Preamble (lines before first `## `) is a special segment.

Run on **every merge**, not just conflicts. This prevents orphans from both sources:
- Conflict path: replaces git's conflicted file with structure-aware resolution
- Clean merge path: overwrites git's clean-but-potentially-orphaned result with structure-aware merge

Three inputs always available when `MERGE_HEAD` exists:
- **base:** `git merge-base HEAD MERGE_HEAD` → `git show <merge-base>:agents/learnings.md`
- **ours:** `git show HEAD:agents/learnings.md`
- **theirs:** `git show MERGE_HEAD:agents/learnings.md`

### Pipeline integration (FR-3)

The resolver must run on all merge paths, not just the conflict path. Two integration points:

1. **Conflict path (existing):** `_auto_resolve_known_conflicts` in `_phase3_merge_parent` — already calls `resolve_learnings_md(conflicts)`. The rewritten function handles this.

2. **All paths (new):** After merge but before commit, run the segment diff3 regardless of conflict status. Insert at top of `_phase4_merge_commit_and_precommit` — single insertion point, all 5 state machine paths converge here. Only runs when `MERGE_HEAD` exists or learnings.md was modified.

For the conflict path, the resolver runs twice: once in phase 3 (conflict resolution) and once in phase 4 (validation re-merge). The phase 4 run is a no-op if phase 3 already produced the correct result — it re-reads base/ours/theirs and produces the same output. This is acceptable overhead for the guarantee that all paths are covered.

Alternatively, skip the phase-4 re-merge if learnings.md is already staged (phase 3 `git add`-ed it). Only run the diff3 in phase 4 when learnings.md was NOT conflicted but was modified by the clean merge.

### Function signature

`resolve_learnings_md(conflicts)` keeps its existing signature for the conflict path. A new function (e.g., `remerge_learnings_md()`) handles the all-paths case — reads base/ours/theirs from `HEAD`/`MERGE_HEAD` instead of index stages `:1:`/`:2:`/`:3:`. Both call the same core diff3 logic.

### Resolution matrix

| Base | Ours | Theirs | Resolution |
|------|------|--------|------------|
| — | — | new | append (theirs created) |
| — | new | — | keep (ours created) |
| — | new-A | new-A | keep (convergent creation) |
| — | new-A | new-B | **conflict** (divergent creation, same heading) |
| entry | entry | entry | keep (unchanged) |
| entry | modified | entry | keep ours (only ours modified) |
| entry | entry | modified | take theirs (only theirs modified) |
| entry | modified-A | modified-A | keep (convergent edit) |
| entry | modified-A | modified-B | **conflict** (divergent edit) |
| entry | — | entry | delete (ours deleted, theirs unchanged) |
| entry | entry | — | delete (theirs deleted, ours unchanged) |
| entry | — | modified | **conflict** (ours deleted, theirs modified) |
| entry | modified | — | **conflict** (theirs deleted, ours modified) |
| entry | — | — | delete (both deleted) |

"Modified" = body lines differ from base (heading is the key, body is the value). Comparison at body level (joined lines string equality), not line-by-line within a segment.

### Conflict output (FR-4)

On conflict: write standard diff3 conflict markers at **line granularity** within the conflicting segment. The heading line (shared key) appears once above the markers; the differing body lines are wrapped in `<<<<<<<`/`=======`/`>>>>>>>` markers. This shows exactly which lines differ, not the entire entry. Report conflicting headings to stderr.

On conflict, the resolver does NOT remove `agents/learnings.md` from the conflicts list and does NOT `git add` it — the caller (`_auto_resolve_known_conflicts`) propagates it to the conflict report, and merge exits with code 3. On successful resolution (no conflicts), `git add` and remove from list as today.

For non-conflict paths (phase 4): the segment diff3 is the primary merge for learnings.md, overwriting git's line-level result. If it detects a segment-level conflict (e.g., both sides modified different bullets within the same entry — git merges cleanly at line level, but segment diff3 sees divergent body edits), block with exit non-zero and emit conflicting headings.

### Preamble handling

Preamble (content before first `## ` heading) is a single segment keyed by `None` or sentinel. Same diff3 rules apply — if both sides modified preamble differently, conflict.

**Affected file:** `src/claudeutils/worktree/resolve.py` — rewrite `resolve_learnings_md()` body (lines 148-167), add `remerge_learnings_md()`, extract shared diff3 core

### Segment parsing

A function to parse learnings content into ordered dict of `{heading_text: body_lines}`:
- Heading: line matching `^## (.+)$`
- Body: all lines from heading to next heading or EOF (including blank lines between entries)
- Preamble: lines before first heading → keyed by `None`

This parser is reusable — precommit validator can also use it.

## Precommit: Structural validation (NFR-1, NFR-2)

Defense-in-depth for manual edits outside the merge pipeline. The diff3 resolver handles merge-time orphans; this catches orphans introduced by hand-editing learnings.md.

Structural invariant: after preamble, every non-blank line must belong to a segment (be under a `## ` heading).

Checks:
1. **Orphaned content** — non-blank, non-heading lines after preamble but before the first `## ` heading
2. **Duplicate headings** — already exists in `validate()` via `extract_titles()`. No new implementation needed.

**Affected file:** `src/claudeutils/validation/learnings.py` — extend `validate()` with orphan detection

### False positive prevention (NFR-2)

- Preamble detection uses the same 10-line skip as `extract_titles()` — no divergence
- Existing clean `agents/learnings.md` used as test fixture to verify zero false positives
- Only checks structural invariants (orphaned content, duplicates), not heuristic content matching

## Key decisions

- **diff3 semantics, not ours-wins:** Conflicts surface to user for manual resolution. Silent data loss (ours-wins dropping branch modifications) eliminated.
- **Merge base involvement:** Three-way comparison distinguishes "created since merge-base" from "deleted since merge-base." Deletion + modification on opposite sides = conflict.
- **Every merge, not just conflicts:** Segment diff3 runs on all merge paths. Eliminates the clean-merge orphan gap entirely. No separate detection layer needed in the merge pipeline.
- **Block, not warn:** Conflicts and structural violations block the merge. Manual fix is cheap. Silent corruption is expensive.
- **Segment parser reuse:** Single parser serves both resolver (diff3 merge) and precommit validator (structural check). Candidate location: `src/claudeutils/validation/learnings.py` (already defines `extract_titles()` with the same heading pattern).
- **Misplaced content deferred:** Heuristic detection of "content under wrong heading" deferred — segment diff3 prevents the known failure modes by never letting git's line-level merge operate on learnings.md.

## Scope

**IN:** diff3 segment merge for learnings.md (all merge paths), precommit structural validation, merge pipeline integration, tests for all
**OUT:** session.md structural validation, generic markdown merger (future — learnings-specific for now), `.gitattributes` custom merge driver, pre-merge rebase strategy

## Testing approach

Integration-first. Prove the merge pipeline behavior end-to-end before decomposing into unit tests.

- **Integration tests (first):** Real git repos via `tmp_path`. Extend `tests/test_worktree_merge_conflicts.py`. Restricted to observed scenarios:
  - Diagnostic reproduction (c330b7d2): branch modifies entry in-place + adds new entries at tail, main adds different entries at tail → segment diff3 overwrites git's line-level result, no orphans
  - Brief reproduction (6086650e): both sides modify same entry (different bullets) → segment diff3 detects divergent edit, conflict markers, merge exits code 3
- **Unit tests (second):** Pure function tests, no git:
  - Segment parser: headings, bodies, preamble, edge cases (empty body, consecutive headings, no preamble)
  - diff3 resolution matrix: each row — created, modified, deleted, convergent, divergent, conflict output format
  - Validator: orphan detection (headingless bullets after preamble, clean file passes)

## Documentation Perimeter

**Required reading (planner must load before starting):**

Implementation context:
- `src/claudeutils/worktree/resolve.py` — current resolver (rewrite target)
- `src/claudeutils/worktree/merge.py` — merge pipeline state machine (integration point)
- `src/claudeutils/validation/learnings.py` — existing validator (extend with orphan check)
- `tests/test_worktree_merge_conflicts.py` — existing merge tests (extend with integration tests)
- `tests/test_validation_learnings.py` — existing validator tests (extend with orphan tests)

Decisions:
- `agents/decisions/testing.md` — TDD conventions, test splitting, e2e over mocked subprocess, red phase assertions, merge workflow simulation
- `agents/decisions/cli.md` — error exit codes, error output to stderr, layer separation

Diagnostics:
- `plans/worktree-merge-resilience/diagnostic.md` — reproduction conditions, root cause
- `plans/worktree-merge-resilience/brief.md` — second instance, detection gap

Memory index triggers (load via `/when` if needed during planning):
- `/when tests simulate merge workflows` — branch-as-merged-parent, amend-preserves patterns
- `/when preferring e2e over mocked subprocess` — real git repos via tmp_path
- `/when writing error exit code` — consolidate display+exit, single Click call
- `/when adding error handling to call chain` — layer separation, context at site, display at top
- `/when resolving session.md conflicts` — existing conflict resolution patterns
- `/when merging worktree with consolidated learnings` — delta-only post-consolidation

## Open questions

None — approach decided, misplaced-content heuristic explicitly deferred.
