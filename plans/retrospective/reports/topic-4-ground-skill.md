# Topic 4: Ground Skill Origins

Evidence bundle for the "external research mandate" topic of the retrospective blog post.

**Key narrative:** confabulated prioritization scoring caught -> external research mandate -> diverge-converge pattern -> WSJF grounding -> self-application (circular dependency insight when redesigning the ground skill itself).

---

## 1. Git Timeline

| Date | Commit | Event |
|------|--------|-------|
| 2026-02-15 | `14eeed90` | Reflexive bootstrapping learning captured during workflow-rca-fixes: "unimproved agents reviewing their own improvements creates a bootstrapping problem" |
| 2026-02-16 09:06 | `ab4813a4` | Research grounded task prioritization: WSJF methodology + ground skill research synthesis (Double Diamond + Rapid Review + RAG). First prioritization attempt had confabulated weights; WSJF grounding fixed it |
| 2026-02-16 10:36 | `cae5ef11` | Ground skill created: SKILL.md + outline + deliverable review. 4-phase procedure (Scope/Diverge/Converge/Output) |
| 2026-02-16 11:23 | `70aa470a` | Ground skill deliverable review: 1 major finding (Write tool missing), brainstorm decision (always opus for generative divergence) |
| 2026-02-18 | `25d797d6` | "When Writing Methodology" decision codified: anti-pattern = internal reasoning alone yields confabulated methodologies; correct pattern = invoke /ground |
| 2026-02-21 | `c2c54ffd` | General-first framing rule propagated from /ground skill usage. Inverted framing anti-pattern identified |
| 2026-02-24 | `f2455d9a` | Ground skill updated: parallel agents, unified explore scope, decision file updates |
| 2026-02-25 | `557c2eed` | /ground applied to /design skill: 6 external frameworks (Stacey, Cynefin, PDR/CDR, ADR). Self-application of grounding to a skill that predated grounding. Grounding report: Strong |
| 2026-02-26-27 | `e632470e` | Design grounding refresh: empirical session data + external research. Diverge-converge v2 with session scraper evidence |
| 2026-03-02 | `ebf903e8` | Reprioritize 79 tasks using WSJF, archive pushback-grounding plan (FRs delivered) |
| 2026-03-06 | `ac37f7ba` | /ground applied to decomposition methodology: DSM, Axiomatic Design, TRL frameworks |

---

## 2. Session Excerpts

### Excerpt 1: The confabulated scoring discovery and WSJF fix

**Source:** Decision file `agents/decisions/workflow-optimization.md`, codified `25d797d6` (2026-02-18), evidence from `ab4813a4` (2026-02-16)

```
### When Writing Methodology

**Anti-pattern:** Producing scoring frameworks, evaluation axes, or "best practice"
documents from internal reasoning alone -- yields confabulated methodologies with
subjective weights and ungrounded criteria.

**Correct pattern:** Invoke `/ground` skill. Diverge-converge with parallel branches:
internal (brainstorm for project-specific dimensions) + external (web search for
established frameworks). Synthesize by mapping internal dimensions onto external skeleton.

**Evidence:** First prioritization attempt produced subjective weights ("Highest/High/Medium")
and 0-3 scores without defined criteria. After grounding in WSJF research, methodology
used Fibonacci scoring with observable evidence sources.
```

### Excerpt 2: WSJF research synthesis — why WSJF over alternatives

**Source:** `plans/reports/task-prioritization-methodology.md`, commit `ab4813a4` (2026-02-16)

```
This methodology adapts **WSJF (Weighted Shortest Job First)** -- Reinertsen's
prioritization framework -- to an internal tooling and agent orchestration context
where "cost" is measured in developer friction, agent reliability, and token budget
rather than revenue.

**Why WSJF over RICE/ICE:**
- RICE requires "Reach" (user count) -- irrelevant for single-developer internal tooling
- ICE is too subjective ("low/medium/high" without decomposition)
- WSJF decomposes Cost of Delay into measurable components and naturally prioritizes
  high-value small work
```

### Excerpt 3: Ground skill design outline — the diverge-converge core

**Source:** `plans/grounding-skill/outline.md`, commit `cae5ef11` (2026-02-16)

```
## Approach

Create a skill that encodes the diverge-converge research methodology proven during
prioritization skill creation. Prevents ungrounded confabulation when producing
methodologies, frameworks, scoring systems, or best-practice documents.

**D-5: Two-branch diverge is the core innovation.**
Internal branch (brainstorm OR explore) captures project-specific dimensions.
External branch (web search) provides established framework skeleton. Neither alone
suffices -- internal-only confabulates, external-only is generic.
```

### Excerpt 4: Ground skill SKILL.md description — the mandate

**Source:** Session `820a3daa` (2026-02-26), design-grounding-update worktree, reading skill frontmatter

```
---
name: ground
description: >-
  Ground claims with external research before asserting methodology. Triggers on
  "ground", "create a scoring system", "design a methodology", "build a framework",
  or "synthesize best practices". Parallel diverge-converge research preventing
  confabulated structures.
---
```

### Excerpt 5: Research foundations — Double Diamond + Rapid Review + RAG

**Source:** `plans/reports/ground-skill-research-synthesis.md`, commit `ab4813a4` (2026-02-16)

```
### Double Diamond (Design Council, 2005)
Origin: Banathy's 1996 divergence-convergence model, adapted by UK Design Council.
Structure: Two diamonds, each diverge->converge.

### Rapid Review (evidence synthesis methodology)
Definition: "A form of knowledge synthesis in which components of the systematic review
process are simplified or omitted to produce information in a timely manner."

### RAG-as-Grounding (LLM hallucination mitigation)
Core principle: External retrieval anchors generated output in verified sources,
reducing hallucination by 42-68%.
```

### Excerpt 6: Self-application — grounding the /design skill

**Source:** Commit `557c2eed` (2026-02-25), applying /ground to /design skill

Commit message:
```
Ground design skill against 6 external frameworks
- Stacey axes (certainty x stability) anchor classification criteria
- Requirements-clarity gate upgraded from prose-only to D+B structured output
- PDR/CDR differentiated criteria for outline-corrector and design-corrector
- Defect/structured-bugfix fourth triage path (Cynefin Complicated domain)
- Grounding report: plans/reports/design-skill-grounding.md (Strong)
```

Session `6e808dbc` (2026-02-26) shows the diverge-converge pattern in action: parallel internal codebase analysis + external research agents dispatched, opus convergence producing the grounding report. Method header reads: "Parallel diverge-converge (codebase + git history mining / external research), opus convergence."

### Excerpt 7: Reflexive bootstrapping — the circular dependency insight

**Source:** Learning captured in `14eeed90` (2026-02-15), codified in `25d797d6` (2026-02-18)

```
## Reflexive bootstrapping for self-referential improvements
- When improving tools/agents, apply each improvement before using that tool
  in subsequent steps
- Phase ordering follows tool-usage dependency graph, not logical grouping
- Collapses design->plan->execute into design->apply for prose-edit work
- Avoids the bootstrapping problem: unimproved agents reviewing their own improvements
- Generalizes: any self-referential improvement task should order by downstream usage,
  not by topic cluster

## Reference upstream in bootstrapping
- Anti-pattern: referencing a downstream consumer of criteria when the consumer hasn't
  been updated yet in the bootstrapping sequence
- Correct pattern: reference the upstream source where criteria are defined, not
  agents/skills that consume them
```

This learning was operationally relevant when the ground skill itself was updated (`f2455d9a`, 2026-02-24) and when /ground was applied to /design (`557c2eed`, 2026-02-25) — the skill being used to ground other skills had to be improved first before being applied.

### Excerpt 8: Empirical grounding refresh — session scraper feeding back into grounding

**Source:** Session `6e808dbc` (2026-02-26), design-grounding-update worktree

The session scraped 8 design sessions for empirical behavioral data, wrote findings to `plans/reports/design-session-empirical-data.md`, then invoked `/ground` with that evidence:

```
Now let me invoke `/ground` with this empirical data as supplementary evidence
for the design skill grounding update
```

Dispatch protocol: parallel Task agents for internal (codebase analysis) and external (web research), external agent returning report path. The convergence produced grounding report v2 with method: "Parallel diverge-converge (session scraper empirical data + targeted external research)."

Key finding from empirical data: the design skill's research phase (A.3-A.4) was rationalized away by the agent — "scout and started reading decision files. Skipped A.3-A.4 (external research) entirely. User noticed 47 minutes later." This drove the structural anchor requirement: a tool call proving external research was attempted.

---

## 3. Key Inflection Points

### Inflection 1: Confabulated scoring exposed (2026-02-16)

The first task prioritization attempt produced subjective weights ("Highest/High/Medium") and 0-3 scores without defined criteria. The scoring looked authoritative but was entirely fabricated — no grounding in any established prioritization framework. This was the catalyst: if the agent could confabulate an entire scoring methodology and present it confidently, the same failure mode threatened any methodology-producing task.

**Commits:** `ab4813a4` (WSJF research + grounding skill research), `cae5ef11` (ground skill created same day)

### Inflection 2: External research mandate formalized (2026-02-16 to 2026-02-18)

The ground skill encoded the mandate: before asserting methodology, run parallel diverge-converge research. Internal-only confabulates; external-only is generic; both together produce grounded output. The "When Writing Methodology" decision (`25d797d6`) made this a permanent behavioral rule.

**Pattern:** Double Diamond (diverge-converge) + Rapid Review (scoped external search) + RAG-as-Grounding (retrieval anchors generated output)

### Inflection 3: Self-application reveals bootstrapping dependency (2026-02-24 to 2026-02-25)

When the ground skill was updated (`f2455d9a`) and then applied to the /design skill (`557c2eed`), the bootstrapping insight from `14eeed90` became directly relevant: the tool being used to ground other skills needed to be grounded and improved first. Phase ordering had to follow the tool-usage dependency graph. The ground skill grounding the design skill was a concrete instance of the reflexive bootstrapping pattern.

### Inflection 4: Empirical feedback loop closes (2026-02-26 to 2026-02-27)

Session scraper data from 8 actual /design sessions fed back into /ground execution, producing grounding report v2 (`e632470e`). The most actionable finding: agents rationalized away the external research step (A.3-A.4 skipped, user caught it 47 minutes later). This drove the structural enforcement requirement — a tool call proving research was attempted, not just a procedural instruction to do it.

### Inflection 5: Methodology spreads to other domains (2026-03-06)

The ground skill applied to decomposition methodology (`ac37f7ba`), pulling in DSM (Design Structure Matrix), Axiomatic Design, and TRL (Technology Readiness Levels) frameworks. The diverge-converge pattern had become the standard approach for any methodology-producing task.
