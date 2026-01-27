# Context

---

## Current State

**Branch:** `skills`

**Current work:** Skill improvement implementations (pre-edit rules, handoff-lite, commit-context)

**Status:** Three designs ready for implementation (see session.md for details)

### Completed

**Process failure diagnosis (2026-01-27):**
- Identified unreliability of documentation-only enforcement for pre-edit skill loading
- Designed rule-based solution using `.claude/rules/` with `paths` frontmatter
- Three rule files will provide automatic context injection when editing domain files

### Ready for Implementation

**Pre-edit rule files:**
- `.claude/rules/skill-development.md` → paths: `.claude/skills/**/*`
- `.claude/rules/hook-development.md` → paths: `.claude/hooks/**/*`
- `.claude/rules/agent-development.md` → paths: `.claude/agents/**/*`
- Each ~10 lines with paths frontmatter and skill loading reminder
- Removes need for Pre-Edit Checks table in CLAUDE.md

**handoff-lite skill:**
- Design: `plans/handoff-skill/design.md`
- Mechanical handoff for efficient models, embedded template, no reference reads

**commit-context skill:**
- Design: `plans/commit-context/design.md`
- Context-aware commit, skips git discovery

**Learnings discoverability fix:**
- Problem: `plans/learnings-management/problem.md`
- Update `.claude/skills/handoff/SKILL.md` with inline @ chain, size measurement, add-learning.py

---

## Handoff

**⚠️ STOP: Do not execute tasks below unless user explicitly requests it.**

See session.md for full task list. Current priorities:
- Pre-edit rule files (3 files)
- handoff-lite skill implementation
- commit-context skill implementation
- Learnings discoverability fix

---

## Recent Decisions

**2026-01-27: Rule-based Pre-Edit Enforcement**
- **Decision:** Use `.claude/rules/` with `paths` frontmatter for pre-edit skill loading
- **Rationale:**
  - Documentation-only enforcement unreliable (relies on model memory/attention)
  - Hooks can't detect skill loading state (only see tool inputs, not conversation context)
  - Rules with path prefixes provide automatic context injection
- **Implementation:** Three rule files replace Pre-Edit Checks table in CLAUDE.md

**2026-01-13: Model Selection for Delegation** (from previous context)
- Use haiku for execution tasks, opus only for architecture/planning
- Cost impact from wrong model selection can be significant
- Haiku sufficient for straightforward execution tasks

---

## Blockers

**None currently.** Three designs ready for implementation.
