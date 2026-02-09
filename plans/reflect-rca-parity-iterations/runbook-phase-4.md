# Phase 4: Memory Index Update

**Scope:** 1 step, ~15 lines added, single session
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
- All 6 coverage items have entries (defense-in-depth, conformance precision, WIP-only, file size awareness, vet alignment, audit decision)
- Phase 4 changes committed

**Runbook Complete:** All 4 phases finished, all 11 steps executed, all 8 design decisions implemented, memory index updated.

**Next:** No further phases. Runbook execution complete.
