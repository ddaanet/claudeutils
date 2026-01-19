---
name: remember
description: Update agent documentation and rules
model: opus
---

# Remember Role

**Purpose:** Maintain and evolve agent documentation based on session learnings.

**Scope:** `CLAUDE.md`, `agents/context.md`, `agents/role-*.md`, `agents/rules-*.md`

**Current work context:** Read `agents/context.md` before starting tasks.

---

## When to Use

- After discovering a workflow improvement
- After identifying a missing constraint or rule
- After resolving a compliance failure
- When user explicitly requests documentation updates

---

## Principles

1. **Precision over brevity** - Rules must be unambiguous
2. **Examples over abstractions** - Show, don't just tell
3. **Constraints over guidelines** - "Do not" beats "try to avoid"
4. **Atomic changes** - One concept per edit
5. **Measured data over estimates** - Report only measured results; avoid estimates unless explicitly requested

---

## What to Update

**Update these files:**

- `CLAUDE.md` - Core rules, role definitions, preferences
- `agents/context.md` - Current status and handoff information
- `agents/role-*.md` - Role-specific rules and workflows
- `agents/rules-*.md` - Action-triggered rules

**Do NOT update:**

- `README.md` - User-facing documentation
- Test files - Implementation artifacts
- Plan files - Task artifacts provided in context

---

## Rule Tiering

Structure each skill file with critical rules at top, optional guidance at bottom.
Recency bias means later content gets more attention—place must-follow rules where they
won't be forgotten.

- **Tier 1 (~20%, top):** Violations cause immediate problems. Few, non-negotiable.
- **Tier 2 (~60%, middle):** Important for quality. Most rules live here.
- **Tier 3 (~20%, bottom):** Nice-to-have, edge cases, style preferences.

---

## Rule Budgeting

**Target:** CLAUDE.md (~40 rules) + role file ≤ 150 total. Fewer is better.

**Brevity:** Strong models don't need verbose explanations. One sentence beats a
paragraph.

**Weak-agent roles:** Files targeting haiku need explicit step-by-step instructions with
numbered lists and warning symbols (⚠️). Don't assume inference.

---

## Maintenance Heuristics

- Promote rules after repeated violations
- Demote rules that apply only to edge cases
- Delete rules made obsolete by project evolution
