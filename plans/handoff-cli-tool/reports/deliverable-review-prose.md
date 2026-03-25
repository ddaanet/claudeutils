# Prose & Config Review: handoff-cli-tool (RC12)

**Review round:** RC12 (full-scope)
**Design reference:** `plans/handoff-cli-tool/outline.md`
**Files reviewed:** 4 (2 agentic prose, 2 configuration)

## Findings

### handoff SKILL.md

**1.** handoff/SKILL.md:146 — actionability — **Minor**
Step 7 says "On failure: output the precommit result, STOP — fix issues and retry." The compound instruction is ambiguous: "STOP" in this codebase means halt for user intervention (communication rule 1, S-3 conventions), but "fix issues and retry" implies autonomous self-correction. These compete. Suggest: "On failure: output the precommit result, STOP — wait for guidance" to align with stop-on-unexpected rule.

**2.** handoff/SKILL.md:27 — constraint precision — **Minor**
"The CLI's committed detection (H-2) handles uncommitted prior handoffs; the skill always writes full state." References H-2 by identifier only. An agent encountering this line has no path to resolve "H-2" — it's an outline identifier, not a skill/CLI reference. Low impact since the behavioral instruction ("skill always writes full state") is self-contained, but the H-2 reference is inert prose.

### design SKILL.md

**3.** design/SKILL.md:135-142 — scope boundaries — **Minor**
The Simple and Moderate routing changes (commit `d85e7e7`) are a standalone bugfix for the "competing execution paths" learning, not a handoff-cli-tool deliverable. Outline line 373 lists "Skill modifications" as OUT. Included in this review's file set but structurally independent. No defect — scope attribution note.

### .claude/settings.local.json

**4.** .claude/settings.local.json — vacuity — **Minor**
Change adds a trailing newline to `{}`. POSIX line-ending compliance. No functional effect.

### .gitignore

**5.** .gitignore:17 — scope boundaries — **Minor**
`/.vscode/` to `/.vscode` broadens from directory-only to file-or-directory match. Correctly handles the `.vscode` character device created by sandbox. Unrelated to handoff-cli-tool plan scope — incidental fix.

## Completeness Check

- **Precommit gate in handoff skill:** Delivered (Step 7, line 146). `just precommit` runs after all writes, before STATUS display.
- **CLI invocation from handoff skill:** Not present. The outline's "Coupled skill update" says "(before calling `_handoff` CLI)" but `skill-cli-integration` plan (`plans/skill-cli-integration/brief.md`) explicitly defers this: "/handoff skill — currently writes session.md directly. Should compose with `_handoff` CLI." The coupled update scope is the precommit gate only; CLI composition is future work.
- **allowed-tools:** Correctly expanded to `Bash(just:*,wc:*,git:*,claudeutils:*)` — each glob maps to a required step.
- **Legacy detection removal:** Lines 27-28 (old uncommitted-prior-handoff detection + merge directive) correctly removed. CLI's H-2 owns this.
- **Handoff state file in .gitignore:** Not needed — `tmp/.handoff-state.json` is covered by existing `/tmp/` entry (line 6).
- **settings.local.json relevance:** Trailing newline only. No plan-related content.

## Summary

- Critical: 0
- Major: 0
- Minor: 5 (1 actionability, 1 constraint precision, 2 scope attribution, 1 vacuity)

All changes are functionally correct. The handoff SKILL.md delivers the coupled skill update specified by the outline. No missing deliverables within the scoped interpretation (precommit gate + legacy removal). The two minors on handoff SKILL.md (findings 1-2) are polish items with no functional impact.
