# Prose Infrastructure Batch

Four small changes to agent infrastructure: one skill removal, one skill creation, one skill fix, one new rule + validator.

## Requirements

### Functional Requirements

**FR-1: Remove opus-design-question skill**
Delete the opus-design-question skill and all references to it. The skill encouraged lazy delegation to opus instead of running opus directly — leads to bad outcomes (circular delegation, context loss).
- Delete: `agent-core/skills/opus-design-question/` (skill directory)
- Edit: `agent-core/fragments/design-decisions.md` — remove the rule directing agents to use this skill. Replace with guidance: "If you need opus-level reasoning, the user sets the model. Do not delegate design decisions to a sub-agent."
- Grep: all skill files, agent definitions, and fragments for references to `opus-design-question` — remove each
- Acceptance: no reference to opus-design-question anywhere in the codebase
- Restart required (skill removal)

**FR-2: Magic-query skill**
Create a skill that appears useful from its name and description but does nothing except log the query. Purpose: feed a search features backlog by capturing what users try to search for.
- Skill name: `magic-query` (or similar — name should invite use)
- Description: deliberately misleading — implies it does something powerful (e.g., "Smart semantic search across project knowledge")
- Behavior: logs the query text to `tmp/magic-query-log.jsonl` (timestamp + query), returns empty/neutral response
- Acceptance: `/magic-query "how do hooks work"` → logged to jsonl, no useful output
- Note: the deception is the point — captures organic search intent

**FR-3: Handoff merge-incremental fix**
Fix the handoff skill's incremental merge detection. Current rule triggers on "Session Handoff date differs from today" — wrong unit. Should trigger on "uncommitted handoff content exists" (git-dirty check on session.md).
- Current behavior: two handoffs on the same day → merge incrementally; different days → overwrite
- Correct behavior: uncommitted changes to session.md → merge incrementally; clean session.md → fresh write
- Detection: `git diff --name-only HEAD -- agents/session.md` non-empty means prior uncommitted handoff
- Edit: handoff skill SKILL.md — change date comparison to git-dirty check
- Acceptance: two handoffs before commit → second merges into first (append Completed, mutate tasks)
- Acceptance: handoff after commit → fresh write (normal path)

**FR-4: Forbid undocumented tasks**
Add rule and validator enforcement: every pending task must reference a plan directory with at least one artifact (requirements.md, problem.md, brief.md, or design.md).

**FR-4a: Rule (fragment)**
- Add to `agent-core/fragments/execute-rule.md` or new fragment: tasks require plan-backed documentation
- "Described inline" tasks are forbidden — inline descriptions lack context, references, and produce results that miss unstated requirements
- Applies to: `p:` directive (must create plan artifact), handoff (must not write undocumented tasks)

**FR-4b: Validator**
- Add validation function in `src/claudeutils/validation/` (new file or extend session validation)
- Parse task entries from session.md, extract plan directory reference
- Check `plans/<slug>/` exists and contains at least one of: requirements.md, problem.md, brief.md, design.md
- Error if task has no plan directory or plan directory is empty
- Integrate into `just precommit` pipeline
- Acceptance: task without plan directory → precommit fails with "task '<name>' has no plan artifact"
- Acceptance: task with `plans/foo/requirements.md` → passes

### Constraints

**C-1: Restart required**
FR-1 (skill removal) requires session restart. Bundle all changes, commit, then restart.

**C-2: Validator scope**
FR-4b validator checks pending tasks only (`- [ ]`, `- [>]`, `- [!]`). Terminal tasks (`- [x]`, `- [-]`, `- [†]`) are exempt — they may reference plans that were cleaned up.

### Out of Scope

- Migrating existing tasks to comply (already done this session — 16 plan files created)
- Validating plan artifact content quality (that's the UNREVIEWED marker's job)
- Changing the `/design` skill to enforce the UNREVIEWED gate (separate concern)
