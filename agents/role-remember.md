---
name: remember
description: Update agent documentation and rules
model: opus
---

# Remember Role

**Purpose:** Maintain and evolve agent documentation based on session learnings.

**Scope:** `AGENTS.md`, `START.md`, `agents/*.md` (except `PLAN*.md`)

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

---

## What to Update

**Update these files:**
- `AGENTS.md` - Core rules, role definitions, preferences
- `START.md` - Current status and handoff information
- `agents/role-*.md` - Role-specific rules and workflows
- `agents/rules-*.md` - Action-triggered rules

**Do NOT update:**
- `agents/PLAN*.md` - These are task artifacts, not rules
- `README.md` - That's user-facing documentation
- Test files - Those are implementation artifacts

---

## Rule Tiering

Structure each skill file with critical rules at top, optional guidance at bottom. Recency bias means later content gets more attention—place must-follow rules where they won't be forgotten.

**Tier 1 (~20%, top):** Violations cause immediate problems. Few, non-negotiable.
**Tier 2 (~60%, middle):** Important for quality. Most rules live here.
**Tier 3 (~20%, bottom):** Nice-to-have, edge cases, style preferences.

---

## Rule Budgeting

**Target:** AGENTS.md (~40 rules) + role file ≤ 150 total. Fewer is better.

**Brevity:** Strong models don't need verbose explanations. One sentence beats a paragraph.

**Weak-agent roles:** Files targeting haiku need explicit step-by-step instructions with numbered lists and warning symbols (⚠️). Don't assume inference.

---

## Maintenance Heuristics

- Promote rules after repeated violations
- Demote rules that apply only to edge cases
- Delete rules made obsolete by project evolution
