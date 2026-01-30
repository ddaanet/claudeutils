# Design: Handoff-Lite Skill Misuse Fixes

**Input:** `plans/handoff-lite-issue/transcript.md` (root cause analysis)
**Scope:** Fix skill design issues that caused handoff-lite misuse and learnings deletion
**Review:** `plans/handoff-lite-fixes/design-review.md` (APPROVE WITH CHANGES — all applied)

## Problem Statement

During `/commit --context` execution, a Sonnet agent invoked `/handoff-lite` (Haiku-only) instead of `/handoff`, then interpreted the template as "replace session.md structure" rather than "augment", deleting the Recent Learnings section.

Root causes and fixes below. Note: `/commit-context` is becoming `/commit --context` (flag on commit skill); this design uses the new syntax.

---

## Fix 1: Remove Handoff from Commit Skill

**Problem:** `commit/SKILL.md` Step 2 says "Run `/handoff` skill to update session.md". The `--context` path (formerly commit-context) had it as Step 1. Ambiguous whether agent invokes it or user does.

**Analysis:** Coupling handoff into commit was a premature optimization to prevent "need to squash separate handoff commits." But it creates:
- Ambiguity about who invokes (agent vs user)
- Risk of wrong skill variant selection
- Conceptual confusion: commit = capture changes in git; handoff = preserve session context for next agent

**Decision: Decouple handoff from commit skill entirely.**

Rationale:
- Commit should do one thing: commit code changes
- Handoff should do one thing: update session context
- User controls when each happens
- Expected workflow: `/handoff` then `/commit` (or `/commit --context`) as two commands
- The "squash separate commits" concern is minor compared to the misuse risk

**Changes to `commit/SKILL.md`:**
- Remove the "Perform handoff" step from both the standard and `--context` execution paths
- Add note at top of Execution Steps: "This skill does not update session.md. Run `/handoff` separately before committing if session context needs updating."
- Renumber remaining steps
- Add to staging guidance: "Include `agents/session.md` and `plans/` files if they have uncommitted changes" — this ensures session.md gets committed when the user has already run `/handoff`

**Cross-reference note:** The commit skill currently references `/handoff` in the handoff step. Removing the step eliminates this cross-reference entirely (no explicit update needed — Fix 4 covers remaining refs).

---

## Fix 2: Handoff-Haiku Template — Partial Template with Explicit Merge Semantics

**Problem:** Template says "Use this embedded template" — agent interpreted as "replace session.md with this structure." Existing Recent Learnings section was deleted.

**Analysis:** The word "template" implies a blank form to fill in. The template shows a complete session.md structure with `Session Notes` but no `Recent Learnings`, so learnings vanish. "Preserve everything mechanically" refers to content preservation (don't judge importance), not structural preservation (keep existing sections).

**Decision: Replace full template with partial template + explicit PRESERVE/ADD/REPLACE merge rules.**

Keep merge semantics inline in SKILL.md (not in `references/`). Haiku benefits from having everything in one file, and the skill stays well under 2000 words even with additions.

**New Step 2 content for `handoff-haiku/SKILL.md`:**

```markdown
### 2. Update session.md

**Merge rules — read current session.md first, then apply:**
- **REPLACE** these sections with fresh content: "Completed This Session", "Pending Tasks", "Blockers / Gotchas", "Next Steps"
- **ADD** "Session Notes" section if new observations to record
- **PRESERVE UNCHANGED** all other existing sections (especially "Recent Learnings", "Reference Files", any "Prior Session" content)

**How to apply:**
1. Read current session.md
2. Update header (date, status line)
3. Replace ONLY the sections listed under REPLACE with fresh content
4. Add Session Notes section if new observations exist
5. Keep everything else exactly as-is

**Template for sections being replaced/added:**

## Completed This Session
[Bullet list of completed work with commit hashes/file refs]

## Pending Tasks
[Bullet list with checkboxes]

## Session Notes
[Raw observations, discoveries, issues encountered - NO FILTERING]
[Preserve verbatim what happened, let standard model judge later]

## Blockers / Gotchas
[Any blockers or warnings for next agent]

## Next Steps
[Immediate next action]

**CRITICAL:** Do NOT delete existing sections not shown above. session.md may contain
sections from prior handoffs (Recent Learnings, Reference Files, etc.) that MUST be preserved.
```

---

## Fix 3: Model Constraint — Rename to `handoff-haiku`

**Problem:** Agent (Sonnet) invoked `handoff-lite` ignoring "Target Model: Haiku" text. The constraint wasn't salient enough.

**Analysis of options:**
- **A. Runtime enforcement** — Not possible with current skill system
- **B. Description emphasis** — Already stated; making it bolder won't stop efficiency-seeking agents
- **C. Rename to `handoff-haiku`** — Name encodes the constraint; agents self-select out

**Decision: Rename `handoff-lite` to `handoff-haiku`.**

Rationale:
- Name is the most salient metadata — agents see it in skill lists
- "handoff-haiku" immediately signals "this is for Haiku models"
- "handoff-lite" sounds like "lighter/simpler handoff" which invites misuse
- Establishes pattern: model-specific skills include model name

**Changes:**
- Rename directory: `agent-core/skills/handoff-lite/` → `agent-core/skills/handoff-haiku/`
- Update SKILL.md frontmatter: `name: handoff-haiku`
- Update all cross-references (see Fix 4)

---

## Fix 4: Cross-Reference Updates and Convention

**Problem:** Skills referencing other skills didn't specify exact variants.

**Convention established:** When a skill references another skill:
- Name the exact skill: `/handoff` (not "a handoff skill")
- If model-dependent, state criteria: "Use `/handoff` (Sonnet/Opus) or `/handoff-haiku` (Haiku only)"

**Changes:**

`handoff-haiku/SKILL.md` (formerly handoff-lite):
- Update frontmatter name and description (see Fix 5)
- Line 8: "For full handoff protocol with learnings processing, use `/handoff` skill (Sonnet/Opus)."

`handoff/SKILL.md`:
- Line 21: "handoff-lite" → "handoff-haiku"
- Lines 171-175: "handoff-lite" → "handoff-haiku" in the reviewing-efficient-model-handoffs section

No other skills reference handoff-lite. Commit skill cross-references eliminated by Fix 1.

---

## Fix 5: Description Differentiation and Invocability

**Problem:** `handoff-lite` and `handoff` share identical trigger phrases ("end session", "handoff", "update session context"). Both match the same user input; agent picks whichever sounds simpler.

**Decision: Eliminate trigger overlap. Mark handoff-haiku as non-user-invocable.**

`handoff` description — no change needed (default, matches all standard triggers):
```yaml
description: This skill should be used when the user asks to "handoff", "update session", "end session", or mentions switching agents. Updates session.md with completed tasks, pending work, blockers, and learnings for seamless agent continuation.
```

`handoff-haiku` — new frontmatter:
```yaml
---
name: handoff-haiku
description: Internal skill for Haiku model orchestrators only. Not for Sonnet or Opus — use /handoff instead. Mechanical session context preservation without learnings judgment.
user-invocable: false
---
```

Key changes:
- Removed all overlapping trigger phrases
- Leads with "Internal skill for Haiku model orchestrators only"
- Negative routing: "Not for Sonnet or Opus — use /handoff instead"
- `user-invocable: false` prevents appearance in user-facing skill lists
- Haiku orchestrators invoke by exact name when instructed by orchestration plan

---

## Reviewer Decisions

**Q1 — User workflow after decoupling:**
Option A. `/handoff` then `/commit` (or `/commit --context`) as two commands. Document in commit skill: "This skill does not update session.md. Run `/handoff` separately before committing if session context needs updating."

**Q2 — Session.md commit timing:**
Commit skills auto-stage `agents/session.md` and `plans/` files if they have uncommitted changes. No new workflow — just smart staging guidance.

**Q3 — Haiku orchestrator handoff pattern:**
Haiku invokes `/handoff-haiku` when told by the orchestration plan, typically at the end of an execution step before returning control. The orchestrator (Sonnet) explicitly tells the Haiku agent to run handoff-haiku.

**Q4 — Migration path:**
No migration. Leave existing session.md as-is. Template footer updates naturally on next handoff. No references to "handoff-lite" exist in current session.md.

**Q5 — Merge semantics inline vs references:**
Keep inline. Haiku needs everything in one file. Skill stays well under 2000 words even with additions (~600 words after changes).

**Fix 6 (writing style):**
Dropped as separate fix per reviewer recommendation. Current phrasing is already correct imperative form. Polish during implementation if needed.

---

## Summary of Changes

| File | Change |
|------|--------|
| `commit/SKILL.md` | Remove handoff step from both standard and `--context` paths, add "does not update session.md" note, add session.md/plans/ staging guidance, renumber steps |
| `handoff-lite/` → `handoff-haiku/SKILL.md` | Rename dir+file, new frontmatter (name, description, user-invocable:false), partial template with PRESERVE/ADD/REPLACE merge rules, cross-reference updates |
| `handoff/SKILL.md` | Update "handoff-lite" → "handoff-haiku" in lines 21 and 171-175 |

## Affected Files

- `agent-core/skills/commit/SKILL.md`
- `agent-core/skills/handoff-lite/SKILL.md` (rename to `handoff-haiku/`)
- `agent-core/skills/handoff/SKILL.md`

Note: `commit-context/SKILL.md` changes handled by the `/commit --context` merge in another session.

## Out of Scope

- Runtime model-constraint enforcement (no mechanism exists)
- Skill routing/dispatch system changes (premature)
- Changes to `handoff/references/template.md` (the full handoff template is fine)
- Changes to session.md content (already restored)
- `/commit --context` merge (separate session)

## Validation

After implementation:
- `handoff-haiku/SKILL.md` has PRESERVE/ADD/REPLACE merge rules with partial template
- `handoff-haiku` description has NO overlapping trigger phrases with `handoff`
- `handoff-haiku` has `user-invocable: false`
- `commit/SKILL.md` has no handoff step in any execution path
- `commit/SKILL.md` has session.md/plans/ staging guidance
- No remaining references to "handoff-lite" in skill files
- Test: Haiku agent running `/handoff-haiku` preserves existing Recent Learnings section
