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

**Heredocs broken in sandbox mode — SOLVED:**
- Root cause: zsh uses `TMPPREFIX` (not `TMPDIR`) for heredoc temp files. Default `/tmp/zsh` is outside sandbox allowlist
- Fix: `export TMPPREFIX="${TMPDIR:-/tmp}/zsh"` in agent-core/configs/claude-env.sh (sourced by .envrc)
- Upstream issue: Claude Code sandbox sets TMPDIR but not TMPPREFIX for zsh — should be reported

**Skills need multi-layer discovery, not just good internal docs:**
- Anti-pattern: Build a well-documented skill and assume agents will find and use it ("build it and they will come")
- Correct pattern: Ensure skill is surfaced via multiple discovery mechanisms — CLAUDE.md fragment, path-triggered `.claude/rules/` entry, in-workflow reminders in related skills, directive skill description
- Rationale: Agents only see skill listing descriptions and always-loaded context. Internal skill docs are invisible until invoked. The opus-design-question skill had excellent 248-line docs but zero external visibility — agents asked the user instead of consulting it.
- Example: 4-layer fix for opus-design-question: fragment + design skill reminder + path rule + directive description

**Shortcut systems need two layers: hook + fragment:**
- Anti-pattern: Rely solely on hook (exact-match only) or solely on fragment (LLM may ignore)
- Correct pattern: Hook for mechanical expansion of standalone shortcuts, fragment for vocabulary comprehension when shortcuts appear inline in natural language
- Rationale: Users naturally embed shortcuts in prose ("design this then hc"). Hooks can't match that (exact match fails), but agent can interpret from vocabulary table. Both layers complement, neither duplicates.

**UserPromptSubmit hooks cannot rewrite prompts:**
- Can only add `additionalContext` or block (exit 2) — original prompt passes through unchanged
- No `matcher` support — fires on every prompt. All filtering must be script-internal
- Use `hookSpecificOutput.additionalContext` for discrete context injection (not shown in transcript)
- Plain text stdout also works but is visible in transcript

**Case-sensitive shortcuts are unreliable for LLM interpretation:**
- Anti-pattern: `X` vs `x` for different commands (e.g., execute vs execute+commit)
- Correct pattern: Use distinct tokens (`xc` vs `x`) rather than case differentiation
- Rationale: LLMs are unreliable at distinguishing case. Two distinct characters are unambiguous

**Sandbox bypass: `permissions.allow` + `dangerouslyDisableSandbox` is the reliable combo:**
- Anti-pattern: Relying on `excludedCommands` for sandbox bypass (buggy — check if fixed:
  https://github.com/anthropics/claude-code/issues/10767,
  https://github.com/anthropics/claude-code/issues/14162,
  https://github.com/anthropics/claude-code/issues/19135)
- Anti-pattern: Adding interpreter prefix (`python3 cmd`) which breaks `permissions.allow` pattern matching
- Correct pattern: Match `permissions.allow` prefix exactly (no `python3`) + use `dangerouslyDisableSandbox: true` for writes outside cwd
- Result: `permissions.allow` auto-grants the sandbox lift (no prompt), `dangerouslyDisableSandbox` reliably bypasses sandbox
- Example: `agent-core/bin/prepare-runbook.py` — direct invocation (has shebang), with `dangerouslyDisableSandbox: true` for `.claude/agents/` write

**Commit skill has no submodule awareness — causes silent sync drift:**
- Anti-pattern: `git status` shows `M agent-core`, agent stages parent files but ignores submodule internals
- Correct pattern: When submodule is modified, inspect inside it, commit submodule first, then stage pointer in parent
- Rationale: Parent commit with dirty submodule pointer creates sync issues that compound across sessions
- Fix designed: `plans/commit-rca-fixes/design.md` (Fix 1)

**Orchestrator stop rules get overridden by LLM judgment:**
- Anti-pattern: Rule says "STOP on dirty git" but agent rationalizes "expected report file" and continues
- Correct pattern: Make rules absolute with "no exceptions" language + delete contradictory scenarios
- Rationale: LLMs will exploit any ambiguity. Contradictory guidance (section 3.3 says stop, scenarios section says continue) guarantees inconsistent behavior
- Fix designed: `plans/commit-rca-fixes/design.md` (Fix 3)

**Plan skills must stage artifacts immediately after prepare-runbook.py:**
- Anti-pattern: Generate artifacts, then tail-call handoff→commit hoping commit discovers them
- Correct pattern: `git add` step files, orchestrator plan, and agent file immediately after prepare-runbook.py
- Rationale: Commit skill stages "specific files only" and may miss `.claude/agents/` files it doesn't know about
- Fix designed: `plans/commit-rca-fixes/design.md` (Fix 2)
