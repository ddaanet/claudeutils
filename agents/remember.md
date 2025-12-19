---
name: remember
description: Documentation updates and rules maintenance
---

# Remember Skill

**Agent:** Strong models (opus/sonnet). See also `planning.md`.

**Prerequisite:** `AGENTS.md`

---

## Documentation Scope

**Update when relevant:**
- `agents/DESIGN_DECISIONS.md` - Architectural choices and rationale
- `agents/STEP*_COMPLETION.md` - Completion notes for handoff

**Avoid:**
- Hardcoded counts (use `just test` for dynamic status)
- Proactive documentation unless requested

---

## Rules Budgeting

**Target:** AGENTS.md (~40 rules) + skill file ≤ 150 total. Fewer is better.

**Brevity:** Strong models don't need verbose explanations. One sentence beats a paragraph.

**Weak-agent skills:** Files targeting haiku need explicit step-by-step instructions with numbered lists and warning symbols (⚠️). Don't assume inference.

Sessions load AGENTS.md plus one skill file. Exception: commit.md and handoff.md load at session end where recency bias helps, so they're effectively budget-exempt.

**Maintenance heuristics:**
- Promote rules after repeated violations
- Demote rules that apply only to edge cases
- Delete rules made obsolete by project evolution

---

## Rule Tiering

Structure each skill file with critical rules at top, optional guidance at bottom. Recency bias means later content gets more attention—place must-follow rules where they won't be forgotten.

**Tier 1 (~20%, top):** Violations cause immediate problems. Few, non-negotiable.
**Tier 2 (~60%, middle):** Important for quality. Most rules live here.
**Tier 3 (~20%, bottom):** Nice-to-have, edge cases, style preferences.
