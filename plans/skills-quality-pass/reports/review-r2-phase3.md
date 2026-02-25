# Phase 3 Review: C/C+ Grade Skills Body Surgery

**Reviewer:** Convergence review (R2)
**Scope:** 5 skills with major body surgery + extraction to references/
**Date:** 2026-02-25

## Summary

**Overall Assessment:** Ready with minor issues

All 5 skills achieved compression targets. NFR-5 extraction completeness is satisfied for all NEW references/ files (Phase 3 deliverables). D+B gate anchoring in design skill is correct and safe. Two description format violations (NFR-6) found in orchestrate and review skills. Three pre-existing runbook references lack body load points (pre-Phase 3, not blocking).

**Issue counts:** 0 critical, 2 major, 3 minor

---

## Per-Skill Analysis

### 1. design/SKILL.md (338 lines, target ~371)

**FRs addressed:** FR-1 (description), FR-2 (preamble removed), FR-3 (3 extractions), FR-5 (gates 1-3, 12)

**NFR-5 extraction completeness:**
| References file | Lines | Body load point | Trigger condition |
|---|---|---|---|
| `research-protocol.md` | 35 | Line 172 | "When external research needed" |
| `discussion-protocol.md` | 20 | Line 227 | Phase B entry |
| `design-content-rules.md` | 140 | Line 278 | C.1 "Content rules:" |

All 3 new references files have trigger + Read instruction. PASS.

**NFR-6 (description format):** "This skill should be used when the user invokes /design..." PASS.

**NFR-7 (D+B gate safety):**
- Gate 1 (Post-Outline Re-check, line 184): `Read plans/<job>/outline.md` provides data for existing downgrade criteria. No new criteria introduced. PASS.
- Gate 2 (Outline Sufficiency, line 231): `Read plans/<job>/outline.md` provides data for existing sufficiency criteria. PASS.
- Gate 3 (C.5 Execution Readiness, line 319): `Read plans/<job>/design.md` provides data for existing direct-execution criteria. PASS.
- Gate 12 (Classification, lines 46-48 + 72): `when-resolve.py` + conditional `Glob`/`Grep`. Data-only anchors. PASS.

**Content preservation:** Research protocol covers A.3-5 with Context7, web research, grounding, outline production. Discussion protocol covers Phase B iteration. Design content rules cover all specified sub-topics (density checkpoint, agent-name validation, classification tables, structure, requirements format, TDD additions, references section, documentation perimeter, skill-loading, execution model). PASS.

**Progressive disclosure:** Body retains triage, routing, outline review, sufficiency gates, and Phase C structure. References hold detail (research how-to, discussion iteration, content rules). The split correctly keeps decision-making in body and detail in references. PASS.

**Prose quality:** Direct imperatives throughout. No hedging, preamble, second-person, or sycophantic patterns. PASS.

---

### 2. runbook/SKILL.md (442 lines, target ~677)

**FRs addressed:** FR-1 (description), FR-2 (preamble removed), FR-3 (3 new extractions)

**NFR-5 extraction completeness (new files):**
| References file | Lines | Body load point | Trigger condition |
|---|---|---|---|
| `tier3-planning-process.md` | 459 | Line 182 | "Full process detail:" in Planning Process section |
| `tdd-cycle-planning.md` | 91 | Line 198 | "When expanding TDD phases in Phase 1" |
| `conformance-validation.md` | 12 | Line 200 | "When design includes external references" |

All 3 new references files have trigger + Read instruction. PASS.

**NFR-5 (pre-existing files):**
| References file | Lines | Body load point | Trigger condition |
|---|---|---|---|
| `patterns.md` | 151 | Line 336 | "Detailed guidance:" in Cycle/Step Ordering |
| `general-patterns.md` | 128 | Line 336 | Same trigger |
| `error-handling.md` | 124 | Line 439 only (References section) | None in body |
| `anti-patterns.md` | 38 | Line 438 only (References section) | None in body |
| `examples.md` | 344 | Line 440 only (References section) | None in body |

3 pre-existing files (`error-handling.md`, `anti-patterns.md`, `examples.md`) lack body load points with trigger conditions. They appear only in the terminal References section. An agent executing this skill has no conditional trigger telling it WHEN to load these files. (See Minor issue 1.)

**NFR-6 (description format):** "This skill should be used when the user invokes /runbook..." PASS.

**Content preservation:** Tier 3 planning process covers Phases 0.5-3.5 with full detail (discovery, outline generation, consolidation gates, simplification, complexity check, sufficiency check with lightweight orchestration exit, phase expansion, assembly, holistic review, pre-execution validation). TDD cycle planning covers numbering, RED/GREEN specs, assertion quality, investigation prerequisites, dependencies, stop conditions. Conformance validation covers trigger, requirement, precision. PASS.

**Progressive disclosure:** Body retains tier assessment, tier 1-2 execution, planning process overview, Phase 4 (prepare artifacts), checkpoints, testing strategy, cycle/step ordering, common pitfalls, template structure. References hold deep detail (tier 3 phases, TDD cycle specs, conformance). Split correctly keeps routing and overview in body, expansion detail in references. PASS.

**Prose quality:** Direct imperatives. No hedging or preamble. PASS.

---

### 3. token-efficient-bash/SKILL.md (203 lines, target ~323)

**FRs addressed:** FR-1 (description), FR-3 (3 extractions), FR-8 (redundant content removed), FR-9 (tail sections removed)

**NFR-5 extraction completeness:**
| References file | Lines | Body load point | Trigger condition |
|---|---|---|---|
| `examples.md` | 94 | Line 199 | "Worked examples:" |
| `directory-changes.md` | 43 | Line 201 | "Directory changes:" |
| `anti-patterns.md` | 40 | Line 203 | "Anti-patterns:" |

All 3 new references files have trigger + Read instruction. PASS.

**NFR-6 (description format):** "This skill should be used when writing bash scripts with 3+ sequential commands." PASS.

**Content preservation:** Examples file has 3 worked examples (file operations, git workflow, setup with expected failures) with output. Anti-patterns file has 3 patterns (redundant error handling, single command overhead, blanket suppression). Directory changes file has trap and subshell approaches. PASS.

**Progressive disclosure:** Body retains the pattern itself, flag explanations, when-to-use guidance, strict mode caveats with code examples. References hold worked examples, anti-patterns, and directory-change details. The body provides enough to apply the pattern; references provide depth and worked demonstrations. PASS.

**FR-8 (redundant content):** No error-handling fragment duplication detected. PASS.
**FR-9 (tail sections):** No "Summary"/"Token Economy Before/After" tail sections present. PASS.

**Prose quality:** Direct. No hedging, preamble, or sycophantic patterns. PASS.

---

### 4. orchestrate/SKILL.md (300 lines, target ~391)

**FRs addressed:** FR-2 (preamble removed), FR-3 (3 extractions), FR-6 (paths), FR-8 (escalation), FR-9 (tail removed)

**NFR-5 extraction completeness:**
| References file | Lines | Body load point | Trigger condition |
|---|---|---|---|
| `common-scenarios.md` | 29 | Line 288 | "For scenario handling" |
| `continuation.md` | 41 | Line 294 | "Full protocol and examples:" |
| `progress-tracking.md` | 40 | Line 245 | "Detailed tracking:" |

All 3 new references files have trigger + Read instruction. PASS.

**NFR-6 (description format):** `description: Execute prepared runbooks with weak orchestrator pattern` — does NOT use "This skill should be used when..." format. **MAJOR issue.** (See Major issue 1.)

**FR-6 (relative paths):** References section (lines 298-301) uses relative paths: `plans/unification/orchestrator-plan.md`, `.claude/agents/unification-task.md`, `plans/unification/steps/step-2-*.md`. No absolute paths detected. PASS.

**Content preservation:** Common scenarios covers 5 scenarios (unexpected results, missing reports, repeated failures, agent hangs, resume after context ceiling). Continuation covers consumption protocol with 3 examples and constraint. Progress tracking covers simple and detailed approaches with file format. PASS.

**Progressive disclosure:** Body retains verification, orchestrator plan reading, step execution (inline + agent delegation), post-step verification, phase boundary checks, checkpoint delegation, error escalation, completion workflow, weak orchestrator pattern statement, constraints. References hold scenario details, continuation protocol, and progress file format. PASS.

**Prose quality:** Direct imperatives throughout. No hedging or sycophantic patterns. PASS.

---

### 5. review/SKILL.md (204 lines, target ~244)

**FRs addressed:** FR-2 (preamble removed), FR-3 (3 extractions), FR-9 (security redundancy removed)

**NFR-5 extraction completeness:**
| References file | Lines | Body load point | Trigger condition |
|---|---|---|---|
| `review-axes.md` | 65 | Line 68 | "Review axes:" in step 3 |
| `common-scenarios.md` | 27 | Line 178 | "Common scenarios:" |
| `example-execution.md` | 52 | Line 176 | "Example execution:" |

All 3 new references files have trigger + Read instruction. PASS.

**NFR-6 (description format):** `description: Review in-progress changes for quality and correctness` — does NOT use "This skill should be used when..." format. **MAJOR issue.** (See Major issue 2.)

**Content preservation:** Review axes has full 10-category checklist (code quality, design conformity, functional completeness, project standards, runbook file refs, self-referential modification, security, testing, documentation, completeness). Common scenarios covers 5 patterns (secrets, multi-concern, pattern violations, already-committed, large changesets). Example execution shows complete interaction flow. PASS.

**Progressive disclosure:** Body retains process structure (scope determination, change gathering, analysis routing, feedback template, output location), constraints, workflow integration, delegation context. References hold detailed checklists, scenarios, and examples. The split correctly keeps decision-making flow in body and reference material in references. PASS.

**Prose quality:** Direct. No hedging, preamble, or sycophantic patterns. PASS.

---

## Issues

### Major

**1. orchestrate/SKILL.md NFR-6 violation — description format**
- Location: `agent-core/skills/orchestrate/SKILL.md:3`
- Current: `description: Execute prepared runbooks with weak orchestrator pattern`
- Required: Must use "This skill should be used when..." format per platform requirement
- Fix: `description: This skill should be used when executing prepared runbooks via weak orchestrator pattern, after /runbook has generated execution artifacts with prepare-runbook.py.`

**2. review/SKILL.md NFR-6 violation — description format**
- Location: `agent-core/skills/review/SKILL.md:3`
- Current: `description: Review in-progress changes for quality and correctness`
- Required: Must use "This skill should be used when..." format per platform requirement
- Fix: `description: This skill should be used when the user requests review of in-progress changes, uncommitted work, recent commits, or branch changes for quality and correctness.`

### Minor

**1. runbook/SKILL.md — 3 pre-existing references lack body load points**
- Files: `references/error-handling.md` (124 lines), `references/anti-patterns.md` (38 lines), `references/examples.md` (344 lines)
- These appear only in the terminal References section (lines 438-440) with no conditional trigger + Read instruction in the body
- An agent has no guidance on WHEN to load these files during execution
- Not a Phase 3 regression (pre-existing), but an NFR-5 gap that was not addressed
- Suggested fix: Add body load points, e.g.: in Common Pitfalls section "Anti-patterns: Read `references/anti-patterns.md` for common mistakes with corrections"; near error tables "Error catalog: Read `references/error-handling.md` for input validation, cycle generation, and integration error handling with recovery protocols"; near examples "Runbook examples: Read `references/examples.md` for complete TDD and general step examples"

**2. review/SKILL.md — "Integration with General Workflow" section restates pipeline position**
- Location: Lines 180-193
- The workflow stages list (lines 188-194) restates the design->runbook->orchestrate->corrector->commit pipeline which is documented in `pipeline-contracts.md`
- Low severity: the section also contains the useful corrector delegation note, so removal is not clean

**3. orchestrate/SKILL.md — checkpoint template recall path uses different tool than skill body**
- Location: Line 161
- Checkpoint delegation template references `agent-core/bin/recall-resolve.sh` (shell wrapper)
- Other skills and the runbook skill body reference `agent-core/bin/when-resolve.py` (Python resolver)
- Both files exist on disk; `recall-resolve.sh` likely wraps `when-resolve.py`
- Inconsistency is cosmetic — agents that know one tool name may not recognize the other

---

## Compression Summary

| Skill | Pre-surgery | Post-surgery | Target | Delta vs target |
|---|---|---|---|---|
| design | 521 | 338 | ~371 | -33 (exceeded) |
| runbook | 1027 | 442 | ~677 | -235 (exceeded) |
| token-efficient-bash | 523 | 203 | ~323 | -120 (exceeded) |
| orchestrate | 521 | 300 | ~391 | -91 (exceeded) |
| review | 384 | 204 | ~244 | -40 (exceeded) |
| **Total** | **2976** | **1487** | **~2006** | **-519 (exceeded)** |

All skills exceeded compression targets. Total body reduction: 1489 lines (50%), with 1973 lines moved to references/. Net corpus change: +484 lines, but only ~1487 lines load by default (body only).

---

## Verdict

2 major NFR-6 description format violations in orchestrate and review require fixes. 3 minor issues are non-blocking. All other review axes (NFR-5 new extractions, NFR-7 gate safety, content preservation, load point quality, progressive disclosure, prose quality, FR-6 relative paths) pass.
