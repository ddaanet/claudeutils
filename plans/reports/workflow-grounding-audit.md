# Workflow Grounding Audit

**Date:** 2026-02-25
**Method:** Inventory of all workflow skills and agents, provenance classification, leverage assessment

## Provenance Categories

### Grounded from Scratch (2)

| Skill | Grounding Source |
|-------|-----------------|
| `/ground` | Double Diamond, Rapid Review, RAG literature — `plans/reports/ground-skill-research-synthesis.md` |
| `/prioritize` | WSJF (SAFe) + opus brainstorm — `plans/reports/task-prioritization-methodology.md` |

### Partially Grounded (3)

| Skill | Grounding Source |
|-------|-----------------|
| `/review-plan` | Jiang et al. 2024, Fan et al. 2025, Mathews & Nagappan 2024 — embedded citations in Section 11 |
| `/requirements` | Referenced via `references/empirical-grounding.md` (not embedded) |
| `/deliverable-review` | ISO 25010 / IEEE 1012 — referenced via decision file |

### Ungrounded — High Leverage

| Skill/Agent | Leverage | What Grounding Would Target |
|-------------|----------|-----------------------------|
| `/design` | Highest — gates all tasks | Complexity triage, fix-category assessment, design methodology |
| `/runbook` | High — generates execution plans | Planning methodology, tier assessment, testing strategy |
| `/orchestrate` | High — executes all plans | Orchestration patterns, escalation, delegation |
| `/handoff` | High — every session boundary | Knowledge transfer, session continuity |
| corrector | High — every review gate | Code review methodology, severity classification |
| design-corrector | High — every design review | Architectural review methodology |

### Ungrounded — Low Grounding Benefit

| Skill/Agent | Reason |
|-------------|--------|
| `/commit` | Mostly mechanical; conventions not methodology |
| artisan | Thin delegation wrapper |
| test-driver | TDD is established methodology (Kent Beck) |
| `/shelve` | Simple archival, no methodology claims |
| `/reflect` | Lower leverage (reactive), though diagnostic taxonomy could benefit |
| tdd-auditor | Post-hoc analysis, low frequency |
| runbook-simplifier | Mechanical consolidation |

## Grounding Priority

1. **`/design`** — highest leverage, most accumulated patches, gates all downstream work. Absorbs structured-bugfix process as routing outcome.
2. **`/runbook`** — three-tier model and testing strategy are project-invented
3. **Review agents** (corrector, design-corrector) — share review methodology, batch together
4. **`/orchestrate`** — weak orchestrator pattern is project-invented
5. **`/handoff`** — session continuity methodology

## Key Insight

`/requirements` was the first grounded skill (manual, pre-/ground) and proved much more reliable than ungrounded peers. Since `/ground` was created, all new workflow work has been grounded — but existing high-leverage skills predate it. `/design` in particular has accumulated 4+ structural patches (triage gate, sufficiency gate, recall artifact, D+B anchors) that might have been unnecessary with grounded foundations.
