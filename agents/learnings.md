# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

**Tool batching unsolved:**
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)

**Cycle numbering gaps relaxed:**
- Was: prepare-runbook.py treated gaps as fatal ERRORs, causing 10+ edits per gap
- Fix: Gaps downgraded to WARNINGs. Duplicates and bad start numbers remain errors.
- Rationale: Document order defines execution sequence — numbers are stable identifiers, not sequence indicators

**General knowledge overrides directives:**
- Anti-pattern: Using `ln -sf` to create symlinks in `.claude/` when `just sync-to-parent` exists
- Root cause: Script-First Evaluation says "execute simple operations directly" — but doesn't say "check for project recipes first"
- Correct pattern: Before ad-hoc commands, check `just --list` for existing recipes that handle the operation
- Fix: Created `project-tooling.md` fragment — project recipes take priority over equivalent ad-hoc commands
- Broader lesson: Loaded context directives must override general knowledge, not compete with it

**SessionStart hook broken:**
- Issue: [#10373](https://github.com/anthropics/claude-code/issues/10373) — SessionStart output discarded for new sessions
- Only works after `/clear`, `/compact`, or `--resume`
- Root cause: `qz("startup")` never called for new interactive sessions
- Don't build features depending on SessionStart until fixed upstream
- Alternative: Use `@agents/session.md` in CLAUDE.md for task context (already loaded)

**Commit RCA fixes active:**
- Fix 1 (submodule awareness): Commit submodule first, then stage pointer in parent
- Fix 2 (artifact staging): prepare-runbook.py stages its own artifacts via `git add`
- Fix 3 (orchestrator stop rule): Absolute "no exceptions" language, deleted contradictory scenarios
- Status: All fixes implemented and committed, active in current workflow
- Prevents: Submodule sync drift, missing artifacts in commits, dirty-state rationalization

**Never auto-commit in interactive sessions:**
- Anti-pattern: Committing after completing work because it "feels like a natural breakpoint"
- Correct pattern: Only commit when user explicitly requests (`/commit`, `ci`, `xc`, `hc`)
- Rationale: Previous rule had ambiguous disjunction (three bullets any-one-sufficient vs "wait for user direction"). With `xc` (execute+commit) shortcuts, auto-commit provides no value — user controls commit timing explicitly

**MCP tools unavailable subagents:**
- Anti-pattern: Assuming quiet-task or other sub-agents can call MCP tools (Context7, etc.)
- Correct pattern: MCP tools only available in main session. Call directly from designer/planner, write results to report file for reuse.
- Confirmed: Empirical test — quiet-task haiku has no access to `mcp__plugin_context7_context7__*` tools
- Impact: Context7 queries cost opus tokens when designer calls them, but results persist for planner reuse

**Hook capture impractical subagents:**
- Anti-pattern: Using PostToolUse hooks to capture Explore/claude-code-guide results
- Correct pattern: Session-log based capture (future work) or quiet agents that write their own reports
- Rationale: Hooks don't fire in sub-agents. Task matcher fires on ALL Tasks (noisy). Better mechanism is session-log extraction.

**Outline-first design workflow:**
- Anti-pattern: Producing full design.md in a single pass, then discovering user wanted different approach
- Correct pattern: Produce freeform outline first, iterate with user via incremental deltas, then generate full design after validation
- Escape hatch: If user already specified approach/decisions/scope, compress outline+discussion into single validation

**Vet catches structure misalignments:**
- Anti-pattern: Writing runbook steps based on assumed structure ("lines ~47-78") without reading actual files
- Correct pattern: Vet agent validates file paths AND structural assumptions via Glob/Read during review
- Example: plan-adhoc Point 0.5 actually at line 95, plan-tdd uses "Actions:" not "Steps:"
- Impact: Prevented execution failures from incorrect section identification
- Critical: Vet review with path validation is a blocker-prevention mechanism, not just quality check

**Model selection design guidance:**
- Anti-pattern: Assigning haiku to tasks requiring interpretation of design intent ("add escape hatch if...")
- Correct pattern: Haiku for explicit edits with exact text provided, sonnet for generating markdown from design guidance
- Rationale: Haiku executes what's specified, sonnet interprets intent and produces explicit text
- Trade-off: Sonnet costs more but prevents re-work from under-specified haiku tasks

**Design review uses opus:**
- Anti-pattern: Using vet-agent for design review (vet is implementation-focused — code quality, patterns, correctness)
- Correct pattern: `Task(subagent_type="general-purpose", model="opus")` for design review — architectural analysis, completeness, consistency, feasibility
- Rationale: general-purpose agent strengths (architecture analysis, multi-file exploration, complex investigation) align with design review needs

**Agent-creator reviews in orchestration:**
- Anti-pattern: Only using agent-creator for interactive agent creation from scratch
- Correct pattern: Task agent creates file from spec, then `plugin-dev:agent-creator` reviews and fixes (YAML syntax, description quality, prompt structure)
- Mechanism: Custom `## Orchestrator Instructions` in runbook specifies per-step subagent_type override. prepare-runbook.py already extracts custom orchestrator sections.
- Confirmed empirically: agent-creator is cooperative in review mode, has Write access

**Template commit contradiction:**
- Anti-pattern: quiet-task.md says "NEVER commit unless task explicitly requires" while prepare-runbook.py appends "Commit all changes before reporting success"
- Root cause: Baseline template designed for ad-hoc delegation (no auto-commit), but orchestrated execution requires clean tree after every step
- Fix: Qualified quiet-task.md line 112 to add "or a clean-tree requirement is specified"
- Broader lesson: Appended context at bottom of agent file has weak positional authority vs bolded NEVER in core constraints section — contradictions resolve in favor of the structurally prominent directive

**Orchestrator model mismatch:**
- Anti-pattern: Using orchestrator's own model (haiku) for all step agent Task invocations
- Root cause: Orchestrate skill said "model: [from orchestrator metadata, typically haiku]" — ambiguous, conflated orchestrator model with step execution model
- Correct pattern: Read each step file's "Execution Model" field and pass that to Task tool's model parameter
- Impact: Haiku step agents skip complex behaviors (vet delegation, commit sequences) that sonnet would follow
- Fix: Clarified orchestrate skill Section 3.1 — model comes from step file, not orchestrator default

**Design-vet-agent replaces inline opus:**
- Was: design skill used `Task(subagent_type="general-purpose", model="opus")` for design review
- Now: design skill uses `Task(subagent_type="design-vet-agent")` — dedicated agent with opus model
- Benefits: Artifact-return pattern (detailed report to file), specialized review protocol, consistent with vet-agent/vet-fix-agent structure
- Three-agent vet system: vet-agent (code, sonnet), vet-fix-agent (code + fixes, sonnet), design-vet-agent (architecture, opus)

**Precommit is read-only:**
- Rule: `just precommit` must not modify source files (unlike `just dev` which autoformats)
- Exemption: Volatile session state (`agents/session.md`) is exempt — `#PNDNG` token expansion runs in precommit
- Rationale: Precommit is validation, not transformation. Session state is ephemeral metadata, not source code.

**Title-words beat kebab-case:**
- Anti-pattern: Using kebab-case identifiers (e.g., `tool-batching-unsolved`) assuming programming convention enforces brevity
- Correct pattern: Use title-words (e.g., `Tool batching unsolved`) — natural language tokenizes more efficiently
- Measured: Kebab-case +31% drift penalty vs title-words +17% when agents get verbose
- Rationale: Hyphens often tokenize as separate tokens; spaces between words don't add overhead

**Root marker for scripts:**
- Anti-pattern: Using `agents/` as project root marker in `find_project_root()`
- Correct pattern: Use `CLAUDE.md` as root marker
- Rationale: Subdirectories may contain their own `agents/` folders (e.g., `agent-core/agents/`), causing scripts to stop at wrong level

**Flags are exact tokens:**
- Anti-pattern: Parsing `/handoff describe commit` as having `--commit` flag (substring match)
- Correct pattern: Flags are exact tokens (`--commit`), not prose containing flag-like words
- Rationale: User prose after command is guidance for the skill, not flags. When ambiguous, assume no flag.

**Ambient awareness beats invocation:**
- From Vercel research: Ambient context (100%) outperformed skill invocation (79%)
- Skills not triggered 56% of cases — decision about "when to invoke" is failure point
- Correct pattern: Embed critical knowledge in loaded context (CLAUDE.md, memory-index)
- Directive: "Prefer retrieval-led reasoning over pre-training knowledge"

**Default semantic mark structural:**
- Anti-pattern: Mark semantic headers with special syntax, leave structural unmarked
- Correct pattern: Default semantic, `.` prefix marks structural (`## .Title`)
- Rationale: Failure mode — orphan semantic header → ERROR (caught) vs silent loss (dangerous)
- Cost: +1 token per structural header (minority case)

**Bare lines beat list markers:**
- Anti-pattern: Using `- ` list markers for keyword index entries
- Correct pattern: Bare lines without markers
- Measured: 49 tokens (bare) vs 57 tokens (list markers) = 14% savings
- Rationale: List markers add no semantic value for flat keyword lists

**Design tables are binding constraints:**
- Anti-pattern: Inventing classification heuristics when design provides explicit rules (e.g., "subsections = structural" when design table shows all ##+ as semantic)
- Correct pattern: Read design classification tables LITERALLY. Apply judgment only where design says "use judgment" (e.g., identifying genuinely structural headers like TOCs, not reclassifying all subsections)
- Rationale: Design decisions are intentional. Overriding them based on assumptions contradicts designer's intent
- Process fix: Skill fixes outlined for `/design` and `/plan-adhoc` — see `plans/memory-index-update/reports/recovery-plan.md`
