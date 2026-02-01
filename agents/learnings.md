# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

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

**General knowledge overrides project directives (Script-First Evaluation gap):**
- Anti-pattern: Using `ln -sf` to create symlinks in `.claude/` when `just sync-to-parent` exists
- Root cause: Script-First Evaluation says "execute simple operations directly" — but doesn't say "check for project recipes first"
- Correct pattern: Before ad-hoc commands, check `just --list` for existing recipes that handle the operation
- Fix: Created `project-tooling.md` fragment — project recipes take priority over equivalent ad-hoc commands
- Broader lesson: Loaded context directives must override general knowledge, not compete with it

**SessionStart hook is broken for new sessions (don't depend on it):**
- Issue: [#10373](https://github.com/anthropics/claude-code/issues/10373) — SessionStart output discarded for new sessions
- Only works after `/clear`, `/compact`, or `--resume`
- Root cause: `qz("startup")` never called for new interactive sessions
- Don't build features depending on SessionStart until fixed upstream
- Alternative: Use `@agents/session.md` in CLAUDE.md for task context (already loaded)

**Commit-rca-fixes implemented (3 fixes active):**
- Fix 1 (submodule awareness): Commit submodule first, then stage pointer in parent
- Fix 2 (artifact staging): prepare-runbook.py stages its own artifacts via `git add`
- Fix 3 (orchestrator stop rule): Absolute "no exceptions" language, deleted contradictory scenarios
- Status: All fixes implemented and committed, active in current workflow
- Prevents: Submodule sync drift, missing artifacts in commits, dirty-state rationalization

**Never auto-commit in interactive sessions:**
- Anti-pattern: Committing after completing work because it "feels like a natural breakpoint"
- Correct pattern: Only commit when user explicitly requests (`/commit`, `ci`, `xc`, `hc`)
- Rationale: Previous rule had ambiguous disjunction (three bullets any-one-sufficient vs "wait for user direction"). With `xc` (execute+commit) shortcuts, auto-commit provides no value — user controls commit timing explicitly

**MCP tools unavailable in sub-agents (Task tool):**
- Anti-pattern: Assuming quiet-task or other sub-agents can call MCP tools (Context7, etc.)
- Correct pattern: MCP tools only available in main session. Call directly from designer/planner, write results to report file for reuse.
- Confirmed: Empirical test — quiet-task haiku has no access to `mcp__plugin_context7_context7__*` tools
- Impact: Context7 queries cost opus tokens when designer calls them, but results persist for planner reuse

**Hook-based session capture is impractical for sub-agent outputs:**
- Anti-pattern: Using PostToolUse hooks to capture Explore/claude-code-guide results
- Correct pattern: Session-log based capture (future work) or quiet agents that write their own reports
- Rationale: Hooks don't fire in sub-agents. Task matcher fires on ALL Tasks (noisy). Better mechanism is session-log extraction.

**Outline-first design workflow prevents wasted opus tokens:**
- Anti-pattern: Producing full design.md in a single pass, then discovering user wanted different approach
- Correct pattern: Produce freeform outline first, iterate with user via incremental deltas, then generate full design after validation
- Escape hatch: If user already specified approach/decisions/scope, compress outline+discussion into single validation
