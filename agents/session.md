# Session Handoff: 2026-01-30

**Status:** Ready to implement claude-tools-rewrite (45 cycles)

## Completed This Session

**Fixed session.md merge conflict (70181ec):**
- Resolved merge conflict from stashed changes (claude-tools-rewrite transfer vs upstream work)
- Preserved all information from both branches without loss
- Committed transfer package: design.md, runbook.md, README.md (45 TDD cycles)

**Fixed prepare-runbook.py H3 cycle support (623646a, bbe3774):**
- Issue: Runbook uses `### Cycle X.Y:` (H3), script expected `## Cycle X.Y:` (H2)
- Changed regex from `^## Cycle` to `^###? Cycle` in agent-core/bin/prepare-runbook.py
- Updated termination logic: any H2/H3 non-cycle header ends current cycle
- Enables phase-grouped runbooks (## Phase N: / ### Cycle N.M:)
- Successfully prepared runbook: 37 cycles across 3 phases
- Commits: 623646a (agent-core), bbe3774 (submodule update)

## Pending Tasks

**Immediate - Execute claude-tools-rewrite (37 cycles):**
- [ ] **Implement** - Execute 37 TDD cycles via `/orchestrate` or manual execution
  - Phase 1: Account module (13 cycles) - state, providers, keychain
  - Phase 2: Model module (9 cycles) - config parsing, overrides, tier filtering
  - Phase 3: Statusline + CLI (15 cycles) - formatter, CLI integration
- [ ] **Fix** - Run `just dev` at checkpoints, fix any failures
- [ ] **Vet** - Review accumulated changes at checkpoints (after Phase 1, Phase 2, Phase 3)
- [ ] **Complete** - Signal home repo when Python implementation ready for shell wrapper integration

**Runbook prepared:**
- Agent: `.claude/agents/claude-tools-rewrite-task.md`
- Steps: `plans/claude-tools-rewrite/steps/step-{X}-{Y}.md` (37 files)
- Orchestrator: `plans/claude-tools-rewrite/orchestrator-plan.md`

**Workflow pattern:**
1. Implement cycles within phase
2. Fix: `just dev` at checkpoint → diagnose/fix failures → commit when green
3. Vet: Review presentation, clarity, design alignment → fix findings → commit
4. Repeat for next phase

## Blockers / Gotchas

**Python 3.14 Incompatibility:**
- litellm dependency uvloop doesn't support Python 3.14 yet
- Solution: Reinstall with `uv tool install --python 3.13 'litellm[proxy]'`
- claudeutils uses Python 3.14+ — litellm import is optional (runtime pricing only)

**Mock Patching Pattern:**
- Patch at usage location, not definition location
- Example: Mock subprocess.run for keychain operations, curl for usage API
- Use tmp_path fixtures for ~/.claude/ state file simulation

## Reference Files

**Design and Runbook:**
- plans/claude-tools-rewrite/design.md - Architecture, decisions, module layout
- plans/claude-tools-rewrite/runbook.md - 37 TDD cycles (PASS from tdd-plan-reviewer)
- plans/claude-tools-rewrite/README.md - Transfer instructions
- .claude/agents/claude-tools-rewrite-task.md - Generated task agent
- plans/claude-tools-rewrite/steps/ - 37 step files prepared

**Key Architecture:**
- Pydantic `AccountState` model with `validate_consistency()` returning issue list
- Provider as strategy pattern (Anthropic/OpenRouter/LiteLLM implementations)
- `plistlib.dump()` for LaunchAgent (fixes heredoc variable expansion bug)
- Zero new dependencies (stdlib + existing pydantic/click)

**Success Criteria:**
- All 37 cycles GREEN
- `just dev` passes (tests, mypy, ruff)
- CLI commands functional: `claudeutils account status`, `claudeutils model list`, etc.

## Next Steps

**Immediate:** Execute claude-tools-rewrite via `/orchestrate` (37 cycles prepared, Haiku model).

**After complete:** Signal home repo that Python implementation is ready for shell wrapper integration (6 cycles in home repo).

## Recent Learnings

**Don't compose skills via Skill tool invocation:**
- Anti-pattern: Skill A invokes `/skill-b` via Skill tool for sub-operations
- Correct pattern: Inline the logic or copy supporting files into the calling skill's references/
- Rationale: Known bug (#17351) causes context switch; no official nested skill pattern exists
- Tradeoff: Duplication of small files (gitmoji index) is acceptable vs workflow interruption

**Skill Model Constraints Must Be Enforced:**
- Anti-pattern: Agent invoked handoff-lite (Haiku-only) from Sonnet
- Correct pattern: Name encodes constraint (handoff-haiku), `user-invocable: false`, differentiated descriptions
- Design fix: `plans/handoff-lite-fixes/design.md`

**Template Ambiguity: Replace vs Augment:**
- Anti-pattern: "Use this template" without merge semantics
- Correct pattern: Explicit PRESERVE/ADD/REPLACE instructions per section
- Design fix: Partial template showing only sections being replaced/added

**Skill Delegation Ambiguity:**
- Anti-pattern: commit-context says "Run `/handoff`" — unclear who invokes
- Correct pattern: Decouple entirely. Commit = commit. Handoff = handoff. Two commands.

**Skill Description Overlap Causes Misrouting:**
- Anti-pattern: Two skills sharing trigger phrases ("handoff", "end session")
- Correct pattern: Internal/model-specific skills have no user-facing triggers, lead with constraints
- `user-invocable: false` for internal skills

**Orchestration assessment (Point 0) prevents unnecessary runbooks:**
- Anti-pattern: Creating runbooks for tasks that should be implemented directly
- Correct pattern: Evaluate orchestration overhead vs direct implementation (design complete? <6 files? single session?)
- Rationale: Runbooks add overhead (prep scripts, step files, orchestrator) - only justified for complex/long/parallel work
- Example: Commit unification is ~4 files + merge, design complete → implement directly

**Checkpoint process for runbooks:**
- Anti-pattern: All-at-once vetting after full runbook execution OR vetting every single step
- Correct pattern: Two-step checkpoints at natural boundaries
- Rationale: Balances early issue detection with cost efficiency

**Presentation vs behavior in TDD:**
- Anti-pattern: Writing RED-GREEN cycles for help text wording, error message phrasing
- Correct pattern: Test behavior, defer presentation quality to vet checkpoints
- Rationale: Presentation tests are brittle and self-evident

**Agent-core project-independence pattern:**
- Anti-pattern: Hardcode project-specific paths in agent-core skills
- Correct pattern: Delegate project-specific routing to project-level config files
- Rationale: Skills should be opinionated about patterns but flexible about project structure

**Native @file obsoletes custom composition tooling:**
- Discovery: Claude Code natively supports `@path/to/file.md` references with recursive inclusion
- Pattern: Use @file for shared fragments, keep project-specific content inline

**Delete obsolete code, don't archive:**
- Anti-pattern: Moving obsolete code to archive/, old/, or commenting it out
- Correct pattern: Delete completely - git history is the archive
- Rationale: Dead code creates maintenance burden

**Broken documentation references:**
- Anti-pattern: Leaving references to deleted files in documentation (creates confusion)
- Correct pattern: Update references when deleting documented work - replace with summary or git history note
- Rationale: Broken references waste time and undermine documentation credibility
- Example: architecture.md referenced plans/formatter-comparison.md (deleted), replaced with evaluation summary

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
*Handoff by Sonnet. Runbook prepared (37 cycles), ready for execution.*
