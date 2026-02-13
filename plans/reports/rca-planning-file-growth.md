# RCA: Planning Pipeline Lacks File Growth Projection

**Date:** 2026-02-13
**Runbook:** worktree-update
**Evidence:** 7+ refactor escalations (18 refactor reports), >1hr wall-clock on line limit fixes
**Impact:** Planning efficiency loss, execution delays, opus escalations for haiku-tier work

---

## Root Cause

**The planning pipeline does not project file growth during runbook creation, and review axes do not validate projected file size against limits.**

**Specific gap:** Between outline generation (Phase 0.75) and phase expansion (Phase 1), there is no step that:
1. Estimates lines added per cycle based on design complexity
2. Projects cumulative file growth across phases
3. Inserts proactive split points when projection exceeds limits

The 400-line limit is enforced at commit time (precommit validation via `scripts/check_line_limits.sh`) but not anticipated during planning.

---

## Contributing Factors

### C1: Planning-Execution Gap

**Planning artifacts lack file growth metadata.**

Current outline structure (`runbook-outline.md`):
- Cycles per phase: ✓ (present)
- Complexity per phase: ✓ (Low/Medium/High)
- Estimated lines per cycle: ✗ (absent)
- Projected file size per phase: ✗ (absent)
- Split point recommendations: ✗ (absent)

**Evidence:** worktree-update outline specified:
- Phase 5: 7 cycles, High complexity
- Phase 7: 13 cycles, High complexity

But provided no estimate that these phases would add:
- Phase 5: ~80 lines (actual)
- Phase 7: ~130+ lines (actual, pre-refactor)

Without projection, planner cannot insert split points at phase boundaries.

### C2: Review Axes Miss Growth Pattern

**`agents/decisions/runbook-review.md` defines 4 review axes, none address file growth:**

| Axis | Checks | Misses |
|------|--------|--------|
| Vacuous Cycles | Behavioral substance | Lines added per cycle |
| Dependency Ordering | Foundation-first | Cumulative file size |
| Cycle Density | Collapse candidates | Growth projection |
| Checkpoint Spacing | Quality gate gaps | File split points |

**Checkpoint Spacing** is conceptually closest but checks cycle count between vet checkpoints, not projected file size.

### C3: Phase 1.4 "File Size Awareness" Underspecified

**`agent-core/skills/runbook/SKILL.md` lines 504-513 introduce "File Size Awareness":**

```markdown
### Phase 1.4: File Size Awareness

**Convention:** When an item adds content to an existing file, note current file size and plan splits proactively.

**Process:**
1. For each item adding content: Note `(current: ~N lines, adding ~M)`
2. If `N + M > 350`: include a split step in the same phase
3. Threshold rationale: 400-line hard limit at commit, 350 leaves ~50-line margin (heuristic)
```

**Problems with this approach:**

1. **Item-level granularity is too late:** By Phase 1 (expansion), phases are already defined. Inserting split steps mid-phase is awkward and breaks phase coherence.

2. **Per-item tracking is error-prone:** Requires planner to:
   - Track cumulative growth per file across phases
   - Sum lines from multiple cycles modifying same file
   - Manually insert split steps when threshold crossed
   - This is cognitive overhead that weak agents (sonnet expansion) handle inconsistently

3. **350-line margin is reactive, not proactive:** By the time a file reaches 350 lines during expansion, the outline structure is frozen. Better to project at outline phase and prevent growth, not react during expansion.

4. **Not enforced by review:** No review agent checks for Phase 1.4 compliance. `plan-reviewer` doesn't validate file growth projections.

**Evidence:** worktree-update execution:
- Phase 1.4 section exists in SKILL.md since 2026-02-12 (before worktree-update planning)
- worktree-update outline created 2026-02-12, no file growth projections present
- Phase expansion (cycles 1.1-7.13) proceeded without split points
- First refactor escalation: Cycle 4.2 (cli.py reached 477 lines, 77 over limit)
- Subsequent refactors: 7.1, 7.2, 6.1, 6.4, 5.6, 5.5, 4.3 (18 total refactor reports)

### C4: Precommit Enforcement Only

**400-line limit enforced exclusively at commit time, not during planning:**

- `scripts/check_line_limits.sh` scans `src/` and `tests/` files
- Fails precommit if any file >400 lines
- Detection is binary: pass/fail, no warnings at 350 lines
- No integration with planning artifacts (runbook doesn't check limits)

**Result:** Planning proceeds blind to limits, execution encounters hard stop, opus refactor agent escalates.

### C5: Formatter Expansion Increases Effective Growth

**Black formatter expands subprocess calls vertically, amplifying line count:**

**Before formatting (1 line):**
```python
subprocess.run(["git", "hash-object", "-w"], input=content, capture_output=True, text=True, check=True)
```

**After formatting (8 lines):**
```python
subprocess.run(
    ["git", "hash-object", "-w"],
    input=content,
    capture_output=True,
    text=True,
    check=True,
)
```

**Cycle 4.2 refactor report:** 15-line expansion across 6-8 subprocess calls due to formatter.

**Impact:** Planning must estimate post-format size, not raw line count. Current planning doesn't account for formatter expansion.

### C6: `_git()` Helper Introduced Late

**worktree-update Cycle 7.1 introduced `_git()` helper to reduce subprocess boilerplate:**

```python
def _git(*args, check=True, **kwargs) -> str:
    """Run git command and return stdout."""
    return subprocess.run(
        ["git", *args], capture_output=True, text=True, check=check, **kwargs
    ).stdout.strip()
```

**Impact:** 24 calls replaced, 477→336 lines (30% reduction).

**Timing issue:** Helper introduced at Cycle 7.1, but could have been designed into Phase 0 (setup). If included in design/outline, all phases would have used helper from start, avoiding growth.

---

## Evidence

### worktree-update Execution Timeline

| Cycle | Event | File Size | Over Limit | Action |
|-------|-------|-----------|------------|--------|
| 1.1 | Initial CLI setup | ~150 lines | - | - |
| 2.1-2.4 | Sandbox registration | ~220 lines | - | - |
| 4.2 | Section filtering | 477 lines | +77 | Refactor (deslop + arch) → 412 |
| 5.2-5.7 | `new` command updates | ~390 lines | - | - |
| 6.1 | `rm` refactor | 397 lines | - | - |
| 6.4 | Cleanup logic | 406 lines | +6 | Refactor (deslop) → 400 |
| 7.1 | Merge clean tree | 430 lines | +30 | Refactor (_git helper) → 399 |
| 7.2 | THEIRS clean tree | 448 lines | +48 | Refactor (consolidate helpers) → 430 |

**Total refactor escalations:** 7+ (18 refactor reports in `plans/worktree-update/reports/`)

**Refactor agents used:**
- Sonnet (deslop, consolidation): 5 escalations
- Opus (architectural splits): 2 escalations (Cycle 4.2, 7.2)

**Wall-clock estimate:** 1hr+ on refactor work alone (not counting planning, execution, vet)

### Design Document Review

**`plans/worktree-update/design.md` specified:**
- 8 modules/functions
- 9 commands/modes
- 37 TDD cycles planned
- No file size projection

**Outline (`runbook-outline.md`) specified:**
- 7 phases (1-7 TDD, 8-9 non-TDD)
- 37 cycles across phases
- Complexity per phase (Low/Medium/High)
- No lines-per-cycle estimate
- No cumulative file growth projection

---

## Proposed Fixes

### Fix 1: Add Growth Projection to Outline Phase (Primary)

**Location:** `agent-core/skills/runbook/SKILL.md` Phase 0.75 (outline generation)

**Add to outline structure:**

```markdown
## File Growth Projection

| File | Current Lines | Cycles Adding | Est. Lines/Cycle | Projected Total | Split Needed? |
|------|---------------|---------------|------------------|-----------------|---------------|
| cli.py | 120 | 25 | 15 | 495 | Yes (Phase 4) |
| test_cli.py | 80 | 30 | 10 | 380 | No |
```

**Calculation heuristics:**

- **Lines per cycle (TDD):** Low: 8-12, Medium: 12-18, High: 18-25
- **Lines per cycle (general):** Low: 5-10, Medium: 10-15, High: 15-20
- **Formatter overhead:** Add 20% to raw estimate for vertical expansion
- **Split threshold:** If projected total >350, insert split at phase boundary

**Process:**
1. Planner identifies files modified by runbook (from design document)
2. For each file: count cycles that add content, classify complexity
3. Estimate lines per cycle based on heuristic
4. Project cumulative growth: `current + (cycles × lines/cycle × 1.2)`
5. If projection >350: add split phase at natural boundary

**Split phase template:**

```markdown
### Phase N+1: File Split — cli.py

**Complexity:** Low (1 cycle)
**Type:** general

**Tasks:**
- Split `cli.py` into:
  - `cli.py` — CLI commands (Click wrappers)
  - `operations.py` — Core operations (wt_path, sandbox, focus)
- Update imports in tests
- Verify precommit passes
```

**When to split:**
- Phase boundary (not mid-phase) to preserve coherence
- After functional milestone (not mid-feature)
- Target: Split produces two files each <300 lines

### Fix 2: Add Growth Validation to Review Axes (Secondary)

**Location:** `agents/decisions/runbook-review.md`

**Add fifth review axis:**

```markdown
### File Growth Projection

Planning must project file size to prevent precommit failures. Every runbook adding >10 cycles to a file must include growth projection.

**Detection — projection is missing when:**
- Outline adds >10 cycles to existing file, but no growth table present
- Projection table missing "Split Needed?" column
- Projected total >350 lines with no split phase planned
- Heuristic (lines/cycle) not documented or implausible (e.g., 5 lines/cycle for High complexity)

**Action:** Add growth projection table to outline. If projection >350, insert split phase at natural boundary.

**Grounding:** Precommit enforces 400-line limit. Planning blind to limits causes execution delays and refactor escalations. Proactive projection prevents reactive refactoring.
```

**Integration with plan-reviewer:**

Update `plan-reviewer` agent prompt to check:
- Outline contains growth projection table when applicable
- Heuristics are reasonable (compare to phase complexity)
- Split phases inserted when projection exceeds 350

### Fix 3: Move File Size Awareness Earlier (Tertiary)

**Location:** `agent-core/skills/runbook/SKILL.md`

**Move Phase 1.4 content to Phase 0.75 (outline):**

Current: Phase 1.4 checks per-item growth during expansion (too late, cognitive load)

Proposed: Phase 0.75 projects holistic growth during outline creation (proactive, less cognitive load)

**Delete:** Lines 504-513 (Phase 1.4: File Size Awareness)

**Rationale:** Projection at outline phase is structural (inserts split phases), not item-level (manual tracking). Outline is reviewed by plan-reviewer before expansion begins.

### Fix 4: Prescribe Helper Pattern in Design (Optional)

**Location:** `agent-core/skills/design/SKILL.md` (if exists) or CLAUDE.md design guidance

**Pattern:** When design specifies repeated subprocess calls, recommend helper function in design phase.

**Example template:**

```markdown
## Design Patterns

**Subprocess Helpers:**

When module uses >5 subprocess calls to same command:
- Extract helper: `_git(*args, **kwargs) -> str`
- Single invocation point reduces formatter expansion
- 30% line count reduction observed (worktree-update Cycle 7.1)
```

**Rationale:** Helper pattern is deterministic (not cognitive), should be design-time decision, not execution-time discovery.

---

## Trade-off Analysis

### Planning-Time Projection (Fix 1) vs Execution-Time Splits (Current Phase 1.4)

| Approach | When | Granularity | Cognitive Load | Split Quality |
|----------|------|-------------|----------------|---------------|
| **Execution-time** (current) | Phase 1 expansion | Per-item | High (manual tracking) | Reactive (mid-phase) |
| **Planning-time** (Fix 1) | Phase 0.75 outline | Per-phase | Medium (heuristic lookup) | Proactive (phase boundary) |

**Fix 1 advantages:**
- Splits at natural boundaries (phase transitions, not mid-phase)
- Reviewed by plan-reviewer before expansion starts
- Heuristic-based (no per-item tracking)
- Prevents growth instead of reacting to it

**Fix 1 disadvantages:**
- Requires heuristics (lines/cycle estimates)
- Heuristics may be inaccurate (first iteration needs tuning)
- Adds planning overhead (growth table creation)

### Validation at Review (Fix 2) vs Validation at Commit (Current)

| Approach | When | Failure Mode | Recovery Cost |
|----------|------|--------------|---------------|
| **Commit-time** (current) | After execution | Precommit fails | High (refactor escalation, opus tier) |
| **Review-time** (Fix 2) | After outline | Plan-reviewer flags | Low (revise outline, re-review) |

**Fix 2 advantages:**
- Catches growth issues before execution starts
- Recovery is cheap (revise outline, not code)
- Plan-reviewer already runs in pipeline

**Fix 2 disadvantages:**
- Adds review axis (complexity for plan-reviewer)
- Heuristic validation (not exact measurement)

---

## Scope Assessment

### Files Requiring Changes

**Primary implementation (Fix 1):**
- `agent-core/skills/runbook/SKILL.md` (Phase 0.75 section)
  - Add growth projection table to outline structure
  - Document heuristics (lines/cycle by complexity)
  - Add split phase insertion logic
  - Estimated: 30-40 lines added

**Secondary validation (Fix 2):**
- `agents/decisions/runbook-review.md` (new axis)
  - Add "File Growth Projection" axis with detection criteria
  - Estimated: 20-30 lines added
- `agent-core/agents/plan-reviewer.md` (prompt update)
  - Include growth validation in review checklist
  - Estimated: 10 lines added

**Tertiary cleanup (Fix 3):**
- `agent-core/skills/runbook/SKILL.md` (delete Phase 1.4)
  - Remove lines 504-513
  - Update references to file size awareness
  - Estimated: 10 lines removed, 5 lines updated

**Optional pattern guidance (Fix 4):**
- Design guidance document (location TBD)
  - Add subprocess helper pattern
  - Estimated: 15-20 lines added

### Estimated Complexity

**Fix 1 (Growth Projection):** Tier 1 - Direct implementation
- Prose artifact (outline table structure)
- Heuristic definition (straightforward)
- No code changes, no tests
- Estimated: 1-2 hours

**Fix 2 (Review Validation):** Tier 1 - Direct implementation
- Prose artifact (review axis definition)
- Agent prompt update (straightforward)
- No code changes, no tests
- Estimated: 1 hour

**Fix 3 (Cleanup):** Tier 1 - Direct implementation
- Delete obsolete section
- Update references
- Estimated: 30 minutes

**Fix 4 (Pattern Guidance):** Tier 1 - Direct implementation
- Prose artifact (pattern description)
- Estimated: 30 minutes

**Total estimated effort:** 3-4 hours for all fixes

### Validation Approach

**Empirical calibration (Fix 1 heuristics):**
- Backtest heuristics against worktree-update execution
- Measure actual lines/cycle by complexity tier
- Adjust heuristics if error >20%

**Regression test (Fix 2):**
- Test plan-reviewer on worktree-update outline
- Verify detection of missing growth projection
- Verify split phase recommendation when projection >350

**Next runbook validation:**
- Apply Fix 1+2 to next TDD runbook
- Measure: Did projection prevent refactor escalations?
- Measure: How accurate were heuristics? (projected vs actual)

---

## Conclusion

**Root cause:** Planning pipeline lacks file growth projection at outline phase. The 400-line limit is enforced at commit (reactive) but not projected during planning (proactive).

**Primary fix:** Add growth projection table to outline phase (Phase 0.75) with heuristics for lines-per-cycle. Insert split phases when projection exceeds 350 lines.

**Impact:** Prevents refactor escalations (7+ observed), reduces wall-clock time (1hr+ observed), lowers opus usage (architectural refactors avoided).

**Complexity:** Low - prose artifacts, heuristic definition, no code changes. Estimated 3-4 hours total for all fixes.

**Next step:** Implement Fix 1 (growth projection) in runbook skill, validate with next TDD runbook.
