# Session Handoff: 2026-01-27

**Status:** Pre-edit rule files implemented; ready for remaining skill implementations

## Completed This Session

**Documentation cleanup (Sonnet):**
- Reviewed context.md for currentness (obsolete markdown formatter content)
- Deleted obsolete plans: formatter-comparison.md, markdown-fence-aware-processing.md
- Deleted obsolete archive: 2026-01-07-markdown-formatter.md
- Updated context.md with current skill improvement work
- Decision already preserved in agents/design-decisions.md:711-772

**Process failure diagnosis (Opus):**
- Sonnet failed to load `plugin-dev:skill-development` before editing SKILL.md (per CLAUDE.md Pre-Edit Checks)
- Root cause: Documentation-only enforcement relies on model memory/attention - unreliable
- Investigated alternatives: hooks (PreToolUse can't detect skill loading state), nested CLAUDE.md (concerns about .claude/ subdirs)
- Solution: `.claude/rules/` with `paths` frontmatter provides hierarchical behavior

**Rule-based pre-edit enforcement implementation (Sonnet):**
- Verified with claude-code-guide agent: rule files cannot invoke tools, only provide context
- Accepted limitation: rules improve discoverability but don't enforce behavior
- Created 4 rule files in `.claude/rules/` with paths frontmatter
  - `skill-development.md` → `.claude/skills/**/*`
  - `hook-development.md` → `.claude/hooks/**/*`
  - `agent-development.md` → `.claude/agents/**/*`
  - `command-development.md` → `.claude/commands/**/*`
- Removed Pre-Edit Checks table from CLAUDE.md (13 lines)
- Fixed justfile sandbox issue (user-fixed: removed /tmp test, then tracing)
- Commit: 3dc94a9 with gitmoji 🔧
- Precommit passed

## Pending Tasks

**Ready for Sonnet implementation:**

- [ ] **Implement handoff-lite skill** - Create `.claude/skills/handoff-lite/SKILL.md`
  - Design: `plans/handoff-skill/design.md`
  - Mechanical handoff for efficient models, embedded template, no reference reads

- [ ] **Implement commit-context skill** - Create `.claude/skills/commit-context/SKILL.md`
  - Design: `plans/commit-context/design.md`
  - Context-aware commit, skips git discovery

- [ ] **Fix learnings discoverability** - Update `.claude/skills/handoff/SKILL.md`
  - Problem: `plans/learnings-management/problem.md`
  - Inline @ chain, size measurement, add-learning.py from references

**Ready for Sonnet implementation (docs refactoring):**

- [ ] **Create decisions/ structure** - Split design-decisions.md into domain files
  - Design: `plans/docs-to-skills/design.md`
  - Create `agents/decisions/` with cli.md, testing.md, workflows.md, delegation.md, architecture.md
  - Extract content from design-decisions.md by domain
  - Create rule files in `.claude/rules/` pointing to domain docs

- [ ] **Refactor CLAUDE.md** - Reduce to ~100 lines of core principles
  - Design: `plans/docs-to-skills/design.md`
  - Move domain content to decisions/*.md
  - Keep: Workflow Selection, Documentation Structure, Terminology, Core Principles
  - Remove: Delegation Principle, Bash Scripting, File System Rules, Tool Batching

- [ ] **Update /remember skill routing** - Route learnings to domain docs
  - Design: `plans/docs-to-skills/design.md`
  - Update `agent-core/skills/remember/skill.md` routing table
  - Add domain inference logic
  - Route to decisions/*.md instead of monolithic design-decisions.md

**Deferred to separate design sessions:**

- [ ] **Model awareness** - Make `/model` switches visible to agents
  - Problem: `plans/model-awareness/problem.md`

- [ ] **Plan-TDD skill** - Add guidance to avoid presentation tests
  - Problem: `plans/plan-tdd-skill/problem.md`

**Deferred until after process improvements:**

- [ ] **Process pending learnings** - `/remember` to consolidate staged learnings
- [ ] **Remove "uv run" references** - Audit subprocess calls
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

**Rule files are passive context, not enforcement:**
- Rule files inject text context but cannot invoke tools or enforce behavior
- Improvement over monolithic CLAUDE.md: contextual guidance appears when editing matching files
- Trade-off: Better discoverability through automatic loading, but still relies on model compliance
- Decision: Proceed with rule files (contextual guidance beats CLAUDE.md bloat)

@agents/learnings/pending.md

---

Git status: Clean working tree, branch skills
Current HEAD: 3dc94a9 (🔧 Add path-based rule files for domain context injection)
