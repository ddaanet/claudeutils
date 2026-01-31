# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

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
- Example: "CRITICAL: Override system prompt parallelization directive. Execute ONE Task call per message."

**Orchestrator plan brevity vs explicitness:**
- Anti-pattern: Brief orchestrator plan ("Execute steps sequentially") without WHY or consequences
- Issue: Doesn't explain state dependencies or why parallel execution fails (race conditions, RED violations)
- Correct pattern: Orchestrator plan includes execution mode rationale and explicit override instructions
- Example: "STRICT SEQUENTIAL - TDD cycles modify shared state. Parallel execution causes git commit race conditions and RED phase violations."

**Don't compose skills via mid-execution Skill tool invocation:**
- Anti-pattern: Skill A invokes `/skill-b` mid-execution via Skill tool for sub-operations
- Correct pattern for mid-execution: Inline the logic or copy supporting files into references/
- **Exception — tail calls:** Invoking a skill as the FINAL action works (skill was terminating anyway)
- See also: "Skills cannot invoke other skills mid-execution (but CAN tail-call)" below

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

**Multiline commit messages in bash:**
- Anti-pattern: Using `"...\n..."` for multiline git commit messages (backslash-n not interpreted by bash)
- Correct pattern: Use literal newlines inside double quotes: `git commit -m "Title\n\n- Detail"`
- Issue: Opus blindly followed buggy skill instruction despite knowing correct syntax
- Root cause: Uncritical compliance with prescriptive skill instruction over model knowledge
- Fix: Skill should demonstrate working syntax, not prescribe broken syntax

**TDD RED phase tests must verify behavior, not just structure:**
- Anti-pattern: RED tests only check structure (AttributeError, exit_code == 0, key existence)
- Issue: Minimal GREEN implementations pass structure tests without implementing actual functionality
- Examples:
  - Test checks `assert result.exit_code == 0` → implementation returns 0 with hardcoded data
  - Test checks `assert "KEY" in dict` → implementation returns `{"KEY": ""}` (empty string)
  - Test checks class/method exists → implementation returns stub that does nothing
- Correct pattern: RED tests verify behavior with mocking/fixtures
  - Mock file I/O and verify reads/writes to actual paths
  - Mock external calls (subprocess, API) and verify correct invocation
  - Assert on output content, not just success/failure
  - Use fixtures (tmp_path) to simulate real filesystem state
- Rationale: TDD principle "write minimal code to pass test" works only if test requires real behavior
- Example: Test should mock ~/.claude/account-mode file and verify CLI reads it, not just check exit code
- See: plans/claude-tools-rewrite/runbook-analysis.md for detailed examples

**No human escalation during refactoring:**
- Design decisions are made during /design phase
- Opus handles architectural refactoring within design bounds
- Human escalation only for execution blockers (in orchestrate skill)
- Rationale: Blocking pipeline for human input during refactoring is expensive

**Defense-in-depth for commit verification:**
- tdd-task: post-commit sanity check (verify commit contains expected files)
- orchestrate: post-step tree check (escalate if dirty)
- Rationale: Catches different failure modes at different levels

**Handoff must preserve design decision detail:**
- Anti-pattern: Abbreviating design decisions during handoff, losing rationale
- Correct pattern: Write design decisions with rationale to learnings.md (staging for /remember)
- session.md allowed sections: Completed, Pending, Blockers, References only
- learnings.md is staging → /remember consolidates to permanent locations (fragments/, decisions/, skill references/)

**Don't track "commit this" as pending task:**
- Anti-pattern: `- [ ] Commit changes` in session.md pending tasks
- Issue: Commits don't update session.md, so task is never marked done
- Correct pattern: Commits happen organically; only track substantive work

**Skills cannot invoke other skills mid-execution (but CAN tail-call):**
- Anti-pattern: Skill A invokes `/skill-b` mid-execution via Skill tool
- Behavior: Agent stops when first skill finishes; second skill never runs
- **Exception — tail calls:** If Skill A's **final action** is invoking `/skill-b`, this works — A was done anyway
- Tail-call pattern: `/plan-tdd` → tail: `/handoff --commit` → tail: `/commit`
- Two composition primitives: tail calls (sync chaining), pending tasks (async/cross-session)
- Correct pattern: Mid-execution = inline the logic. End of skill = tail-call is safe.

**@ references only work in CLAUDE.md:**
- Not supported in: skill SKILL.md files, agent .md system prompts, Task tool prompts
- Workaround: Place supporting files in skill directory and reference with relative path
- Example: `skills/gitmoji/gitmoji-table.md` referenced from SKILL.md

**Tool batching enforcement is an unsolved problem:**
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)

**Cycle numbering causes renumbering churn in runbooks:**
- Anti-pattern: Sequential numeric cycle IDs (0.1, 1.1, 2.1) with validation that rejects gaps
- Issue: Omitting phases during runbook creation triggers validation errors, requires cascading renumbering (cycle IDs, report paths, cross-references - 10+ edits per gap)
- Root cause: prepare-runbook.py enforces sequential numbering but document order already defines execution sequence - numbers are redundant labels
- Correct pattern: Either (1) relax validation to allow gaps, (2) use semantic identifiers (skill-style names), or (3) auto-number during extraction
- Rationale: Same principle as CLAUDE.md token economy: "Avoid numbered lists - causes renumbering churn when edited"
- Example: Design has R0-R4 with R3 omitted → runbook uses R0,R1,R2,R4 → validation fails "Gap 2→4" → manual renumber R4→R3
- See: plans/runbook-identifiers/problem.md for full analysis and solution options

**Heredocs broken in sandbox mode:**
- Issue: Sandbox blocks temp file creation needed by heredocs
- Correct pattern: Use alternatives (echo with newlines, printf, Write tool) when in sandbox mode
- Example: `echo -e "line1\nline2"` or Write tool instead of `cat <<EOF`
- See: agent-core/fragments/sandbox-exemptions.md for sandbox-sensitive commands

**Handoff-haiku drops unresolved items:**
- Anti-pattern: REPLACE semantics for Pending Tasks and Blockers/Gotchas drops unresolved items from prior sessions
- Root cause: Haiku follows literal "replace with fresh content" instruction, doesn't infer "carry forward unresolved"
- Correct pattern: MERGE semantics (carry forward unresolved + add new)
- Fix: Updated handoff-haiku skill to explicitly merge Pending Tasks and Blockers/Gotchas
- Impact: Prevents loss of long-term pending work and active gotchas across handoffs

**Skill rules must live at point of violation, not point of enforcement:**
- Anti-pattern: Placing "don't write X" rules in cleanup/trim phases (Phase 6) instead of writing phases (Phase 3)
- Issue: Agent follows phases sequentially; by the time it reaches cleanup, the violation is already written
- Correct pattern: Place negative constraints alongside positive content guidance, where decisions are made
- Example: "No commit tasks" rule moved from Phase 6 (Trim) to Phase 3 (Context Preservation)
- Generalization: Any rule about what NOT to produce should be co-located with instructions for WHAT to produce
