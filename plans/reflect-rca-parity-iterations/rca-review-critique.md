# Critical Review: rca-review.md

**Subject:** `plans/reflect-rca-parity-iterations/rca-review.md`
**Reviewed against:** Original RCA (`rca.md`), D+B outline (`plans/reflect-rca-prose-gates/outline.md`), implemented skills (commit SKILL.md, orchestrate SKILL.md), learnings.md

---

## 1. Gap 3 Assessment: Overclaims Closure

The review declares Gap 3 "CLOSED" (line 14). This is too strong. The D+B fix addresses the *structural* cause of prose gate skipping (steps without tool calls get scanned past), but the fix's own design documents acknowledge residual risk.

**Evidence the review omits:**

- `outline.md` (the D+B fix itself) inherits Option B's risk assessment from `design.md:127-132`: "the agent could still skip the gate paragraphs and jump to the bash block within the step." The D+B hybrid merges gates INTO action steps rather than keeping them separate, which reduces but does not eliminate this. The gate evaluation paragraphs between `Read agents/session.md` and `just precommit` in commit SKILL.md (lines 90-106) are still prose judgment that can be scanned past after the Read completes.
- The outline explicitly states "No changes to other skills" (line 107). The convention ("every step must open with a tool call") applies only going forward. Existing skills beyond commit and orchestrate were not audited or retrofitted. The review treats the fix as closing the *general* prose gate problem, but it only addresses two specific skill files.
- The convention is enforced by an HTML comment (SKILL.md line 86-88, orchestrate SKILL.md line 94-95) -- itself a form of prose guidance that could be ignored during future skill authoring. The outline acknowledged the need for a lint script as "the real long-term solution" (outline.md:87) but that was explicitly out of scope.

**Correct assessment:** Gap 3 is *substantially mitigated* for the two modified skills, not closed. The structural pattern is addressed, but no enforcement mechanism prevents recurrence in new or unmodified skills. The review should distinguish between "root cause addressed in known instances" and "class of failure eliminated."

## 2. Gap 5 Assessment: Under-examines the Mechanism

The review says the D+B fix makes full precommit "the anchored default path" and `--test` "requires explicit agent choice to deviate" (line 33). This needs scrutiny.

**What the implemented commit skill actually shows:**

Looking at SKILL.md line 25-27, the `--test` flag is a first-class documented option with its own section in the Flags block. Line 133 shows `just precommit` with an inline comment `# or: just test (--test) / just lint (--lint)`. The `--test` path is embedded *inside* the anchored step, not outside it. An agent following the merged Step 1 can legitimately choose `--test` mode by reading the flag documentation at the top of the skill.

The review's claim that deviation "requires explicit agent choice" (line 33) is technically true but misleading. The flag is prominently documented, has a dedicated usage example (line 35: `/commit --test`), and has a named workflow pattern (lines 38-40: "TDD workflow pattern"). The anchoring of `just precommit` as the default does nothing to prevent an agent from applying the `--test` flag when it judges the commit to be test-only work -- which is exactly the scenario the RCA identified (rca.md:101, 105).

**Correct assessment:** The D+B fix has near-zero effect on Gap 5. The `--test` bypass is a feature-level decision, not a prose-gate-skipping problem. The agent choosing `--test` is executing the skill correctly, just with a flag that happens to skip line limits. The mitigation claim should be "negligible" not "partial."

## 3. "Unchanged" Classifications: Missing Indirect Effects

The review asserts Gaps 1, 2, and 4 are "UNCHANGED" by the D+B fix. This is mostly accurate but misses a subtle interaction with Gap 2.

**Gap 2 interaction with D+B:** The RCA says the precommit check at commit time catches file size violations but "doesn't prevent the write-then-split rework loop" (review line 49). The review correctly identifies this. However, the D+B fix *does* make it more likely that `just precommit` actually runs (which was the specific failure in iteration 3 -- rca.md:98-106). Before the D+B fix, precommit might not run at all, meaning the file size violation would not be caught even at commit time. After the fix, precommit reliably runs, so file size violations are caught sooner (at commit time rather than next session).

This is not "unchanged" -- it is the same relationship as Gap 5. The D+B fix does not prevent oversized files from being written, but it does ensure the commit-time safety net fires. The review correctly identifies this logic for Gap 5 (line 33: "probability of accidental bypass is reduced") but fails to apply the same reasoning to Gap 2. Gap 2 should also be "partially mitigated" -- not for file-size awareness during writing, but for ensuring the commit-time check actually executes.

## 4. Staleness Assessment: Incomplete

The review identifies two stale passages (lines 63-65):
- Line 145: "No fix implemented yet"
- Line 189: "remains at `requirements` status"

**Additional stale passages missed:**

- rca.md line 143: "identifies the root cause of why precommit might not have been run, but the fix directions are 'not yet implemented.'" -- The fix directions HAVE been implemented. The entire Fix 3 section (lines 139-145) reads as if the prose gates plan is still at requirements stage.
- rca.md line 253-265 (Additional Context section): "The parity test work did NOT happen against a stable pipeline" and "Were they interleaved?" This section poses an open question about concurrent workflow evolution that was never resolved. The review does not flag this as stale, but it is an unresolved question from the RCA that should be either answered or marked as no longer relevant. The D+B fix is itself evidence of continued pipeline evolution.
- rca.md line 103-105: "The session handoff at aca8371 does not mention running `just precommit`... The pattern likely extended to precommit execution." The word "likely" marks speculation. The D+B fix's own rca.md (`plans/reflect-rca-prose-gates/rca.md`) provides stronger evidence -- the prose gates RCA confirms the structural mechanism. This doesn't make the passage factually wrong, but the hedging is now unnecessary given the confirmed diagnosis.

## 5. Net Assessment: Glosses Over Ranking Stability

The review claims "The RCA's root cause ranking (rca.md:243-248) remains valid" (line 69) and reproduces the ranking with minor edits. This deserves more scrutiny.

**Problem 1: The ranking conflates root causes with gaps.** The original RCA lists 5 root causes (RC1-RC5) in lines 78-118 and 5 gaps in lines 162-209. These are different taxonomies -- root causes explain WHY iterations happened; gaps describe WHAT is still missing. The review's "Net Assessment" mixes them: it lists "No conformance validation" (Gap 1 / RC1), "Prose gate skipping" (Gap 3 / RC3), "Test description imprecision" (Gap 4 / RC5ish), and "No file size awareness" (Gap 2 / RC4). But RC2 (Vet Agent Scope Limitation) and RC5 (False "Visual Parity Validated" Claim) are dropped from the ranking without explanation. RC5 is particularly relevant -- it describes a systemic issue where agents make unverified claims about completion, which the D+B fix does not address.

**Problem 2: Iteration attribution is simplistic.** The review assigns iterations to single root causes (e.g., "conformance validation -- Caused iterations 0-2"). But the original RCA shows iterations had multiple contributing causes. Iteration 1 was caused by RC1 (no conformance check), RC2 (vet scope too narrow), RC5 (false completion claim), AND RC4/Gap 4 (imprecise test descriptions). Attributing it to a single root cause obscures interaction effects.

## 6. Missing Interaction Effects Between Gaps

The review analyzes each gap in isolation. It does not consider how gaps compound.

**Gap 1 + Gap 4 interaction:** Conformance validation (Gap 1) would only be as good as its specification. If test descriptions are imprecise (Gap 4), a conformance checkpoint using those descriptions would produce false positives. The review recommends addressing Gap 1 and Gap 4 as the "highest-impact remaining work" (line 76) but does not note that Gap 4 must be resolved before Gap 1 can be effective for conformance-type work.

**Gap 3 + Gap 5 interaction:** The review treats these as independent, but they share a failure mode. An agent that has internalized the D+B fix for prose gates could still bypass precommit by using `--test` mode (Gap 5). The prose gate fix ensures precommit *appears in the execution path*, but the `--test` flag provides a legitimate within-path way to skip line limits. Together, they form a defense-in-depth gap: the outer defense (prose gate) is fixed, but the inner bypass (flag) remains.

## 7. Missing Risk: Convention Without Enforcement

The review does not flag the most significant risk of the D+B fix: the convention ("every step must open with a tool call") is documented but unenforced.

**Current state of enforcement:**
- HTML comments in two skill files (commit SKILL.md:86-88, orchestrate SKILL.md:94-95)
- A learnings.md entry ("Prose gate D+B hybrid fix")
- An implementation-notes.md entry

**What is missing:**
- No lint script validates the convention (outline.md:87 explicitly defers this)
- No pre-commit hook checks for prose-only skill steps
- No agent-creator or vet-fix-agent instruction to verify tool-call-first convention in new skills
- No inventory of existing skills that may violate the convention

The review should have flagged this as a regression risk. The D+B fix is a structural improvement, but without automated enforcement, the next skill author can reintroduce prose-only gates. This is analogous to the "hard limits vs soft limits" learning in learnings.md -- conventions without enforcement normalize deviance.

## 8. Missing Risk: D+B Fix Has Not Been Empirically Validated

The review takes the D+B fix at face value based on its design. But nowhere does it ask: **has the fix been tested in a real execution?** The prose gates problem was discovered through actual execution failures (3 recurrences per rca.md). The fix has been implemented, but there is no evidence cited that a commit skill execution post-fix actually performed Gates A and B before running precommit, or that an orchestrate execution actually detected a phase boundary via the Read anchor.

The original RCA was empirical (grounded in specific commits, specific sessions, specific failures). The review of the fix is theoretical (based on design documents, not execution evidence). This asymmetry should be noted.

## 9. Minor Issues

- Line 21 cites "outline.md:9-44" but the outline does not have that many content lines before Change 2 starts at line 45. The specific line range for Change 1 content is approximately lines 9-43. Minor, but indicates the review may have been composed from memory rather than verified against the source.
- The review does not mention `design.md` at all. The outline explicitly states it "Refines original design.md based on critical analysis. Replaces Option D with D+B hybrid" (outline.md:3). The design.md contains the trade-off analysis and risk assessments for all four options. The review evaluating the fix without referencing the design's own risk analysis is a gap.
- The "Highest-impact remaining work" statement (line 76) names Gap 1 and Gap 4 but not Gap 2. Given that Gap 2 contributed to 2 iterations (3-4) while Gap 4 contributed to 1 iteration (iteration 1 survivors), the prioritization of Gap 4 over Gap 2 is not justified by the RCA's own evidence.

## Summary Verdict

The review is competent as a status update but weak as an analytical assessment. Its primary failures:

1. **Overclaims Gap 3 closure** -- the fix addresses the known instances but does not eliminate the class of failure
2. **Overclaims Gap 5 mitigation** -- the `--test` bypass is a feature, not a prose gate; the D+B fix has negligible effect on it
3. **Inconsistent treatment of Gap 2** -- applies "partial mitigation" logic to Gap 5 but not Gap 2, despite identical mechanism
4. **No interaction analysis** -- gaps are reviewed in isolation; compounding effects are missed
5. **Misses the enforcement gap** -- convention without enforcement is the most likely regression vector
6. **No empirical validation** -- evaluates the fix from design documents without asking whether it has been tested in practice
