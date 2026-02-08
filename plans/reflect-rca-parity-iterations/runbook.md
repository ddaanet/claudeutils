# Runbook: Parity Test Quality Gap Fixes

**Context:** Close remaining parity test quality gaps through guidance updates, convention changes, and optional tooling. Addresses 5 root causes from statusline-parity RCA plus 3 Opus-identified concerns.

**Source:** `design.md` (8 design decisions, 3-tier sequencing), `rca.md`, `rca-review-critique.md`
**Design:** `plans/reflect-rca-parity-iterations/design.md`

**Status:** Ready for execution
**Created:** 2026-02-08
**Reviewed:** 2026-02-08 (runbook-outline-review-agent, phase vet reviews)

---

## Weak Orchestrator Metadata

**Total Steps**: 11

**Execution Model**:
- Steps 1-7, 9-11: Haiku (simple edits, file creation, scripted tasks)
- Step 8: Sonnet (semantic audit requiring categorization judgment)

**Step Dependencies**:
- Phase 1 (Steps 1-2): Sequential (Step 2 uses Step 1 changes as commit vehicle)
- Phase 2 (Steps 3-8): Partially parallel
  - Steps 3, 6, 7, 8: Fully independent, can run in parallel
  - Steps 4-5: Sequential pair, prerequisite for Phase 3 Step 9
- Phase 3 (Steps 9-10): Sequential, depends on Phase 2 complete (Gap 4 prerequisite)
- Phase 4 (Step 11): Sequential, depends on all prior phases complete

**Error Escalation**:
- Haiku → Sonnet: Step encounters design ambiguity, file path mismatch, or unexpected validation failure
- Sonnet → User: Audit decision thresholds unclear (Step 8), design decisions conflict, or critical structural issues

**Report Locations**: `plans/reflect-rca-parity-iterations/reports/step-{1..11}-execution.md` or `n1-audit.md` (Step 8)

**Success Criteria**: All 11 steps complete, all 8 design decisions (DD-1 through DD-8) implemented, memory index updated with all changes

**Prerequisites**:
- Design document complete at `plans/reflect-rca-parity-iterations/design.md` (✓ verified)
- RCA document available at `plans/reflect-rca-parity-iterations/rca.md` (✓ verified)
- All target files exist:
  - `agent-core/skills/commit/SKILL.md` (✓ verified)
  - `agents/decisions/testing.md` (✓ verified)
  - `agents/decisions/workflow-advanced.md` (✓ verified)
  - `agent-core/skills/plan-tdd/SKILL.md` (✓ verified)
  - `agent-core/skills/plan-adhoc/SKILL.md` (✓ verified)
  - `agent-core/agents/vet-fix-agent.md` (✓ verified)
  - `agents/memory-index.md` (✓ verified)

---

## Common Context

**Requirements (from design):**
- FR-1: Conformance test cycles mandatory when design has external reference — addressed by Gap 1 fix (Step 9)
- FR-2: Test descriptions for conformance work include exact expected strings — addressed by Gap 4 fix (Steps 4-5)
- FR-3: `--test`/`--lint` commit modes restricted to WIP commits — addressed by Gap 5 fix (Step 1)
- FR-4: Planning-time file size awareness — addressed by Gap 2 fix (Steps 6-7)
- FR-5: Vet alignment includes conformance checking as standard — addressed by N2 (Step 10)
- FR-6: Defense-in-depth pattern documented — addressed by Q5 (Step 3)
- FR-7: Skill step tool-call-first convention audit — addressed by N1 (Step 8, conditional)
- FR-8: D+B empirical validation — addressed by N3 (Step 2)
- NFR-1: No orchestration pipeline changes — all fixes through existing mechanisms
- NFR-2: Changes apply going forward — no retroactive plan fixes
- NFR-3: Hard limits or no limits — no warning-only modes

**Scope boundaries:**
- In scope: Guidance updates, convention changes, conditional tooling (audit-based)
- Out of scope: Orchestration pipeline changes, persistent test artifacts from references, retroactive fixes, pre-write hooks, D+B implementation changes, concurrent pipeline evolution

**Key Constraints:**
- Phase 2 Steps 4-5 (Gap 4) must be committed BEFORE Phase 3 Step 9 (Gap 1) begins
- Step 8 (N1 audit) has conditional output — lint ships only if ≥80% compliance threshold met
- All changes are guidance documents and agent definitions — no code changes, no automated tests

**Project Paths:**
- Skills: `agent-core/skills/{commit,plan-tdd,plan-adhoc}/SKILL.md`
- Decisions: `agents/decisions/{testing,workflow-advanced,defense-in-depth}.md`
- Agents: `agent-core/agents/vet-fix-agent.md`
- Memory: `agents/memory-index.md`
- Reports: `plans/reflect-rca-parity-iterations/reports/`

**Conventions:**
- All edits preserve existing file structure (headings, sections)
- Report paths follow `step-N-execution.md` pattern (except Step 8: `n1-audit.md`)
- Success criteria include measurable outcomes (file exists, line count, content elements present)
- Validation includes reading updated files to verify changes applied

---

# Phase 1: Tier 1 Fixes (Trivial, Immediate)

**Scope:** 2 steps, ~20 lines of changes, single session
**Model:** Haiku execution
**Complexity:** Low (single-file edits with clear instructions)

---

## Step 1: Add WIP-Only Restriction to Commit Skill Flags

**Objective:** Clarify that `--test` and `--lint` flags in commit skill are exclusively for WIP commits during TDD execution, not for bypassing validation in final commits.

**Design Reference:** DD-3 (design lines 95-106)

**Current State:**
- File: `agent-core/skills/commit/SKILL.md`
- Flags section (around lines 19-40) documents `--test` and `--lint` with usage examples
- No explicit restriction on when these flags can be used
- An agent can legitimately choose `--test` mode for what it judges as test-only work, bypassing line limits

**Changes Required:**

1. **Locate Flags section** (search for "## Flags" or "Validation level" heading):
   - Update `--test` description: Add "(TDD GREEN phase WIP commits only)"
   - Update `--lint` description: Add "(Post-lint WIP commits only)"
   - After flag descriptions: Insert "**Scope:** WIP commits only. All feature/fix commits must use full `just precommit`."

2. **Locate TDD workflow pattern section** (search for "TDD workflow pattern"):
   - Current text: "After GREEN phase: `/commit --test` for WIP commit"
   - Update to: "After GREEN phase: `/commit --test` for WIP commit (bypasses lint/complexity, test-only validation)"
   - Add below: "After REFACTOR complete: `/commit` for final amend (full precommit required, no flags)"

**Expected Outcome:**
- Flags section explicitly states "WIP commits only" scope restriction
- TDD workflow pattern emphasizes final commits require full precommit
- No functional change to flag behavior — only documentation clarity

**Implementation:**
```
Edit agent-core/skills/commit/SKILL.md:
- Locate Flags section, update --test and --lint descriptions with WIP qualifiers
- After flag descriptions: Insert scope restriction line
- Locate TDD workflow pattern section, update with explicit bypass note and final commit requirement
```

**Validation:**
- Read updated file, verify changes match DD-3 intent: "WIP commits only, final commits require full precommit"
- Verify no unintended changes to other sections (commit message style, execution steps)

**Success Criteria:**
- Flags section includes "WIP commits only" restriction
- TDD workflow pattern distinguishes WIP commits (flags OK) from final commits (full precommit required)
- File structure unchanged (headings, examples preserved)

**Error Conditions:**
- If file structure changed unexpectedly → escalate to sonnet for review
- If DD-3 language ambiguous → re-read design lines 95-106 for exact wording

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-1-execution.md`

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

## Phase 1 Checkpoint

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

## Step 3: Create defense-in-depth.md Decision Document

**Objective:** Document the layered mitigation pattern as a reusable principle for future quality gate design, covering the Gap 3 + Gap 5 interaction and general defense-in-depth approach.

**Design Reference:** DD-6 (design lines 137-146)

**File:** `agents/decisions/defense-in-depth.md` (new)

**Content Structure:**

```markdown
## Defense-in-Depth Pattern

**Decision Date:** 2026-02-08

**Decision:** Quality gates should be layered with multiple independent checks to prevent single-point failures. No single gate should be trusted as the sole enforcement mechanism.

**Rationale:** [From DD-6 — multiple quality gates interact to catch different failure modes]

**Pattern layers (from outer to inner):**
1. **Outer defense:** D+B hybrid ensures precommit appears in execution path (gates prose steps from skipping validation)
2. **Middle defense:** Precommit catches line limits, lint, test failures (hard validation at commit time)
3. **Inner defense:** Vet-fix-agent catches quality and alignment issues (semantic review before commit)
4. **Deepest defense:** Conformance tests catch spec-to-implementation drift (executable contracts)

**Gap 3 + Gap 5 interaction:**
- Gap 3 (prose gate skipping): D+B hybrid fix ensures precommit runs (outer defense)
- Gap 5 (WIP-only bypass): `--test`/`--lint` flags provide legitimate within-path bypass of line limits
- Defense-in-depth: D+B (outer) + WIP-only restriction (inner) close this interaction — D+B ensures gates run, WIP-only ensures bypass is scoped to appropriate commits

**Example application:**
[Describe how statusline-parity iterations demonstrate gap in single-layer validation]

**Applicability:**
- This pattern applies beyond parity tests — use for any quality gate design
- When adding new quality mechanisms, consider which layer they belong to
- Multiple layers compensate for individual gate weaknesses (e.g., tests can pass but miss visual conformance)

**Related decisions:**
- DD-3 (WIP-only restriction) — inner defense layer
- DD-5 (Vet alignment) — inner defense layer
- DD-1 (Conformance tests) — deepest defense layer
```

**Implementation:**
Write new file to `agents/decisions/defense-in-depth.md` with the structure above. Expand sections marked with [brackets] using design context from DD-6 and RCA (plans/reflect-rca-parity-iterations/rca.md).

**Expected Outcome:**
- New decision document exists at specified path
- Contains ~60-80 lines documenting layered mitigation pattern
- Includes Gap 3 + Gap 5 interaction analysis
- References related design decisions (DD-3, DD-5, DD-1)

**Validation:**
- Read created file, verify structure matches template
- Verify all four layers documented with clear descriptions
- Verify Gap 3 + Gap 5 interaction explained

**Success Criteria:**
- File exists at `agents/decisions/defense-in-depth.md`
- Contains pattern description, layer enumeration, Gap 3+5 interaction, applicability guidance
- Between 60-80 lines total
- Decision date is 2026-02-08

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-3-execution.md`

---

## Step 4: Expand "Conformance Validation for Migrations" in testing.md

**Objective:** Update the existing conformance validation section to document tests as executable contracts and the conformance exception to prose test descriptions.

**Design Reference:** DD-2 (design lines 79-93), partial fulfillment of Gap 4

**File:** `agents/decisions/testing.md` (existing, edit)

**Current State:**
- Section "Conformance Validation for Migrations" (around line 128)
- Currently ~13 lines, sparse content
- Basic pattern documented but missing precision guidance

**Changes Required:**

Expand section to ~30 lines covering:

1. **Tests as executable contracts (DD-1 principle):**
   - When design includes external reference (shell prototype, API spec, visual mockup), tests bake expected behavior into assertions
   - Reference consumed at authoring time, tests become permanent living documentation
   - Example: statusline-parity tests should assert exact expected strings from shell reference (e.g., `🥈 sonnet \033[35m…`), not just structure ("contains emoji")

2. **Exact expected strings requirement:**
   - For conformance work, test assertions include exact expected output from the reference
   - This eliminates translation loss between spec and implementation
   - Addresses RC5 from RCA: "Visual Parity Validated" false completion claims are detectable when tests include exact strings

3. **Conformance exception to prose descriptions:**
   - Standard TDD: Use prose descriptions, not full test code (per workflow-advanced.md)
   - Conformance exception: Prose descriptions MUST include exact expected strings from reference
   - This is not full test code — it is precise prose

4. **Example contrast table (from DD-2 lines 86-91):**
   ```
   | Standard prose | Conformance prose |
   |----------------|-------------------|
   | "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator" |
   ```

**Implementation:**
Locate "## Conformance Validation for Migrations" section (around line 128). Expand from ~13 lines to ~30-35 lines with the four elements above. Preserve existing content (comparison pattern, benefits, example, impact) and integrate new content.

**Expected Outcome:**
- Section expanded with tests-as-executable-contracts principle
- Exact expected strings requirement documented
- Conformance exception to prose descriptions explained
- Example contrast table included (standard vs conformance prose)

**Validation:**
- Read updated section, verify ~30-35 lines total
- Verify all four elements present (contracts, exact strings, prose exception, example table)
- Verify existing content preserved (decision date, pattern, benefits, impact)

**Success Criteria:**
- Section length ~30-35 lines (was ~13 lines)
- Contains all four elements from design DD-2
- Example contrast table matches design lines 86-91
- Existing "Decision Date: 2026-02-05" and other fields preserved

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-4-execution.md`

---

## Step 5: Add Conformance Exception to "Prose Test Descriptions Save Tokens" in workflow-advanced.md

**Objective:** Update the prose test descriptions decision to document the conformance exception — when to use precise prose with exact expected strings instead of abstracted behavioral prose.

**Design Reference:** DD-2 (design lines 79-93), completes Gap 4

**File:** `agents/decisions/workflow-advanced.md` (existing, edit)

**Current State:**
- Section "Prose Test Descriptions Save Tokens" (around lines 187-199)
- Documents token savings from prose descriptions vs. full test code
- No exception documented for conformance work

**Changes Required:**

Add conformance exception after existing "Impact" line (around line 199), before next heading. New content (~10-12 lines):

```markdown
**Conformance exception:**

For conformance-type work with exact specifications (external reference, API spec, visual mockup), prose descriptions MUST include the exact expected strings from the reference.

This is not full test code — it is precise prose that preserves the specification.

**Example contrast:**

| Standard prose | Conformance prose |
|----------------|-------------------|
| "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator" |

**Rationale:** Standard prose is efficient for behavioral tests. For conformance work, the specification IS the exact string — abstracting it introduces translation loss. Precise prose preserves spec fidelity while maintaining token efficiency (still more compact than full test code).
```

**Implementation:**
Locate "### Prose Test Descriptions Save Tokens" section (around line 187). Find the "Impact:" line (around line 199). After this line, insert the conformance exception content above.

**Expected Outcome:**
- Section expanded with conformance exception (~10-12 lines added)
- Example contrast table matches Step 4 and design DD-2
- Rationale explains when to use precise vs. abstracted prose

**Validation:**
- Read updated section, verify exception content appears after "Impact" line
- Verify example table matches design lines 86-91
- Verify rationale explains conformance work vs. standard behavioral tests

**Success Criteria:**
- Exception content added after "Impact" line (or current location)
- Example table included with both rows (standard prose, conformance prose)
- Rationale paragraph explains spec preservation vs. token efficiency trade-off

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-5-execution.md`

---

## Step 6: Add Planning-Time File Size Awareness to plan-tdd Skill

**Objective:** Update plan-tdd skill to include convention for noting current file sizes when adding content and proactively planning splits when approaching the 400-line limit.

**Design Reference:** DD-4 (design lines 108-119)

**File:** `agent-core/skills/plan-tdd/SKILL.md` (existing, edit)

**Current State:**
- Skill documents TDD runbook creation process
- No guidance on file size awareness during planning

**Changes Required:**

Add file size awareness convention to planner guidance sections. Exact location depends on current structure — search for sections discussing cycle planning or implementation details. Add ~15 lines:

```markdown
### Planning-Time File Size Awareness

**Convention:** When a cycle adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each cycle adding content to existing file: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: Include a split step in the same phase
3. Threshold is 350, not 400 — leaves 50-line margin for vet fixes and minor additions

**Why 350:** The 400-line limit is a hard fail at commit time. Planning to the exact limit creates brittleness. A 50-line margin is pragmatic.

**Example:**
- Cycle 3.2 adds format_model() to display.py (current: ~320 lines, adding ~40)
- Cycle 3.2: Implement format_model() (~360 lines total)
- Cycle 3.3: Split display.py into display_core.py + display_formatters.py

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.
```

**Implementation:**
Locate planner guidance sections in plan-tdd/SKILL.md (likely within Phase 1-3 or cycle planning sections). Insert the file size awareness convention content above. Integrate with existing guidance — if there's a "Cycle Planning" section, add this as a subsection.

**Expected Outcome:**
- Convention documented with process steps (note sizes, check threshold, plan splits)
- Rationale explains 350-line margin (not 400)
- Example demonstrates notation and split planning
- Clarifies this is planning convention, not runtime enforcement

**Validation:**
- Read updated skill, verify convention content present
- Verify 350-line threshold explained with margin rationale
- Verify example shows both notation and split step

**Success Criteria:**
- ~15 lines added to plan-tdd/SKILL.md
- Contains process steps, threshold (350), example, runtime enforcement note
- Integrated with existing planner guidance sections

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-6-execution.md`

---

## Step 7: Add Planning-Time File Size Awareness to plan-adhoc Skill

**Objective:** Update plan-adhoc skill with the same file size awareness convention as plan-tdd, adapted for non-TDD context.

**Design Reference:** DD-4 (design lines 108-119)

**File:** `agent-core/skills/plan-adhoc/SKILL.md` (existing, edit)

**Current State:**
- Skill documents ad-hoc runbook creation process
- No guidance on file size awareness during planning

**Changes Required:**

Add file size awareness convention to planner guidance sections. Content is nearly identical to Step 6, adapted for non-TDD terminology (~15 lines):

```markdown
### Planning-Time File Size Awareness

**Convention:** When a step adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each step adding content to existing file: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: Include a split step in the same phase
3. Threshold is 350, not 400 — leaves 50-line margin for vet fixes and minor additions

**Why 350:** The 400-line limit is a hard fail at commit time. Planning to the exact limit creates brittleness. A 50-line margin is pragmatic.

**Example:**
- Step 2.3 adds authentication handlers to routes.py (current: ~330 lines, adding ~35)
- Step 2.3: Implement authentication handlers (~365 lines total)
- Step 2.4: Split routes.py into routes_auth.py + routes_core.py

**No runtime enforcement:** This is a planning convention. The commit-time `check_line_limits.sh` remains the hard gate. This prevents write-then-split rework loops.
```

**Implementation:**
Locate planner guidance sections in plan-adhoc/SKILL.md (likely within Point 1 phase-by-phase expansion or step planning sections). Insert the file size awareness convention content. Integrate with existing guidance.

**Expected Outcome:**
- Convention documented with process steps (adapted from plan-tdd Step 6)
- Example uses ad-hoc terminology (step numbers, not cycle numbers)
- Rationale and threshold (350) identical to plan-tdd version

**Validation:**
- Read updated skill, verify convention content present
- Verify example uses ad-hoc terminology (not TDD cycles)
- Verify threshold and rationale match plan-tdd Step 6

**Success Criteria:**
- ~15 lines added to plan-adhoc/SKILL.md
- Contains process steps, threshold (350), example adapted for ad-hoc context
- Integrated with existing planner guidance sections

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-7-execution.md`

---

## Step 8: Manual Skill Audit → Decision on Lint Script

**Objective:** Audit all skills for tool-call-first convention compliance, categorize findings, and decide whether to ship `scripts/check_skill_steps.py` as a hard fail linter.

**Design Reference:** DD-7 (design lines 148-158)

**Model:** Sonnet (requires semantic judgment for categorization)

**Process:**

1. **Discover all skill files:**
   ```bash
   find agent-core/skills -name "SKILL.md" -type f | sort
   ```

2. **For each skill file, audit numbered steps:**
   - Locate all numbered step headings (`### N.`, `### N.M.`)
   - For each step: Check if first 5 lines after heading contain a tool call (Read, Write, Edit, Bash, Grep, Glob, Task, etc.)
   - Categorize:
     - **Compliant:** Step has tool call in first 5 lines
     - **Legitimately exempt:** Step is prose-only checkpoint or decision point (e.g., "Assess complexity", "Decide on approach")
     - **Non-compliant:** Step should have tool call but doesn't (e.g., delegates to haiku but opens with prose, not Task call)

3. **Produce audit report:**
   Write to `plans/reflect-rca-parity-iterations/reports/n1-audit.md`:
   - Audit summary: Total skills, total steps, compliance percentage
   - Breakdown by category (compliant, exempt, non-compliant)
   - List of non-compliant steps with file paths
   - List of legitimately exempt steps with rationale

4. **Decision threshold (from DD-7):**
   - **If ≥80% comply with few false positives (<10% of compliant flagged):**
     - Ship lint: Create `scripts/check_skill_steps.py` with `<!-- no-tool-call-check -->` exemption marker
     - Update justfile: Add skill step validation to precommit recipe
     - Document decision: "Lint ships — 80% threshold met, convention validated"
   - **If <80% comply or many false positives (≥10%):**
     - Don't ship: Convention remains guidance only
     - Document decision: "Lint not shipped — compliance below threshold, convention needs refinement"

5. **Conditional outputs:**
   - **Path A (ship lint):** Audit report + `scripts/check_skill_steps.py` + justfile edit
   - **Path B (don't ship):** Audit report documenting decision rationale

**Expected Outcome:**
- Audit report exists with compliance metrics
- Decision documented (ship or don't ship) with threshold analysis
- If shipping: Lint script and justfile edit created

**Validation:**
- Read audit report, verify all skills audited
- Verify decision threshold correctly applied (≥80% = ship, <80% = don't ship)
- If shipping: Verify script exists and justfile updated

**Success Criteria:**
- Audit report at `plans/reflect-rca-parity-iterations/reports/n1-audit.md` with compliance percentage
- Decision documented with threshold evidence
- Conditional outputs match decision (Path A or Path B)

**Report Path:** `plans/reflect-rca-parity-iterations/reports/n1-audit.md`

**Note:** This step uses sonnet model due to semantic categorization required (distinguishing "legitimately exempt" from "non-compliant" requires judgment about step intent).

---

## Phase 2 Checkpoint

**Completion Criteria:**
- Step 3: defense-in-depth.md created with layered mitigation pattern (~60-80 lines)
- Step 4: testing.md "Conformance Validation for Migrations" expanded (~30 lines)
- Step 5: workflow-advanced.md "Prose Test Descriptions Save Tokens" has conformance exception (~10 lines added)
- Step 6: plan-tdd/SKILL.md has file size awareness convention (~15 lines)
- Step 7: plan-adhoc/SKILL.md has file size awareness convention (~15 lines)
- Step 8: N1 audit report complete with decision (conditional: lint ships or doesn't ship)

**Verification before proceeding to Phase 3:**
- Gap 4 changes (Steps 4-5) must be committed before Phase 3 begins
- Gap 4 defines "precise test descriptions" that Gap 1 (Phase 3 Step 9) mandates

**Next Phase:** Phase 3 (Tier 3 fixes — Gap 1 conformance test cycles, N2 vet alignment)
# Phase 3: Tier 3 Fixes (Moderate, Depends on Gap 4)

**Scope:** 2 steps, ~40 lines total, single session
**Model:** Haiku execution
**Complexity:** Moderate (multi-file skill edits, dependency on Gap 4 completion)

**Dependency:** Phase 3 starts AFTER Phase 2 is fully committed. Gap 4 (Phase 2 Steps 4-5) defines what "precise test descriptions" means; Gap 1 (Phase 3 Step 9) mandates when they're required.

---

## Step 9: Add Mandatory Conformance Test Cycles to plan-tdd and plan-adhoc

**Objective:** Update both planning skills to mandate conformance test cycles when the design document includes an external reference (shell prototype, API spec, visual mockup).

**Design Reference:** DD-1 (design lines 64-77)

**Prerequisites:**
- **Phase 2 committed** — Gap 4 (Steps 4-5) must be committed before executing this step
- Gap 4 defined "conformance exception to prose test descriptions" in testing.md and workflow-advanced.md
- This step (Gap 1) mandates WHEN conformance tests are required — when design has external reference

**Context:**
- Gap 4 provides the precision guidance (exact expected strings)
- Gap 1 provides the trigger condition (external reference in design)
- Together they close the conformance gap identified in statusline-parity RCA

**Files:**
- `agent-core/skills/plan-tdd/SKILL.md` (existing, edit)
- `agent-core/skills/plan-adhoc/SKILL.md` (existing, edit)

**Changes Required:**

### For plan-tdd/SKILL.md:

Add conformance test cycles guidance to planner sections (likely Phase 2-3 cycle planning). Content (~15 lines):

```markdown
### Mandatory Conformance Test Cycles

**Trigger:** When design document includes external reference (shell prototype, API spec, visual mockup) in `Reference:` field or spec sections.

**Requirement:** Planner MUST include conformance test cycles that bake expected behavior from the reference into test assertions.

**Mechanism:**
- Reference is consumed at authoring time (during planning)
- Expected strings from reference become test assertions
- Tests are permanent living documentation of expected behavior (reference not preserved as runtime artifact)

**Test precision (from Gap 4):**
- Use precise prose descriptions with exact expected strings from reference
- Example: "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator"
- NOT abstracted: "Assert output contains formatted model with emoji and color"

**Rationale:** Tests that include exact expected strings eliminate translation loss between spec and implementation. This addresses statusline-parity failures where tests verified structure but not conformance.

**Related:** See testing.md "Conformance Validation for Migrations" for detailed guidance.
```

### For plan-adhoc/SKILL.md:

Add conformance validation steps guidance (adapted for non-TDD context). Content (~15 lines):

```markdown
### Mandatory Conformance Validation Steps

**Trigger:** When design document includes external reference (shell prototype, API spec, visual mockup) in `Reference:` field or spec sections.

**Requirement:** Runbook MUST include validation steps that verify implementation conforms to the reference specification.

**Mechanism:**
- Reference is consumed during planning
- Expected behavior from reference becomes validation criteria in runbook steps
- Validation can be: conformance test cycles, manual comparison steps, or automated conformance checks

**Validation precision (from Gap 4):**
- When using test-based validation: Use precise prose descriptions with exact expected strings
- Example validation criterion: "Output matches shell reference: `🥈 sonnet \033[35m…` with double-space separators"
- NOT abstracted: "Output contains formatted model with appropriate styling"

**Rationale:** Conformance validation closes the gap between specification and implementation. Exact expected strings prevent abstraction drift.

**Related:** See testing.md "Conformance Validation for Migrations" for detailed guidance.
```

**Implementation:**

1. **For plan-tdd/SKILL.md:**
   - Read file to identify planner guidance sections
   - Search for section heading containing "Phase 2" or "Phase 3" or "Cycle" or "Planning" in planner workflow
   - After identifying appropriate section (likely within Phase 2-3 cycle decomposition guidance), insert "Mandatory Conformance Test Cycles" content as a new subsection
   - Use Edit tool to add content, preserving existing structure

2. **For plan-adhoc/SKILL.md:**
   - Read file to identify planner guidance sections
   - Search for section heading containing "Point 1" or "Step Planning" or "Phase-by-Phase" in planner workflow
   - After identifying appropriate section (likely within Point 1 expansion guidance), insert "Mandatory Conformance Validation Steps" content as a new subsection
   - Use Edit tool to add content, preserving existing structure

**Expected Outcome:**
- Both skills updated with conformance requirements
- Trigger condition clear (external reference in design)
- Precision guidance references Gap 4 (exact expected strings)
- Rationale explains why (translation loss prevention)

**Validation:**
- Read both updated skills
- Verify trigger condition documented ("external reference")
- Verify precision guidance references Gap 4 or testing.md
- Verify rationale explains conformance vs structure distinction

**Success Criteria:**
- plan-tdd/SKILL.md: ~15 lines added documenting mandatory conformance test cycles
- plan-adhoc/SKILL.md: ~15 lines added documenting mandatory conformance validation steps
- Both reference DD-1 mechanism (reference consumed at authoring, tests permanent)
- Both reference Gap 4 precision guidance (exact expected strings) OR testing.md conformance section

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-9-execution.md`

---

## Step 10: Add Explicit Alignment Criterion to vet-fix-agent

**Objective:** Update vet-fix-agent to include alignment checking as a standard review criterion (not conditional on design reference presence).

**Design Reference:** DD-5 (design lines 121-135)

**File:** `agent-core/agents/vet-fix-agent.md` (existing, edit)

**Current State:**
- Review protocol has "Design anchoring" as a dimension when design reference provided
- Alignment (does implementation match spec?) is broader than design anchoring

**Changes Required:**

Locate review criteria section (likely within "### 3. Review Changes" or similar). Add explicit alignment criterion (~5 lines):

```markdown
**Alignment:**
- Does the implementation match stated requirements and acceptance criteria?
- For work with external references (shell scripts, API specs, mockups): Does implementation conform to the reference specification?
- Check: Compare implementation behavior against requirements summary (provided in task prompt)
- Flag: Deviations from requirements, missing features, behavioral mismatches
```

**Integration:**
- This becomes a standard review dimension alongside code quality, test coverage, design anchoring, etc.
- When design includes external reference, alignment includes conformance checking
- Not a separate "conformance mode" — alignment is always-on

**Implementation:**

1. Locate review protocol section (search for "### 3. Review Changes" or "Review dimensions")
2. After existing review criteria (code quality, design anchoring, etc.), add "Alignment" criterion
3. Integrate with existing protocol — alignment check happens during step 3 review

**Expected Outcome:**
- Alignment criterion added to standard review protocol
- Conformance checking is a special case of alignment (when external reference present)
- Not a conditional mode — alignment always checked

**Validation:**
- Read updated vet-fix-agent.md
- Verify alignment criterion added to review protocol
- Verify criterion explains both general alignment and conformance special case

**Success Criteria:**
- ~5 lines added to vet-fix-agent.md review protocol
- Alignment criterion present with check and flag guidance
- Conformance mentioned as special case (external references)

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-10-execution.md`

---

## Phase 3 Checkpoint

**Completion Criteria:**
- Step 9: plan-tdd and plan-adhoc both updated with conformance requirements (~30 lines total across 2 files)
- Step 10: vet-fix-agent updated with alignment criterion (~5 lines)
- All Phase 3 changes committed

**Verification:**
- Gap 1 (conformance test cycles) implemented via Step 9
- N2 (vet alignment) implemented via Step 10
- Gap 4 prerequisite satisfied (Phase 2 Steps 4-5 committed before Phase 3 started)

**Next Phase:** Phase 4 (Memory index update — final step)
# Phase 4: Memory Index Update

**Scope:** 1 step, ~16 index entries (~20-25 total lines), single session
**Model:** Haiku execution
**Complexity:** Low (append-only operation)

---

## Step 11: Add Memory Index Entries for All New Decisions

**Objective:** Update memory-index.md with entries for all new decisions and guidance created in Phases 1-3, enabling future on-demand discovery.

**Design Reference:** All DD-1 through DD-8, implementation coverage

**File:** `agents/memory-index.md` (existing, append)

**Coverage Required:**

All changes from Phases 1-3 that introduce new knowledge or modify existing conventions:

1. **defense-in-depth.md** (Phase 2 Step 3, Q5) — Layered mitigation pattern
2. **Conformance precision** (Phase 2 Steps 4-5, Gap 4) — testing.md + workflow-advanced.md updates
3. **WIP-only restriction** (Phase 1 Step 1, Gap 5) — commit skill flag scope
4. **Planning-time file size awareness** (Phase 2 Steps 6-7, Gap 2) — plan-tdd + plan-adhoc convention
5. **Vet alignment** (Phase 3 Step 10, N2) — vet-fix-agent standard criterion
6. **Tool-call-first audit report** (Phase 2 Step 8, N1) — conditional lint decision based on compliance threshold

**New Entries Format:**

```markdown
## agents/decisions/defense-in-depth.md

Defense-in-Depth Pattern — quality gates layered with multiple independent checks, single-point failure prevention
Gap 3 + Gap 5 interaction — D+B hybrid outer defense plus WIP-only restriction inner defense
Pattern layers — outer (D+B ensures precommit), middle (precommit validation), inner (vet review), deepest (conformance tests)
Pattern applicability — use for any quality gate design, multiple layers compensate for individual weaknesses

## agents/decisions/testing.md

Conformance tests as executable contracts — when design has external reference, tests bake expected behavior into assertions
Exact expected strings requirement — test assertions include exact output from reference, eliminates translation loss
Conformance exception to prose descriptions — precise prose with exact strings for conformance work

## agents/decisions/workflow-advanced.md

Conformance exception to prose test descriptions — precise prose with exact expected strings when design has external reference

## agent-core/skills/commit/SKILL.md

WIP-only restriction for test/lint flags — --test and --lint for WIP commits only, final commits require full precommit

## agent-core/skills/plan-tdd/SKILL.md

Mandatory conformance test cycles — when design has external reference, planner must include conformance cycles
Planning-time file size awareness — note current file sizes, plan splits proactively at 350-line threshold

## agent-core/skills/plan-adhoc/SKILL.md

Mandatory conformance validation steps — when design has external reference, runbook must include conformance validation
Planning-time file size awareness — note current file sizes, plan splits proactively at 350-line threshold

## agent-core/agents/vet-fix-agent.md

Alignment as standard review criterion — does implementation match requirements and acceptance criteria, always-on check

## plans/reflect-rca-parity-iterations/reports/n1-audit.md

Tool-call-first convention audit — skill step compliance assessment, conditional lint decision
```

**Implementation:**

1. **Read memory-index.md** to identify current structure and last entry
2. **Determine insertion point:**
   - Create new `##` sections for new files: `## agents/decisions/defense-in-depth.md` and `## plans/reflect-rca-parity-iterations/reports/n1-audit.md`
   - Other sections may already exist (testing.md, workflow-advanced.md, commit/SKILL.md, etc.) — append new entries to existing sections
3. **Append entries** following memory-index format:
   - Title-words format (not kebab-case)
   - Bare lines (no list markers)
   - Keyword-rich descriptions (enable discovery)
   - Group by file (section heading = file path with `##` prefix for new files)
4. **Verify coverage:**
   - All 6 coverage items documented
   - Entries reference design decisions (DD-1 through DD-8) where applicable

**Expected Outcome:**
- Memory index updated with ~16 index entries across 8 file sections (~20-25 total lines including multi-line entries)
- All Phase 1-3 changes represented
- Entries follow memory-index conventions (title-words, bare lines, keyword-rich)

**Validation:**
- Read updated memory-index.md
- Verify all 6 coverage items have corresponding entries
- Verify entries follow format (title-words, bare lines, grouped by file)
- Verify new sections created for defense-in-depth.md and n1-audit.md

**Success Criteria:**
- ~16 index entries added to memory-index.md across 8 file sections (~20-25 total lines including multi-line entries)
- All coverage items documented: defense-in-depth pattern, conformance precision (2 files), WIP-only restriction, file size awareness (2 files), vet alignment, tool-call-first audit report
- Entries keyword-rich for discovery (e.g., "layered mitigation", "exact expected strings", "350-line threshold")
- New `##` sections created for defense-in-depth.md and n1-audit.md

**Report Path:** `plans/reflect-rca-parity-iterations/reports/step-11-execution.md`

---

## Phase 4 Checkpoint

**Completion Criteria:**
- Step 11: Memory index updated with all Phase 1-3 changes documented
- All 6 coverage items have entries (defense-in-depth, conformance precision, WIP-only, file size awareness, vet alignment, audit report)
- Phase 4 changes committed

**Runbook Complete:** All 4 phases finished, all 11 steps executed, all 8 design decisions implemented, memory index updated.

**Next:** No further phases. Runbook execution complete.
