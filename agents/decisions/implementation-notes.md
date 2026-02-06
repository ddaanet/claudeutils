# Implementation Notes

Detailed implementation decisions for claudeutils codebase. Consult this document when implementing similar features or patterns.

## @ references limitation

**Context:** CLAUDE.md supports `@file.md` references for progressive disclosure.

**Limitation:** @ references only work in `CLAUDE.md`. Not supported in:
- Skill `SKILL.md` files
- Agent `.md` system prompts
- Task tool prompts

**Workaround:** Place supporting files in skill directory and reference with relative path.

**Example:** `skills/gitmoji/gitmoji-table.md` referenced from SKILL.md using relative path.

**Impact:** Skill documentation must use inline content or relative paths for supporting files.

## Skill Rules Placement: Point of Violation

**Context:** Multi-phase skill procedures with content generation and cleanup.

**Anti-pattern:** Placing "don't write X" rules in cleanup/trim phases instead of writing phases.

**Problem:** Agent follows phases sequentially; by the time it reaches cleanup, the violation is already written.

**Correct pattern:** Place negative constraints alongside positive content guidance, where decisions are made.

**Example:** "No commit tasks" rule moved from Phase 6 (Trim) to Phase 3 (Context Preservation).

**Generalization:** Any rule about what NOT to produce should be co-located with instructions for WHAT to produce.

**Impact:** Prevents violations rather than detecting them after the fact.

## .Claude Code Hooks and Sessions

### SessionStart Hook Limitation

**Context:** SessionStart hook output is discarded for new interactive sessions.

**Issue:** [#10373](https://github.com/anthropics/claude-code/issues/10373) — `qz("startup")` never called for new interactive sessions.

**Works:** After `/clear`, `/compact`, or `--resume`.

**Workaround:** Use `@agents/session.md` in CLAUDE.md for task context (already loaded).

**Impact:** Don't build features depending on SessionStart until fixed upstream.

### UserPromptSubmit Hook Filtering

**Decision:** UserPromptSubmit hooks fire on every prompt; no `matcher` field support.

**Pattern:** All filtering logic must be script-internal, not in settings.json configuration.

**Rationale:** Different hook events have different API capabilities; script-level filtering is more flexible.

**Example:** PreToolUse/PostToolUse support `matcher`, UserPromptSubmit does not.

### Hook Capture Impractical for Subagents

**Anti-pattern:** Using PostToolUse hooks to capture Explore/claude-code-guide results.

**Problem:** Hooks don't fire in sub-agents spawned via Task tool. Task matcher fires on ALL Tasks (noisy).

**Correct pattern:** Session-log based capture (future work) or quiet agents that write their own reports.

**Impact:** Sub-agents can have tools (Bash, Write) but hook interceptors won't execute.

### MCP Tools Unavailable in Subagents

**Anti-pattern:** Assuming quiet-task or other sub-agents can call MCP tools (Context7, etc.).

**Correct pattern:** MCP tools only available in main session. Call directly from designer/planner, write results to report file for reuse.

**Confirmed:** Empirical test — quiet-task haiku has no access to `mcp__plugin_context7_context7__*` tools.

**Impact:** Context7 queries cost opus tokens when designer calls them, but results persist for planner reuse.

### Loaded Skill Overrides Fresh-Session Framing

**Anti-pattern:** After `/clear`, treating loaded skill content as informational rather than actionable.

**Correct pattern:** If skill content is present in context (via command injection), execute it immediately.

**Rationale:** `/clear` resets conversation history but skill invocation injects actionable instructions. The skill IS the task — "fresh session" is not a reason to pause.

## .Version Control Patterns

### Commits Are Sync Points

**Principle:** Every version control commit synchronizes files, submodules, and context (session.md).

**Trigger:** When adding new kind of state to versioned content, design extension point in /commit skill to check for that state.

**Current sync checks:**
- Submodule commits (step 1b)
- Session.md freshness (step 0)

**Future examples:** Large file tracking, external dependency manifests, generated artifacts.

**Impact:** Commit skill serves as synchronization checkpoint for all versioned state.

### Never Auto-Commit in Interactive Sessions

**Anti-pattern:** Committing after completing work because it "feels like a natural breakpoint".

**Anti-pattern:** Running raw `git commit` to bypass skill protocol (no STATUS display, no clipboard).

**Correct pattern:** Only commit when user explicitly requests (`/commit`, `ci`, `xc`, `hc`).

**Correct pattern:** ALL commits follow commit skill protocol — STATUS display is mandatory, not optional.

**Rationale:** With `xc` (execute+commit) shortcuts, auto-commit provides no value — user controls commit timing explicitly.

**Reinforcement:** "Fix X and do Y" means fix X, do Y, then STOP. Commit is never implicit in task completion.

## .Tokenization and Formatting

### Title-Words Beat Kebab-Case

**Decision:** Use title-words (e.g., `Tool batching unsolved`) instead of kebab-case identifiers (e.g., `tool-batching-unsolved`).

**Measured:** Kebab-case +31% drift penalty vs title-words +17% when agents get verbose.

**Rationale:** Hyphens often tokenize as separate tokens; spaces between words don't add overhead.

**Impact:** More efficient token usage for identifiers and headers.

### Bare Lines Beat List Markers

**Decision:** Use bare lines without markers for flat keyword lists.

**Anti-pattern:** Using `- ` list markers for keyword index entries.

**Measured:** 49 tokens (bare) vs 57 tokens (list markers) = 14% savings.

**Rationale:** List markers add no semantic value for flat keyword lists.

**Impact:** 14% token reduction for index structures.

### Default Semantic, Mark Structural

**Decision:** Default semantic, `.` prefix marks structural (`## .Title`).

**Syntax:** Dot is part of the title text, after the markdown header marker.
- ✅ Correct: `## .Title` (dot after `## `)
- ❌ Wrong: `.## Title` (dot before `##`)

**Anti-pattern:** Mark semantic headers with special syntax, leave structural unmarked.

**Rationale:** Failure mode — orphan semantic header → ERROR (caught) vs silent loss (dangerous).

**Cost:** +1 token per structural header (minority case).

**Impact:** Safe by default with minimal overhead.

## .Design and Requirements

### Design Tables Are Binding Constraints

**Decision:** Read design classification tables LITERALLY. Apply judgment only where design says "use judgment".

**Anti-pattern:** Inventing classification heuristics when design provides explicit rules (e.g., "subsections = structural" when design table shows all ##+ as semantic).

**Rationale:** Design decisions are intentional. Overriding them based on assumptions contradicts designer's intent.

**Process fix:** Skill fixes outlined for `/design` and `/plan-adhoc`.

**Impact:** Implementation matches design intent without interpretation drift.

### Header Titles Not Index Entries

**Anti-pattern:** Adding header titles to memory-index.md and claiming "entries exist".

**Correct pattern:** Index entries are `Title — keyword description` where description captures semantic content for discovery.

**Rationale:** Validation checks structural requirements (entry exists); design defines content requirements (entry is keyword-rich). Both must be met.

**Impact:** Don't dismiss critical vet feedback by reframing it as a less-severe related finding.

### Phase-Grouped Runbook Header Format

**Decision Date:** 2026-02-05

**Decision:** Use `### Phase N` (H3) for visual grouping and `## Step N.M:` (H2) for steps.

**Anti-pattern:** Using `## Phase N` (H2) and `### Step N.M:` (H3) — prepare-runbook.py can't find steps.

**Rationale:** prepare-runbook.py regex matches `^## Step` — steps must be H2 for extraction.

**Implementation:** assemble-runbook.py outputs correct format; manual runbooks need header level awareness.

**Impact:** Runbook processing tools work correctly with phase-grouped structure.

## Prose Gate D+B Hybrid Fix

**Decision Date:** 2026-02-06

**Problem:** Skill steps with only prose judgment (no tool call) get skipped during execution. Manifested in 3 cases: commit skill session freshness (Step 0), commit skill vet checkpoint (Step 0b), orchestrate skill phase boundary (3.4).

**Root cause:** Execution-mode cognition optimizes for "next tool call." Steps without tool calls register as contextual commentary, not actionable work.

**Fix (D+B Hybrid):** Combines Option D (Read/Bash anchor) with Option B (restructure into adjacent step):
1. Eliminate standalone prose gates — merge each gate into its adjacent action step
2. Anchor with tool call — each gate's first instruction is a Read or Bash call providing data for evaluation
3. Explicit control flow — gate evaluation uses if/then with explicit branch targets

**Convention:** Every skill step must open with a concrete tool call (Read/Bash/Glob). Prose-only judgment steps are a structural anti-pattern.

**Design:** `plans/reflect-rca-prose-gates/outline.md`

**Impact:** Prevents prose gates from being skipped; establishes convention for future skill design.
