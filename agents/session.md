# Session Handoff: 2026-01-27

**Status:** Process failure diagnosed; rule-based solution designed for pre-edit skill loading

## Completed This Session

**Process failure diagnosis (Opus):**
- Sonnet failed to load `plugin-dev:skill-development` before editing SKILL.md (per CLAUDE.md Pre-Edit Checks)
- Root cause: Documentation-only enforcement relies on model memory/attention - unreliable
- Investigated alternatives: hooks (PreToolUse can't detect skill loading state), nested CLAUDE.md (concerns about .claude/ subdirs)
- Solution: `.claude/rules/` with `paths` frontmatter provides hierarchical behavior

**Designed rule-based pre-edit enforcement:**
- Three rule files with path prefixes trigger skill loading reminders
- `.claude/rules/skill-development.md` → paths: `.claude/skills/**/*`
- `.claude/rules/hook-development.md` → paths: `.claude/hooks/**/*`
- `.claude/rules/agent-development.md` → paths: `.claude/agents/**/*`
- Each rule reminds to load corresponding `/plugin-dev:*` skill before editing

## Pending Tasks

**Ready for Sonnet implementation:**

- [ ] **Create pre-edit rule files** - `.claude/rules/{skill,hook,agent}-development.md`
  - Each ~10 lines with paths frontmatter and skill loading reminder
  - Provides automatic context injection when editing domain files
  - Remove Pre-Edit Checks section from CLAUDE.md (rules replace it)

- [ ] **Implement handoff-lite skill** - Create `.claude/skills/handoff-lite/SKILL.md`
  - Design: `plans/handoff-skill/design.md`
  - Mechanical handoff for efficient models, embedded template, no reference reads

- [ ] **Implement commit-context skill** - Create `.claude/skills/commit-context/SKILL.md`
  - Design: `plans/commit-context/design.md`
  - Context-aware commit, skips git discovery

- [ ] **Fix learnings discoverability** - Update `.claude/skills/handoff/SKILL.md`
  - Problem: `plans/learnings-management/problem.md`
  - Inline @ chain, size measurement, add-learning.py from references

**Deferred to separate design sessions:**

- [ ] **Model awareness** - Make `/model` switches visible to agents
  - Problem: `plans/model-awareness/problem.md`

- [ ] **Plan-TDD skill** - Add guidance to avoid presentation tests
  - Problem: `plans/plan-tdd-skill/problem.md`

**Deferred until after process improvements:**

- [ ] **Process pending learnings** - `/remember` to consolidate staged learnings
- [ ] **Remove "uv run" references** - Audit subprocess calls
- [ ] **Review context.md from main** - Markdown formatter migration status
- [ ] **Evaluate bin/poptodo and bin/shelve** - Integration with shelve skill
- [ ] **Session size tooling** - Add @ chain line count to add-learning.py or standalone script (needs test suite)

## Blockers / Gotchas

**None currently.**

## Next Steps

Sonnet can implement the three ready designs (`handoff-lite`, `commit-context`, learnings discoverability fix) independently.

## Recent Learnings

**Documentation-only enforcement is unreliable:**
- Anti-pattern: Relying on CLAUDE.md tables/rules for mandatory behavior (model may skip/forget)
- Correct pattern: Use `.claude/rules/` with `paths` frontmatter for automatic context injection
- Rationale: Rules load automatically when working with matching files - no model memory required

**Hooks can't enforce "load skill before action":**
- PreToolUse hooks can intercept tool calls but can't detect conversation context (skill loading state)
- Hook agent gets tool input, transcript path - but not semantic context of main agent
- Hooks are for validating/blocking actions, not enforcing prerequisite context

**Rules `paths` vs nested CLAUDE.md:**
- `paths` frontmatter controls WHEN rule loads (conditional on file pattern)
- Multiple rule files with different path prefixes = hierarchical behavior
- Nested CLAUDE.md in .claude/ subdirs works but rules pattern is cleaner

@agents/learnings/pending.md

---

Git status: Clean working tree, branch skills
Current HEAD: 4308e30 (📋 Session handoff: skill improvement designs complete)
