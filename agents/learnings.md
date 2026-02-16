# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## When visible primitives enable decomposition
- Anti-pattern: Loading all justfile recipes into agent context via @-reference — primitives (wt-rm, wt-merge) visible alongside skills that wrap them
- Correct pattern: Curate in-context recipe list to essential commands only. Primitives exist as fallback but aren't in agent's active context
- Rationale: Agent reads skill, understands internals, selects "simpler" primitive that lacks side effects (session.md updates). Rule additions fail (4 instances same pattern) because rules compete for attention. Structural fix: reduce primitive visibility
- Fix: CLAUDE.md @.cache/just-help*.txt → inline 5-recipe list; removed cache infrastructure entirely
## When shortcuts bypass upstream steps
- Anti-pattern: Pre-evaluating whether a shortcut's chain has work to do (e.g., `hc` → check git status → clean → skip handoff entirely)
- Correct pattern: Invoke the expansion directly. Each step in the chain creates preconditions for the next. Checking downstream preconditions before running upstream steps aborts chains that would have succeeded.
- Same class as "execute directly" deviation — premature termination of multi-step chains based on downstream precondition evaluation
- Fix: execute-rule.md Tier 1 shortcuts section: "Shortcuts are mechanical expansions — invoke directly. Do not pre-evaluate."
## When execute directly skips safety
- Anti-pattern: Design skill triage → "Simple → execute directly" → skip skill checks, recipe checks, cwd rules
- Correct pattern: "Execute directly" means skip design ceremony, not skip operational rules. Skill-check-first and recipe-check-first still apply.
- Root cause: "Simple" classification creates execution mode that optimizes throughput by rationalizing away ALL friction, not just design-level ceremony
- Fix: Design skill Simple path updated to say "Check for applicable skills and project recipes first, then execute directly"
## When orchestrator handles review delegation
- Anti-pattern: Expecting execution agents to delegate review (to any reviewer, not just plugin-dev)
- Correct pattern: Orchestrator delegates ALL reviews after execution agents commit
- Rationale: (1) Sub-agents lack Task and Skill tools — cannot delegate to any reviewer. (2) All reviews must be delegated to prevent implementer bias — implementer never reviews own work. Domain-specific routing: vet-fix-agent (code), skill-reviewer (skills), agent-creator (agents), plan-reviewer (planning), vet-fix-agent + doc-writing skill (human docs). See artifact review routing table in pipeline-contracts.md.
## When deliverable review catches drift
- Anti-pattern: Relying solely on per-step vet reviews for quality assurance
- Correct pattern: Post-orchestration deliverable review catches inter-file consistency gaps (stale copies, broken references, missing cross-references) that per-step vet misses
- Evidence: memory-index skill drifted during execution (3 entries missing); workflows-terminology.md referenced non-existent agent; runbook skill missing general-patterns.md reference
- These were invisible to per-step vet because each step's artifacts were internally consistent
## When writing methodology
- Anti-pattern: Producing scoring frameworks, evaluation axes, or "best practice" documents from internal reasoning alone — yields confabulated methodologies with subjective weights and ungrounded criteria
- Correct pattern: Invoke `/ground` skill. Diverge-converge with parallel branches: internal (brainstorm for project-specific dimensions) + external (web search for established frameworks). Synthesize by mapping internal dimensions onto external skeleton.
- Evidence: First prioritization attempt produced subjective weights ("Highest/High/Medium") and 0-3 scores without defined criteria. After grounding in WSJF research, methodology used Fibonacci scoring with observable evidence sources.
## When research deliverables misplaced
- Anti-pattern: Writing research synthesis documents to tmp/ — they're ephemeral and won't survive across sessions
- Correct pattern: Research deliverables that inform future work go to plans/reports/ (persistent, tracked). Only scratch computation goes to tmp/.
- Rationale: tmp/ is gitignored. Research synthesis is a reusable artifact referenced by skill creation and future prioritization runs.
## When relaunching similar task
- Anti-pattern: Launching a fresh agent with the same prompt after a stopped/killed agent, losing prior context
- Correct pattern: Use Task tool's `resume` parameter with the prior agent's ID. The agent retains full prior context (files read, reasoning done) and continues from where it stopped.
- Rationale: Stopped agents may have completed expensive operations (file reads, web searches). Resuming preserves that work; relaunching repeats it.
## When naming triggers
- Anti-pattern: Naming `/when` triggers after the anti-pattern, outcome, or self-assessment ("When synthesizing ungrounded methodology", "When deliverable review catches drift", "When resuming killed agents")
- Correct pattern: Name triggers after the **activity at the decision point** — what the agent is doing when it needs the knowledge. Use the broadest verb that still triggers correctly. No self-assessment terms (agent can't evaluate what it doesn't know).
- Examples: "When writing methodology" not "When synthesizing ungrounded methodology". "When relaunching similar task" not "When resuming killed agents".
- Same principle as `/when choosing name`: discovery and recall over precision.
## When reviewing skill structure
- Anti-pattern: Delegating deliverable review to Task agent — agent lacks cross-project context (other skills' allowed-tools, fragment conventions, memory index patterns)
- Correct pattern: Interactive review with full context (CLAUDE.md fragments, learnings, memory index loaded). The reviewer needs to compare against project-wide patterns, not just the artifact's internal consistency.
- Evidence: Task agent found 5 minor issues but missed the major finding (Write missing from allowed-tools). Only detectable by comparing against 18 other skills' allowed-tools fields.
## When writing CLI output
- Anti-pattern: CLI suggesting destructive commands in output (e.g., `"use: git branch -D <slug>"`). LLM agents treat CLI output as instructions and execute the suggested command.
- Correct pattern: Report the problem without prescribing destructive workarounds. Let the calling agent or user decide the action. CLI should refuse destructive operations, not suggest them.
- Evidence: `_worktree rm` suggested `git branch -D` for unmerged branch. Agent followed the instruction, permanently deleting the only copy of unmerged parent repo changes.
## When analyzing task insertion patterns
- Anti-pattern: Assuming all single-task insertions share the same urgency profile. Overall data (n=65) showed 61.5% prepend, suggesting "always prepend" is natural behavior.
- Correct pattern: Segment by origin. `p:` directives (n=29) distribute evenly (34.5% prepend). Workflow continuations dominate the prepend signal. Different insertion policies needed per origin type.
- Evidence: Session scraping + git correlation across 337 sessions, 506 commits. Handoff skill says "append" but agents correctly override for both populations.
- Implication: Handoff skill should say "insert at estimated priority position" not "append" — agents already exercise good judgment.
## When reviewing runbooks after expansion
- Anti-pattern: Relying on text-based review (plan-reviewer) to catch all runbook defects. Text review validates TDD discipline, prescriptive code, vacuity — but misses execution-time concerns.
- Correct pattern: Add structural validation after text review: (1) file lifecycle graph (create→modify ordering), (2) RED plausibility (expected failures valid given prior GREEN), (3) test count reconciliation (checkpoint numbers match test functions). File lifecycle and test count are deterministic (scriptable). RED plausibility may need LLM judgment.
- Evidence: Holistic review caught formatting/metadata issues and one dependency ordering bug, but would not have caught an "already-passing RED" from cycle consolidation.
## When batching runbook cycles
- Anti-pattern: Planning 4 identical-pattern cycles separately (e.g., 4 status levels each adding one artifact check to the same function), then optimizing post-hoc.
- Correct pattern: Detect identical patterns during Phase 1 expansion and consolidate upfront. Indicators: same function modified, same test structure, only the fixture data differs. Parametrized cycle with table of inputs replaces N separate RED/GREEN rounds.
- Evidence: Workwoods P1 cycles 1.2-1.5, P5 cycles 5.5-5.7, P4 cycles 4.3-4.6 all exhibited this pattern. Post-hoc optimization saved 12 items but required 5 parallel agents + holistic re-review.