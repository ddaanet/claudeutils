# Todo

Deferred work items and shelved context.

---

## Backlog

### 2026-01-19 - Session: Unification Phase 3 (Incomplete - Phase 4 Blocked)

**Branch:** unification
**Status:** Phase 3 complete, Phase 4 blocked on precommit fixes
**Archived to:** `agents/shelf/unification-phase3-session.md`

**Completed:**
- Phase 3: All 5 design steps executed
- Design deliverable: `scratch/consolidation/design/compose-api.md` (34K, ready for Phase 4)
- Oneshot workflow complete and archived
- Merged oneshot to unification, then unification to markdown

**Blocked:**
- Phase 4 implementation blocked on precommit check fixes
- Must fix precommit in markdown branch first

**Next Steps:**
1. Fix precommit checks in markdown branch
2. Return to unification branch
3. Execute Phase 4: Implement composition module and CLI

**Key Files:**
- Design: `plans/unification/design.md`
- Phase 4 plan: `plans/unification/phases/phase4.md`
- Implementation spec: `scratch/consolidation/design/compose-api.md`

---

### 2026-01-19 - Convert agent-core to Claude Code Plugin

**Priority:** High (after unification complete)

**Context:**
- Current: agent-core as git submodule with manual sync (`just sync-to-parent`)
- Pain point: Manual sync required after every change, easy to forget
- Solution: Convert to Claude Code plugin for auto-discovery

**Benefits:**
- ✅ No manual sync needed
- ✅ Works across all projects simultaneously
- ✅ Version management via plugin system
- ✅ Single source of truth (no file duplication)
- ✅ Portable paths via `${CLAUDE_PLUGIN_ROOT}`

**Tasks:**
- [ ] Complete unification work first (blocker)
- [ ] Create `.claude-plugin/plugin.json` in agent-core
- [ ] Create `agents/` directory in agent-core (currently missing)
- [ ] Test plugin installation: `claude plugin install /Users/david/code/agent-core`
- [ ] Update agent-core README with plugin usage
- [ ] Optional: Remove submodule from claudeutils (or keep during transition)
- [ ] Optional: Update justfile with plugin-focused tasks (bump-version, test-install)

**Future Enhancement:**
- Add Python tooling (pyproject.toml, src/, tests/) when complex transforms needed
- Example: prepare-execution script for plan → execution artifacts

**Reference:** Discussion on 2026-01-19 about plugin structure compatibility

---

### 2026-01-19 - Create handoff-discussion Skill

**Priority:** Medium

**Context:**
- Need pattern for handing off complex design discussions to conversational opus
- Current manual approach: Write comprehensive handoff to `agents/auto-agent-discussion.md`
- Pattern should automate handoff document creation

**Requirements:**
- Template for discussion handoffs (problem, context files, questions, goals)
- Progressive disclosure pattern (like shelve skill)
- Include file references instead of repeating content
- Should work for design exploration, architecture decisions, trade-off analysis

**Tasks:**
- [ ] Create skill structure: `skills/handoff-discussion/`
- [ ] Write skill instructions in `SKILL.md`
- [ ] Create discussion handoff template
- [ ] Document when to use (design exploration, multi-option decisions)
- [ ] Add to agent-core for reusability

**Reference:** Created manual handoff on 2026-01-19 for plan-to-execution script design

---

### 2026-01-18 - Session: unification

**Branch:** unification

**Task:** Phase 2 - Analysis Phase

**Status:** Ready to start

**This Session:**
- Resolved Phase 1 blocker: git submodule integration
- Verified Phase 2 readiness (all checks passed)
- Report: `tmp/phase2-readiness.md`

**Handoff to Next Session:**
- Phase 2 Ready
- Key files: `plans/unification/phases/phase2.md`, `plans/unification/phases/consolidation-context.md`
- Execution pattern: Delegate with context + phase file, reports to `plans/unification/reports/`

**Archived to:** `agents/shelf/unification-session.md`

---

### 2026-01-18 - Context: unification

**Project:** Rules Unification Project

**Key Documents:**
- Design: `plans/unification/design.md`
- Plans: `plans/unification/consolidation-plan.md`, `plans/unification/phases/`
- Reports: `plans/unification/reports/`

**Architecture:**
- agent-core: Shared fragments (git submodule)
- claudeutils: Generation tooling (Python module)

**Archived to:** `agents/shelf/unification-context.md`

---

### Deferred from Task Agent Pattern Session (Option A)

**Context Monitoring Skill:**
- [ ] Web search for existing Claude Code context monitoring skill
- [ ] Build context monitoring skill if not found
- [ ] Configure thresholds: >100k notify, >125k immediate handoff
- [ ] Install in agent-core for reusability

**Pattern Documentation:**
- [ ] Document pattern: Plan-specific agent (`agent-core/pattern-task-plan-agent.md`)
- [ ] Document pattern: Task phase planning (`agent-core/pattern-task-phase-planning.md`)
- [ ] Document pattern: Ad-hoc scripting (`agent-core/pattern-adhoc-scripting.md`)

**Tooling:**
- [ ] Create plan splitter input format spec (`agent-core/specs/plan-splitter-input-format.md`)
- [ ] Create plan-specific agent creation script (`agent-core/scripts/create-plan-agent.*`)

**Phase 2 Application:**
- [ ] Build Phase 2 plan using weak orchestrator pattern
- [ ] Review Phase 2 plan with fresh sonnet agent

---

### 2026-01-19 - Merge Skills and Agents to Prompt-Composer Framework

**Priority:** High (after markdown job complete)

**Context:**
- Current skills (.claude/skills/*) and agents (agent-core/agents/*) will be converted to prompt-composer framework
- Existing role-*.md files in agents/ directory will be merged with new skills and agents
- This is a consolidation of the agent architecture into a unified framework

**Tasks:**
- [ ] Convert current skills to prompt-composer framework
- [ ] Convert agent-core agents to prompt-composer framework
- [ ] Merge existing role-*.md files with new skills and agents
- [ ] Update documentation to reflect new framework
- [ ] Test converted skills and agents

**Blocked by:** Markdown job completion

**Reference:** Context from session.md Phase 4 cleanup discussion

---

### 2026-01-19 - TDD Integration Deferred Items

**Context:** From TDD workflow integration design session

- [ ] Project-specific test command configuration (currently hardcoded: `just test`, `just lint`, `just precommit`)
- [ ] Add line limits to agent docs (when markdown processing fixed)
- [ ] Documentation refactoring support (when docs exceed line limits)

**Reference:** `plans/tdd-integration/design.md`

---

- [ ] (empty - items added as needed)
