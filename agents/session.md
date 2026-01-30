# Session Handoff: 2026-01-30

**Status:** Recovery strategy decided - use `claude0` for weak orchestration, resume from Cycle 1.3

## Completed This Session

**Orchestration recovery strategy decided:**
- Analyzed 4 options: upgrade orchestrator, remove system prompt, TUI scripting, strengthen skill directives
- Decision: Use `claude0` alias (`claude --system-prompt "Empty."`) for weak orchestration
- Rationale: Removes main system prompt entirely, eliminating the parallelization directive conflict at source
- Note: Bash tool still carries git guidance independently of main system prompt

**Heredoc sandbox test:**
- Tested heredoc in sandboxed Bash after .envrc change - still broken
- Error: `can't create temp file for here document: operation not permitted`
- Sandbox blocks temp file creation required by heredocs

## Pending Tasks

**Immediate - Resume claude-tools-rewrite execution:**
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

**Current git state is clean:**
- Commits: c115164 (1.1), dd042cd (1.2)
- Source: AccountState model exists, no validate_consistency method
- Safe to resume from Cycle 1.3 (no corruption or partial states)

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

Use `claude0` to run orchestrator for sequential TDD cycle execution starting at Cycle 1.3. ONE Task call per message. Checkpoint after Phase 1 (11 cycles).

## Recent Learnings

**Orchestrator parallel execution despite sequential plan:**
- Anti-pattern: Launching multiple Task calls in single message when orchestrator plan says "sequential"
- Root cause: System prompt parallelization directive (strong) overrode orchestrate skill sequential requirement (weak) due to syntactic vs semantic dependency mismatch
- Correct pattern: ONE Task call per message when execution mode is sequential, regardless of syntactic independence
- Fix: Use `claude0` (`--system-prompt "Empty."`) to remove competing directives entirely
- See: plans/claude-tools-rewrite/why-parallel-execution.md for full analysis

**Syntactic vs semantic dependencies in orchestration:**
- Anti-pattern: Checking only parameter dependencies (syntactic) to determine parallelizability
- Issue: TDD cycles appear syntactically independent (no parameter dependencies) but are semantically state-dependent (git commits, file edits)
- Correct pattern: Execution mode metadata in orchestrator plan overrides syntactic independence check
- Example: Step files should declare `execution_mode: sequential-required` with reason

**Weak vs strong directive language:**
- Anti-pattern: Weak phrasing ("always sequential unless...") competing with strong system prompt directives ("MUST", "maximize")
- Observation: System prompt repetition (3x) and emphasis (all-caps) signals higher priority than single-statement skill rules
- Correct pattern: Skills needing to override system prompt must use explicit override syntax with equal or stronger emphasis
- Alternative: Remove competing system prompt entirely (`claude0`)

**Don't compose skills via Skill tool invocation:**
- Anti-pattern: Skill A invokes `/skill-b` via Skill tool for sub-operations
- Correct pattern: Inline the logic or copy supporting files into the calling skill's references/
- Rationale: Known bug (#17351) causes context switch; no official nested skill pattern exists

**Orchestration assessment (Point 0) prevents unnecessary runbooks:**
- Anti-pattern: Creating runbooks for tasks that should be implemented directly
- Correct pattern: Evaluate orchestration overhead vs direct implementation (design complete? <6 files? single session?)

**Checkpoint process for runbooks:**
- Anti-pattern: All-at-once vetting after full runbook execution OR vetting every single step
- Correct pattern: Two-step checkpoints at natural boundaries (Fix: `just dev` + Vet: review quality)

**Presentation vs behavior in TDD:**
- Anti-pattern: Writing RED-GREEN cycles for help text wording, error message phrasing
- Correct pattern: Test behavior, defer presentation quality to vet checkpoints

**Quiet agent pattern for delegation:**
- Anti-pattern: Agents return verbose output to orchestrator context
- Correct pattern: Agents write detailed reports to files, return only filename (success) or structured error (failure)

**Phase-grouped TDD runbooks:**
- Anti-pattern: Expecting all runbooks to use flat H2 structure (## Cycle X.Y)
- Correct pattern: Support both H2 and H3 cycle headers for phase-grouped runbooks (## Phase N / ### Cycle X.Y)
- Fix: prepare-runbook.py regex changed from `^## Cycle` to `^###? Cycle`

---
*Handoff by Opus. Recovery strategy decided: claude0 for orchestration. 35 cycles remaining.*
