# Phase 1 Fix Plan

**Status**: Outline
**Date**: 2026-01-15

---

## Gaps to Fix

1. **Git submodule integration** - agent-core not added as submodule
2. **Compose script paths** - Uses `../agent-core/` (sibling) instead of `agent-core/` (submodule)
3. **Uncommitted changes** - claudeutils branch has modified and untracked files

---

## Fix Steps

### Step 1: Add agent-core as submodule to claudeutils
- `git submodule add /Users/david/code/agent-core agent-core`
- Verify `.gitmodules` created
- Verify `agent-core/` directory populated

### Step 2: Update compose.sh paths
- Change `../agent-core/fragments/` → `agent-core/fragments/`
- Regenerate CLAUDE.md
- Verify output unchanged

### Step 3: Commit all claudeutils changes
- Stage modified files: CLAUDE.md, agents/session.md, agents/rules-handoff.md
- Stage new files: agents/compose.sh, agents/compose.yaml, agents/README.md
- Stage submodule: agent-core, .gitmodules
- Commit with descriptive message

### Step 4: Validate
- Fresh clone test (or `git submodule update --init`)
- Run compose.sh from fresh state
- Verify CLAUDE.md generates correctly

---

## Orchestration Revision (for Phase 2)

### Problems from Phase 1
- Noise accumulation from previous steps in reused agents
- Verbose execution reports (redundant with session logs)
- Review agents produced verbose reports, failed to detect issues
- Bloated reports polluted orchestrator context

### New Pattern
1. **Plan-specific execution agent** - Shared plan context in system prompt (enables caching)
2. **Fresh agent per step** - No reuse, no noise accumulation
3. **Minimal reporting** - Agent returns success/failure + brief summary, not verbose log
4. **No stepwise review** - Assumption: stepwise prompting provides adherence
5. **Single final review** - Sonnet reviews diff (git diff) after all work complete, not logs

### Implementation
- Create base execution agent prompt (plan-agnostic)
- Inject plan context via system prompt prefix
- Define terse return format: `done: <one-line summary>` or `blocked: <reason>`
- Final review prompt: "Review git diff, identify issues, be terse"

---

## Success Criteria

- [ ] agent-core is git submodule in claudeutils
- [ ] compose.sh uses submodule path
- [ ] All Phase 1 work committed
- [ ] Submodule workflow validated (clone + init)
