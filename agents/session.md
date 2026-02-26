# Session Handoff: 2026-02-26

**Status:** Hook output improvements complete; all audit design decisions implemented.

## Completed This Session

**PreToolUse recipe-redirect consolidation:**
- Extended `agent-core/hooks/pretooluse-recipe-redirect.py` with 5 new patterns: python/python3 script redirect (FR-1), python -m tool strip (FR-2), python -c block (FR-3), uv run redirect (FR-4), rm index.lock block (FR-5)
- Routing table architecture: `_match_blocks` (hard block, exit 2) + `_match_python_uv` + `_match_tool_wrappers` (soft redirect, additionalContext)
- Absorbed `pretooluse-block-rm-lock.sh` into consolidated Python script, deleted shell script
- All hook messages include rationale for agent compliance
- Removed "Script invocation" prose rule from CLAUDE.md — hook enforces mechanically
- Shortened all hook commands in settings.json: dropped `python3`/`bash` prefixes and `$CLAUDE_PROJECT_DIR` — scripts have shebangs, hooks run from project root
- Recall artifact: `plans/precommit-python3-redirect/recall-artifact.md` (keys-only format)
- Requirements: `plans/precommit-python3-redirect/requirements.md`

**Hook output audit:**
- Empirically verified output channel audience model via test hook (`tmp/test-hook-channels.py`, TEST=1–7)
- `additionalContext` → agent-only; `systemMessage` → user-only; `permissionDecisionReason` → both (repeats twice in CLI); stderr+exit 2 → both (1 line, `[hook-path]:` prefix noise)
- `permissionDecisionReason` + empty string falls back to "Blocked by hook" platform label — same 4 UI lines; short non-empty reason is better
- Design decisions: all `_Redirect` cases become blocks; remove `_Redirect`/`_Block` distinction (single block type); use `permissionDecision:deny` + short reason + `additionalContext` + `systemMessage`
- `pretooluse-recall-check.py` is architecturally broken — exit 0 advisory arrives after Task dispatches (no model re-run between PreToolUse hook and tool execution); must block; gate by `subagent_type` discriminator
- EXECUTION_AGENTS set: `{artisan, test-driver, corrector, runbook-corrector, design-corrector, outline-corrector, runbook-outline-corrector, tdd-auditor, refactor}`
- `userpromptsubmit-shortcuts.py` systemMessage design: brief expansions (c, y) → same text both audiences; Tier 2 injections → behavioral outline + non-blank line count e.g. `discuss: assess, stress-test, state verdict. (N lines)`; Tier 2.5 guards → authored ~60 char user summary; ~60 char terminal constraint (29 char prefix, 90 char width)
- Token count preferred over line count for injection weight; deferred — `claudeutils tokens` cache plan not located

**Hook output improvements:**
- `pretooluse-recipe-redirect.py` — removed `_Redirect`/`_Block`/`_Action` classes; added `_deny()` helper; all cases now use `permissionDecision:deny` + `permissionDecisionReason` + `additionalContext` + `systemMessage`
- `pretooluse-recall-check.py` — rewrote with `subagent_type` discriminator gate; EXECUTION_AGENTS set (9 types); non-execution agents pass through; execution agents without recall-artifact blocked via `permissionDecision:deny`; fixes architectural issue where exit 0 advisory had no effect
- `pretooluse-block-tmp.sh` + `pretooluse-symlink-redirect.sh` — migrated from `stderr + exit 2` to `permissionDecision:deny` JSON + `exit 0`; bash scripts use `jq -n --arg` for safe JSON construction
- `userpromptsubmit-shortcuts.py` — added `c`/`y` Tier 1 shortcuts; `_nonblank()` helper + `DIRECTIVE_SYSTEM_MSGS` dict; Tier 2 systemMessage now behavioral outline + line count; Tier 2.5 guards now emit authored systemMessage summaries; final `if context_parts:` block includes systemMessage

## Pending Tasks

- [x] **Hook output improvements** — Implement audit design decisions: pretooluse-recipe-redirect.py (remove _Redirect/_Block, all blocks via permissionDecision:deny + short reason + additionalContext + systemMessage), pretooluse-recall-check.py rewrite (agent-type discriminator, EXECUTION_AGENTS block gate), pretooluse-block-tmp.sh + pretooluse-symlink-redirect.sh migrate from exit 2 to permissionDecision:deny, userpromptsubmit-shortcuts.py systemMessage improvements (behavioral outlines for Tier 2, authored summaries for Tier 2.5, add c/y shortcuts) | sonnet

## Blockers / Gotchas

**claudeutils tokens cache plan not located:** Token count in hook systemMessage (preferred over line count) requires `claudeutils tokens` without API latency. Use non-blank line count as fallback (implemented); swap when cache lands.

**test-hook-channels.py still in settings.json:** `tmp/test-hook-channels.py` remains in Bash PreToolUse hooks (has guard — only fires on `echo test-hook` commands). Ephemeral test artifact; cleanup deferred.

## Next Steps

No pending tasks. Branch ready to merge to main.

## Reference Files

- `plans/precommit-python3-redirect/recall-artifact.md` — recall artifact for hook work
- `tmp/test-hook-channels.py` — empirical test hook (ephemeral, can delete)
