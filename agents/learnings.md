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
## Deliverables in gitignored tmp/
- Anti-pattern: Writing actionable reports (RCA, designs, audits) to tmp/ which is gitignored
- Correct pattern: Research deliverables go to plans/ directories where they're tracked. Only ephemeral scheduling/diagnostic artifacts belong in tmp/
- Rationale: Commits are sync points — session.md references must resolve in the same commit. Gitignored paths break state synchronization across sessions
- Distinction: tmp/ = throwaway (execution logs, scratch). plans/ = actionable (designs, RCA reports, audits)
## Git worktree submodule gotchas
- Unpushed submodule commits: `git submodule update --init` clones from remote, fails if commit not pushed
- Fix: `--reference <local-checkout>` uses local objects as alternates, avoids remote fetch
- Worktree removal: `git worktree remove` refuses with submodules (even after `deinit -f --all`)
- Fix: `--force` flag required; warn user about uncommitted changes before forcing
- Symlinks work: relative symlinks (../../agent-core/...) resolve correctly per-worktree after submodule init
## Recipe failure → retry recipe
- Anti-pattern: Recipe fails partway, agent manually completes remaining steps with ad-hoc commands
- Correct pattern: Fix obstruction (e.g., remove stale lock), retry the recipe from scratch
- Rationale: Recipes are atomic units — manually finishing bypasses error handling, ordering, side effects
- Fix: Added "Partial failure recovery" rule to project-tooling.md
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
## Rephrase feedback before applying
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
