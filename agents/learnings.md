# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## Tool batching unsolved
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)
## "Scan" triggers unnecessary tools
- Anti-pattern: "Scan X.md" or "check X.md for..." where X is @-referenced via CLAUDE.md
- Correct pattern: "Check loaded X context" — content already in memory, no Read/Grep needed
- Applies to: memory-index.md, learnings.md, session.md, any @-referenced file
- Fix: Updated plan-tdd, plan-adhoc, commit skill to use "check loaded context" language
## Structural header dot syntax
- Anti-pattern: `.## Title` (dot before markdown marker)
- Correct pattern: `## .Title` (dot is part of title text, after `## `)
- Fix: Added explicit ✅/❌ examples to implementation-notes.md
- Rationale: "Prefix" is ambiguous — examples prevent misinterpretation
## Hard limits vs soft limits
- Anti-pattern: Validators that print warnings but don't fail build
- Correct pattern: Either fail build (hard error) or don't check (no validation)
- Rationale: "Normalize deviance" principle — warnings create false sense of compliance
- Example: memory-index word count changed from warning to hard error, exposed 62 violations
- Trade-off: Hard limits force immediate resolution but may need tuning (word count 8-12 may be too strict)
## Organizational sections and index pollution
- Anti-pattern: Index entries pointing to organizational sections (H2 with only H3 subsections)
- Correct pattern: Mark organizational sections structural (`.` prefix), autofix removes corresponding entries
- Judgment location: Decision happens at source (decision file), not at index — once structural, removal is automatic
- Recursive rule: Applies at all heading levels (H2, H3, H4) — any heading with no direct content before sub-headings
## Index entry key preservation
- Anti-pattern: Shortening index entry by changing key (part before em-dash)
- Correct pattern: Shorten description (after em-dash), preserve key exactly as header title
- Rationale: Validator matches index keys to decision file headers — changed key = orphan entry error
- Example: "Never auto-commit in interactive sessions — ..." → keep full key, shorten description only
## Batch edit token efficiency
- Marker format (`<<<` `>>>` `===`) saves 13% tokens vs JSON
- No quotes, braces, colons, or escaping needed
- Multi-line content handled naturally without escaping
- Script location: `agent-core/bin/batch-edit.py`
## Commits must remove invalidated learnings
- Anti-pattern: Adding enforcement without removing the "not enforced" learning in same commit
- Correct pattern: When a change invalidates a learning, remove/update that learning atomically
- Constraint added: handoff skill step 4b, commit-delegation.md step 3
- Trigger: Changes to enforcement (validators, scripts) or behavioral rules (fragments, skills)
## Restart vs model change
- Anti-pattern: Saying "Restart: yes" because task needs different model
- Correct pattern: Restart only for structural changes (agents, hooks, plugins, MCP, API config)
- Model changes: Use `/model` command at runtime, no restart needed
- Fix: Added "Restart triggers" definition to execute-rule.md
## Skill dependencies in requirements
- Anti-pattern: Deferring skill loading to A.1 judgment when requirements explicitly mention agent/skill creation
- Correct pattern: Scan requirements for skill dependency indicators during A.0, load immediately
- Indicators: "sub-agent" → agent-development, "invoke skill" → skill-development, etc.
- Fix: Added skill dependency scan to design skill A.0 checkpoint
## Manual runbook assembly bypasses automation
- Anti-pattern: Using `cat` + `Write` to assemble phase files into runbook.md during planning
- Correct pattern: Leave phase files separate, holistic review reads multiple files, prepare-runbook.py assembles
- Rationale: Assembly logic (metadata calc, cycle numbering validation) belongs in prepare-runbook.py, not manual process
- Manual assembly error-prone: wrong cycle count, missing metadata, inconsistent formatting
- Review agent can read multiple phase files — doesn't need pre-assembled input
- Fix: Updated plan-tdd Phase 4/5 to clarify prepare-runbook.py handles assembly, planner provides phase files
## Output requires vet+fix with alignment
- Anti-pattern: Implement task → commit without verification
- Correct pattern: Implement → vet-fix-agent review with alignment check → escalate UNFIXABLE → handoff → commit
- Alignment = verify output matches design/requirements/acceptance criteria
- Reports exempt: They ARE the verification artifacts
- Model-agnostic: Applies to haiku, sonnet, opus equally
- Delegation requires specification: If delegating implementation, provide criteria for alignment verification
- Fix: Commit skill Step 1 Gate B (vet checkpoint) — all models, alignment-focused
## Delegation without plan causes drift
- Anti-pattern: Opus specifies "do X | haiku" without runbook/acceptance criteria
- Correct pattern: Opus provides runbook OR acceptance criteria when delegating implementation
- Consequence: Without criteria, executing agent cannot verify alignment, vet cannot check drift
- Haiku-specific: Handoff uses `/handoff-haiku` not `/handoff` (no learnings judgment)
- Root cause of session deviation: Task had model spec but no execution spec
- Fix: Handoff skill now requires haiku tasks to include acceptance criteria (table + examples)
## Vet-fix-agent confabulation from design docs
- Anti-pattern: Give vet-fix-agent full design.md when reviewing phase checkpoint — agent may confabulate issues from future phases
- Correct pattern: Precommit-first grounds agent in real work; explicit IN/OUT scope prevents confabulating future-phase issues
- Rationale: Agent saw `horizontal_token_bar` in Phase 2 design, invented that test existed and claimed to fix it
- Key insight: Fix claims are dangerous (trusted by orchestrator), observations less so
- Mitigations: Precommit-first, explicit scope, "Do NOT flag items outside provided scope" constraint
## Phase boundaries require checkpoint delegation
- Anti-pattern: Treat checkpoint as part of step execution, skip vet-fix-agent delegation, proceed to next phase
- Correct pattern: Phase boundary = hard stop requiring explicit checkpoint delegation per orchestrate skill 3.3
- Rationale: Checkpoints catch bugs (logic error in format_context() found at Phase 2→3 boundary checkpoint)
- Fix: D+B hybrid merged phase boundary into 3.3 with Read anchor for phase detection
## Prose gate D+B hybrid fix
- Root cause: Execution mode optimizes for "next tool call" — prose-only steps get scanned but not executed
- Fix: Merge gates into adjacent action steps + anchor each gate with Read/Bash tool call
- Commit skill: Steps 0+0b+1 → single Step 1 (Gate A: Read session.md, Gate B: git diff, then validation)
- Orchestrate skill: 3.3+3.4 → merged 3.3 (tree check + Read next step for phase boundary)
- Convention: Every skill step must open with a tool call — documented in implementation-notes.md
## Deliverables go to plans/
- Repeated: 2026-02-06, 2026-02-08
- Anti-pattern: Writing actionable artifacts to tmp/ which is gitignored
- Correct pattern: If artifact will be referenced in a followup session → `plans/`. If not → `tmp/`
- Decision principle: "Will this be referenced later?" — not "Is this type in a known list?"
- Recurrence cause: Category-matching heuristic ("this isn't a report/design/audit") defeats the principle. New artifact types (feature request bodies, issue drafts) bypass enumerated categories
- Contributing: `tmp-directory.md` fragment says "ad-hoc work: use tmp/" without distinguishing tracked vs untracked output
- Rationale: Commits are sync points — session.md references must resolve in the same commit
## Git worktree submodule gotchas
- Unpushed submodule commits: `git submodule update --init` clones from remote, fails if commit not pushed
- Fix: `--reference <local-checkout>` uses local objects as alternates, avoids remote fetch
- Worktree removal: `git worktree remove` refuses with submodules (even after `deinit -f --all`)
- Fix: `--force` flag required; warn user about uncommitted changes before forcing
- Symlinks work: relative symlinks (../../agent-core/...) resolve correctly per-worktree after submodule init
## Recipe failure → retry recipe
- Anti-pattern: Recipe fails partway, agent manually completes remaining steps with ad-hoc commands
- Correct pattern: Fix obstruction (e.g., delete conflicting untracked file), retry the recipe from scratch
- Rationale: Recipes are atomic units — manually finishing bypasses error handling, ordering, side effects
- Fix: Added "Partial failure recovery" rule to project-tooling.md
## Lightweight TDD tier assessment
- Anti-pattern: Using full runbook (Tier 3) for straightforward fixture creation with repetitive pattern
- Correct pattern: Tier 2 (lightweight TDD) for ~15-20 cycles with same pattern — plan cycle descriptions, delegate individually, checkpoint every 3-5 cycles
- Rationale: Full runbook overhead (phase files, prepare-runbook.py, orchestrator) not justified for simple repetitive work
- Example: Markdown test corpus — 16 fixtures following same pattern (input/expected pairs), completed via lightweight TDD
- Tier boundaries: Tier 1 (1-3 cycles), Tier 2 (4-10 cycles OR 10-20 repetitive), Tier 3 (>20 cycles with complexity)
## Corpus defines correct behavior
- Anti-pattern: Rewriting fixtures to avoid triggering known bugs (makes tests pass by hiding defects)
- Correct pattern: Fixtures define correct behavior — failing tests are the signal that code needs fixing
- Rationale: Test corpus purpose is detecting changes required to process corpus correctly
## excludedCommands sandbox bypass unreliable
- Anti-pattern: Relying on `excludedCommands` in settings.json for filesystem/network sandbox bypass
- Correct pattern: Use `dangerouslyDisableSandbox: true` per-call + `permissions.allow` for prompt skip
- Evidence: npm added to excludedCommands, still got EPERM on `~/.npm/_cacache/` writes
- Known issues: #10767 (git SSH), #14162 (DNS), #19135 (logic conflict)
## Pipeline idempotency over exact match
- Anti-pattern: Pipeline test asserting remark output matches preprocessor expected fixtures
- Correct pattern: Assert full pipeline idempotency — `(preprocessor → remark)²` produces same result
- Rationale: Remark legitimately reformats (table padding, blank lines) — exact match conflates preprocessor correctness with formatter style
## Temporal validation for empirical analysis
- Anti-pattern: Running analysis on session history without checking if feature existed during those sessions
- Correct pattern: Correlate session timestamps with git history to validate feature availability
- Rationale: Sessions before feature creation yield expected-zero results, invalidating analysis
- Example: Memory index created Feb 1, sessions analyzed Feb 5-8 → valid (all had access)
- Git commands: `git log --format="%ai" --follow <file>` for creation date, session mtime for analysis window
- Strengthens findings: 0% recall validated across 200 sessions, all post-creation and post-stability
## Namespace collision in prefix design
- Anti-pattern: Reusing a symbol for new semantics without checking existing conventions
- Correct pattern: Check existing notation conventions before introducing new prefix semantics
- Rationale: `.` prefix on headers means "structural section" (validated by precommit). Reusing `.` in a different namespace (command syntax like `/when .section`) is safe because contexts don't overlap
- Resolution: `/when .section` and `/when ..file` use `.`/`..` as command mode switches (not heading prefixes), avoiding collision
## Prompt caching not file caching
- Anti-pattern: Assuming Claude Code deduplicates file reads or maintains a file cache (re-reading = free)
- Correct pattern: Each Read appends a new content block to conversation; "caching" = prompt prefix matching at API level (92% reuse, 10% cost)
- Rationale: No application-level dedup. 20-block lookback window limits cache hits when many tool calls intervene
- @-references (system prompt) are more cache-efficient than Read (messages) for always-needed content
## Behavioral triggers beat passive knowledge
- Anti-pattern: `/what` and `/why` operators for definitional/rationale knowledge — LLMs don't proactively seek context
- Correct pattern: `/when` (behavioral) and `/how` (procedural) only — these prescribe action, creating retrieval intention
- Rationale: LLMs use what's in context or ignore it; they don't probe for definitions unless specifically instructed
- Consequence: If a learning can't be phrased as `/when` or `/how`, it's either a fragment (ambient) or lacks actionable content
## Fuzzy bridge: density and clarity
- Anti-pattern: Index triggers must exactly match decision file headings (forces verbose triggers or cryptic headings)
- Correct pattern: Index triggers fuzzy-compressed for density, headings stay as readable prose, fuzzy engine bridges the gap
- Rationale: "how encode path" fuzzy-matches "How to encode paths" — index saves tokens, headings stay clear
- Validator uses same fuzzy engine: each trigger must uniquely expand to one heading, each heading reachable by exactly one trigger
## Design skill lacks resume logic
- Anti-pattern: Invoking `/design` when design is mid-flight — restarts from Phase A instead of resuming
- Correct pattern: When design is in progress, manually continue from current phase (read outline, proceed to Phase B/C)
- Rationale: `/design` is linear A→B→C with no "load existing artifacts" step
- Impact: For `/when` design, outline was updated directly this session, bypassing `/design` skill
## wt-merge empty submodule failure
- Anti-pattern: `git commit` in `set -e` script with nothing staged → exits 1, kills script before next step
- Correct pattern: Guard with `git diff --quiet --cached || git commit ...`
- Broader pattern: Recipe success ≠ task success — verify git state after recipe (unmerged commits, stale branches)
- Fix: justfile line 133 guarded, 4 stale worktrees recovered
## Agent scope creep in orchestration
- Anti-pattern: Prompt says "execute step N" without scope constraint — agent reads ahead and executes step N+1
- Correct pattern: Prompt must include "Execute ONLY this step. Do NOT read or execute other step files."
- Secondary: Orchestrator must verify agent return describes only the assigned step, not additional work
- Related: Checkpoint delegations must include explicit "commit all changes before returning"
- Anti-pattern: Receive user feedback, immediately apply changes, present result
- Correct pattern: Receive feedback → rephrase understanding → ask for validation → apply
- Rationale: Misinterpreting feedback in /design leads to wrong architectural decisions; rephrase catches misunderstandings early
- Scope: Especially important in /design, but generally applicable
## Sub-agent rules file injection limitation
- Anti-pattern: Assuming vet-fix-agent (sub-agent via Task) receives rules file context injection
- Correct pattern: Rules files fire in main session only; sub-agents don't receive injection
- Consequence: Domain context must be carried explicitly — planner writes it into runbook, orchestrator passes through task prompt
- Related: Hooks also don't fire in sub-agents (documented in claude-config-layout.md)
## Planning-time domain detection principle
- Anti-pattern: Expecting weak orchestrator (haiku) to detect domain and route to specialist agents
- Correct pattern: Planner (opus/sonnet) detects domain, encodes domain skill references in runbook vet steps
- Rationale: Weak orchestrator executes mechanically; domain detection requires intelligence; Dunning-Kruger prevents runtime self-assessment of knowledge gaps
- Pattern: "encode concerns at planning time, not orchestration time"
## Structured criteria manage overload
- Anti-pattern: Splitting review across multiple agents (quality + alignment + domain = 3 invocations)
- Correct pattern: Single vet-fix-agent with domain skill file providing explicit checklists and good/bad examples
- Rationale: One agent per concern is expensive; structured skill files provide bounded criteria (not unbounded reasoning)
- Trade-off: Cost over theoretical fidelity; skill file quality determines review quality
## No auto-stash, require clean tree
- Anti-pattern: Using `git stash` to work around dirty tree before merge/rebase operations
- Correct pattern: Require clean tree to assert process integrity. Exception: session context files (session.md, jobs.md, learnings.md) auto-committed as pre-step
- Rationale: Stash is fragile (conflicts on pop, lost stashes). Clean tree forces explicit state management
- Related: wt-merge skill design — clean tree gate with session context exception
## Always script non-cognitive solutions
- Anti-pattern: Using agent judgment for deterministic operations (conflict resolution with known pattern, session file updates)
- Correct pattern: If solution is non-cognitive (deterministic, pattern-based), script it. Always auto-fix when possible.
- Examples: Session context merge conflicts (keep both sides), worktree task removal from session.md, gitmoji → no judgment needed
- Corollary: Reserve agent invocations for cognitive work (design, review, ambiguous decisions)
## Plugin-dev skill fallback
- When plugin-dev guidance is incomplete or inconsistent, fallback to claude-code-guide agent
- Example: hooks.json format conflict — plugin-dev:hook-development said wrapper format for hooks.json, claude-code-guide clarified direct format is correct
- Pattern: plugin-dev skills are curated snapshots, claude-code-guide has live docs access
## Per-artifact vet coverage required
- Anti-pattern: Create/expand multiple runbook phases in sequence → commit all without individual vet reviews
- Correct pattern: Each phase file is a production artifact → each requires vet-fix-agent review before proceeding
- Root cause: Batch momentum — once first artifact skips review, switching cost increases for each subsequent one
- Rationalization escalation: "Phase 0 was the hard one" → each subsequent phase rationalized as lower risk
- Phase 0 vet found 13 issues in file that "followed the design" — proof that template-following ≠ correctness
- Gate B structural gap: Boolean presence check (any report?), not coverage ratio (artifacts:reports 1:1)
- "Proceed" scope: Activates execution mode which optimizes throughput, rationalizing away friction (vet checkpoints)
## Sequential Task launch breaks parallelism
- Anti-pattern: Launch Task agents one at a time (Phase 1 → wait → Phase 2 → wait...) when all inputs ready and no dependencies
- Correct pattern: Batch all independent Task calls in single message (6 vet reviews → 6 Task calls in one message)
- Root cause: Tool batching rule doesn't explicitly cover Task tool — extension principle not documented
- Wall-clock impact: Sequential = sum(task_times), parallel = max(task_times) — wastes ~14 min for 6 reviews
- Fix needed: Add Task tool section to tool-batching.md with explicit examples
## Failed merge leaves untracked debris
- Anti-pattern: Assume aborted merge is clean — retry merge, get "untracked files would be overwritten"
- Correct pattern: After merge abort, check for new untracked files materialized during merge attempt
- Rationale: Git materializes new files from source branch during merge, aborts without cleaning them up
- Fix: `git clean -fd -- <affected-dirs>` to remove debris, then retry merge
- Diagnostic: File count (untracked vs files added by source branch) and birth timestamps match merge attempt time
## Never agent-initiate lock file removal
- Anti-pattern: Agent removes .git/index.lock after git error suggests "remove the file manually"
- Correct pattern: Stop on unexpected git lock error, report to user, wait for guidance
- Rationale: Lock may indicate active git process; removal by agent bypasses "stop on unexpected results" rule
- Scope: All git operations (merge, commit, rebase) — wait 2s and retry, never delete lock files
- Contributing factor: Project directives scoped lock handling to commit only, agent over-generalized
## Vet-fix-agent context-blind validation
- Anti-pattern: Trust vet-fix-agent output without validation, no execution context provided in delegation
- Vet validates against current filesystem not execution-time state — Phase 6 error: "fixed" edify-plugin → agent-core
- UNFIXABLE issues in reports don't trigger escalation (manual detection required)
- Correct pattern: Provide execution context (IN/OUT scope, changed files, requirements), grep UNFIXABLE after return
- Fix: vet-requirement.md updated with execution context template + UNFIXABLE detection protocol; vet-fix-agent.md updated with execution context section in review protocol
- UNFIXABLE grep is mechanical (consistent with weak orchestrator) — not a judgment call
## Delegation vs execution routing
- Anti-pattern: Single fragment covering both interactive routing and orchestration delegation — conflicting signals
- Correct pattern: Split into execution-routing.md (interactive: understand first, do directly) and delegation.md (orchestration: dispatch to agents)
- Rationale: "Delegate everything" is correct for runbook orchestration, wrong for interactive work
- Fix: delegation.md 131→44 lines (orchestration only), execution-routing.md 25 lines (interactive routing)
## Submodule commit orphan recovery
- Anti-pattern: Reset dev branch to match main — loses submodule commits that only existed on dev
- Correct pattern: Before branch reset, check for submodule commits not on target branch (`git merge-base --is-ancestor`)
- Diagnostic: `git ls-tree <parent-commit> -- agent-core` to extract submodule pointer, then check ancestry
- Recovery: `git -C agent-core merge <orphaned-commit>` if commit still exists as loose object
- Example: focus-session.py (ff056c7) orphaned when dev reset to main, recovered via parent repo history
## E2E over mocked subprocess
- Anti-pattern: Dual test suite — e2e for behavior + mocked subprocess for speed
- Correct pattern: E2E only with real git repos (tmp_path fixtures), mocking only for error injection
- Rationale: Git with tmp_path is fast (milliseconds), subprocess mocks are implementation-coupled (command strings not outcomes), interesting bugs are state transitions that mocks can't catch
- Exception: Mock subprocess for error injection only (lock files, permission errors)
## Flexible phase numbering support
- Anti-pattern: Hardcoding phase validation to expect 1-based numbering (phases 1-N)
- Correct pattern: Detect starting phase number from first file, validate sequential from that base
- Rationale: Design decisions may use 0-based (Phase 0 = foundational step) or 1-based numbering
- Implementation: `start_num = phase_nums[0]`, validate against `range(start_num, start_num + len)`
- Also supports general vs TDD detection: Step headers = general, Cycle headers = TDD
- Fix: agent-core/bin/prepare-runbook.py lines 410-445
## Self-referential runbook modification
- Anti-pattern: Runbook step uses `find plans/` or `sed -i` on `plans/` directory — includes `plans/<plan-name>/` itself
- Correct pattern: Exclude plan's own directory (`-not -path 'plans/<plan-name>/*'`) or enumerate specific target directories
- Detection: Check if any step's file-mutating command scope overlaps `plans/<plan-name>/` (excluding `reports/`)
- Root cause: Blanket directory operations look correct but scope includes the executing runbook
- Fix: Added `-not -path` exclusion to Phase 0 step 12; vet criterion added to main repo
## Worktree merge loses pending tasks
- Anti-pattern: `git checkout --ours agents/session.md` during worktree merge — discards worktree-side pending tasks
- Correct pattern: Extract new pending tasks from worktree session.md before resolving conflict, append to main
- Algorithm: Parse both sides' Pending Tasks by task name regex, diff, append new worktree-side tasks to main
- Example: "Execute plugin migration" task created in worktree, lost by blind --ours resolution
- Fix: Outlined in `plans/worktree-skill/outline.md` Session File Conflict Resolution section
