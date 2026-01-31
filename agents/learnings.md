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

**prepare-runbook.py must stage its own artifacts:**
- Anti-pattern: Generate artifacts, then rely on downstream skills/commit to discover and stage them
- Correct pattern: `git add` inside prepare-runbook.py itself — script owns knowledge of what it creates
- Rationale: Commit skill stages "specific files only" and may miss `.claude/agents/` files. Putting `git add` in plan skills duplicates logic and couples them to script internals
- Fix designed: `plans/commit-rca-fixes/design.md` (Fix 2)

**All tiers must end with `/handoff --commit`, never bare `/commit`:**
- Anti-pattern: Tier 1/2 skip handoff because "no session restart needed"
- Correct pattern: Always tail-call `/handoff --commit` — handoff captures session context and learnings regardless of tier
- Rationale: Handoff is about context preservation, not just session restart. Even direct implementations produce learnings and update pending task state

**Vet uses two agents, selected by caller context:**
- `vet-agent` — review only (caller has context to apply fixes: Tier 1/2 direct/lightweight)
- `vet-fix-agent` — review + apply critical/major fixes (orchestration: Tier 3, no other agent has context)
- Tool list enforces contract: vet-agent has no Edit tool, vet-fix-agent has Edit
- Anti-pattern: single agent with mode flag (LLM may ignore, tool list can't enforce)

**Handoff `--commit` tail-call means session.md assumes commit succeeds:**
- Anti-pattern: Writing "Ready to commit" in Status or "pending commit" in footer when `--commit` flag is active
- Correct pattern: Write status reflecting post-commit state — the tail-call makes commit atomic with handoff
- Rationale: Next session reads session.md post-commit. Stale commit-pending language causes agents to re-attempt already-completed commits. The rule against commit tasks in Pending/Next Steps must extend to ALL sections

**Hook output visibility — `systemMessage` vs `additionalContext`:**
- Anti-pattern: Using `systemMessage` in hook output expecting Claude to see it
- Correct pattern: Use `hookSpecificOutput.additionalContext` for Claude-visible context; `systemMessage` is user-facing only
- Three visibility channels: `additionalContext` → Claude sees; `systemMessage` → user sees; stderr + exit 2 → Claude sees as error
- `.claude/hooks/hooks.json` is NOT a valid config location — hooks go in settings.json only

**Symlinks can silently become regular files:**
- Anti-pattern: Assume symlinks in `.claude/hooks/` persist across tool operations
- Correct pattern: Verify symlinks after any operation that reformats files (`just dev`, `ruff format`)
- Rationale: Formatters follow symlinks and may replace them with reformatted copies. `just dev` did this to both hook .py files

**Shell command continuation in hooks can be exploited:**
- Anti-pattern: Allowing `command.startswith(pattern + ' ')` for restore commands — permits `cd /root && malicious_cmd`
- Correct pattern: Use exact match only (`command in restore_patterns`) for security-sensitive restore operations
- Rationale: Shell operators (&&, ;, ||) can chain additional commands. Exact match prevents exploitation while still allowing the intended restore command

**Hooks only active in main agent session:**
- Anti-pattern: Expecting hooks (PreToolUse/PostToolUse/UserPromptSubmit) to fire in sub-agents spawned via Task tool
- Correct pattern: Test hooks manually in main session, or document sub-agent limitation in testing procedures
- Rationale: Hooks load at main session startup and don't propagate to sub-agent execution contexts. Sub-agents can have tools (Bash, Write) but hook interceptors won't fire.

**Hook messages need dual output for user+agent visibility:**
- Anti-pattern: Using only `additionalContext` or only `systemMessage` in hook output
- Correct pattern: Include both `additionalContext` (agent sees) and `systemMessage` (user sees) in hook JSON output
- Rationale: Users need to see hook warnings/expansions directly. Agents need context injection. Dual output ensures both audiences get the message.

**Agent frontmatter YAML must be strictly valid:**
- Anti-pattern: Placing `<example>` blocks directly in frontmatter with `description:` (single-line syntax)
- Correct pattern: Use `description: |` multi-line syntax with all examples indented as part of the field value
- Rationale: YAML parsers treat unindented content after `description:` as new fields. Invalid YAML prevents agent registration. Multi-line string syntax (`|`) makes examples part of description value.

**General knowledge overrides project directives (Script-First Evaluation gap):**
- Anti-pattern: Using `ln -sf` to create symlinks in `.claude/` when `just sync-to-parent` exists
- Root cause: Script-First Evaluation says "execute simple operations directly" — but doesn't say "check for project recipes first"
- Correct pattern: Before ad-hoc commands, check `just --list` for existing recipes that handle the operation
- Fix: Created `project-tooling.md` fragment — project recipes take priority over equivalent ad-hoc commands
- Broader lesson: Loaded context directives must override general knowledge, not compete with it

**Ambiguous directive language causes unwanted behavior:**
- Anti-pattern: "Drive to completion, then stop" in #execute expansion — ambiguous enough to trigger commit
- Issue: Agent interpreted "drive to completion" as including handoff+commit, violating "never commit unless asked"
- Correct pattern: Explicit prohibition — "Complete the task, then stop. Do NOT commit or handoff."
- Rationale: LLMs exploit ambiguity. Clear boundaries prevent scope creep in automation directives
- Distinction: `x` (execute only) vs `xc` (execute + commit) must be unambiguous in expansion text

**Don't delegate when context is already loaded:**
- Anti-pattern: Reading files, gathering context, then delegating to another agent (which re-reads everything)
- Correct pattern: If you already have files in context, execute directly — delegation adds re-reading overhead
- Rationale: Token economy. Agent overhead (context setup + re-reading) exceeds cost of continuing in current model
- Corollary: Delegate when task requires *new* exploration you haven't done yet

**Prose questions with multiple options create ambiguous one-letter responses:**
- Anti-pattern: "Want me to A or B? Would you rather capture B first?" — `y` binds to last question, not first option
- Correct pattern: Use AskUserQuestion tool for multi-option choices (structured labels, no ambiguity)
- Rationale: Users type `y`/`n` for quick responses. Prose questions with trailing yes/no make `y` ambiguous when multiple options were presented
- Fix: Added communication rule 5 in `agent-core/fragments/communication.md`

**Redundant routing layers waste tokens through double-assessment:**
- Anti-pattern: Entry point skill (oneshot) assesses complexity, then routes to planning skill which re-assesses complexity (tier assessment)
- Correct pattern: Single entry point with triage that routes directly to the appropriate depth — no intermediate routing layer
- Rationale: Each assessment reads files, analyzes scope, produces output. Two assessments for the same purpose is pure waste
- Example: Oneshot assessed simple/moderate/complex, then /plan-adhoc re-assessed Tier 1/2/3 — same function, different labels

**First delegated agent failing doesn't mean start over — vet agent has context:**
- Anti-pattern: When removal agent makes mistakes and vet catches them, launching a new fix agent (which re-reads everything)
- Correct pattern: If vet agent has the context of what's wrong, leverage it. If caller also has context (from reading vet report), apply fixes directly
- Rationale: Tier 1/2 pattern — caller reads report, applies fixes with full context. No need for another agent round-trip