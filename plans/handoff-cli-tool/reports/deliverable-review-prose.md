# Prose+Config Review: handoff-cli-tool (RC10 Layer 1)

**Design reference:** plans/handoff-cli-tool/outline.md
**Prior review:** RC9 (0C/0M/0m)
**Methodology:** Full-scope fresh review per scoping-deliverable-review-iterations learning. No delta-scoping.

## Files Reviewed

| File | Type | Delta (cumulative, merge-base to HEAD) |
|------|------|----------------------------------------|
| agent-core/skills/handoff/SKILL.md | Agentic prose | +6/-2 |
| agent-core/skills/design/SKILL.md | Agentic prose | +3/-4 |
| .claude/settings.local.json | Configuration | +1/-1 (trailing newline) |
| .gitignore | Configuration | +1/-1 (`/.vscode/` to `/.vscode`) |

## Findings

None.

## Per-File Assessment

### agent-core/skills/handoff/SKILL.md

Three changes delivered across commits 52db16c..45f33d6..392e463:

**1. allowed-tools (line 4):** `Bash(wc:*)` expanded to `Bash(just:*,wc:*,git:*,claudeutils:*)`. Each glob maps to a skill step: `just:*` (Step 7 precommit), `git:*` (Steps 1/2 diff/status checks), `claudeutils:*` (Step 2 `_worktree ls`). No excess grants, no missing permissions.

**2. Fresh-write-resets-Completed (line 28):** Added at the generation point (Step 1) per the correctional-instructions learning. Codifies that fresh-write paths produce only current-conversation content. Consistent with outline H-2 "Overwrite" mode for first-handoff/committed state.

**3. Precommit Gate — Step 7 (lines 147-149):** Satisfies outline line 375 coupled skill update requirement. Concrete instruction: command (`just precommit`), failure behavior (output + STOP), success behavior (continue to STATUS). Deterministic gate. Correctly positioned after all mutation steps (2-6) and before display (Step 8). Step numbering updated: old Step 7 (Display STATUS) renumbered to Step 8.

**Design requirement check:** Outline says "before calling `_handoff` CLI." The skill does not yet call `_handoff` CLI (Skill integration is future scope per outline line 379). In the current architecture where the skill does writes itself, "after writes, before display" is the functionally equivalent position. The gate exists and will be correctly positioned when CLI integration happens.

**Actionability:** All three changes are concrete and unambiguous. No hedging or vague instructions.

**Constraint precision:** Precommit gate specifies exact command, exact failure behavior (STOP), exact success behavior. No agent judgment needed.

**Scope boundaries:** Skill's domain boundary unchanged. Steps 1-6 (gather + write), 7 (gate), 8 (display), continuation.

### agent-core/skills/design/SKILL.md

Single change (commit d85e7e7): Simple routing loophole fix.

**Conformance note:** Outline line 373 places "Skill modifications" in OUT scope. This change is a concurrent bugfix addressing the "competing execution paths" learning, not a plan deliverable. Reviewed because it was in the provided file set.

**Functional correctness:** Old routing had steps 3-4 offering competing permissions ("implement directly" then "chain to /inline"). Agent would execute at step 3, bypassing /inline corrector gates. New routing removes step 3, makes `/inline` the sole execution path via step 3 (Follow Continuation), with explicit prohibition ("Do NOT implement directly"). Closes the documented loophole.

**Actionability:** Three numbered steps, each with a concrete action. No ambiguity about what the agent does.

**Determinism:** Simple classification maps to exactly one routing path. No conditional branching within the path.

### .claude/settings.local.json

Content: `{}` with trailing newline added (POSIX compliance). No semantic change.

### .gitignore

`/.vscode/` changed to `/.vscode`. Removes trailing slash, broadening the pattern from directory-only to file-or-directory. Correctly ignores the `.vscode` character device created by Claude Code sandboxing (visible in filesystem as `crw-rw-rw-`). Both forms verified via `git check-ignore`.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 0 |
