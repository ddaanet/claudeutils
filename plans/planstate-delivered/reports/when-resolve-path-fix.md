# Report: when-resolve.py Path Fix

## Summary

Fixed bare `when-resolve.py` occurrences (without `agent-core/bin/` prefix) in three skill files.

## Files Modified

### `agent-core/skills/deliverable-review/SKILL.md` (line 106)

- Before: `` batch-resolve via `when-resolve.py "when <trigger>" ...` ``
- After: `` batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...` ``

### `agent-core/skills/runbook/SKILL.md` (lines 122, 140, 229, 236)

- Line 122: Tier 1 recall context — `when-resolve.py "when <trigger>" "how <trigger>"` → `agent-core/bin/when-resolve.py "when <trigger>" "how <trigger>"`
- Line 140: Tier 2 recall context — same pattern
- Line 229: Phase 0.5 batch-resolve bullet — `when-resolve.py "when <trigger>"` → `agent-core/bin/when-resolve.py "when <trigger>"`
- Line 236: artifact-absent fallback — `when-resolve.py` (standalone) → `agent-core/bin/when-resolve.py`

### `agent-core/skills/design/SKILL.md` (line 97)

Table row for Level 1 local knowledge had two bare occurrences:
- `` batch-resolve via `when-resolve.py` `` → `` batch-resolve via `agent-core/bin/when-resolve.py` ``
- `Direct Read, when-resolve.py, scout, or Grep` → `Direct Read, agent-core/bin/when-resolve.py, scout, or Grep`

## Files Left Untouched (per instructions)

- `agent-core/bin/when-resolve.py` — the script itself
- `agent-core/skills/when/SKILL.md` — already fully pathed
- `agent-core/skills/recall/SKILL.md` — per do-not-touch list
- `agent-core/skills/memory-index/SKILL.md` — already fully pathed
- `agent-core/skills/how/SKILL.md` — already fully pathed
- `agent-core/agents/` — already fixed in prior session

## Verification

Post-fix grep confirms all occurrences in the four target files now use `agent-core/bin/when-resolve.py`. Untouched files remain unchanged.
