# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/codify` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---

## When a proximal requirement reveals lifecycle gaps
- Triage feedback (Gap 7) required a post-execution comparison point. Investigation: /commit too generic (fires all sessions), /handoff wrong scope (session state not execution assessment). Root cause: inline execution (Tier 1, /design direct execution) has no lifecycle skill. The pipeline state machine goes /requirements → /design → /runbook → /orchestrate → /deliverable-review → /commit, but work classified as execution-ready exits through an unstructured gap between /design and /handoff.
- Correct pattern: the proximal requirement points at the structural gap. Fix the gap (inline execution skill covering pre-work + execute + post-work), and the proximal requirement becomes one FR among many.
- Corollary: conditional gates ("skip Read if no /design ran") reintroduce prose-gate failure modes. The D+B principle applies: unconditional Read, file absence is the negative path. A Read returning file-not-found is cheaper than the risk of a missed comparison.
## When implementation modifies pipeline skills
- Anti-pattern: Using the full runbook pipeline (prepare-runbook.py → orchestrator → step files) when the planned work modifies pipeline skills (/design, /runbook) or pipeline contracts. Self-modification coupling: a runbook step that edits the runbook skill creates stale-instruction risk for subsequent steps.
- Correct pattern: Structure as inline task sequence orchestrated through session pending tasks. Each task executes with fresh CLAUDE.md loads, sidestepping stale instructions. TDD discipline preserved — executing session dispatches test-driver via Task tool per cycle. Corrector dispatch per task replaces checkpoint gates.
- Also applies when: no parallelization benefit (strict dependency chain negates Tier 3's parallel step execution), overhead/value mismatch (pipeline coordination cost > error-recovery value for ~10 sequential work units).
## When delegating TDD cycles to test-driver
- Anti-pattern: Sending all N cycles in a single prompt. Agent loses focus on later cycles, context overloaded with spec it hasn't reached yet. Also: full prompt may trigger hooks on path patterns in test fixture descriptions.
- Correct pattern: Piecemeal — one cycle per invocation. Resume the same agent for subsequent cycles (preserves accumulated file reads + implementation context). Continue until agent context nears 150k. Fresh agent if context exhausted.
- Context priming: Sub-agents don't share parent context. Each NEW agent must self-prime by running `when-resolve.py` on relevant recall-artifact entries. Include instruction: "Read plans/X/recall-artifact.md, then batch-resolve relevant entries via `agent-core/bin/when-resolve.py`." Resumed agents already have this context.
## When assessing just precommit cost
- `just precommit` is fast when the test suite is green, thanks to test sentinel. Not a heavy operation in the common case — valid as both entry gate and exit gate without redundant overhead concern.
## When editing skill files
- The `description` field is dual-purpose: CLI picker display AND agent triggering (no separate field — #28934). Lead with action verb (user display), then trigger phrases (agent matching). H1 title is body content only. Fallback: first paragraph if `description` omitted.
- Extraction safety: every content block moved to references/ must leave trigger condition + Read instruction in SKILL.md body.
- Control flow verification: after restructuring conditional branches, enumerate all paths, verify user-visible output on each.
- D+B gate additions: must not change gate decision outcome on existing paths.
- Entry point naming: named entry points (`execute`) not `--flag` conventions. Skills parse prose args, not CLI flags.
- Prose quality: `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework.
- Triggers: editing skills, skill surgery, deslop, extraction, progressive disclosure, restructuring conditional branches
- Pending: consolidate into `/skill-dev` skill (front-loads plugin-dev:skill-development via continuation passing)
## When writing recall artifacts for sub-agents
- Two distinct artifact models: pipeline recall (grouped entries with relevance notes, selective resolution by consuming skill) vs sub-agent injection (flat trigger list, resolve-all, no selection judgment). Sub-agents have no parent context — they can't judge which entries are relevant, making selective resolution circular.
- Anti-pattern: Using pipeline-model artifacts (grouped, relevance notes) when the consumer is a delegated agent. The grouping invites selective resolution which the agent can't perform.
- Correct pattern: Flat list for sub-agent injection. Delegation prompt says "resolve ALL entries." Pipeline model for skills/orchestrators that have topic context for selection.
## When loaded decisions miss error context
- Decisions loaded via `/recall broad` early in session aren't functionally present when errors fire later (context rotation). The agent processes lint error against immediate context (error message, rule description), not against decisions loaded 50k+ tokens earlier.
- Anti-pattern: Adding another recall pass as prose instruction ("recall after lint failure") — this is a prose gate, same failure mode as the original recall.
- Correct pattern: Structural injection — PostToolUse hook injects memory-index content on first lint/precommit red after green (state-transition gated). Separate PreToolUse recall gate forces index scanning before fix attempt. Two layers: injection (availability) + gate (application).
## When handling deliverable review findings
- Anti-pattern: "Minor findings deferred — no pending task created." Deferral without a tracking mechanism is abandonment. The finding disappears from all active surfaces.
- Correct pattern: Every finding must resolve to one of: (1) fix inline now, or (2) pending task as issue tracker entry. There is no third option. "Noted in report" is not a resolution — reports are not checked proactively.
- Rationale: Session.md pending tasks are the issue tracker. If work isn't there, it doesn't exist.
## When routing Moderate classification to runbook
- Requirements can be behaviorally complete (every FR has testable acceptance criteria) but structurally incomplete (no module layout, function decomposition, wiring decisions). The /design Moderate route skips design entirely — "Route to /runbook." The /runbook Tier 3 has Phase 0.75 (runbook outline) but that's runbook structure, not implementation approach.
- Anti-pattern: Letting structural decisions (package layout, shared components, error patterns, test organization) get made implicitly during runbook cycle planning or ad-hoc by the executing agent.
- Correct pattern: When requirements lack structural decisions, generate a lightweight outline before /runbook. The outline materializes "how" decisions (module structure, component boundaries, wiring) alongside the "what" (behavioral spec). Skip only when requirements are functionally complete — behavioral + structural.
- Single data point: recall-cli-integration. Trigger condition needs sharper criteria before modifying /design skill.
## When orchestrating multi-step delegated execution
- Anti-pattern: Splitting post-step verification into separate tool calls. First check (git status) returns clean → exit momentum suppresses second check (just lint). The sub-agent "already linted" rationalization makes the skip feel safe.
- Correct pattern: Single compound command (`git status --porcelain && just lint`). Compound commands can't be partially executed — both run or neither. Same principle as `_fail` consolidating display+exit.
- Also applies: `execute` entry point in session.md. `execute` is a same-turn chaining flag (skill → skill within one conversation). session.md always crosses a context boundary — `execute` there bypasses Phase 2 recall (D+B anchor). Precommit lint catches this mechanically.
## When writing multiline strings in indented code
- Anti-pattern: Triple-quoted strings flush-left or with inconsistent indentation to avoid unwanted whitespace in the value. Breaks visual code structure.
- Correct pattern: `from textwrap import dedent`, then `dedent("""\n    indented content\n    """)`. Keeps the string visually aligned with surrounding code while stripping common leading whitespace at runtime.
- Scope: non-docstring multiline strings (test fixtures, template content, heredoc-style text). Docstrings have their own `inspect.cleandoc` handling.
## When reading validation command output
- Anti-pattern: `just precommit 2>&1 | tail -N` or similar truncation. Validation output is a diagnostic signal — truncation hides the pass/fail/xfail summary that distinguishes real failures from expected noise. Agent then draws wrong conclusions from incomplete data.
- Correct pattern: Show full output from `just precommit`, `just test`, `just lint`. If output is too long, fix the recipe (add `--quiet`, `--tb=no`), not the consumption site.
- Evidence: xfail traceback from `pytest-markdown-report` was visually identical to real failure. Agent tailed output, missed summary counts, ran `git stash` diagnostic cycle, still drew wrong conclusion. Full output would have shown "30 passed, 1 xfailed" immediately.