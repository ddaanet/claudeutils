# Operational Practices

Agent reliability patterns, artifact management, implementation practices, and known issues.

## .Artifact and Review Patterns

### When Placing Deliverable Artifacts

**Decision Date:** 2026-02-12

**Decision:** If artifact will be referenced in a followup session → `plans/reports/`. If not → `tmp/`.

**Decision principle:** "Will this be referenced later?" — not "Is this type in a known list?"

**Specific rule:** Research synthesis documents that inform future work (prioritization, skill design, grounding reports) → `plans/reports/` (persistent, tracked, survives sessions). Only scratch computation and intermediate files → `tmp/` (gitignored).

**Anti-pattern:** Writing research synthesis to `tmp/` — it won't survive across sessions and can't be referenced in future planning.

### When Requiring Per-Artifact Vet Coverage

**Decision Date:** 2026-02-12

**Decision:** Each production artifact requires vet-fix-agent review before proceeding.

**Root cause:** Batch momentum — once first artifact skips review, switching cost increases for each subsequent one.

### When Launching Task Agents In Parallel

**Decision Date:** 2026-02-12

**Decision:** Batch all independent Task calls in single message.

**Wall-clock impact:** Sequential = sum(task_times), parallel = max(task_times).

### When Background Agents Crash

**Decision Date:** 2026-02-12

**Correct pattern:** Check output files and git diff — agents complete work before classifyHandoffIfNeeded error fires.

**Recovery:** Use `run_in_background=true` to avoid the error entirely.

### When Refactoring Agents Need Quality Directives

**Decision Date:** 2026-02-12

**Correct pattern:** Include explicit deslop and factorization directives in refactor prompts.

**Rationale:** Refactor agent focuses on warnings (line limits, complexity), doesn't proactively optimize for token efficiency.

## .Agent Reliability Patterns

### When Relaunching Similar Task

**Decision Date:** 2026-02-18

**Anti-pattern:** Launching a fresh agent with the same prompt after a stopped/killed agent, losing prior context.

**Correct pattern:** Use Task tool's `resume` parameter with the prior agent's ID. The agent retains full prior context (files read, reasoning done) and continues from where it stopped.

**Threshold for fresh launch:** If prior agent exchanged >15 messages (context likely near-full — 200K limit approaches), fresh launch is correct. Otherwise resume.

**Rationale:** Stopped agents may have completed expensive operations (file reads, web searches). Resuming preserves that work; relaunching repeats it.

### When Exploration Agents Report False Findings

**Decision Date:** 2026-02-12

**Correct pattern:** Verify file existence claims from quiet-explore agents (ls, git ls-tree).

### When Scrubbing Learnings Before Design Input

**Decision Date:** 2026-02-12

**Decision:** Validate learnings against current evidence before using as design constraints.

**Rationale:** Learnings are session-scoped observations, not verified invariants — can be stale or wrong.

### When Diagnosing Review Agent Quality Gaps

**Decision Date:** 2026-02-16

**Problem:** Review agent produces defective fixes. Need to isolate whether the cause is model tier, input content, delegation prompt, or agent instructions.

**Diagnostic procedure (2×2 controlled experiment):**

1. **Identify the defect** in the review agent's output. Note the specific confabulation or error.

2. **Recover the pre-review artifact** from git history (`git show <commit>:<path>`). This is the input the review agent received.

3. **Create test worktrees** at the pre-review commit (`just wt-new <name> <commit>`). One per experimental condition.

4. **Run the review at the alternate model tier** (e.g., opus if original was sonnet). Use the same agent type. Compare: does the alternate model avoid the defect?

5. **Run the original model on the alternate artifact** (cross condition). If the original outline was sonnet-generated, run sonnet review on opus-generated outline. Isolates input content as a variable.

6. **Extract delegation prompts** from session transcripts to control for prompt quality:
   ```python
   # Parse .jsonl session file for Task tool calls
   for msg in session:
       for block in msg.content:
           if block.type == 'tool_use' and block.name == 'Task':
               print(block.input.prompt)
   ```
   Session files at `~/.claude/projects/<project-path>/<session-id>.jsonl`.

7. **Analyze the 2×2 matrix:**

   | | Model A review | Model B review |
   |---|---|---|
   | **Model A input** | original | controlled |
   | **Model B input** | controlled | controlled |

   - Column difference = model tier effect
   - Row difference = input content effect
   - Prompt comparison = delegation quality effect (eliminated if equivalent)

**Artifacts to preserve:** Commit test worktree results before cleanup. Merge test branches with `--no-ff` then revert changes to preserve commit history without polluting the working tree.

**When to apply:** After interactive review catches defects that automated review missed. The diagnostic determines whether to change model tier, agent instructions, or both.

### When Running Multi-Reviewer Diagnostics

**Decision Date:** 2026-02-18

**Anti-pattern:** Running a single reviewer and trusting all findings. Exploration agents produce false positives from over-reading; opus reviewers miss implementation-level issues detectable only by reading source code.

**Correct pattern:** Run 3+ independent reviewers in parallel (opus review, exploration, inline RCA against source code). Cross-reference findings — real issues appear in multiple reviewers or survive verification against source. False positives get filtered by disagreement.

**Evidence:** 3-way review of runbook-phase-1.md found 8 real issues (each reviewer found unique ones) and filtered 2 false positives. Exploration flagged "critical" line number issue that was correct; opus missed `_git()` return value issue only caught by reading source code directly.

### When Performing Root Cause Analysis

**Decision Date:** 2026-02-18

**Anti-pattern:** Finding first cause and jumping to solution (e.g., "expansion has defects → add more review rounds").

**Correct pattern:** Multi-layer RCA with explicit stops between layers.
- L1: What are the symptoms? STOP.
- L2: What caused them? STOP.
- L3: Why was that cause allowed? STOP.
Only then does the fix address the cause, not the symptoms.

**Evidence:** Merge data loss RCA — L1: bugs in code. L2: haiku generated safety-critical code. L3: delegation model assigns by type not risk + no review gate covers behavioral safety. Fix: model floor for Tier 1 steps AND safety criteria in vet.

### When Searching Adjacent Domains

**Decision Date:** 2026-02-18

**Anti-pattern:** Narrowing search to one domain after user feedback (e.g., "not security?" → drop all security searches). Interpreting a correction as exclusion rather than asking for clarification.

**Correct pattern:** When user questions missing coverage ("not X?"), they may mean "why no X?" not "exclude X." Safety and security are adjacent — both warrant research even when the triggering incident is one or the other.

**Evidence:** User said "not security?" meaning "why aren't you searching for security too?" — interpreted as "this isn't about security" and dropped security entirely.

## .Architectural Principles

### When Temporal Validation Required For Analysis

**Decision Date:** 2026-02-12

**Decision:** Correlate session timestamps with git history to validate feature availability before analysis.

**Git commands:** `git log --format="%ai" --follow <file>` for creation date, session mtime for analysis window.

### .When Behavioral Triggers Beat Passive Knowledge

**Decision Date:** 2026-02-12

**Decision:** `/when` (behavioral) and `/how` (procedural) only — these prescribe action, creating retrieval intention.

**Consequence:** If a learning can't be phrased as `/when` or `/how`, it's either a fragment (ambient) or lacks actionable content.

### .When Enforcement Cannot Fix Judgment

**Decision Date:** 2026-02-12

**Decision:** Enforcement works for structural/mechanical checks; judgment requires conversation-level intervention.

**Rationale:** Writing agent can satisfy any structural check with wrong content.

## .Git Workflow Patterns

### When Git Operation Fails

**Decision Date:** 2026-02-18

**Anti-pattern:** Attributing git failure to a plausible-sounding restriction without reading the error message. Confabulating explanations ("git refuses to merge with active worktree" — false) creates false premises for subsequent decisions, deletes test coverage to work around non-existent limitations.

**Correct pattern:** Read actual error output. Reproduce with a minimal case before restructuring. Test failures that seem like infrastructure problems may reveal real production bugs.

**Deeper pattern:** Confabulation serves as license to stop investigating. A "can't be fixed" explanation converts a solvable problem into an unsolvable one, justifying coverage-reducing workarounds.

### When No-Op Merge Orphans Branch

**Decision Date:** 2026-02-12

**Decision:** Always create merge commit when `git merge --no-commit` was initiated.

**Rationale:** Without merge commit, branch is unreachable from HEAD → `git branch -d` rejects.

### When Naming Tasks For Worktrees

**Decision Date:** 2026-02-12

**Decision:** Constrain task names to `[a-zA-Z0-9 ]` — slug derivation is near-identity.

### When Requiring Clean Git Tree

**Decision Date:** 2026-02-12

**Decision:** Require clean tree before merge/rebase operations. No `git stash` workarounds.

**Exception:** Session context files (session.md, learnings.md) auto-committed as pre-step.

**Rationale:** Stash is fragile (conflicts on pop, lost stashes). Clean tree forces explicit state management.

### When Failed Merge Leaves Debris

**Decision Date:** 2026-02-12

**Decision:** After merge abort, check for untracked files materialized during the attempt.

**Anti-pattern:** Assume aborted merge is clean — retry fails with "untracked files would be overwritten."

**Fix:** `git clean -fd -- <affected-dirs>` to remove debris, then retry.

### When Git Lock Error Occurs

**Decision Date:** 2026-02-12

**Decision:** Stop on unexpected git lock error, report to user, wait for guidance. Never delete lock files.

**Anti-pattern:** Agent removes `.git/index.lock` after git error suggests manual removal.

**Rationale:** Lock may indicate active process; removal bypasses "stop on unexpected results" rule.

## .Known Issues

### When ClassifyHandoffIfNeeded Bug Occurs

**Bug:** `ReferenceError: classifyHandoffIfNeeded is not defined` in Claude Code's SubagentStop processing.

**Affected:** v2.1.27+. NOT fixed.

**Scope:** Only `run_in_background=false` Task calls fail. `run_in_background=true` works.

**Workaround:** Use `run_in_background=true` for Task calls.

**GitHub issues:** #22087, #22544.

## .Sub-agent Limitations

### When Sub-Agents Cannot Spawn Sub-Agents

**Limitation:** Task tool is unavailable in sub-agents. All delegation must originate from main session.

**Also unavailable:** MCP tools (Context7), hooks.

**Available:** Read, Grep, Glob, Bash, Write, Edit (direct tool use only).

### When Resolving Session.md Conflicts During Merge

**Decision Date:** 2026-02-18

**Anti-pattern:** Using `git checkout main -- agents/session.md` to resolve conflicts — discards all branch-side session data (new tasks, metadata) without verification.

**Correct pattern:** After any session.md conflict resolution, read the full file and compare against the known task list. Verify no tasks were dropped. Branch session.md may contain tasks added during worktree work that don't exist on main.

**Evidence:** "Simplify when-resolve CLI" task existed only in worktree-merge-errors branch session.md. `checkout main --` silently dropped it. Caught only because user requested explicit content verification.

### When Removing Worktrees With Submodules

**Decision Date:** 2026-02-18

**Anti-pattern:** `wt rm` removes worktree directory but leaves `.git/modules/agent-core/config` `core.worktree` pointing to the deleted directory. Also doesn't check if submodule branch has unmerged commits (parent repo branch merged but submodule branch diverged).

**Correct pattern:** `wt rm` must (1) restore submodule's `core.worktree` to main checkout path, (2) check submodule branch merge status before deletion. Both are data-loss vectors — stale config breaks all submodule operations, unmerged submodule branch loses commits.

**Evidence:** `git -C agent-core` failed with "cannot chdir to removed directory" after `wt rm runbook-skill-fixes`. Agent-core branch had 3 files of real diffs silently orphaned.

### When Importing Artifacts From Worktrees

**Decision Date:** 2026-02-18

**Transport:** `git show <branch>:<path>` from main — no cross-tree sandbox access needed. All worktrees share the git object store.

**Scope:** Only design.md and requirements.md are import candidates (small, authored). Runbooks (phase files, steps, orchestrator plans) are bulky, generated, implementation-oriented — require explicit intent, not casual import.

**Ownership check:** Before importing, verify no active worktree owns the target plan directory (`git worktree list` + check branch names). Importing into a worktree-owned plan creates merge conflicts when that worktree merges back.

**Supersedes:** "When worktree agents need cross-tree access" (additionalDirectories unnecessary for transport).

### When Workaround Requires Creating Dependencies

**Decision Date:** 2026-02-18

**Anti-pattern:** Escalating workarounds for a tool limitation — each fix creates a new problem requiring another fix. Each step locally rational, trajectory absurd.

**Stop condition:** If a workaround requires more than 2 steps or introduces new dependencies, stop and report the tool limitation. "Pre-resolve conflict" is bounded: edit conflicting regions of files that ALREADY EXIST on both sides. Creating new files, new modules, or new dependency chains means you've left "pre-resolution" and entered "manual reimplementation."

**Deeper pattern:** Sunk cost momentum — each workaround invests more context, making "just one more fix" feel cheaper than stopping. The "stop on unexpected results" rule doesn't fire because each step is rationalized as part of the documented workaround path.

**Evidence:** 6-step escalation chain during design-workwoods merge. Two commits on main, partially-created planstate module, still not merged.

### When Recovering Agent Outputs

**Decision Date:** 2026-02-18

**Anti-pattern:** Manually reading agent session log and retyping content.

**Correct pattern:** Script extraction from task output files. Agent Write calls are JSON-structured in `tmp/claude/.../tasks/<agent-id>.output`. Parse with jq or Python, recover deterministically.

**Prototype:** `plans/prototypes/recover-agent-writes.py`

## .Python Patterns

### When Extracting Git Helper Functions

**Pattern:** Private `_git(*args, check=True, **kwargs) -> str` helper — 1 line per call, fits 88-char limit.

**Evidence:** 24 calls replaced, 477→336 lines (30% reduction) in worktree cli.py.

### When Fixture Shadowing Creates Dead Code

**Anti-pattern:** Defining local function with same name as pytest fixture — function is unreachable dead code.

**Detection:** Grep for function definitions that duplicate fixture names, check if test functions use fixture injection.

### When Test Corpus Defines Correct Behavior

**Anti-pattern:** Rewriting fixtures to avoid triggering known bugs.

**Correct pattern:** Fixtures define correct behavior — failing tests are the signal that code needs fixing.

## .Memory Index Patterns

### .When Index Keys Must Be Exact

**Decision:** Index entry key must exactly match heading key — fuzzy matching is only for resolver runtime recovery.

**Rationale:** Exact keys are deterministic and debuggable.

### When DP Matrix Has Zero-Ambiguity

**Decision:** Initialize DP matrix with -inf for impossible states, 0.0 only for base case.

**Evidence:** "when mock tests" scored 128.0 against candidate with no matching chars — positive score from nothing.

## .Runbook Validation Patterns

### When Phase Numbering Is Flexible

**Decision:** Detect starting phase number from first file, validate sequential from that base.

**Rationale:** Design decisions may use 0-based or 1-based numbering.

### When Checking Self-Referential Modification

**Anti-pattern:** Runbook step uses `find plans/` — includes the executing plan's own directory.

**Correct pattern:** Exclude plan's own directory or enumerate specific targets.

## .Naming Patterns

### When Avoiding CLI Skill Name Collision

**Decision:** Check CLI built-ins before naming skills.

**Scope:** /help, /plan, /review, /model, /clear, /compact, and other built-in commands.

### When Choosing Name

**Decision:** Prioritize human discovery and recall over thematic alignment or cleverness.

**Applies to:** Skill names (slash commands), agent names, command names — any user-facing identifier the human must remember or search for.

**Priority order:**
1. **Discoverability** — The word the user thinks of when they need the capability should match the handle. "I need to ground this" → `/ground`, not `/found`.
2. **Recall** — Short, common words beat etymologically precise ones. If a user can't remember the name after one use, it's wrong.
3. **Thematic alignment** — Nice to have (e.g., construction metaphors pairing with a plugin named "edify"), but never at the cost of discoverability.

**Anti-pattern:** Choosing `/found` (Latin *fundare*, pairs with "edify") over `/ground` (the word people actually use when describing the need).

**Test:** "What word would someone type if they needed this capability and didn't know the command existed?" That word is the name.
