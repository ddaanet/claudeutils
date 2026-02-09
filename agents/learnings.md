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
## Temporal validation for empirical analysis
- Anti-pattern: Running analysis on session history without checking if feature existed during those sessions
- Correct pattern: Correlate session timestamps with git history to validate feature availability
- Rationale: Sessions before feature creation yield expected-zero results, invalidating analysis
- Example: Memory index created Feb 1, sessions analyzed Feb 5-8 → valid (all had access)
- Git commands: `git log --format="%ai" --follow <file>` for creation date, session mtime for analysis window
- Strengthens findings: 0% recall validated across 200 sessions, all post-creation and post-stability
## Namespace collision in prefix design
- Anti-pattern: Proposing `.` prefix for new navigation syntax when `.` already means "structural section" in decision files
- Correct pattern: Check existing notation conventions before introducing new prefix semantics
- Rationale: `.` prefix on headers is validated by precommit (validate-decision-files.py) — reusing it for navigation creates ambiguity
- Fix: `§` operator reuses existing unique identifiers (header titles, filenames) instead of inventing new prefix
## Memory-as-file enables Read caching
- Anti-pattern: Script extracts section content from multi-section files, outputs as text (no caching)
- Correct pattern: Each memory = individual file, `/when` outputs `@file` reference, agent Reads (prefix-cached by Claude Code)
- Rationale: Claude Code uses prompt prefix caching — Read results stay in conversation, subsequent API turns get 90% cheaper cache hits on the stable prefix
- Correction: "Subsequent reads free" is wrong — re-reading same file adds duplicate copy to context window. Benefit is cheap subsequent turns, not free re-reads
- Consequence: Script becomes resolver (trigger → filepath), not extractor (trigger → content). Read once per session, not repeatedly
- Trade-off: ~169 individual files vs 10 multi-section files — directory structure mirrors current sections
## Prompt caching not file caching
- Anti-pattern: Assuming Claude Code deduplicates file reads or maintains a file cache (re-reading = free)
- Correct pattern: Each Read appends a new content block to conversation; "caching" = prompt prefix matching at API level (92% reuse, 10% cost)
- Rationale: No application-level dedup. 20-block lookback window limits cache hits when many tool calls intervene
- @-references (system prompt) are more cache-efficient than Read (messages) for always-needed content
- Design implication: For `/when`, emit `@file` references for agent to Read once; don't encourage repeated reads of same file
