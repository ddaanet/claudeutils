# RCA Review: Impact of D+B Hybrid Fix on Parity Failure Gaps

**Reviewed:** `plans/reflect-rca-parity-iterations/rca.md`
**In light of:** `plans/reflect-rca-prose-gates/outline.md` (D+B hybrid, now complete per `agents/jobs.md`)

---

## Context

The RCA (`rca.md`) identified 5 root causes and 5 remaining gaps from the statusline-parity execution, which required 4 iterations across 3 sessions despite exact specifications. The prose gates fix (`reflect-rca-prose-gates`) has since been implemented. This review assesses how the fix changes the gap landscape.

## Gap Status After D+B Hybrid

### Gap 3: Prose Gates — CLOSED

**RCA claim (now stale):** "The `reflect-rca-prose-gates` plan remains at `requirements` status" (rca.md:189). Fix 3 section states "No fix implemented yet" (rca.md:145).

**Current state:** Plan is `complete` in `agents/jobs.md`. The D+B hybrid was implemented per `plans/reflect-rca-prose-gates/outline.md`.

**What was fixed:**
- Commit skill: Steps 0 + 0b + 1 merged into single Step 1 (outline.md:9-44). Gate A anchored with `Read agents/session.md`, Gate B with `git diff`/`git status` Bash calls. `just precommit` is in the same step body with no step boundary to skip.
- Orchestrate skill: 3.4 merged into 3.3 with `Read` anchor for phase boundary detection (outline.md:45-72).
- Convention: Every skill step must open with a tool call (outline.md:74-87).

**RC3 mitigation:** The precommit-not-run root cause (rca.md:98-106) is directly addressed. The merged step structure eliminates the prose-only gate that execution-mode cognition optimized past.

**Evidence from learnings:** `agents/learnings.md` contains "Prose gate D+B hybrid fix" entry documenting the pattern.

### Gap 5: `--test` Commit Mode — PARTIALLY MITIGATED

**RCA recommendation:** Three options — remove `--test` mode, add line-limits to `just test`, or restrict `--test` to WIP commits (rca.md:203-209).

**D+B effect:** Full precommit is now the anchored default path in the merged Step 1. The `--test` escape hatch still exists but requires explicit agent choice to deviate from the anchored flow. The probability of accidental bypass is reduced but not eliminated.

**Remaining risk:** An agent classifying a commit as "test-only work" could still invoke `--test` mode, skipping `check_line_limits.sh`.

### Gap 1: No Conformance Validation — UNCHANGED

**RCA description:** The orchestration pipeline validates at unit test and code quality levels but has no mechanism to validate conformance against an external reference (rca.md:163-176).

**Why D+B doesn't help:** The prose gates fix addresses *execution of existing checks*, not *addition of new validation dimensions*. Conformance validation requires a new step type in the orchestration pipeline — comparing actual output to external reference. This is orthogonal to whether existing gates are skipped.

**Impact:** This was the primary driver of iterations 0-2 (rca.md:243-244). The RCA ranks it #1 by impact.

### Gap 2: No Pre-Write File Size Check — UNCHANGED

**RCA description:** No mechanism to warn about file size during writing; constraint only checked at commit time (rca.md:178-184).

**Why D+B doesn't help:** File size awareness is a planning/tooling concern. The D+B fix ensures precommit *runs* (catching violations at commit time), but doesn't prevent the write-then-split rework loop.

**Impact:** Contributed to iterations 3-4 (rca.md:244). Lower priority — the RCA recommends planning-time awareness as the higher-leverage fix.

### Gap 4: Test Description Imprecision — UNCHANGED

**RCA description:** Prose test descriptions introduce translation loss for conformance work where specifications are exact (rca.md:193-199).

**Why D+B doesn't help:** This is a runbook authoring quality concern. The D+B fix improves execution of existing steps, not the precision of step specifications.

**Impact:** Enabled iteration 1's 8 issues to survive TDD cycles (rca.md:244). The RCA recommends exact expected strings in test descriptions for conformance-type work.

## RCA Staleness

Two passages in `rca.md` are now factually incorrect:
- Line 145: "No fix implemented yet" → D+B hybrid implemented and complete
- Line 189: "remains at `requirements` status" → plan status is `complete`

## Net Assessment

The D+B hybrid closes **1 of 5 gaps** fully (Gap 3) and partially mitigates another (Gap 5). The RCA's root cause ranking (rca.md:243-248) remains valid:

1. **No conformance validation** — Primary driver (iterations 0-2), unchanged
2. **Prose gate skipping** — Secondary driver (iteration 3), now fixed
3. **Test description imprecision** — Enabler (iteration 1 survivors), unchanged
4. **No file size awareness** — Contributor (iterations 3-4), unchanged

The highest-impact remaining work is Gap 1 (conformance validation in orchestration) and Gap 4 (specification precision for conformance work). These require design decisions about how the orchestration pipeline handles plans with external references.
