# Recall Artifact: Orchestrate Evolution

**Generated:** 2026-02-24
**Augmented:** 2026-02-24 (runbook planning — added implementation/testing entries from Phase 0.5 discovery)
**Context:** Design review session — `/recall all` loaded 14 decision files, assessed relevance during 6-amendment update.

## When Delegation Requires Commit Instruction

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** FR-5 directly — agent definition footer must include clean tree requirement. D-2 agent caching embeds this.

Agents optimize for stated task; cleanup not implied. Include explicit "commit before returning" in every delegation prompt. Corrector is frequent offender.

## When Limiting Agent Scope

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** FR-6 — scope enforcement via structural context absence + prose boundary.

Give executing agent step + design + outline only. Scope enforced structurally by context absence — agents can't scope-creep without other step files.

## When Running Post-Step Verification

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** FR-7 — verification script design. D-3 remediation protocol.

After each step: git status → if dirty, resume agent or fix → grep UNFIXABLE. Clean tree is hard requirement, no exceptions.

## When Resuming Interrupted Orchestration

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** D-3 remediation — resume from last checkpoint, not ad-hoc debugging.

Resume from last runbook checkpoint. Run checkpoint verification commands. Systematically fix remaining items. Verify with project recipes. No ceiling recovery protocol → debugging-as-assessment → reactive fix mode → recipe bypass under urgency.

## When Haiku Rationalizes Test Failures

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** D-1 rationale — why sonnet replaces haiku as default orchestrator.

Haiku commits code despite failing regression tests, rationalizing failures as "expected behavior change." Regression test failures during TDD GREEN phase are bugs, not expected behavior. Evidence: Cycle 1.2 haiku committed with 3 failing tests.

## When Classifying Errors By Tier

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** D-4 simplified escalation — tier-aware classification informs the 2-level model.

Sonnet/opus execution agents self-classify and report classified error; haiku agents report raw errors for orchestrator to classify. With sonnet default (D-1), agents self-classify — orchestrator classifies only on fallback.

## When Designing Timeout Mechanisms

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** D-3 execution bounds — `max_turns` for spinning, duration timeout gap.

Time and tool count address independent failure modes. Spinning → `max_turns`. Hanging → duration timeout. Platform only supports `max_turns`; duration timeout noted as gap.

## When Selecting Agent Type For Orchestrated Steps

**Source:** `agents/decisions/orchestration-execution.md`
**Relevance:** D-2 agent caching — plan-specific agents mandatory, discoverable after restart.

Plan-specific agent is mandatory for `/orchestrate`. Session restart makes custom agents discoverable. `tdd-task` only for ad-hoc cycles outside prepared runbooks.

## When Choosing Review Gate

**Source:** `agents/decisions/pipeline-contracts.md`
**Relevance:** Phase boundary checkpoints — T6 corrector routing, UNFIXABLE escalation pattern.

Transformation table T1-T6 defines review gates per pipeline stage. T6 (steps → implementation) uses corrector at checkpoints. Fix-all pattern: fix everything, label unfixable, caller greps UNFIXABLE.

## When Declaring Phase Type

**Source:** `agents/decisions/pipeline-contracts.md`
**Relevance:** D-6 inline phase handling — inline eligibility criteria, orchestration delegation model.

Phase types: `tdd`, `general`, `inline`. Inline: orchestrator-direct execution, no Task dispatch. Eligibility: no runtime feedback loop, all decisions pre-resolved. prepare-runbook.py skips step-file generation for inline phases.

## When Selecting Model For TDD Execution

**Source:** `agents/decisions/pipeline-contracts.md`
**Relevance:** D-5 ping-pong TDD — model assignment by complexity type during runbook expansion.

Pattern complexity → haiku. State machine complexity → sonnet minimum. Synthesis complexity → opus. Classification during `/runbook` expansion, not orchestration time.

## When Setting Orchestrator Execution Mode

**Source:** `agents/decisions/workflow-core.md`
**Relevance:** Orchestrate skill rewrite — sequential execution mode metadata.

Execution mode metadata in orchestrator plan overrides system prompt parallelization directives. TDD cycles modify shared state — parallel execution causes race conditions. ONE Task call per message when sequential.

## When Assessing Orchestration Tier

**Source:** `agents/decisions/workflow-core.md`
**Relevance:** Context for D-2 — Tier 3 (full runbook) produces the orchestrator plans this design consumes.

Three tiers: direct implementation, lightweight delegation, full runbook. Tier 3 sequence: 4-point process → prepare-runbook.py → handoff → restart → orchestrate.

## When Checking Complexity Before Expansion

**Source:** `agents/decisions/workflow-planning.md`
**Relevance:** Runbook planning constraint — planner must check complexity before expansion, callback if too large.

Check complexity BEFORE expansion; callback to previous level if too large. Complexity assessment is planning concern (sonnet/opus), not executor concern (haiku).

## When Bootstrapping Self-Referential Improvements

**Source:** `agents/decisions/workflow-planning.md`
**Relevance:** Phase ordering — this design modifies orchestrate skill used to execute itself.

When improving tools/agents, apply each improvement before using that tool in subsequent steps. Phase ordering follows tool-usage dependency graph.

## When Agent Ignores Injected Directive

**Source:** `agents/decisions/workflow-optimization.md`
**Relevance:** D-2 agent definition design — appended context vs core constraints positional authority.

Appended context at bottom of agent file has weak positional authority vs bolded NEVER in core constraints. Contradictions resolve in favor of structurally prominent directive. Agent definitions must avoid internal contradictions.

## When Step Agent Uses Wrong Model

**Source:** `agents/decisions/workflow-optimization.md`
**Relevance:** Orchestrator plan format — model comes from step file metadata, not orchestrator default.

Read each step file's "Execution Model" field and pass to Task tool's model parameter. Orchestrate skill must not use its own model for step agents.

## When Designing Quality Gates

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** D-3 verification script — layered defense pattern (outer: tool call gate, middle: precommit, inner: corrector review).

Four defense layers: D+B hybrid (execution flow), precommit (automated), corrector review (semantic), conformance tests (deepest). No single layer sufficient. verify-step.sh is layer 2; phase boundary corrector is layer 3.

## When Placing Quality Gates

**Source:** `agents/decisions/defense-in-depth.md`
**Relevance:** Gate placement — commit chokepoint, not ambient rules.

Gate at the chokepoint (commit). Scripted check blocks mechanically. No judgment needed at the gate. Ambient rules without enforcement are aspirational.

## When Writing Red Phase Assertions

**Source:** `agents/decisions/testing.md`
**Relevance:** D-5 ping-pong TDD — test quality rules cached in tester agent.

RED phase tests must verify behavior, not just structure. Tests checking only structure (exit_code == 0, key existence) produce stubs. RED tests verify behavior with mocking/fixtures.

## When GREEN Phase Verification Includes Lint

**Source:** `agents/decisions/testing.md`
**Relevance:** D-5 GREEN gate — verification must include lint, not just test pass.

GREEN verification command must be `just check && just test`. Lint is required gate before commit. Evidence: Cycle 1.1 GREEN commit had F821, required fix commit.

## When Custom Agents Need Session Restart For Discoverability

**Source:** `agents/learnings.md`
**Relevance:** D-2 agent caching model — plan-specific agents discoverable after restart, workflow includes this boundary.

Plan-specific agents in `.claude/agents/` discoverable as `subagent_type` values after session restart. prepare-runbook.py → restart → orchestrate workflow naturally includes this boundary.

## When Sub-Agent Rules Not Injected

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** D-2 agent caching — rules files don't fire in sub-agents, domain context must be embedded in agent definition.

Rules files fire in main session only. Domain context must be carried explicitly — planner writes it into runbook, orchestrator passes through task prompt. Agent definitions must embed all needed context.

## When Editing Runbook Step Or Agent Files

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** Source-not-generated constraint — generated agent files must not be edited directly.

Edit source (phase files in `plans/<job>/`), then re-run prepare-runbook.py. Common Context extracted from phase preambles and injected into all step/cycle files.

## When Ordering Fragments In CLAUDE.md

**Source:** `agents/decisions/prompt-structure-research.md`
**Relevance:** D-2 agent definition design — positional authority of cached context sections.

Strong primacy bias — critical rules at document start. Recency bias at end. Middle weakest. Agent definitions should place constraints in primacy position, plan context in middle, scope enforcement in recency position.

## When Writing Rules For Different Models

**Source:** `agents/decisions/prompt-structure-research.md`
**Relevance:** D-2 agent templates — different instruction density for haiku vs sonnet execution agents.

Haiku needs explicit steps, markers, DO NOT examples. Sonnet handles clear bullets with context. Opus handles concise prose. Agent templates should match instruction style to execution model.

## When Preferring E2E Over Mocked Subprocess

**Source:** `agents/decisions/testing.md`
**Relevance:** verify-step.sh and verify-red.sh testing — E2E with real git repos in tmp_path, not mocked subprocess.

E2E only with real git repos (tmp_path fixtures), mocking only for error injection. Git with tmp_path is fast (milliseconds). Interesting bugs are state transitions that mocks can't catch.

## When Hitting File Line Limits

**Source:** `agents/decisions/implementation-notes.md`
**Relevance:** prepare-runbook.py is ~1500 lines and will grow — look for code quality improvements (dedup, dead code, helpers), not file splitting as first resort.

Look for code quality improvements first — redundant calls, dead code, extraction candidates. Black expansion of 5+ line call sites signals too many parameters for inline use — extract a helper.
