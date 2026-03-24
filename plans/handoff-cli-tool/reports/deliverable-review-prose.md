# Prose+Config Review: handoff-cli-tool (RC8)

**Date:** 2026-03-24
**Design reference:** plans/handoff-cli-tool/outline.md
**Methodology:** agents/decisions/deliverable-review.md
**Scope:** Full-scope review. Four files (2 agentic prose, 2 configuration).
**Prior review:** RC7 prose review (0C/0M/0m).

## Files Reviewed

| File | Type | Delta (vs merge-base) |
|------|------|----------------------|
| agent-core/skills/handoff/SKILL.md | Agentic prose | +6/-2 (net +4) |
| agent-core/skills/design/SKILL.md | Agentic prose | +3/-4 (net -1) |
| .claude/settings.local.json | Configuration | +1/-1 |
| .gitignore | Configuration | +1/-1 |

## Critical Findings

None.

## Major Findings

None.

## Minor Findings

None.

## Per-File Assessment

### agent-core/skills/handoff/SKILL.md

**Axes evaluated:** Conformance, Functional correctness, Functional completeness, Vacuity, Excess, Actionability, Constraint precision, Determinism, Scope boundaries.

**Changes (4 commits in submodule: 52db16c..45f33d6):**
1. Fresh-write-resets-Completed rule added to Step 1 (52db16c)
2. Step 7 Precommit Gate inserted; old Step 7 renumbered to Step 8 (392e463)
3. `allowed-tools` expanded: `Bash(wc:*)` to `Bash(just:*,wc:*,git:*)` (4226b23)
4. `allowed-tools` expanded further: added `claudeutils:*` (45f33d6)

**Conformance:** Outline line 375: "Handoff skill must add `just precommit` as a pre-handoff gate (before calling `_handoff` CLI)." Step 7 (line 148-149) runs `just precommit` after all mutation steps (2-6) and before STATUS display (Step 8). The parenthetical "(before calling `_handoff` CLI)" describes a future state where the skill calls the CLI; the current skill does not call `_handoff` CLI (confirmed: no match for `_handoff` in file). The precommit gate is positioned correctly relative to the current skill structure: after writes, before display. Requirement satisfied.

**Functional completeness:** All `allowed-tools` additions correspond to commands used in the skill body: `just:*` for Step 7 (`just precommit`), `git:*` for Step 1 (`git diff HEAD`, `git rev-parse`), `claudeutils:*` for Step 2 (`claudeutils _worktree ls`). No missing tool permissions.

**Actionability:** Step 7 (line 149): "Run `just precommit` after all writes ... On failure: output the precommit result, STOP -- fix issues and retry. On success: continue to STATUS display." Directly executable, unambiguous stop/continue behavior, no interpretation needed.

**Constraint precision:** Gate applies after all mutation steps (2 through 6). No bypass path exists between Steps 2-6 and Step 8.

**Determinism:** Same inputs produce same gate behavior. Precommit is a deterministic validation (lint, format, test sentinel).

**Scope boundaries:** Skill scope unchanged -- steps 1-6, 7 (new), 8 (renumbered). Continuation section unchanged. Agent knows when to stop.

**Vacuity:** Step 7 performs real validation (lint, format, tests). Not ceremonial.

**Excess:** No content beyond what was specified.

### agent-core/skills/design/SKILL.md

**Axes evaluated:** Conformance, Functional correctness, Functional completeness, Vacuity, Excess, Actionability, Constraint precision, Determinism, Scope boundaries.

**Changes (1 commit in submodule: d85e7e7):** Simple routing restructured. Old steps 3-4 ("Execute: implement directly" then "Follow Continuation to /inline") collapsed to step 3 ("Follow Continuation to /inline") with explicit prohibition "Do NOT implement directly." Moderate routing collapsed from multi-step prose/non-prose branching to single-sentence routing.

**Conformance:** This change is outside the handoff-cli-tool plan's direct scope. Outline line 373 (OUT): "Skill modifications (commit/status skills updated separately)." The coupled skill update (line 375) names only the handoff skill. This design SKILL.md change addresses the "When skill steps offer competing execution paths" learning (agents/learnings.md) -- a separate bugfix, not a plan deliverable.

**Functional correctness (observation):** Old routing had steps 3-4 offering competing execution permissions ("implement directly" vs "chain to /inline"). New routing makes `/inline` the sole execution path. The prohibition "Do NOT implement directly" closes the loophole explicitly. Correct fix for the learning.

**Determinism:** Same classification produces same routing path. No ambiguity in step sequencing.

**Actionability:** Each routing path terminates in a single action (Follow Continuation). No interpretation needed.

**Excess:** The change is not specified by this plan's outline. However, it was delivered as a bugfix alongside the plan work (separate commit d85e7e7 with its own commit message). Not a conformance finding -- it's correctly scoped outside the plan. Included in this review because it was in the diff set provided.

### .claude/settings.local.json

**Axes evaluated:** Conformance, Functional correctness, Functional completeness, Vacuity, Excess.

Content: `{}` (empty JSON object with POSIX trailing newline). Merge-base had sandbox/permissions keys that were removed. Valid JSON. The file serves as a version-controlled placeholder for local settings that Claude Code auto-generates. No semantic change relevant to this plan.

**Conformance:** No specification in the outline for this file. Change is housekeeping.

### .gitignore

**Axes evaluated:** Conformance, Functional correctness, Functional completeness, Vacuity, Excess.

`/.vscode/` changed to `/.vscode`. Both patterns ignore the `.vscode` directory at project root. The trailing-slash form only matches directories; the no-slash form matches both files and directories named `.vscode`. Standard normalization -- `.vscode` is always a directory. No functional impact.

**Conformance:** No specification in the outline for this file. Change is housekeeping.

## Summary

| Severity | Count |
|----------|-------|
| Critical | 0 |
| Major | 0 |
| Minor | 0 |

Handoff skill precommit gate (Step 7) satisfies the outline's coupled skill update requirement. Allowed-tools additions are grounded in actual command usage within the skill body. Design SKILL.md change is outside plan scope (concurrent bugfix, not a plan deliverable). Configuration files contain formatting-only changes with no plan specification. Three consecutive review rounds (RC6, RC7, RC8) with 0C/0M/0m for the prose+config layer.
