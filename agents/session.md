# Session Handoff: 2026-01-26

**Status:** TDD runbook review mechanism implemented; prescriptive code anti-pattern detected and fixed

## Completed This Session

**TDD runbook process failure diagnosis:**
- Root cause: /plan-tdd generated prescriptive runbooks with exact Python code in GREEN phases
- Violation: Agents became code copiers instead of implementers
- Impact: 6/11 cycles in composition API runbook contained implementation code
- Design document (compose-api.md) showed function implementations, influencing runbook generation

**TDD review mechanism created:**
- Created /review-tdd-plan skill in agent-core/skills/review-tdd-plan/SKILL.md
- Created tdd-plan-reviewer agent in agent-core/agents/tdd-plan-reviewer.md
- Updated /plan-tdd skill Phase 5 to trigger reviewer (stops on violations, shows user)
- Updated CLAUDE.md TDD workflow route to include review step
- Agent-core commits: 0cfd422 (review mechanism), 037282d (justfile fix)

**Justfile sync-to-parent fix:**
- Changed from absolute to relative symlink paths (../../agent-core/...)
- Improves portability across machines
- Successfully synced: 13 skills, 3 agents, 1 hook

**Key artifacts locations:**
- Review skill: agent-core/skills/review-tdd-plan/SKILL.md
- Reviewer agent: agent-core/agents/tdd-plan-reviewer.md
- Updated workflow: CLAUDE.md lines 6-9
- Parent symlinks: .claude/skills/review-tdd-plan, .claude/agents/tdd-plan-reviewer.md

## Pending Tasks

- [ ] **Commit parent repo changes** (IMMEDIATE)
  - Modified: CLAUDE.md (TDD workflow route updated)
  - Modified: agent-core submodule reference (points to 037282d)
  - Use /gitmoji + /commit for emoji-prefixed message

- [ ] **Fix composition API runbook** (BLOCKED - pending review)
  - Original issue still exists: prescriptive code in GREEN phases
  - Need to apply review feedback from plans/unification/consolidation/reports/runbook-review.md:586-748
  - Restructure cycles: X.1 simplest happy path → X.2 error handling → X.3 features
  - Replace code blocks with behavior descriptions and hints

- [ ] **Execute revised runbook** (AFTER FIXES)
  - Run prepare-runbook.py to generate artifacts
  - Use /orchestrate for TDD cycle execution

## Blockers / Gotchas

**Composition API runbook still needs fixes:**
- Contains prescriptive implementation code (the problem we just diagnosed)
- Not yet fixed - review mechanism created but fixes not applied
- Next session should run tdd-plan-reviewer to validate or apply fixes manually

**Symlink removal issue during sync:**
- .claude/agents/quiet-task.md had com.apple.provenance extended attribute
- Required sandbox bypass to remove protected symlink
- Pattern: Use xattr -d or dangerouslyDisableSandbox for stuck symlinks

**Agent-core workflow:**
- Always work in ~/code/claudeutils/agent-core/ (submodule working copy)
- Commit in agent-core first, then update parent submodule reference
- Run just sync-to-parent to install symlinks in parent .claude/

## Next Steps

Commit parent repo changes (CLAUDE.md + agent-core submodule update) with /gitmoji + /commit

---

## Recent Learnings

**TDD runbook anti-pattern (CRITICAL):**
- Anti-pattern: GREEN phases with exact implementation code
  ```markdown
  **GREEN Phase:**
  ```python
  def load_config(config_path: Path) -> dict:
      # exact code here
  ```
  ```
- Correct pattern: Behavior descriptions with hints
  ```markdown
  **GREEN Phase:**
  **Behavior**: Minimal load_config() to pass tests
  **Hint**: Use yaml.safe_load(), Path.open()
  ```
- Rationale: Tests should drive implementation, not scripts prescribe it
- First cycle: Simplest functional happy path (not trivial stub, but not all features)

**Review delegation in workflows:**
- Phase 5 of /plan-tdd now triggers tdd-plan-reviewer agent
- Agent writes report to plans/*/reports/runbook-review.md
- Workflow STOPs on violations, shows user, waits for decision
- User can apply fixes or approve anyway (judgment required)

**Skill organization:**
- Skills live in agent-core/skills/ (synced to parent .claude/skills/)
- Agents live in agent-core/agents/ (synced to parent .claude/agents/)
- Hooks live in agent-core/hooks/ (synced to parent .claude/hooks/)
- sync-to-parent creates relative symlinks for portability

**Progressive disclosure principle:**
- Don't preload all workflow docs (token economy)
- Read specific guides only when executing that workflow
- CLAUDE.md removed non-existent tdd-workflow.md reference
- Workflow routes should be concise, details in skills/agents
