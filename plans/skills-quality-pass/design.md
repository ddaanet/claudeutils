# Skills Quality Pass — Design

## Problem

30 skills (7,182 lines total) and 13 agent files have accumulated prose quality issues and structural anti-patterns. Two workstreams:

1. **Prose deslop:** Hedging, preamble, second-person, narrative examples, redundant framing, redundant always-loaded content, tail section overhead, conditional path bloat
2. **D+B gate anchoring:** 12 prose-only judgment gates lacking tool-call anchors

**Compression methodology:** Segment → Attribute → Compress framework from `plans/reports/skill-optimization-grounding.md`. Estimated ~1,770 lines removable (25% of corpus).

## Requirements

**Functional:**
- FR-1: Tighten description frontmatter across 18 skills (improve wording within platform-required "This skill should be used when..." format — tighter triggers, less verbose)
- FR-2: Remove/fold "When to Use" preamble sections (13 skills)
- FR-3: Extract narrative content to references/ for C/C+-grade skills (runbook, orchestrate, review, token-efficient-bash, design)
- FR-4: Trim/extract for B-/B skills needing surgery (reflect, shelve, plugin-dev-validation, review-plan)
- FR-5: Anchor 12 prose-only gates with tool calls per D+B pattern
- FR-6: Fix correctness issues (worktree `list_plans()` → CLI, orchestrate absolute paths, requirements stale note)
- FR-7: Add "When Refactoring Procedural Prose" decision entry to implementation-notes.md + memory-index
- FR-8: Remove redundant always-loaded content (6 skills duplicate fragments already in system prompt)
- FR-9: Remove tail section overhead (12 skills end with redundant "Additional Resources"/"Integration"/"Summary" sections)
- FR-10: Extract conditional path bloat to references/ (5 largest skills keep >30-line conditional paths in body)

**Non-functional:**
- NFR-1: Control flow correctness — every routing/branching path must produce correct behavior after restructuring
- NFR-2: User reporting correctness — user-visible output (classification blocks, status messages, routing decisions) must emit correctly on every path
- NFR-3: Opus model for all prose edits to skills/agents/fragments (per pipeline-contracts.md)
- NFR-4: Bootstrapping order — fix tools used in the fix process first (corrector agents → skills that delegate to them)
- NFR-5: Extraction completeness — every content block moved to references/ must leave a trigger + Read instruction in main body
- NFR-6: Description format preservation — description rewrites must stay within platform-required "This skill should be used when..." format (per plugin-dev:skill-development)
- NFR-7: D+B gate safety — added tool calls must not change decision outcomes on existing paths

**Out of scope:**
- Creating an optimize-skill skill (discussed, decided against — low recurrence frequency)
- Runbook/design skill progressive disclosure optimization (next session topic)
- Full recall-gate inventory D+B fixes beyond the 12 identified (recall-specific gates already have tool-required enforcement)

## Architecture

### Workstream 1: Deslop

**Phase structure by effort level:**

**Mechanical (description + preamble):**
All 18 description fixes retain the platform-required "This skill should be used when..." format but tighten wording: remove verbose phrasing, sharpen trigger phrases, ensure third-person. Preamble removal: delete "When to Use" section, keep counter-conditions folded into description.

**Skills needing description fix:**
error-handling, gitmoji, token-efficient-bash, next, when, how, recall, ground, codify, handoff, prioritize, worktree, doc-writing, deliverable-review, memory-index, reflect, runbook, design

**Skills needing "When to Use" removal (13):**
codify, doc-writing, gitmoji, next, opus-design-question, orchestrate, reflect, release-prep, review, runbook, shelve, handoff-haiku, design

**Body surgery (C/C+ grade — extract to references/):**
- `runbook` (1027 → ~677 lines, −350): Extract Tier 3 planning phases 0.5–3.5 → `references/tier3-planning-process.md`; TDD Cycle Planning Guidance → `references/tdd-cycle-planning.md`; Conformance Validation → `references/conformance-validation.md`; unify duplicate consolidation gates (phases 0.85 and 2.5)
- `orchestrate` (521 → ~391 lines, −130): Extract "Common Scenarios" → `references/common-scenarios.md`; continuation protocol → `references/continuation.md`; condense "Weak Orchestrator Pattern" rationale; extract progress tracking detail; fix hardcoded absolute paths
- `review` (384 → ~244 lines, −140): Extract "Analyze Changes" 10-category checklist → `references/review-axes.md`; Common Scenarios → `references/common-scenarios.md`; Example Execution → `references/example-execution.md`; remove security redundancy
- `token-efficient-bash` (523 → ~323 lines, −200): Extract 3 worked examples → `references/examples.md`; anti-patterns → `references/anti-patterns.md`; directory changes → `references/directory-changes.md`; remove token economy before/after and Summary tail
- `design` (521 → ~371 lines, −150): Extract research protocol (A.3-5) → `references/research-protocol.md`; discussion protocol (B) → `references/discussion-protocol.md`; C.1 content rules → `references/design-content-rules.md`; remove A.1 clarification paragraphs; remove binding constraints + output expectations tails

**Body surgery (B-/B grade — trim/extract):**
- `review-plan` (587 → ~487 lines, −100): Extract violation/correct examples → `references/review-examples.md`; output format template → `references/report-template.md`; remove Key Principles tail
- `reflect` (304 → ~234 lines, −70): Extract "Key Design Decisions" → `references/rca-design-decisions.md`; Examples → `references/rca-examples.md`
- `requirements` (278 → ~213 lines, −65): Unify extract/elicit shared steps; remove Integration Notes tail; condense Key Principles table
- `shelve` (136 → ~81 lines, −55): Remove 40-line Example Interaction (models "I'll help you..." register); remove "When to Use" preamble; condense Critical Constraints
- `plugin-dev-validation` (528 → ~408 lines, −120): Extract Good/Bad Examples per artifact type → `references/examples-per-type.md`; remove Alignment Criteria section; remove Usage Notes tail

**Redundant always-loaded content (FR-8, 6 skills):**
- `error-handling` (20 lines): Nearly duplicates `agent-core/fragments/error-handling.md` — assess whether skill adds value beyond fragment
- `handoff-haiku`: Task metadata format restates execute-rule.md
- `commit`: Secrets rule restates always-loaded fragment
- `token-efficient-bash`: Reconciliation with error-handling fragment
- `reflect`: Integration section
- `orchestrate`: Escalation rule

**Tail section overhead (FR-9, 12 skills):**
codify, gitmoji, handoff, orchestrate, reflect, release-prep, requirements, review, token-efficient-bash, deliverable-review, ground, prioritize — remove redundant "Additional Resources"/"Integration"/"Summary"/"Key Principles" sections that restate body content or obvious workflow position

**Correctness fixes:**
- `worktree` Mode B step 1: Replace `list_plans(Path('plans'))` with `claudeutils _worktree ls`
- `orchestrate` References section: Replace absolute paths with relative
- `requirements`: Remove stale "Integration Notes" section

### Workstream 2: D+B Gate Anchoring

**12 gates, 7 files. Fix pattern:** Add a tool call (Read, Bash, Grep, Glob) that opens the judgment step, producing output the decision logic operates on.

**High priority (3 — all in design skill):**

| # | Gate | Fix |
|---|------|-----|
| 1 | Post-Outline Complexity Re-check | Add `Read plans/<job>/outline.md` before downgrade criteria |
| 2 | Outline Sufficiency Gate (Phase B exit) | Add `Read plans/<job>/outline.md` before sufficiency criteria |
| 3 | Direct Execution Criteria C.5 | Add `Read plans/<job>/design.md` before execution-readiness criteria |

**Medium priority (4):**

| # | File | Gate | Fix |
|---|------|------|-----|
| 4 | commit | Production artifact classification | Add Grep for artifact paths after git diff |
| 5 | handoff | Command derivation from plan status | Add `Bash: claudeutils _worktree ls` before derivation |
| 6 | requirements | Extract vs Elicit mode detection | Add Glob/Read of `plans/<job>/requirements.md` as primary signal |
| 7 | codify | Target file routing | Add Grep of candidate domain files before routing |

**Low priority (5):**

| # | File | Gate | Fix |
|---|------|------|-----|
| 8 | handoff | Prior handoff detection | Simplify to structural date check |
| 9 | runbook-outline-corrector | Growth projection | Add `wc -l` for target files |
| 10 | corrector | Task type validation | Add Read of input file at Step 1 |
| 11 | design-corrector | Document type validation | Add Grep for runbook markers |
| 12 | design | Classification gate (borderline) | Recall Bash partially anchors — add Glob for behavioral code check |

### Workstream 3: Doc Update

Add to `agents/decisions/implementation-notes.md`:

**"When Refactoring Procedural Prose"**
- Anti-pattern: Deslop/restructuring that merges adjacent branches or rewords conditionals without verifying each path's user-visible output
- Correct pattern: Enumerate control flow paths before editing, verify each path's output after
- Evidence: Design skill deslop combined two fast paths, regressed user-facing classification message

Add to `agents/memory-index.md`:
```
/when refactoring procedural prose | deslop restructure control flow regression user-visible output
```

## Key Design Decisions

- D-1: **No optimize-skill skill.** Low recurrence frequency; the runbook IS the procedure for batch passes. Decision entry fills the regression-prevention gap at lower cost.
- D-2: **Bootstrapping order.** Fix corrector agents (gates 9-11) before skills that delegate to them (design, commit, handoff). This ensures improved agents review improved skills.
- D-3: **Description format.** Keep platform-required "This skill should be used when..." format (enforced by plugin-dev:skill-development and skill-reviewer). Improve wording within the format: tighten trigger phrases, remove verbose preamble, ensure third-person. Do NOT replace with noun phrases — that breaks platform discovery.
- D-4: **Progressive disclosure target.** C/C+ skills should compress 25-38% via extraction to references/. A+ benchmarks: brief (42 lines), project-conventions (32 lines), how/when (49 lines each). Compression budgets per content category from grounding report (plans/reports/skill-optimization-grounding.md).
- D-5: **Control flow verification.** After restructuring any skill with conditional branches (design, commit, handoff, requirements, codify, orchestrate), enumerate all paths and verify user-visible output on each. This is a review criterion, not a separate step — the corrector receives it as context.
- D-6: **Gate fix pattern.** Add tool call that produces output → prose judgment operates on output → if/then with explicit branch targets. The tool call IS the anchor; the judgment following it is acceptable because it operates on loaded data.

## Implementation Notes

**Affected files (all workstreams combined):**

Skills (19 files):
- `agent-core/skills/commit/SKILL.md` — FR-5 (gate), FR-2 possible
- `agent-core/skills/codify/SKILL.md` — FR-1, FR-2, FR-5
- `agent-core/skills/deliverable-review/SKILL.md` — FR-1, FR-2
- `agent-core/skills/design/SKILL.md` — FR-1, FR-2, FR-5 (×3 gates)
- `agent-core/skills/doc-writing/SKILL.md` — FR-1, FR-2
- `agent-core/skills/error-handling/SKILL.md` — FR-1
- `agent-core/skills/gitmoji/SKILL.md` — FR-1, FR-2
- `agent-core/skills/ground/SKILL.md` — FR-1
- `agent-core/skills/handoff/SKILL.md` — FR-1, FR-5 (×2 gates)
- `agent-core/skills/handoff-haiku/SKILL.md` — FR-2
- `agent-core/skills/how/SKILL.md` — FR-1
- `agent-core/skills/memory-index/SKILL.md` — FR-1
- `agent-core/skills/next/SKILL.md` — FR-1, FR-2
- `agent-core/skills/orchestrate/SKILL.md` — FR-2, FR-3, FR-6
- `agent-core/skills/plugin-dev-validation/SKILL.md` — FR-4
- `agent-core/skills/prioritize/SKILL.md` — FR-1
- `agent-core/skills/recall/SKILL.md` — FR-1
- `agent-core/skills/reflect/SKILL.md` — FR-1, FR-2, FR-4
- `agent-core/skills/release-prep/SKILL.md` — FR-2
- `agent-core/skills/requirements/SKILL.md` — FR-5, FR-6
- `agent-core/skills/review/SKILL.md` — FR-3
- `agent-core/skills/runbook/SKILL.md` — FR-1, FR-2
- `agent-core/skills/shelve/SKILL.md` — FR-2, FR-4
- `agent-core/skills/token-efficient-bash/SKILL.md` — FR-1, FR-3
- `agent-core/skills/when/SKILL.md` — FR-1
- `agent-core/skills/worktree/SKILL.md` — FR-1, FR-6

Agents (3 files):
- `agent-core/agents/corrector.md` — FR-5
- `agent-core/agents/design-corrector.md` — FR-5
- `agent-core/agents/runbook-outline-corrector.md` — FR-5

Decision files (2 files):
- `agents/decisions/implementation-notes.md` — FR-7
- `agents/memory-index.md` — FR-7

**Testing strategy:** `just precommit` after each phase. No behavioral code → no unit tests. Control flow verification via manual path enumeration for skills with conditional branches.

**Phase typing guidance:**
- FR-1 + FR-2 (description + preamble): general — mechanical edits, high file count
- FR-3 + FR-4 (body surgery): general — progressive disclosure restructuring
- FR-5 (D+B anchoring): general — structural edits to procedural steps
- FR-6 (correctness): general — targeted fixes
- FR-7 (doc update): inline — two-file additive edit
- FR-8 + FR-9 (redundant content + tail sections): general — can batch with FR-3/FR-4 per-skill
- FR-10 (conditional path extraction): general — overlaps with FR-3 body surgery

## Documentation Perimeter

**Required reading (planner must load before starting):**
- `plans/skills-quality-pass/reports/skill-inventory.md` — per-skill grades, specific issues, quoted examples
- `plans/skills-quality-pass/reports/full-gate-audit.md` — 12 gates with fix directions
- `agents/decisions/implementation-notes.md` — D+B pattern definition, skill placement rules
- `agents/decisions/pipeline-contracts.md` — prose artifact model selection (opus)
- `agent-core/skills/project-conventions/SKILL.md` — deslop rules (bundled)
- `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework (compression budgets per content category)

**Skill to load:** `plugin-dev:skill-development` — description format, progressive disclosure, writing style requirements

**Context7:** Not needed.

## References

- `plans/skills-quality-pass/reports/skill-inventory.md` — sonnet scout: 30-skill audit with grades, content segmentation, compression opportunities
- `plans/skills-quality-pass/reports/full-gate-audit.md` — sonnet scout: 12 prose-only gates
- `plans/reports/skill-optimization-grounding.md` — Segment → Attribute → Compress framework (LLMLingua/ProCut adapted)
- `plans/recall-tool-anchoring/reports/recall-gate-inventory.md` — prior recall-specific gate audit (31 gates, 13 files)
- `plans/recall-tool-anchoring/recall-artifact.md` — D+B pattern entry "How to Prevent Skill Steps From Being Skipped"
- `agents/decisions/implementation-notes.md` — D+B hybrid fix codified decision

## Next Steps

Route to `/runbook plans/skills-quality-pass/design.md` — general phases, opus execution model.
