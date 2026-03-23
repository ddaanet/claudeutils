# Prose & Config Deliverable Review (RC5)

**Design reference:** `plans/handoff-cli-tool/outline.md`
**Date:** 2026-03-23
**Scope:** Four files (2 agentic prose, 2 configuration). Full-scope review.
**Prior review:** RC4 prose review (0C/0M/1m).

## Files Reviewed

| File | Type | Delta (vs main) |
|------|------|-----------------|
| `agent-core/skills/design/SKILL.md` | Agentic prose | +3/-17 (net -14) |
| `agent-core/skills/handoff/SKILL.md` | Agentic prose | +6/-2 (net +4) |
| `.claude/settings.local.json` | Configuration | +1/-1 (trailing newline) |
| `.gitignore` | Configuration | +1/-1 |

## RC4 Finding Verification

| RC4 Finding | Status |
|-------------|--------|
| m-1: design/SKILL.md change outside plan scope | Persists (observation) — design SKILL.md change remains attributed to this plan. Not actionable within plan scope. |

## Findings

### Critical

None.

### Major

None.

### Minor

None.

## Per-File Assessment

### `agent-core/skills/handoff/SKILL.md`

**Changes from main:**
1. `allowed-tools` expanded from `Bash(wc:*)` to `Bash(just:*,wc:*,git:*,claudeutils:*)`
2. Step 7 "Precommit Gate" inserted before STATUS display (old Step 7 renumbered to Step 8)

**Conformance:** The outline states: "Handoff skill must add `just precommit` as a pre-handoff gate (before calling `_handoff` CLI)." Step 7 runs `just precommit` after all file mutations (session.md, learnings.md, plan-archive.md) and before Step 8 (STATUS display). The gate is positioned after writes but before any downstream handoff output, satisfying the design intent. The skill does not yet call `_handoff` CLI (that integration is deferred per "Skill integration (future)"), so "before calling `_handoff` CLI" has no current anchor. The gate is correctly positioned relative to what exists: after mutations, before display.

**Functional correctness:** The gate instruction specifies failure behavior ("output the precommit result, STOP -- fix issues and retry") and success behavior ("continue to STATUS display"). Both paths are unambiguous. The `allowed-tools` addition of `just:*` is necessary for `just precommit` to execute within the skill's sandbox.

**Functional completeness:** All three file mutations that could introduce precommit-failing content (session.md, learnings.md, plan-archive.md) are enumerated as preceding the gate. No mutation path bypasses it.

**Vacuity:** The gate performs real work -- `just precommit` runs format, lint, and test checks. Not ceremonial.

**Excess:** The `git:*` and `claudeutils:*` additions to `allowed-tools` are forward-looking (skill-CLI integration is deferred). However, the skill already uses `git diff HEAD` in Step 1 (prior handoff detection) and `claudeutils _worktree ls` in Step 2 (command derivation). These tool permissions were previously missing -- the skill relied on the calling agent's tool permissions. Adding them is a correctness fix, not excess.

**Actionability:** "Run `just precommit` after all writes" is directly executable. "On failure: output the precommit result, STOP" maps to observable actions. "fix issues and retry" is appropriately open-ended for error recovery.

**Constraint precision:** No judgment words. "after all writes" is enumerable. "On failure / On success" is binary.

**Determinism:** Step ordering (7 before 8) is unambiguous. Same precommit failures produce the same stop behavior.

**Scope boundaries:** Changes are limited to `allowed-tools` line and a new step. No other skill content modified.

### `agent-core/skills/design/SKILL.md`

**Changes from main:** Simple routing (line 135-139) restructured:
- Removed "Execute: check for applicable skills and project recipes first, then implement directly" (step 3)
- Removed Moderate agentic-prose path (7-line inline-plan generation sub-procedure)
- Removed Moderate non-prose path (7-line outline generation sub-procedure)
- Added "Do NOT implement directly -- `/inline` provides corrector gates and triage feedback"
- Moderate routing collapsed to single-line per path

**Conformance:** The outline's Scope OUT says "Skill modifications (commit/status skills updated separately)." The coupled skill update exception names only the handoff skill. This change is outside plan scope.

**Functional correctness:** The change is correct. It closes the "competing execution paths" loophole documented in learnings ("When skill steps offer competing execution paths"). The old Simple routing had step 3 "implement directly" competing with step 4's chain to `/inline`. The new version removes the direct-implementation permission and makes `/inline` the sole execution path.

The Moderate routing collapse is also correct. The expanded sub-procedures duplicated guidance that belongs in `/inline` and `/runbook` respectively. The collapsed form routes to the right downstream skill without redundant inline instructions.

**Excess:** Outside plan scope. The fix is valid but should be attributed elsewhere. Observation only -- no action needed, consistent with RC4 finding.

### `.claude/settings.local.json`

Content: `{}` (3 bytes: `{`, `}`, newline). The diff shows `+1/-1` which is a trailing newline normalization. No semantic change. No findings.

### `.gitignore`

`/.vscode/` changed to `/.vscode`. The trailing slash removal means the pattern now matches both a file and a directory named `.vscode` at the root. Git's default behavior already matches directories without trailing slashes, so this is a minor normalization that broadens the pattern slightly (also matches a hypothetical `.vscode` file). Functionally correct for IDE artifact exclusion. Outside plan scope but benign.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 0 |

The RC4 minor finding (design SKILL.md scope attribution) persists as an observation but does not warrant a new finding -- it was already identified and dispositioned in RC4. All four files are functionally correct. The handoff skill precommit gate satisfies the outline's coupled skill update requirement. No new findings.

**Verdict:** Pass. No blocking findings.
