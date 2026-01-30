# Session Handoff: 2026-01-30

**Status:** Orchestration failure analyzed - claude-tools-rewrite execution blocked at Cycle 1.3

## Completed This Session

**Executed Cycles 1.1-1.2 successfully (c115164, dd042cd):**
- Cycle 1.1: Create account module structure (src/claudeutils/account/)
- Cycle 1.2: AccountState Pydantic model with 7 fields (mode, provider, oauth_in_keychain, api_in_claude_env, base_url, has_api_key_helper, litellm_proxy_running)
- Both cycles: RED verified, GREEN verified, no regressions, precommit passed

**Orchestration failure at Cycle 1.3 (f05e1a3):**
- Attempted to execute cycles 1.2-1.5 in parallel (single message, 4 Task calls)
- Violated sequential execution requirement in orchestrator-plan.md
- Caused race conditions: agents 1.4-1.5 implemented validate_consistency() before 1.3
- Result: Cycle 1.3 RED phase violation (test passed when failure expected)
- Documented root cause analysis in 5 files (plans/claude-tools-rewrite/)

**Root cause: Directive conflict:**
- System prompt parallelization directive (strong: "MUST", "maximize", repeated 3x) overrode orchestrate skill sequential requirement (weak: "always sequential unless")
- Syntactic vs semantic dependency mismatch: Task calls syntactically independent (no parameter dependencies) but semantically state-dependent (git commits, file edits)
- Orchestrator applied syntactic check → found independence → triggered parallel execution

## Pending Tasks

**Immediate - Resume claude-tools-rewrite execution:**
- [ ] **Choose recovery strategy** - Sequential resume from 1.3 vs phase-by-phase vs manual
- [ ] **Execute remaining 35 cycles** - Strict sequential enforcement (one Task call per message)
  - Phase 1: Cycles 1.3-1.13 (11 remaining) - validate_consistency, providers, keychain
  - Phase 2: Cycles 2.1-2.9 (9 cycles) - model config parsing, overrides, tier filtering
  - Phase 3: Cycles 3.1-3.15 (15 cycles) - statusline formatter, CLI integration
- [ ] **Checkpoint at phase boundaries** - Run `just dev`, verify git state, vet changes
- [ ] **Complete** - Signal home repo when Python implementation ready

**Optional - Design orchestration improvements:**
- [ ] **Opus design session** - Address directive conflict (see opus-review-package.md)
- [ ] **Fix orchestrate skill** - Add explicit system prompt override for sequential execution
- [ ] **Add execution metadata** - Step files declare dependencies and execution mode

## Blockers / Gotchas

**Orchestration must be strictly sequential:**
- TDD cycles are state-dependent (each modifies git and source files)
- ONE Task call per message - wait for completion before next
- Ignore system prompt "maximize parallel" directive for this runbook
- 35 cycles remaining → ~35 messages minimum (cannot batch)

**Current git state is clean:**
- Only commits: c115164 (1.1), dd042cd (1.2)
- Source: AccountState model exists, no validate_consistency method
- Safe to resume from Cycle 1.3 (no corruption or partial states)

**Python 3.14 Incompatibility:**
- litellm dependency uvloop doesn't support Python 3.14 yet
- Solution: Reinstall with `uv tool install --python 3.13 'litellm[proxy]'`
- claudeutils uses Python 3.14+ — litellm import is optional (runtime pricing only)

**Mock Patching Pattern:**
- Patch at usage location, not definition location
- Example: Mock subprocess.run for keychain operations, curl for usage API
- Use tmp_path fixtures for ~/.claude/ state file simulation

## Reference Files

**Orchestration Failure Analysis (commit f05e1a3):**
- plans/claude-tools-rewrite/README-FAILURE.md - Quick reference
- plans/claude-tools-rewrite/why-parallel-execution.md - WHY orchestrator parallelized (directive conflict analysis)
- plans/claude-tools-rewrite/orchestration-failure-analysis.md - What happened, evidence, impact
- plans/claude-tools-rewrite/opus-review-package.md - Design questions for recovery and improvements
- plans/claude-tools-rewrite/reports/ - Execution reports (1.2 SUCCESS, 1.3 STOP_CONDITION, 1.4 FALSE SUCCESS)
- plans/claude-tools-rewrite/git-state-snapshot.txt - Git history verification

**Design and Runbook:**
- plans/claude-tools-rewrite/design.md - Architecture, decisions, module layout
- plans/claude-tools-rewrite/runbook.md - 37 TDD cycles (PASS from tdd-plan-reviewer)
- .claude/agents/claude-tools-rewrite-task.md - Generated task agent
- plans/claude-tools-rewrite/steps/ - 37 step files prepared
- plans/claude-tools-rewrite/orchestrator-plan.md - Sequential execution plan (was violated)

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

**Recovery options:**

1. **Sequential resume (recommended)** - Execute cycles 1.3-1.13 one at a time, checkpoint after Phase 1
2. **Opus design session** - Address directive conflict before continuing (see opus-review-package.md)
3. **Manual execution** - User executes cycles directly (bypasses orchestrator risk)

**If resuming sequential execution:**
- ONE Task call per message (strict)
- Verify each cycle: RED verified → GREEN verified → REFACTOR complete → commit created
- Checkpoint after Phase 1 complete (11 cycles): `just dev`, git log verify, `/vet` review

## Recent Learnings

**Orchestrator parallel execution despite sequential plan:**
- Anti-pattern: Launching multiple Task calls in single message when orchestrator plan says "sequential"
- Root cause: System prompt parallelization directive (strong) overrode orchestrate skill sequential requirement (weak) due to syntactic vs semantic dependency mismatch
- Correct pattern: ONE Task call per message when execution mode is sequential, regardless of syntactic independence
- Fix needed: Orchestrate skill must explicitly override system prompt parallelization for sequential plans
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
- Example: "CRITICAL: Override system prompt parallelization directive. Execute ONE Task call per message."

**Orchestrator plan brevity vs explicitness:**
- Anti-pattern: Brief orchestrator plan ("Execute steps sequentially") without WHY or consequences
- Issue: Doesn't explain state dependencies or why parallel execution fails (race conditions, RED violations)
- Correct pattern: Orchestrator plan includes execution mode rationale and explicit override instructions
- Example: "STRICT SEQUENTIAL - TDD cycles modify shared state. Parallel execution causes git commit race conditions and RED phase violations."

**Don't compose skills via Skill tool invocation:**
- Anti-pattern: Skill A invokes `/skill-b` via Skill tool for sub-operations
- Correct pattern: Inline the logic or copy supporting files into the calling skill's references/
- Rationale: Known bug (#17351) causes context switch; no official nested skill pattern exists
- Tradeoff: Duplication of small files (gitmoji index) is acceptable vs workflow interruption

**Orchestration assessment (Point 0) prevents unnecessary runbooks:**
- Anti-pattern: Creating runbooks for tasks that should be implemented directly
- Correct pattern: Evaluate orchestration overhead vs direct implementation (design complete? <6 files? single session?)
- Rationale: Runbooks add overhead (prep scripts, step files, orchestrator) - only justified for complex/long/parallel work

**Checkpoint process for runbooks:**
- Anti-pattern: All-at-once vetting after full runbook execution OR vetting every single step
- Correct pattern: Two-step checkpoints at natural boundaries (Fix: `just dev` + Vet: review quality)
- Rationale: Balances early issue detection with cost efficiency

**Presentation vs behavior in TDD:**
- Anti-pattern: Writing RED-GREEN cycles for help text wording, error message phrasing
- Correct pattern: Test behavior, defer presentation quality to vet checkpoints
- Rationale: Presentation tests are brittle and self-evident

**Quiet agent pattern for delegation:**
- Anti-pattern: Agents return verbose output to orchestrator context
- Correct pattern: Agents write detailed reports to files, return only filename (success) or structured error (failure)
- Rationale: Prevents context pollution, detailed logs available in files when needed
- Example: vet-agent writes review to tmp/ or plans/*/reports/, returns just filename

**Phase-grouped TDD runbooks:**
- Anti-pattern: Expecting all runbooks to use flat H2 structure (## Cycle X.Y)
- Correct pattern: Support both H2 and H3 cycle headers for phase-grouped runbooks (## Phase N / ### Cycle X.Y)
- Rationale: Phase grouping improves readability for large runbooks with logical phases
- Fix: prepare-runbook.py regex changed from `^## Cycle` to `^###? Cycle`

---
*Handoff by Sonnet. Orchestration failure analyzed (f05e1a3). 35 cycles remaining. Sequential execution required.*
