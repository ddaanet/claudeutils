# Prose+Config Review: handoff-cli-tool (RC3)

**Design reference:** `plans/handoff-cli-tool/outline.md`
**Date:** 2026-03-23
**Scope:** Agentic prose (1 file) + configuration (2 files). Cumulative review of all plan-attributed changes.

## Files Reviewed

| File | Type | Delta |
|------|------|-------|
| `agent-core/skills/handoff/SKILL.md` | Agentic prose | +6/-2 |
| `.claude/settings.local.json` | Configuration | +1/-1 |
| `.gitignore` | Configuration | +1/-1 |

## Prior Finding Verification

| Finding | Round | Status |
|---------|-------|--------|
| C#1 (round 1): `Bash(wc:*)` missing `just:*`, `git:*` | R1 | FIXED — `Bash(just:*,wc:*,git:*,claudeutils:*)` |
| N-1 (round 2): Missing `Bash(claudeutils:*)` | R2 | FIXED — `claudeutils:*` present at line 4 |

## New Findings

No critical or major findings.

### Minor

**1. SKILL.md Step 7 placement diverges from outline wording**

- **File:** `agent-core/skills/handoff/SKILL.md:147-149`
- **Axis:** Conformance
- **Severity:** Minor

Outline says: "Handoff skill must add `just precommit` as a pre-handoff gate (before calling `_handoff` CLI)." SKILL.md places the precommit gate as Step 7 "after all writes (session.md, learnings.md, plan-archive.md)" — i.e. post-write, pre-STATUS. The skill does not call the `_handoff` CLI (skill-CLI integration deferred to `plans/skill-cli-integration/`), so "before calling `_handoff` CLI" has no anchor point. Current placement is the correct adaptation: validates after all file mutations, before display. When skill-CLI integration lands, the gate will need repositioning to satisfy the outline's "before calling `_handoff` CLI" placement. No action needed now — documenting for traceability.

**2. `.gitignore` and `.claude/settings.local.json` are outside outline scope**

- **Files:** `.gitignore:17`, `.claude/settings.local.json:1`
- **Axis:** Excess
- **Severity:** Minor

Neither file appears in the outline's IN scope. Changes are incidental cleanup during plan execution:
- `.gitignore`: `/.vscode/` changed to `/.vscode` — removes trailing slash so pattern matches sandbox char-device artifact (not a directory). Functionally correct.
- `.claude/settings.local.json`: Reduced from 9-line sandbox/permissions config to `{}`. Permissions now handled by `settings.json`. Functionally correct.

Both changes are benign and justified by their commit messages. No conformance issue — flagged only because they are attributed to this plan's deliverable set but have no design basis.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 2 |

All prior findings (C#1, N-1) verified fixed. Two minor observations: Step 7 placement is a correct adaptation of the outline's coupled-skill-update requirement given deferred CLI integration; two config files are out-of-scope cleanup included in the deliverable set.

**Verdict:** Pass. No blocking findings.
