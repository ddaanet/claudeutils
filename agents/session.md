# Session Handoff: 2026-01-30

**Status:** Learnings separation migration complete

## Completed This Session

**Learnings separation migration executed:**
- Created migration 001-separate-learnings.md with step-by-step instructions and verification checklist
- Created agents/learnings.md with 12 learnings extracted from session.md
- Updated CLAUDE.md to reference learnings.md under Current Work
- Updated handoff skill to append learnings to separate file (never trim)
- Updated remember skill to consolidate from learnings.md with keep-recent behavior
- Commits: agent-core a228d26, claudeutils a205a72

**Vet review and fixes applied:**
- Vet-agent identified 4 issues (2 major, 2 minor)
- Fixed template.md to remove Recent Learnings section from session.md structure
- Fixed notification threshold from "approaches 80" to explicit "80+ lines"
- Clarified "most recent" as "at bottom of file" for keep-recent behavior
- Updated migration checklist to clarify parallel execution option for agent-core repo
- Amended agent-core commit a228d26 with all fixes

## Pending Tasks

**Immediate - Resume claude-tools-rewrite execution:**
- [ ] **Amend claudeutils commit** - Include updated agent-core submodule reference after amend
- [ ] **Execute remaining 35 cycles using `claude0`** - Run orchestrator with `claude --system-prompt "Empty."` to avoid parallelization directive
  - Phase 1: Cycles 1.3-1.13 (11 remaining) - validate_consistency, providers, keychain
  - Phase 2: Cycles 2.1-2.9 (9 cycles) - model config parsing, overrides, tier filtering
  - Phase 3: Cycles 3.1-3.15 (15 cycles) - statusline formatter, CLI integration
- [ ] **Checkpoint at phase boundaries** - Run `just dev`, verify git state, vet changes
- [ ] **Complete** - Signal home repo when Python implementation ready

**Research:**
- [ ] **Look into TUI scripting for orchestrator** - External automation of Claude Code TUI for step-by-step execution control (alternative to in-process orchestration)

**Optional - Design orchestration improvements:**
- [ ] **Fix orchestrate skill** - Add explicit system prompt override for sequential execution (backup if claude0 approach has issues)
- [ ] **Add execution metadata** - Step files declare dependencies and execution mode

## Blockers / Gotchas

**Use `claude0` for orchestration:**
- Alias: `claude --system-prompt "Empty."` removes main system prompt
- Still loads CLAUDE.md, skills, hooks - only removes tool usage policy and parallelization directives
- Bash tool retains its own git guidance independently
- TDD cycles remain state-dependent: ONE Task call per message

**Current git state:**
- claudeutils: a205a72 (learnings migration, needs amend for updated agent-core)
- agent-core: a228d26 (amended with vet fixes)
- Need to amend claudeutils commit to reference updated agent-core submodule

**Python 3.14 Incompatibility:**
- litellm dependency uvloop doesn't support Python 3.14 yet
- Solution: Reinstall with `uv tool install --python 3.13 'litellm[proxy]'`
- claudeutils uses Python 3.14+ -- litellm import is optional (runtime pricing only)

**Mock Patching Pattern:**
- Patch at usage location, not definition location
- Example: Mock subprocess.run for keychain operations, curl for usage API
- Use tmp_path fixtures for ~/.claude/ state file simulation

**Heredocs broken in sandbox:**
- Sandbox blocks temp file creation needed by heredocs
- .envrc changes did not resolve this
- Use alternatives (echo, printf, Write tool) when in sandbox mode

## Reference Files

**Migration Documentation:**
- agent-core/migrations/001-separate-learnings.md - Migration instructions with verification checklist
- tmp/migration-001-review.md - Initial vet review before fixes
- tmp/agent-core-migration-review.md - Final vet review (Needs Minor Changes → all fixed)

**Orchestration Failure Analysis (commit f05e1a3):**
- plans/claude-tools-rewrite/why-parallel-execution.md - WHY orchestrator parallelized (directive conflict analysis)
- plans/claude-tools-rewrite/orchestration-failure-analysis.md - What happened, evidence, impact
- plans/claude-tools-rewrite/opus-review-package.md - Design questions for recovery and improvements
- plans/claude-tools-rewrite/reports/ - Execution reports (1.2 SUCCESS, 1.3 STOP_CONDITION, 1.4 FALSE SUCCESS)

**Design and Runbook:**
- plans/claude-tools-rewrite/design.md - Architecture, decisions, module layout
- plans/claude-tools-rewrite/runbook.md - 37 TDD cycles (PASS from tdd-plan-reviewer)
- .claude/agents/claude-tools-rewrite-task.md - Generated task agent
- plans/claude-tools-rewrite/steps/ - 37 step files prepared
- plans/claude-tools-rewrite/orchestrator-plan.md - Sequential execution plan

**Key Architecture:**
- Pydantic `AccountState` model with `validate_consistency()` returning issue list
- Provider as strategy pattern (Anthropic/OpenRouter/LiteLLM implementations)
- `plistlib.dump()` for LaunchAgent (fixes heredoc variable expansion bug)
- Zero new dependencies (stdlib + existing pydantic/click)

**Success Criteria:**
- All 37 cycles GREEN (currently: 2/37 complete)
- `just dev` passes (tests, mypy, ruff)
- CLI commands functional: `claudeutils account status`, `claudeutils model list`, etc.

## Next Steps

Amend claudeutils commit to include updated agent-core submodule reference. Then resume claude0 orchestrator execution for Cycle 1.3.

---
*Handoff by Sonnet. Learnings separation complete, all vet issues fixed.*
