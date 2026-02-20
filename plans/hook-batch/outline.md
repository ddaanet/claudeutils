# Hook Batch: Outline

## Approach

Five hook events implemented as separate phases. Each phase produces a self-contained hook script. UserPromptSubmit is the largest (9 changes to existing 839-line script). Other 4 are new short scripts.

All hooks use command type (deterministic, fast, no LLM cost). Scripts live in `agent-core/hooks/`. Hook configuration source of truth: `agent-core/hooks/hooks.json`, merged into `.claude/settings.json` by `just sync-to-parent`.

## Phases

### Phase 1: UserPromptSubmit improvements

Modify `agent-core/hooks/userpromptsubmit-shortcuts.py` (839 lines). Nine changes:

**Tier 1 (commands):**
1. **Line-based shortcut matching** — Shortcuts trigger on own line within multi-line prompts, not full-prompt-only. First shortcut match wins.
2. **r expansion** — Replace "Error if no in-progress task" with graduated lookup: conversation context → session.md → git status. Report only if genuinely nothing to resume.
3. **xc/hc shortcut messages** — Compress to `[execute, commit]` / `[handoff, commit]` style, noting these are shorthand for skill continuation chains (e.g., `/handoff and /commit`).

**Tier 2 (directives):**
4. **Additive directives** — Directives are section-scoped (from prefix to next directive or end of message), not first-match-wins. Multiple directives in one prompt each inject their expansion for their section.
5. **p: dual output** — Concise systemMessage (like d: already has), full expansion in additionalContext.
6. **b: brainstorm directive** — Diverge without converging. No evaluation, no ranking. Dual output. Long-form alias: `brainstorm:`.
7. **q: and learn: directives** — Documented in execute-rule.md but not implemented. Both use dual output. Long-form aliases: `question:` (for q:), `learn:` (already long-form).

**Tier 2.5 (pattern guards):**
8. **Skill-editing guard** — Pattern match editing verbs + skill/agent → inject plugin-dev reminder via additionalContext. Fires alongside other tiers (additive).
9. **CCG integration** — Platform capability keywords → inject claude-code-guide agent reminder via additionalContext. Additive.

**Implementation details:** `plans/hook-batch/userpromptsubmit-plan.md` has pattern specs and expansion strings for items 4-9. Items 1-3 are new (from design discussion).

**Plan overrides (superseded by design discussion):**
- Execution order in userpromptsubmit-plan.md Step 2 says "first directive match wins, returns" — superseded by D-7. Implement additive directive scanning (all directives in prompt inject their expansion, no early return after first match).
- Item 5 (b: directive) in the plan says "Needs user input before implementing" — resolved by D-5. b: = brainstorm, diverge without converging.

**Phase type:** TDD — behavioral changes to testable pattern-matching logic.

### Phase 2: PreToolUse recipe-redirect

New script: `agent-core/hooks/pretooluse-recipe-redirect.py`
Matcher: `Bash`

When agent attempts a raw command that has a project recipe, inject additionalContext redirecting to the proper tool. NOT blocking (exit 0) — sandbox denylist is the enforcement layer; this hook explains WHY the command failed.

Pattern matches:
- `ln` → `just sync-to-parent`
- `git worktree` → `claudeutils _worktree`
- `git merge` → `claudeutils _worktree merge`

Note: `python3` and `python` are denied in settings.json denylist but are NOT redirect patterns for this hook — they have no project recipe equivalent. The hook only redirects commands with an explicit project recipe replacement.

Input: stdin JSON with `tool_input.command`
Output: additionalContext with redirect suggestion, or silent pass-through.

**Phase type:** TDD — command pattern matching, testable.

### Phase 3: PostToolUse auto-format

New script: `agent-core/hooks/posttooluse-autoformat.sh`
Matcher: `Write|Edit`

After Write/Edit completes on a Python file, run ruff + docformatter on that specific file. Not full `just format` (too slow per-edit).

Logic:
1. Extract `file_path` from tool_input (both Write and Edit provide `file_path` in tool_input). Use `python3 -c` or `jq` for JSON parsing — do not use raw Bash string manipulation on JSON.
2. Skip if not `.py` file
3. Run `ruff check --fix-only --quiet <file>` then `ruff format --quiet <file>`
4. Run `docformatter --in-place <file>` if docformatter available
5. Silent on success; stderr on failure (non-fatal)

**Phase type:** General — integration with external formatters, hard to unit-test in isolation.

### Phase 4: Session health checks

Two delivery mechanisms for the same health checks — SessionStart (primary) and Stop (fallback).

**SessionStart script:** `agent-core/hooks/sessionstart-health.sh` (matcher: `*`)
Fires after `/clear`, `/compact`, `--resume`. Writes session-scoped flag file (`$TMPDIR/health-{session_id}`) on fire.

**Stop fallback script:** `agent-core/hooks/stop-health-fallback.sh` (matcher: `*`)
Fires on every Stop event. Checks for flag file — if present (SessionStart already displayed), skip. If absent (new session, #10373), run health checks and write flag.

**Output:** systemMessage (user-targeted status, not agent context).

Three features:
1. **Dirty tree warning** — `git status --porcelain` → if non-empty, show warning
2. **Learnings health** — `learning-ages.py --summary` → one-liner (line count, entries ≥7 days, staleness)
3. **Stale worktree detection** — `git worktree list` → flag worktrees with no recent commits

Prerequisite: Add `--summary` flag to `agent-core/bin/learning-ages.py` (one-liner output for hook injection).

**Phase type:** General — shell integration, external command orchestration.

### Phase 5: Hook infrastructure + integration

**Hook configuration source of truth:** Create `agent-core/hooks/hooks.json` containing all hook registrations (matchers, script paths, timeouts). This is the source file — `.claude/settings.json` hooks section is generated output.

**sync-to-parent update:** Add hook config merge to `just sync-to-parent`:
- Helper script (`agent-core/bin/sync-hooks-config.py`) reads `hooks.json`, merges `hooks` key into `.claude/settings.json`, preserves non-hook settings (permissions, sandbox, plugins)
- Requires `dangerouslyDisableSandbox` (settings.json is in `denyWithinAllow`)

**Registration entries:**
- SessionStart: health script
- Stop: health fallback script
- PreToolUse Bash: recipe-redirect (alongside existing submodule-safety; preserve existing Write|Edit matchers)
- PostToolUse Write|Edit: auto-format (existing PostToolUse Bash matcher for submodule-safety unchanged)
- UserPromptSubmit: no change (same script, new behavior)

Restart required after deployment.

**Phase type:** General — tooling, configuration, verification.

## Key Decisions

- D-1: All hooks use command type (not prompt) — deterministic, fast, no LLM tokens
- D-2: Python for UserPromptSubmit (existing) and recipe-redirect (complex pattern matching). Bash for auto-format, SessionStart, and Stop fallback (simple command orchestration)
- D-3: PostToolUse auto-format runs file-specific ruff/docformatter, not full `just format`
- D-4: Session health uses dual delivery: SessionStart (primary) + Stop fallback (bypasses #10373 for new sessions)
- D-5: b: = brainstorm (diverge without converging, complements d: which converges)
- D-6: PreToolUse recipe-redirect is informative (additionalContext), not blocking (exit 0)
- D-7: Directives are additive and section-scoped, not first-match-wins
- D-8: Hook config source of truth is `agent-core/hooks/hooks.json`, merged into settings.json by sync-to-parent

## Scope

**IN:**
- UserPromptSubmit: 9 improvements (line-based matching, r expansion, xc/hc messages, additive directives, p: dual output, b: brainstorm, q:+learn:, skill-editing guard, ccg)
- PreToolUse: recipe-redirect hook
- PostToolUse: auto-format hook
- Session health: SessionStart + Stop fallback (3 health checks)
- learning-ages.py: --summary flag
- hooks.json: config source of truth
- sync-to-parent: hook config merge
- Restart verification

**OUT:**
- Sandbox denylist configuration (manual user setup, already documented)
- AskUserQuestion removal from communication.md (already done)
- Upstream fix for #10373

## Files Affected

| File | Action | Phase |
|------|--------|-------|
| `agent-core/hooks/userpromptsubmit-shortcuts.py` | Modify (839→~980 lines) | 1 |
| `agent-core/hooks/pretooluse-recipe-redirect.py` | New | 2 |
| `agent-core/hooks/posttooluse-autoformat.sh` | New | 3 |
| `agent-core/hooks/sessionstart-health.sh` | New | 4 |
| `agent-core/hooks/stop-health-fallback.sh` | New | 4 |
| `agent-core/bin/learning-ages.py` | Modify (add --summary) | 4 |
| `agent-core/hooks/hooks.json` | New (config source of truth) | 5 |
| `agent-core/bin/sync-hooks-config.py` | New (merge helper) | 5 |
| `justfile` (agent-core) | Modify (sync-to-parent recipe) | 5 |
