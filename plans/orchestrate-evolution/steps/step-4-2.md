# Step 4.2

**Plan**: `plans/orchestrate-evolution/runbook.md`
**Execution Model**: opus
**Phase**: 4

---

## Phase Context

**Scope:** Rewrite orchestrate SKILL.md, update refactor agent and delegation fragment. Final phase — all code/infrastructure from Phases 1-3 exists; opus writes about implemented artifacts, not forward references.

**Files:** `agent-core/skills/orchestrate/SKILL.md` (rewrite), `agent-core/agents/refactor.md` (modify), `agent-core/fragments/delegation.md` (modify)

**Depends on:** Phase 1 (agent caching model — `{name}-task` naming, Plan Context embedding), Phase 2 (verify-step.sh, structured orchestrator plan format with pipe-delimited steps), Phase 3 (TDD agents: tester/implementer/test-corrector/impl-corrector, step file splitting, verify-red.sh, TDD role markers)

**Key constraints:**
- All files are architectural artifacts → opus mandatory (per recall: "When Selecting Model For Prose Artifact Edits")
- SKILL.md every section must open with a tool call (per recall: "How to Prevent Skill Steps From Being Skipped" — D+B hybrid pattern)
- Positional authority in agent definitions: constraints in primacy, plan context middle, scope enforcement recency (per recall artifact)
- Design section references: D-1 through D-6 must all be addressed in SKILL.md rewrite
- Prose atomicity: all SKILL.md edits in a single step (one opus pass writes complete skill)
- Sonnet default (D-1): remove haiku orchestrator assumption throughout
- delegation.md is a CLAUDE.md fragment loaded via @-reference — changes affect all sessions

---

---

## Step 4.2: Refactor agent and delegation fragment updates

**Objective:** Update refactor.md and delegation.md to align with new orchestration model.

**Execution Model:** Opus

**Implementation:**

**refactor.md (243 lines → ~273 lines):**

Three targeted additions to existing agent definition:

1. **Deslop directives** — Insert before Step 3 (Refactoring Protocol, line 99):
   - "Prefer factorization over splitting: extract shared logic into helpers before considering module splits"
   - "Remove dead code during refactoring — don't preserve unused imports, functions, or variables"
   - "Token economy: reference file paths, don't repeat file contents in reports"
   - Per recall: "When Refactoring Agents Need Quality Directives"

2. **Factorization-before-splitting rule** — Add to Refactoring Evaluation section (after line 42):
   - "Before splitting a module: check for duplicate code, unused helpers, repeated kwargs patterns. Extract shared logic first — the module may shrink below threshold without splitting."
   - Per recall artifact: "When Hitting File Line Limits"

3. **Resume pattern** — Add to Return Protocol section (after line 183):
   - "If interrupted mid-refactoring: orchestrator should resume this agent (save agent ID). Fresh launch only if >15 messages exchanged."
   - Per delegation.md Delegate Resume pattern

**delegation.md (55 lines → ~55 lines, net zero change):**

Four modifications to existing fragment:

1. **Sonnet default** — Replace Model Selection list (lines 9-17):
   - Remove "Haiku: Execution, implementation, simple edits, file operations"
   - Change "Sonnet: Default for most work, balanced capability" to "Sonnet: Default for all execution tasks"
   - Keep "Opus: Architecture, complex design decisions only"
   - Remove "Never use opus for straightforward execution tasks." (covered by orchestrate skill)

2. **File reference pattern** — Add after Pre-Delegation Checkpoint (after line 23):
   - "Dispatch with file reference: `Execute step from: plans/<name>/steps/step-N.md` — agent reads step file for full context. Do not inline step content in prompt."

3. **Agent caching note** — Add after file reference pattern:
   - "Plan-specific agents (`{name}-task`, `{name}-corrector`) embed design and outline context. Prompt needs only the step file reference — Plan Context is baked into the agent definition."

**Expected Outcome:** refactor.md gains ~30 lines of quality directives and resume pattern. delegation.md updated to reflect sonnet-default model with file reference dispatch.

**Error Conditions:**
- Insertion at wrong location disrupts agent flow → verify surrounding context before inserting
- delegation.md changes conflict with CLAUDE.md @-reference loading → validate fragment still parseable

**Validation:**
- `just precommit` passes (lint, format)
- refactor.md: search for "factorization" — present in Evaluation section
- refactor.md: search for "deslop" or "dead code" — present before Step 3
- refactor.md: search for "resume" — present in Return Protocol section
- delegation.md: no "Haiku" in Model Selection list
- delegation.md: contains "file reference" pattern
- delegation.md: contains "agent caching" or "Plan Context" note
