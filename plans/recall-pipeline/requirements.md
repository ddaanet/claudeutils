**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Recall Pipeline

Improve recall system reliability and data quality. Operates on the recall infrastructure in `src/claudeutils/recall/` and `src/claudeutils/recall_cli/`.

## Requirements

### Functional Requirements

**FR-1: Recall deduplication**
Detect and merge duplicate recall entries across decision files (`agents/decisions/*.md`). Duplicates arise from parallel worktrees writing similar entries independently.
- Acceptance: Two entries with identical trigger phrases but different wording → flagged for merge with diff shown
- Acceptance: Entries with overlapping semantic scope but different triggers → flagged as candidates (not auto-merged)

**FR-2: Stdin format parsing**
Parse recall entries from stdin in pipeline contexts. Currently `claudeutils _recall resolve` takes positional arguments; pipeline use requires stdin streaming.
- Acceptance: `echo "when X\nwhen Y" | claudeutils _recall resolve -` reads from stdin
- Acceptance: Mixed stdin + positional args → error (not silently combined)

**FR-3: Usage scoring**
Score recall entries by resolution frequency for pruning and prioritization. Track how often each entry is resolved across sessions.
- Acceptance: `claudeutils _recall stats` shows per-entry resolution count and last-used date
- Acceptance: Entries with zero resolutions in N sessions flagged as candidates for removal

### Out of Scope

- Changing recall entry format in decision files
- Modifying the memory-index structure (separate plan: active-recall)
- Automatic pruning (scoring informs human decisions)
