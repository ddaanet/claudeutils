# Design: Parity Test Quality — Remaining Gap Fixes

**Source:** `outline.md` (validated), `rca.md`, `rca-review-critique.md`, `reports/explore-pipeline.md`
**Mode:** General (guidance updates, mechanical fixes, tooling)
**Consumer:** `/plan-adhoc`

---

## Problem Statement

The statusline-parity plan required 4 iterations to reach acceptable state despite exact specifications. The RCA identified 5 root causes and 5 remaining gaps. The D+B hybrid fix addressed Gap 3 (prose gate skipping) for two skills. Four gaps remain open, plus three Opus-identified concerns (N1-N3).

**Goal:** Close remaining gaps through guidance updates, convention changes, and optional tooling. No orchestration pipeline changes.

---

## Requirements

**Source:** `rca.md` (5 gaps), `rca-review-critique.md` (9 findings), `outline.md` (resolved decisions)

**Functional:**
- FR-1: Conformance test cycles mandatory when design has external reference — addressed by Gap 1 fix (plan-tdd, plan-adhoc updates)
- FR-2: Test descriptions for conformance work include exact expected strings — addressed by Gap 4 fix (testing.md, workflow-advanced.md)
- FR-3: `--test`/`--lint` commit modes restricted to WIP commits — addressed by Gap 5 fix (commit skill)
- FR-4: Planning-time file size awareness — addressed by Gap 2 fix (plan-tdd, plan-adhoc)
- FR-5: Vet alignment includes conformance checking as standard — addressed by N2 (vet-fix-agent)
- FR-6: Defense-in-depth pattern documented — addressed by Q5 (new decision doc)
- FR-7: Skill step tool-call-first convention audit — addressed by N1 (manual audit → decision)
- FR-8: D+B empirical validation — addressed by N3 (execution test)

**Non-functional:**
- NFR-1: No orchestration pipeline changes — conformance triggers through existing mechanisms
- NFR-2: Changes apply going forward — no retroactive plan fixes
- NFR-3: Hard limits or no limits — no warning-only modes (per learnings)

**Out of scope:**
- Pre-write file size hooks (deferred — planning awareness is higher leverage)
- Concurrent pipeline evolution (scheduling concern, not quality gate)
- Lint script for tool-call-first convention (deferred until audit validates feasibility)

---

## Architecture

No new systems. All changes are guidance/convention updates to existing files, plus one optional script.

**Change topology:**

```
Gap 4 (test precision)
  ↓ enables
Gap 1 (conformance cycles)    Gap 5 (WIP-only bypass)    Gap 2 (file size awareness)
  ↓ extends
N2 (vet alignment)             N1 (skill audit)            N3 (empirical validation)
                                Q5 (defense-in-depth doc)
```

**Dependency:** Gap 4 must land before Gap 1 is effective. All others are independent.

---

## Key Design Decisions

### DD-1: Conformance Tests as Executable Contracts

**Decision:** When a design includes an external reference (shell prototype, API spec, visual mockup), the planner MUST include conformance test cycles that bake expected behavior into test assertions.

**Mechanism:**
- Planner detects `Reference:` field or external spec in design document
- Planner adds conformance test cycle(s) that assert exact expected strings/output from the reference
- Reference is consumed at authoring time — not preserved as runtime artifact
- Tests become permanent living documentation of expected behavior

**Rationale:** The statusline-parity failure was that tests verified structure ("contains emoji") not conformance ("output matches `🥈 sonnet \033[35m…`"). Tests that bake in exact expected strings eliminate the translation loss between spec and implementation.

**Where enforced:** plan-tdd and plan-adhoc skill files — mandatory section in planner guidance.

### DD-2: Conformance Exception to Prose Test Descriptions

**Decision:** The "Prose Test Descriptions Save Tokens" convention (`workflow-advanced.md`) gets a conformance exception.

**Current rule:** Use prose descriptions, not full test code, in runbook RED phases.

**Exception:** For conformance-type work with exact specifications, prose descriptions MUST include the exact expected strings from the reference. This is not full test code — it is precise prose.

**Example contrast:**

| Standard prose | Conformance prose |
|----------------|-------------------|
| "Assert output contains formatted model with emoji and color" | "Assert output contains `🥈` followed by `\033[35msonnet\033[0m` with double-space separator" |

**Rationale:** Standard prose is efficient for behavioral tests. But for conformance work, the specification IS the exact string — abstracting it introduces the translation loss that caused 8 parity issues. This also addresses RC5 ("Visual Parity Validated" without evidence) — when test descriptions include exact expected strings, a false completion claim is detectable through test execution.

### DD-3: WIP-Only Restriction for `--test`/`--lint`

**Decision:** Commit skill clarifies that `--test` and `--lint` flags are exclusively for WIP commits during TDD execution. Final commits always use full `just precommit`.

**Current state:** The flags exist and are documented, but there's no explicit restriction on when they can be used. An agent can legitimately choose `--test` mode for what it judges as test-only work, bypassing line limits.

**Fix:** Add explicit scope restriction in commit skill:
- `--test`: TDD GREEN phase only (before lint fixes)
- `--lint`: Post-lint-fix commits only (before complexity)
- All other commits: full `just precommit` (mandatory, no exceptions)

**Why not remove the flags:** They serve a legitimate purpose in TDD workflow — committing after GREEN phase before lint is clean. Removing them would break the TDD commit cadence.

### DD-4: Planning-Time File Size Awareness

**Decision:** Planners note current file sizes when adding content to existing files and plan splits proactively when additions would approach the 400-line limit.

**Mechanism:** Convention in plan-tdd and plan-adhoc:
- When a cycle adds content to an existing file, planner notes `(current: ~N lines, adding ~M)`
- If `N + M > 350`, planner includes a split step in the same phase
- Threshold is 350, not 400 — leaves margin for vet fixes and minor additions

**Why 350:** The 400-line limit is a hard fail. Planning to the exact limit creates brittleness — a vet fix adding error handling could push past. 50-line margin is pragmatic.

**No runtime enforcement:** This is a planning convention, not a hook. The commit-time `check_line_limits.sh` remains the hard gate. This prevents the write-then-split rework loop by catching it at planning time.

### DD-5: Vet Alignment as Standard Practice

**Decision:** Alignment checking is always-on in vet-fix-agent, not conditional on a special field.

**Current state:** Vet-fix-agent has "Design anchoring" as a review dimension when design reference is provided. But alignment (does implementation match spec?) is broader than design anchoring (does implementation follow design decisions?).

**Extension:** Add alignment to the standard review criteria in vet-fix-agent:
- "Does the implementation match stated requirements and acceptance criteria?"
- This is not a new mode — it's making explicit what "design anchoring" should already cover
- When a design includes an external reference, alignment includes conformance

**Why not a separate conformance mode:** Adding modes adds complexity. Alignment is fundamental to every review. Making it explicit (not adding a conditional branch) is simpler and more robust.

### DD-6: Defense-in-Depth Documentation

**Decision:** Create `agents/decisions/defense-in-depth.md` documenting the layered mitigation pattern.

**Content:** Document how multiple quality gates interact:
- D+B ensures precommit runs (outer defense)
- Precommit catches line limits, lint, test failures (middle defense)
- Vet-fix-agent catches quality and alignment issues (inner defense)
- Conformance tests catch spec-to-implementation drift (deepest defense)

**Gap 3 + Gap 5 interaction:** D+B ensures precommit appears in execution path. `--test` provides legitimate within-path bypass of line limits. Defense-in-depth: D+B (outer) + WIP-only restriction (inner) close this interaction.

**Pattern applicability:** This pattern applies beyond parity tests. Document it as a reusable principle for future quality gate design.

### DD-7: Skill Step Tool-Call-First Audit (Deferred Decision)

**Decision:** Manual audit of existing skills first. Ship lint as hard fail only if audit validates.

**Process:**
1. Audit all files in `agent-core/skills/*/SKILL.md`
2. For each numbered step (`### N.`), check if first 5 lines after heading contain a tool call
3. Catalog: steps that comply, steps that legitimately have no tool call, steps that should but don't
4. **If ≥80% comply with few false positives:** Ship `scripts/check_skill_steps.py` as hard fail with `<!-- no-tool-call-check -->` exemption marker
5. **If <80% comply or many false positives:** Don't ship — convention remains guidance only

**Why defer the decision:** The outline learning "hard limits vs soft limits" says either fail build or don't check. But we don't know yet if the convention holds. Auditing first prevents shipping a linter that immediately breaks precommit for most skills.

### DD-8: D+B Empirical Validation

**Decision:** Run commit skill in a real execution and verify gates fire.

**Process:**
- Execute `/commit` on a trivial change
- Verify Gate A (Read session.md) executes
- Verify Gate B (git diff for production artifacts) executes
- Verify validation (just precommit) executes
- Document evidence in `plans/reflect-rca-prose-gates/reports/d-b-validation.md`

**Why:** The RCA was empirical (grounded in specific failures). The fix was validated theoretically (design review). Empirical validation closes the asymmetry.

---

## Implementation Notes

### Files Changed

| File | Change | Gap | Tier |
|------|--------|-----|------|
| `agent-core/skills/commit/SKILL.md` | Add WIP-only restriction to `--test`/`--lint` flags | Gap 5 | 1 |
| `agents/decisions/testing.md` | Expand "Conformance Validation for Migrations" — tests as executable contracts, conformance exception to prose descriptions | Gap 4 | 2 |
| `agents/decisions/workflow-advanced.md` | Update "Prose Test Descriptions Save Tokens" — add conformance exception with example | Gap 4 | 2 |
| `agents/decisions/defense-in-depth.md` (new) | Layered mitigation pattern, Gap 3+5 interaction, reusable principle | Q5 | 2 |
| `agent-core/skills/plan-tdd/SKILL.md` | Mandatory conformance test cycles when design has external reference; planning-time file size awareness | Gap 1, 2 | 3 |
| `agent-core/skills/plan-adhoc/SKILL.md` | Same conformance and file size awareness guidance | Gap 1, 2 | 3 |
| `agent-core/agents/vet-fix-agent.md` | Add alignment to standard review criteria (not conditional) | N2 | 3 |
| `plans/reflect-rca-prose-gates/reports/d-b-validation.md` (new) | D+B empirical validation report — evidence that gates fire | N3 | 1 |
| `agents/memory-index.md` | Add entries for new decisions | All | 3 |
| `scripts/check_skill_steps.py` (conditional) | Lint for tool-call-first convention — only if audit supports | N1 | 2 |
| `justfile` (conditional) | Add skill step validation to precommit — only if lint ships | N1 | 2 |

### Testing Strategy

**No automated tests.** All changes are guidance documents and agent definitions — validated by vet-fix-agent review, not test suites.

**N3 (empirical validation):** Manual execution test documented in a report file.

**N1 (skill audit):** Manual audit produces a report. If lint ships, it's tested by running on existing skills.

### Affected Files Detail

**`agent-core/skills/commit/SKILL.md`** — Gap 5
- Current: Flags documented with usage examples but no scope restriction
- Change: Add explicit "WIP commits only" scope to `--test` and `--lint` flag descriptions
- Location: Flags section (top of file) and validation execution section
- Size: ~5 lines of prose

**`agents/decisions/testing.md`** — Gap 4
- Current: "Conformance Validation for Migrations" is 13 lines (128-140), sparse
- Change: Expand to ~30 lines covering: tests as executable contracts, exact expected strings, conformance exception to prose descriptions, example contrast table
- Location: Expand existing section at line 128

**`agents/decisions/workflow-advanced.md`** — Gap 4
- Current: "Prose Test Descriptions Save Tokens" at lines 187-199
- Change: Add conformance exception paragraph with example table (~10 lines)
- Location: After existing "Impact" line (199), before next heading

**`agents/decisions/defense-in-depth.md`** (new) — Q5
- Content: ~60-80 lines documenting layered mitigation pattern
- Sections: Pattern description, layer enumeration, Gap 3+5 interaction analysis, applicability guidance
- Standalone file — no cross-references needed except memory-index entry

**`agent-core/skills/plan-tdd/SKILL.md`** — Gap 1, 2
- Conformance: Add mandatory section about conformance test cycles when design has `Reference:` or external spec
- File size: Add planning-time awareness convention (note sizes, plan splits at 350)
- Location: Within planner guidance sections (exact location depends on current structure)

**`agent-core/skills/plan-adhoc/SKILL.md`** — Gap 1, 2
- Same conformance and file size awareness as plan-tdd, adapted for non-TDD context
- Conformance tests are regular validation steps, not RED-GREEN cycles

**`agent-core/agents/vet-fix-agent.md`** — N2
- Current: Has "Design anchoring" in review criteria
- Change: Add explicit "Alignment" criterion: "Does implementation match stated requirements and acceptance criteria?"
- Location: Review criteria section
- Size: ~3 lines

---

## Tier Sequencing

**Tier 1 (trivial, immediate — single step each):**
1. Gap 5: WIP-only restriction in commit skill
2. N3: D+B empirical validation (execute and document)

**Tier 2 (low complexity — can be parallel):**
3. Gap 4: Testing.md + workflow-advanced.md conformance precision updates
4. Gap 2: Planning-time file size awareness in plan-tdd + plan-adhoc
5. Q5: Create defense-in-depth.md
6. N1: Manual skill audit → decision on lint script

**Tier 3 (moderate — depends on Gap 4):**
7. Gap 1: Mandatory conformance test cycles in plan-tdd + plan-adhoc
8. N2: Vet alignment enhancement

**Sequencing constraint:** Tier 3 starts after Gap 4 (Tier 2) is landed. Gap 4 defines what "precise test descriptions" means; Gap 1 mandates when they're required.

**Memory index:** Updated as final step after all other changes land.

---

## What This Doesn't Do

- No orchestration pipeline changes — conformance triggers through existing TDD cycles and vet checkpoints
- No persistent test artifacts from references — expected behavior baked into tests at authoring time
- No retroactive fix of existing plans — conventions apply going forward
- No pre-write hooks for file size — planning awareness + commit-time check is sufficient
- No changes to D+B hybrid implementation — convention lint is complementary, deferred
- No solution to concurrent pipeline evolution — scheduling concern, separate job

---

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/testing.md` — current conformance validation entry (expand target)
- `agents/decisions/workflow-advanced.md` — prose test descriptions (exception target)
- `agent-core/skills/commit/SKILL.md` — flag documentation (restriction target)
- `agent-core/skills/plan-tdd/SKILL.md` — planner guidance (conformance + file size target)
- `agent-core/skills/plan-adhoc/SKILL.md` — planner guidance (same)
- `agent-core/agents/vet-fix-agent.md` — review criteria (alignment target)
- `plans/reflect-rca-parity-iterations/rca.md` — root causes for defense-in-depth doc context

**No Context7 or external research needed.** All changes are internal guidance updates.

## Next Steps

1. Route to `/plan-adhoc` for runbook generation
2. Tier assessment will determine if full runbook is needed (likely Tier 2 — multiple files, clear scope, no architectural uncertainty)
