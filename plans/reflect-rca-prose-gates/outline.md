# Outline: Prose Gates Fix (D+B Hybrid)

Refines original design.md based on critical analysis. Replaces Option D with D+B hybrid.

## Principle

Eliminate standalone prose gates. Merge each gate into its adjacent action step, with gate's tool call as the step's first instruction.

## Change 1: Commit Skill — Merge Steps 0 + 0b + 1

**Current:** Three separate steps (0 → 0b → 1), first two prose-only, third has bash.

**Proposed:** Single step with two gate prefixes before the action.

```
### 1. Pre-commit validation

**Gate A — Session freshness:**
Read `agents/session.md`.
[evaluation criteria — same as current]
If stale: run /handoff first. Return here after.

**Gate B — Vet checkpoint:**
```bash
git diff --name-only $(git merge-base HEAD @{u} 2>/dev/null || echo HEAD~5)
git status --porcelain
```
[classify files, check for vet report]
If unvetted production artifacts: STOP, delegate to vet-fix-agent.

**Validation:**
```bash
just precommit
git diff --cached --stat
```
```

**Why this works:**
- No step boundary to skip — gates are paragraphs within the action step
- Each gate opens with a tool call (Read, Bash) — registers as actionable
- Action is conditional on gate pass — explicit flow, not separate step

**Fixes step 0b baseline bug:** `git merge-base` scopes to session branch divergence, not just last commit.

## Change 2: Orchestrate Skill — Restructure 3.4 as Control Flow

**Current:** 3.4 is a separate prose subsection agents scan past to reach 3.5/next cycle.

**Proposed:** Merge phase detection into 3.3 (post-step verification) with explicit conditional:

```
### 3.3 Post-step verification and phase boundary

After agent returns:
```bash
git status --porcelain
```
[existing tree check]

**Phase boundary — Read next step:**
Read `plans/<name>/steps/step-{N+1}.md` (first 10 lines).

IF `Phase:` field differs from current step's phase (or no next step):
  → Delegate to vet-fix-agent checkpoint. Template:
  [existing template]
  → Do NOT proceed until checkpoint agent returns.

IF same phase:
  → Proceed to 3.5.
```

**Why different from commit skill:** This is a conditional branch in a loop, not a sequential gate. The fix is control flow (if/then with explicit branch targets), not just Read-anchoring.

## Change 3: Convention — Point-of-Violation, Not Fragment

**Don't create** `skill-design-convention.md`. A prose rule against prose rules is circular.

**Instead:** Add a structural comment at the top of each skill template:

```
<!-- DESIGN RULE: Every step must open with a tool call (Read/Bash/Glob).
     Prose-only steps get skipped. See: learnings.md "Prose skill gates" -->
```

Place at the authoring point (skill file header), not a separate fragment agents must discover.

**Future enforcement:** Lint script that parses skill .md files, flags steps without a tool call in first 3 lines. Not in scope for this fix but is the real long-term solution.

## Change 4: Decision Documentation

- `agents/decisions/implementation-notes.md` — add entry for D+B hybrid rationale
- `agents/learnings.md` — update "Prose skill gates skipped" learning to reference the fix (or remove if convention is documented)

## Files Touched

| File | Change |
|---|---|
| `agent-core/skills/commit/SKILL.md` | Merge steps 0+0b+1 into single gated step |
| `agent-core/skills/orchestrate/SKILL.md` | Merge 3.4 into 3.3, add control flow |
| `agents/decisions/implementation-notes.md` | Decision entry |
| `agents/learnings.md` | Update/remove superseded learning |

## What This Doesn't Do

- No new files (scripts, fragments, hooks)
- No changes to hook infrastructure
- No changes to other skills (apply convention going forward, not retroactively)
