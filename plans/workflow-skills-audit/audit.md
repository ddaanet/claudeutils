# Workflow Skills Audit Report

**Date:** 2026-02-06
**Scope:** plan-adhoc alignment with plan-tdd, design skill audit

---

## Part 1: Align plan-adhoc with plan-tdd

### Structural Comparison

| Aspect | plan-tdd | plan-adhoc | Aligned? |
|--------|----------|------------|----------|
| Frontmatter fields | name, description, model, allowed-tools, requires, outputs | description, allowed-tools, user-invocable | Divergent |
| Tier assessment | Phase 0 with explicit format | "Three-Tier Assessment" section | Aligned (content matches) |
| Codebase discovery | Phase 2 step 4 (REQUIRED) | Point 0.5 (REQUIRED) | Aligned |
| Memory discovery | Phase 2 step 3.5 | Point 0.5 step 1 | Aligned |
| Outline generation | Phase 1.5 | Point 0.75 | Aligned |
| Outline review agent | runbook-outline-review-agent (fix-all) | runbook-outline-review-agent (fix-all) | Aligned |
| Consolidation gate (outline) | Phase 1.6 | Missing | **GAP** |
| Complexity check before expansion | Phase 2.5 | Missing | **GAP** |
| Phase-by-phase expansion | Phase 3 with per-phase tdd-plan-reviewer | Point 1 with per-phase vet-agent | Aligned (different reviewer) |
| Consolidation gate (runbook) | Phase 4.5 | Missing | **GAP** |
| Assembly | Phase 4 (do NOT manually assemble) | Point 2 (manual concatenation) | **CONFLICT** |
| Final review | Phase 5 holistic review | Point 3 holistic review | Aligned |
| prepare-runbook.py | Phase 5 step 4 (auto) | Point 4 | Aligned |
| Tail-call handoff | Phase 5 step 6 | Point 4.1 step 3 | Aligned |
| Clipboard copy | Phase 5 step 5 | Point 4.1 step 2 | Aligned |
| Checkpoints section | Full checkpoint spec (light/full) | Missing | **GAP** |
| Documentation perimeter | Phase 1 step 0 | Point 0.5 step 0 | Aligned |
| Reference files | 4 files (patterns, anti-patterns, error-handling, examples) | None | **GAP** |

### Specific Changes to Port from plan-tdd to plan-adhoc

#### 1. Consolidation Gate After Outline (HIGH)

**What:** plan-tdd Phase 1.6 merges trivial phases with adjacent complexity before expensive expansion.

**Why:** Reduces orchestrator overhead by batching simple work with adjacent complexity. plan-adhoc generates full runbooks where this is equally valuable.

**Port:** Add "Point 0.85: Consolidation Gate -- Outline" between Point 0.75 and Point 1 in `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md`. Adapt from TDD version:
- Remove TDD-specific language (cycles -> steps)
- Keep merge constraints (never cross phases, max 10 steps)
- Keep skip conditions (no trivial phases, already compact)

#### 2. Complexity Check Before Expansion (HIGH)

**What:** plan-tdd Phase 2.5 assesses expansion complexity BEFORE generating step content, with callback mechanism.

**Why:** Prevents expensive generation of poorly-structured work. plan-adhoc can generate bloated runbooks without this gate.

**Port:** Add "Point 0.9: Complexity Check Before Expansion" after the consolidation gate in `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md`. Adapt:
- Replace "cycles" with "steps"
- Keep callback levels: step -> outline -> design -> requirements
- Keep fast-path: pattern steps get template+variations, trivial phases get inline instructions
- Keep trigger thresholds (25 steps -> callback to design, 10 steps/phase -> split)

#### 3. Fix Assembly Contradiction (HIGH)

**What:** plan-tdd Phase 4 explicitly says "Do NOT manually assemble" and defers to prepare-runbook.py. plan-adhoc Point 2 says "Concatenate phase files" into runbook.md manually.

**Why:** Manual assembly was identified as an anti-pattern in learnings.md ("Manual runbook assembly bypasses automation"). prepare-runbook.py handles assembly with validation (metadata calc, numbering validation). The plan-adhoc manual concatenation contradicts this established decision.

**Fix in** `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md`, Point 2:
- Remove manual concatenation instructions (step 1: "Concatenate phase files")
- Add "Do NOT manually assemble" warning matching plan-tdd Phase 4
- Explain that prepare-runbook.py in Point 4 handles assembly
- Keep metadata preparation (step 2) and consistency check (step 3) as pre-assembly validation

#### 4. Consolidation Gate After Assembly (MEDIUM)

**What:** plan-tdd Phase 4.5 merges isolated trivial steps with related features after assembly.

**Why:** Second consolidation pass catches trivial steps that weren't visible at outline level.

**Port:** Add "Point 2.5: Consolidation Gate -- Runbook" between Point 2 and Point 3 in `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md`. Adapt:
- Replace "cycles" with "steps"
- Keep constraints (never cross phases, keep merged steps manageable, preserve isolation)
- Keep skip conditions (no trivial steps, already compact)

#### 5. Add Checkpoints Section (MEDIUM)

**What:** plan-tdd has a comprehensive Checkpoints section describing light checkpoints (Fix + Functional) and full checkpoints (Fix + Vet + Functional) at phase boundaries.

**Why:** plan-adhoc runbooks also execute via `/orchestrate`, which has checkpoint delegation at phase boundaries (orchestrate skill section 3.4). The plan-adhoc skill should document expected checkpoint behavior so runbooks include appropriate checkpoint markers.

**Port:** Add "## Checkpoints" section to `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md`. Simplify from TDD version:
- Remove TDD-specific items (xfail markers, integration test patterns)
- Keep light checkpoint (Fix + Functional) at every phase boundary
- Keep full checkpoint (Fix + Vet + Functional) at final phase
- Keep `checkpoint: full` marking guidance for cross-module phases

#### 6. Frontmatter Alignment (LOW)

**What:** plan-tdd has `name`, `model`, `requires`, `outputs` fields. plan-adhoc is missing `name`, `model`, `requires`, `outputs`.

**Port:** Add to plan-adhoc frontmatter:
```yaml
name: plan-adhoc
model: sonnet
requires:
  - Design document from /design
  - CLAUDE.md for project conventions (if exists)
outputs:
  - Execution runbook at plans/<job-name>/runbook.md
  - Ready for prepare-runbook.py processing
```

#### 7. Add Reference Files (LOW)

**What:** plan-tdd has 4 reference files (patterns, anti-patterns, error-handling, examples). plan-adhoc has none.

**Why:** Reference files provide on-demand guidance without bloating the main skill. plan-adhoc could benefit from error-handling and examples references.

**Recommendation:** Consider creating at minimum:
- `agent-core/skills/plan-adhoc/references/error-handling.md` — Error catalog adapted from TDD version
- `agent-core/skills/plan-adhoc/references/examples.md` — Ad-hoc runbook examples

This is low priority because the main skill already covers error handling inline and the existing reference in "References" section points to real example runbooks.

### Intentional Divergences (No Action Needed)

These differences are by design and should NOT be ported:

| Divergence | Reason |
|------------|--------|
| RED/GREEN/REFACTOR cycle format | TDD-specific methodology |
| Prose test descriptions | TDD-specific (plan-adhoc uses script evaluation) |
| tdd-plan-reviewer agent | TDD-specific anti-pattern detection |
| Cycle X.Y numbering | TDD convention; plan-adhoc uses Step N or Step N.M |
| "What NOT to Test" section | TDD-specific presentation vs behavior guidance |
| Cycle Breakdown Guidance | TDD decomposition methodology |
| Phase 3.1-3.6 (per-phase guidance) | TDD RED/GREEN generation rules |

---

## Part 2: Design Skill Audit

### Current State Assessment

**File:** `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` (320 lines)

The design skill has three phases:
- **Phase A:** Research + Outline (A.0-A.6)
- **Phase B:** Iterative Discussion
- **Phase C:** Generate Design (C.1, C.3-C.5)

Note: Phase C skips C.2 (likely historical numbering artifact).

### Finding 1: No Checkpoint Commits Around design-vet-agent (HIGH)

**Current behavior:** The design skill invokes design-vet-agent at C.3, applies fixes at C.4, then does handoff+commit at C.5. There is no intermediate commit between the design document creation (C.1) and the vet review (C.3).

**Problem:** If design-vet-agent applies fixes (it fixes ALL issues including minor per its agent definition), the resulting commit conflates the original design with the vet fixes. There is no snapshot of the pre-vet design.

**Recommendation:** Add checkpoint commits:
1. **Before C.3 (vet):** Commit the design document as-is after C.1 completes. This preserves the designer's original output in git history.
2. **After C.4 (fixes applied):** The existing C.5 handoff+commit handles this.

**Implementation in** `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md`:
- Add "C.2: Checkpoint Commit" between C.1 and C.3
- Content: "Commit design document before vet review. This preserves the designer's original output. Use `/commit` skill."
- This is a prose gate (no tool call), which is known to be skipped (see learnings.md "Prose skill gates skipped"). To mitigate, make the commit the first concrete action: "Run `git add plans/<job-name>/design.md && git commit -m 'draft design'`" or delegate via `/commit`.

**Concern:** The "prose gates skipped" learning warns that steps without concrete tool calls get scanned but not executed. A checkpoint commit step that just says "commit now" may be skipped. It should include an explicit Bash tool call or `/commit` invocation.

### Finding 2: Complexity Triage is Current (OK)

The complexity triage (simple/moderate/complex) at step 0 is consistent with the three-tier model documented in `agents/decisions/workflow-core.md` ("Orchestration Assessment: Three-Tier Implementation Model"). The routing is correct:
- Simple -> execute directly
- Moderate -> skip design, route to planning skill
- Complex -> proceed with Phases A-C

The `agents/decisions/workflow-optimization.md` "Routing Layer Efficiency" decision warns against double assessment (design skill assesses complexity, then planning skill re-assesses tiers). The current design addresses this: it routes moderate tasks directly to planning skills, which then do their own tier assessment. This is acceptable because the two assessments answer different questions:
- Design skill: "Does this need architectural design?" (simple/moderate/complex)
- Planning skill: "How should implementation be structured?" (Tier 1/2/3)

However, the routing-layer-efficiency decision explicitly calls this an anti-pattern: "Oneshot assessed simple/moderate/complex, then /plan-adhoc re-assessed Tier 1/2/3 -- same function, different labels." This suggests the assessments ARE considered redundant. Currently, the design skill does not pass its assessment context to the planning skill, so the planning skill starts fresh.

**Recommendation (LOW):** Consider passing the design skill's complexity assessment as context to the planning skill invocation to avoid full re-analysis. This is a minor optimization.

### Finding 3: Missing Session State Check Enforcement (LOW)

The design skill states at step 0: "Session state check: If session has significant pending work (>5 tasks), suggest /shelve before proceeding."

This is another prose gate with no concrete tool call. Per the "prose gates skipped" pattern, this check may be routinely skipped.

**Recommendation:** Make this check concrete by either:
- Adding a Bash command to count pending tasks: `grep -c '^\- \[ \]' agents/session.md`
- Or delegating to a script that checks pending task count

### Finding 4: A.2 Delegation Pattern is Sound (OK)

The A.2 step correctly delegates exploration to quiet-explore agents, keeping opus focused on design reasoning. The quiet-explore delegation uses artifact-return pattern (report path specified, agent returns filepath).

### Finding 5: outline-review-agent Exists (OK)

At A.6, the design skill delegates to `outline-review-agent` with `subagent_type="outline-review-agent"`. Agent definition confirmed at `/Users/david/code/claudeutils/agent-core/agents/outline-review-agent.md`. A separate `runbook-outline-review-agent.md` also exists for the planning skills' outline review. No gap here.

### Finding 6: Phase C Numbering Gap (LOW)

Phase C has steps C.1, C.3, C.4, C.5 -- missing C.2. This suggests either a historical removal or the checkpoint commit should fill C.2. The recommendation in Finding 1 naturally fills this gap.

### Finding 7: design-vet-agent Fix-All vs Caller Fix Pattern (OK)

The workflow decision "Review Agent Fix-All Pattern" lists design-vet-agent as a fix-all agent. The design skill at C.3 invokes it and at C.4 reads the report to "Address all critical and major priority feedback." But design-vet-agent already fixes ALL issues (including minor). The C.4 step implies the caller re-fixes, which is redundant.

**Resolution:** C.4 should be reworded. design-vet-agent applies fixes; the caller at C.4 reads the report to:
- Check for ESCALATION (unfixable issues)
- Verify satisfaction with the applied fixes
- Optionally re-review if design-vet-agent's fixes were significant

The current C.4 wording ("Address all critical and major priority feedback: Critical issues MUST be fixed before proceeding") implies the caller does the fixing, contradicting the fix-all pattern.

**Recommendation:** Reword C.4 to match the fix-all pattern:
```
Read the review report from the filepath returned by design-vet-agent.

Check for ESCALATION: If unfixable issues reported, address them before proceeding.

Review applied fixes: design-vet-agent applied all fixes (critical, major, minor).
If fixes are satisfactory, proceed to C.5.
If significant re-review needed, re-delegate to design-vet-agent.
```

---

## Prioritized Action Items

### High Priority

1. **Fix assembly contradiction in plan-adhoc** -- Point 2 manual concatenation contradicts established "no manual assembly" decision and plan-tdd Phase 4. Change to pre-assembly validation only, defer actual assembly to prepare-runbook.py.
   - File: `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` lines 268-283

2. **Add consolidation gate after outline** -- Port plan-tdd Phase 1.6 to plan-adhoc as Point 0.85.
   - File: `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (insert after Point 0.75)

3. **Add complexity check before expansion** -- Port plan-tdd Phase 2.5 to plan-adhoc as Point 0.9.
   - File: `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (insert after consolidation gate)

4. **Add checkpoint commit before design-vet-agent** -- Fill C.2 gap in design skill with concrete commit action.
   - File: `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` (insert between C.1 and C.3)

### Medium Priority

5. **Add consolidation gate after assembly** -- Port plan-tdd Phase 4.5 to plan-adhoc as Point 2.5.
   - File: `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (insert after Point 2)

6. **Add checkpoints section** -- Document checkpoint expectations for ad-hoc runbooks.
   - File: `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` (new section)

7. **Reword design skill C.4** -- Align with fix-all pattern (design-vet-agent applies fixes, caller checks for escalations).
   - File: `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` lines 269-279

### Low Priority

9. **Align plan-adhoc frontmatter** -- Add name, model, requires, outputs fields.
   - File: `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/SKILL.md` lines 1-5

10. **Consider reference files** -- Create error-handling.md and examples.md for plan-adhoc.
    - Directory: `/Users/david/code/claudeutils/agent-core/skills/plan-adhoc/references/`

11. **Pass complexity context from design to planning skill** -- Avoid redundant re-assessment.
    - Files: design SKILL.md (pass context), plan-adhoc SKILL.md (receive context)

12. **Make session state check concrete** -- Add tool call to prevent prose gate skipping.
    - File: `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md` step 0
