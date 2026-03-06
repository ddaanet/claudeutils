# Deliverable Review: session-scraping (re-review)

**Date:** 2026-03-06
**Methodology:** agents/decisions/deliverable-review.md
**Context:** Re-review after rework. Previous review: `deliverable-review.md` (2026-03-02, 1 critical, 2 major, 2 minor).

## Inventory

| Type | File | Lines |
|------|------|-------|
| Code | `plans/prototypes/session-scraper.py` | 707 |

Single deliverable. Inventory script reports 0 files (prototype predates branch merge base; modified, not created). Inventory derived from `git diff main`.

**Design conformance summary:** 6/6 data models implemented. 4/4 pipeline stages implemented. 4/4 CLI commands present. All 5 previous findings fixed and verified.

## Previous Findings — Verification

All 5 findings from the 2026-03-02 review are resolved:

| # | Finding | Severity | Fix | Verified |
|---|---------|----------|-----|----------|
| 1 | FR-4 merge commit parent tracing absent | Critical | `merge_parents` field on CorrelationResult, `--merges` scan with `^2` parent inspection (lines 538-594) | Yes |
| 2 | Scanner missing agent-*.jsonl files | Major | `AGENT_RE` regex + scan loop with `removeprefix("agent-")` (lines 131-140) | Yes |
| 3 | Silent CalledProcessError in unattributed scan | Major | Warning to stderr (lines 535-536) | Yes |
| 4 | JSON decode errors unlogged | Minor | Warning with path and exception (lines 196-197) | Yes |
| 5 | Subtype field check via content inspection | Minor | Explicit `msg_subtype == "tool_result"` check before content fallback (lines 245-246) | Yes |

## Critical Findings

None.

## Major Findings

1. **Merge parent branch-to-project-dir mapping uses substring match** — `correlate_session_tree()` line 585
   - Design requirement: Key Decision 4 — "map parent branches to worktree session dirs via encoded path convention"
   - Current behavior: `branch in pdir.name` matches any project directory whose encoded path contains the branch name as a substring. Branch "main" matches every project dir containing "main" (e.g., `-Users-david-code-maintenance-tool-`). Branch "fix" matches `-Users-david-code-prefix-fix-suffix-`.
   - Impact: False positive session dir mappings in `merge_parents`. Multi-project environments would return unrelated project dirs for most merge commits.
   - Suggested fix: Match branch slug as the final path component of the decoded project dir, or require exact segment match between `-` delimiters in the encoded path.

## Minor Findings

**Functional completeness:**
- `correlate` text output (lines 700-703) omits `merge_parents` data. JSON output includes it via `model_dump()`. Users running `correlate` in text mode see no merge parent information despite it being computed.

**Robustness:**
- Tool call refs (`t1`, `t2`, ...) are assigned per-file in `parse_session_file()`. After aggregation in `build_session_tree()`, refs from different files collide. `tree` text output displays these non-unique refs (line 679). Not user-facing in practice — `--expand` only exists on `parse` command (single-file scope) — but tree display is misleading.
- `interrupt_text` concatenation (line 320) joins `first_text` and `"\n".join(raw_strings)` without separator. Could theoretically produce false interrupt match if text fragments span the boundary. Extremely unlikely in practice.

## Gap Analysis

| Design Requirement | Status | Reference |
|---|---|---|
| FR-1: Project directory enumeration | Covered | `scan_projects()` lines 101-141 |
| FR-1: Path decoding | Covered | `_decode_project_path()` lines 93-98 (lossy, documented) |
| FR-1: Prefix filtering | Covered | `scan_projects(prefix=...)` lines 107-119 |
| FR-1: UUID + agent file listing | Covered | UUID (line 122) + agent (line 131) |
| FR-2: 6 entry types | Covered | `EntryType` enum + all branches in `parse_session_file` |
| FR-2: User prompt classification (KD-6) | Covered | All 4 categories implemented |
| FR-2: Skill invocation detection | Covered | `<command-name>` tag parsing, lines 366-387 |
| FR-2: Tool call/result correlation | Covered | `pending_tools` state machine, lines 178-311 |
| FR-2: Interactive tool outputs | Covered | `INTERACTIVE_TOOLS` frozenset, line 33 |
| FR-2: Interrupt detection | Covered | String + list formats, lines 318-330, 355-364 |
| FR-2: Commit hash extraction (KD-2) | Covered | `_extract_commit_hash()` + `GIT_COMMIT_MARKERS` |
| FR-2: Noise suppression (C-1, KD-3) | Covered | Content summary + `--expand`/`--all-detail` |
| FR-3: Sub-agent discovery | Covered | `build_session_tree()` subagents dir, lines 420-435 |
| FR-3: Source tagging | Covered | `agent_source` field, `cur_agent` tracking |
| FR-3: Commit hash collection | Covered | `commit_hashes` set in SessionTree |
| FR-4: Git metadata lookup | Covered | `_git_commit_info()` lines 447-492 |
| FR-4: Forward/reverse index (C-2, KD-4) | Covered | `session_commits` + `commit_sessions` dicts |
| FR-4: Merge commit tracing | Covered | `merge_parents` dict, lines 538-594 (Major #1: imprecise matching) |
| FR-4: Unattributed commits | Covered | Last 50 commits check, lines 518-536 |
| C-3: Prototype scope | Covered | Single script, no production module changes |
| CLI interface | Covered | Click group with scan/parse/tree/correlate |

## Summary

- **Critical:** 0
- **Major:** 1 (merge parent substring matching)
- **Minor:** 3 (text output gap, ref collision, concatenation separator)
