# Deliverable Review: Ground Skill

**Date:** 2026-02-16
**Artifacts reviewed:** 2 files, 193 lines total
**Review type:** Interactive with full context (learnings, fragments, plugin-dev skill-development guidance)
**Design baseline:** `plans/grounding-skill/outline.md` (8 decisions)
**Research baseline:** `plans/reports/ground-skill-research-synthesis.md`

---

## Summary

1 major, 5 minor findings. All 8 design decisions implemented. Research traceability confirmed. Major finding: `Write` missing from `allowed-tools` despite file-writing phases.

---

## Design Decision Conformance

| Decision | Status | Notes |
|----------|--------|-------|
| D-1: Triggers on claim type | Pass | Frontmatter description lists four claim types and concrete trigger phrases |
| D-2: Orchestrator-invoked | Pass | No self-detection; `user-invocable: true` + description trigger phrases |
| D-3: Inline parameterization | Pass | Parameters as Phase 1 decision points; detailed guidance in references/ |
| D-4: Mandatory quality label | Pass | Phase 3: "mandatory"; Phase 4: required section; criteria.md: placement format |
| D-5: Two-branch diverge | Pass | Phase 2: "Neither is optional -- both are required." |
| D-6: Output location convention | Pass | Phase 4: `plans/reports/<topic>.md` |
| D-7: Search query templates | Pass | criteria.md: 4 template categories |
| D-8: Convergence template | Pass (with addition) | All 3 required sections + useful Adaptations section (see M-3) |

---

## Research Traceability

| Quality label | Research synthesis definition | Implementation definition | Match? |
|---------------|-------------------------------|---------------------------|--------|
| Strong | Multiple established frameworks, adapted with project-specific criteria | 2+ established frameworks found, adapted with project-specific criteria | Yes (quantified) |
| Moderate | One framework with partial applicability, supplemented by internal analysis | 1 framework with partial applicability, supplemented by internal analysis | Yes |
| Thin | No directly applicable framework; project-derived with structural inspiration only | No directly applicable framework; structural inspiration only | Yes |
| None | External search returned no relevant results; ungrounded internal reasoning only | External search returned no relevant results | Yes |

Trigger criteria match research synthesis exactly (4 mandatory claim types, 3 exemption categories).

---

## Major Findings

### F-1: `Write` missing from `allowed-tools`

**File:** `agent-core/skills/ground/SKILL.md:11`
**Axis:** Functional completeness
**Description:** `allowed-tools` lists `Read, Grep, Glob, Bash, WebSearch, WebFetch, Task` but omits `Write`. The procedure requires the executing agent to write files:
- Phase 2 Branch B (line 51): "Write external branch output to `tmp/ground-external-<topic>.md`"
- Phase 4 (line 64): "Write the grounded reference document to `plans/reports/<topic>.md`"

Every other skill with file-writing phases includes `Write`: design (`Task, Read, Write, Bash, Grep, Glob, WebSearch, WebFetch`), runbook, handoff, remember, doc-writing, requirements, shelve, reflect, release-prep. The design skill is the closest analog (research + synthesis + write).

**Fix:** Add `Write` to allowed-tools. Suggested: `Read, Write, Grep, Glob, Bash, WebSearch, WebFetch, Task`

---

## Minor Findings

### M-1: Word count below outline targets

**File:** Both files
**Axis:** Progressive disclosure / word count
**Description:** SKILL.md: 571 words vs ~800 target (71%). grounding-criteria.md: 609 words vs ~900 target (68%). Content is functional and complete — targets were overestimated rather than content omitted. Informational.

### M-2: Explore mode delegation lacks prompt specificity

**File:** `agent-core/skills/ground/SKILL.md:42`
**Axis:** Actionability
**Description:** Brainstorm mode specifies output expectations ("Generate project-specific dimensions, constraints, desiderata, evaluation axes"). Explore mode says only "Surface existing codebase patterns, prior decisions, current conventions relevant to the topic." An agent would need to infer the explore delegation prompt and expected output format.

### M-3: Convergence template adds Adaptations section beyond D-8 spec

**File:** `agent-core/skills/ground/references/grounding-criteria.md:84-106`
**Axis:** Excess
**Description:** D-8 specifies three required sections (Framework Mapping, Grounding Assessment, Sources). Implementation adds Adaptations (what was changed, project-specific additions, deliberate exclusions). Useful excess; SKILL.md line 59 includes Adaptations in its parenthetical, maintaining internal consistency.

### M-4: Temporary file topic slug unspecified

**File:** `agent-core/skills/ground/SKILL.md:44,51`
**Axis:** Determinism
**Description:** Branch output paths use `<topic>` placeholder without derivation guidance. Different agents might slug differently ("prioritization" vs "task-prioritization"). Low impact — files cleaned up in Phase 4.

### M-5: Judgment words in inclusion criteria and source evaluation

**File:** `agent-core/skills/ground/SKILL.md:28,42,48` and `references/grounding-criteria.md:52`
**Axis:** Constraint precision
**Description:** Four instances of judgment words ("relevant", "actionable") across both files:
- SKILL.md:28 — "relevance to project context, actionable methodology"
- SKILL.md:42 — "conventions relevant to the topic"
- SKILL.md:48 — "relevant to project context? Actionable methodology?"
- criteria.md:52 — "Most tasks work with narrow + sonnet"

The Trigger Criteria section in criteria.md does better: "Does the output assert how things *should* be done, or describe how things *are* done?" — measurable heuristic. The inclusion criteria could follow the same pattern.

### M-6: Brainstorm delegation doesn't specify subagent_type

**File:** `agent-core/skills/ground/SKILL.md:41`
**Axis:** Actionability
**Description:** "Delegate to Task agent (opus/sonnet per parameter)" doesn't specify which `subagent_type` to use with the Task tool. Explore mode names `quiet-explore` explicitly (line 42). Inconsistent specificity between the two branches.

---

## Plugin-dev Skill Axes

| Check | Result |
|-------|--------|
| Second-person violations | None found |
| Description quality | Third-person with 6 concrete trigger phrases |
| Writing style | Imperative/infinitive throughout |
| Progressive disclosure | SKILL.md is procedure; all criteria, templates, parameterization in references/ |
| Resource references | All 4 SKILL.md references to `references/grounding-criteria.md` match actual sections |
| Directory structure | Matches outline specification |

---

## Assessment

**Verdict: Conditional pass.** All 8 design decisions implemented faithfully. Research traceability confirmed. F-1 (`Write` missing) is a functional gap that prevents the skill from executing its own procedure — fix before next use. 6 minor findings are non-blocking.
