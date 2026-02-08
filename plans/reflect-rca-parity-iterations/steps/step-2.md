# Step 2

**Plan**: `plans/reflect-rca-parity-iterations/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 2: D+B Validation via Step 1 Commit

**Objective:** Execute `/commit` skill using Step 1 changes as the commit vehicle, and document evidence that Gate A (Read session.md), Gate B (git diff), and validation (just precommit) all execute correctly per D+B hybrid fix.

**Design Reference:** DD-8 (design lines 160-172) — "Execute `/commit` on a trivial change" → Step 1 changes ARE the trivial change

**Context:**
- The prose gate D+B hybrid fix (plans/reflect-rca-prose-gates/) merged gates into action steps with tool call anchors
- The fix was validated theoretically (design review) but not empirically (actual execution)
- This step closes the empirical validation gap by using Step 1 changes as the commit vehicle

**Prerequisites:**
- Step 1 complete — Step 1 changes (commit skill WIP-only restriction) provide the trivial change needed for D+B validation
- Working directory clean except for Step 1 changes

**Implementation:**

1. **Verify Step 1 changes are staged:**
   ```bash
   git status
   git add agent-core/skills/commit/SKILL.md
   ```

2. **Invoke `/commit` skill:**
   - Use: `/commit --context` (skip discovery since we know what changed)
   - Expected: Skill executes Step 1 sequence (Gate A: Read session.md, Gate B: git diff, validation: just precommit)
   - Observe: All three gates execute in the correct order

3. **Capture evidence:**
   - Gate A evidence: Read tool call with session.md path visible in transcript OR session.md content snippet in context (search for "Pending Tasks" heading or similar)
   - Gate B evidence: git diff output visible showing Step 1 changes to agent-core/skills/commit/SKILL.md
   - Validation evidence: `just precommit` command visible in execution with test count, lint result, line limit check output

4. **Document findings:**
   Write to `plans/reflect-rca-parity-iterations/reports/d-b-validation.md`:
   - Execution timestamp
   - Command invoked: `/commit --context`
   - Gate A: Did Read session.md execute? (yes/no, evidence snippet)
   - Gate B: Did git diff execute? (yes/no, evidence snippet showing Step 1 changes)
   - Validation: Did just precommit execute? (yes/no, evidence showing test count, lint result)
   - Overall: D+B hybrid fix confirmed (yes/no)
   - Commit hash of Step 1 changes

**Expected Outcome:**
- All three gates execute in sequence
- Commit succeeds with Step 1 changes
- Evidence documented in report file

**Unexpected Result Handling:**
- If any gate does NOT execute: Mark gate as FAILED in report with reason (e.g., "Gate A: FAILED — session.md not found, Read tool did not execute"), continue validation of remaining gates, escalate to sonnet after all gates checked
- If `just precommit` fails: Document precommit error, check if Step 1 changes introduced lint error (unlikely, but verify), escalate to sonnet
- If session.md not found: Mark Gate A as "FAILED — File not found, gate did not execute" in report, continue with Gate B and validation
- If commit fails for any other reason (network error, disk full, permission denied): Document error message, STOP, escalate to sonnet

**Validation:**
- Report file exists at specified path
- Report documents all three gates with evidence
- Commit hash recorded in report matches git log

**Success Criteria:**
- Report confirms all three gates executed
- Commit created with Step 1 changes
- Evidence snippets present (session.md snippet, git diff snippet, precommit output snippet)

**Report Path:** `plans/reflect-rca-parity-iterations/reports/d-b-validation.md`

**Note:** This step consumes the Step 1 changes by committing them. After this step, Step 1 and Step 2 are both complete and committed together as Phase 1.

---


**Completion Criteria:**
- Step 1: Commit skill updated with WIP-only restriction (verify file edits applied)
- Step 2: D+B validation report exists at `plans/reflect-rca-parity-iterations/reports/d-b-validation.md` with all three gate results (Gate A, Gate B, validation)
- Both changes committed via `/commit` executed in Step 2 (Step 1 changes + validation report committed together)

**Next Phase:** Phase 2 (Tier 2 fixes — low complexity, parallelizable)
# Phase 2: Tier 2 Fixes (Low Complexity, Parallelizable)

**Scope:** 6 steps, ~200 lines total (4 edits + 2 new files), single session
**Model:** Haiku execution (steps 3-7), Sonnet for N1 audit (step 8)
**Complexity:** Low-moderate (multi-file edits, clear scope, internal sequencing for Gap 4 → Gap 1)

**Parallelization:**
- Steps 3, 6, 7, 8 are fully independent and can run in parallel
- Steps 4-5 (Gap 4) are prerequisites for Phase 3 Step 9 (Gap 1)
- All Phase 2 steps must complete before Phase 3 starts

**Conditional output:**
- Step 8 produces either: (a) audit report + `scripts/check_skill_steps.py` + justfile entry, OR (b) audit report documenting decision not to ship lint

---
