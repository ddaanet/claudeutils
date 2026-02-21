# Plan Lifecycle Terminology Grounding

**Grounding:** Moderate — One directly applicable framework (SmartBear Collaborator review workflow), supported by CI/CD delivery/deployment distinction and value stream mapping rework terminology. No single framework covers the full lifecycle.

---

## Research Foundation

### External sources

**SmartBear Collaborator review workflow** (primary, strongest match):
Named phases: Planning → Annotating → Inspection → **Rework** → Completed. Uses "Rework" (not "Defective" or "Rejected") for the post-review correction state. Supports cycles: Rework → Inspection → Rework. Terminal states: Completed, Cancelled/Rejected.
Source: [Collaborator Review Phases](https://support.smartbear.com/collaborator/docs/working-with/concepts/phases.html)

**CI/CD pipeline terminology** (supporting, "delivered" validation):
- Continuous Delivery = artifact built, tested, ready for deployment (manual gate to production)
- Continuous Deployment = automatically deployed to production
- Our model: main branch IS production. "Delivered" = merged to main. Matches CD's "delivered to repository" meaning, not the weaker "in staging" interpretation.
Sources: [Octopus CI/CD](https://octopus.com/devops/ci-cd/), [AWS CI/CD Guide](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-cicd-litmus/understanding-cicd.html)

**Value stream mapping** (supporting, "rework" validation):
"Rework" is standard waste category. "Defect rate" = ratio of work rejected at a stage and sent back for rework. The terminology pair is defect (the finding) + rework (the corrective action/state).
Sources: [Atlassian VSM Guide](https://www.atlassian.com/continuous-delivery/principles/value-stream-mapping), [DORA VSM Guide](https://dora.dev/guides/value-stream-management/)

**Kanban Official Guide** — Deliberately agnostic on state names. "Done" is the only universal terminal. Teams define their own states.
Source: [Kanban University Guide](https://kanban.university/kanban-guide/)

**DORA metrics** — Measures delivery performance (lead time, deployment frequency) but doesn't prescribe intermediate state names. Teams map their own value streams.
Source: [DORA Metrics Guide](https://dora.dev/guides/dora-metrics/)

### Internal analysis

Full brainstorm at `tmp/ground-internal-lifecycle.md`. Seven dimensions analyzed: LLM agent naming constraints, marker file semantics, review loop mechanics, transition ambiguity, delivered vs deployed, terminal state clarity, plan-vs-task state mapping.

---

## Adapted Terminology

### Proposed → Grounded lifecycle

Original: `requirements → designed → planned → ready → review-pending → [defective ↔ review-pending] → completed → delivered`

**Grounded:** `requirements → designed → planned → ready → review-pending → [rework ↔ review-pending] → reviewed → delivered`

Two name changes from the brief's proposal, both supported by evidence.

### Change 1: "defective" → "rework"

**General principle:** Post-review correction states in workflow systems should name the corrective action, not the deficiency. SmartBear Collaborator names this phase "Rework"; value stream mapping uses "rework" as the standard corrective action category. No established framework uses a deficiency label ("defective", "broken") for a re-workable state.

**Project instance:** `rework` replaces `defective` in our lifecycle.

| Dimension | Evidence |
|-----------|----------|
| External precedent | SmartBear Collaborator uses "Rework" phase. VSM uses "rework" as standard corrective action term. No external source uses "defective" for a re-workable state. |
| LLM agent behavior | "Defective" implies terminality — risks conflation with task `[✗]` failed. "Rework" is action-suggestive (names what to do, not what's wrong). |
| Pattern consistency | Matches bare-noun pattern of `requirements`. `rework.md` reads naturally as filename. |
| Cross-domain collision | "Failed" collides with task `[✗]`. "Rejected" implies human authority. "Rework" has zero collision with task status vocabulary. |

### Change 2: "completed" → "reviewed"

**General principle:** Terminal-sounding state names should be reserved for actual terminal states. When a workflow has a post-"completed" step, using "completed" for a non-terminal state violates the widespread convention that "completed" means "done" (SmartBear, Kanban, task management all use it as terminal).

**Project instance:** `reviewed` replaces `completed` because our lifecycle has a post-review delivery step (merge to main). "Reviewed" signals that something follows.

| Dimension | Evidence |
|-----------|----------|
| External precedent | No direct support (SmartBear uses "Completed" as terminal). The change is driven by the general principle above. |
| LLM agent behavior | "Completed" sounds terminal — agent may not look for remaining action (merge). "Reviewed" implies something follows. |
| Cross-domain collision | HIGH collision: task `[x]` = completed (terminal), plan `completed` = pre-terminal (one step from delivered). "Reviewed" has NONE. |
| Grammatical consistency | Past participle matching `designed`, `planned`, `delivered`. |
| Action suggestiveness | `[reviewed] → _worktree merge` reads as "review passed, now merge." `[completed] → _worktree merge` reads as contradiction. |

### Kept unchanged

- **review-pending**: Workflow review gates use an "awaiting review" state distinct from both the pre-review and post-review states. SmartBear calls it "Inspection"; our "review-pending" serves the same role. No conflicts with task status vocabulary.
- **delivered**: In CD pipelines, "delivered" means artifact is available in the target repository; "deployed" implies infrastructure beyond the repository. Our main branch is production — "delivered" (merged to main) matches the CD meaning without implying deployment infrastructure we don't have.

---

## Grounding Assessment

**Quality: Moderate**

SmartBear Collaborator provides a concrete named framework with matching review-loop states (Rework, Completed, cycles). CI/CD and VSM provide supporting evidence for specific terms. However:

- No single framework covers plan lifecycle from requirements through delivery
- The pre-execution states (requirements → designed → planned → ready) are project-specific — no external framework maps to design-then-plan-then-execute
- The "reviewed" rename is internally motivated (cross-domain collision avoidance) without direct external precedent

**Searches performed:** 5 web searches (kanban states, DORA metrics, CI/CD pipeline stages, value stream mapping, software workflow state machines). 2 page fetches (Kanban University official guide, DORA value stream management guide, SmartBear Collaborator phases).

**Gaps:** No framework found that models the full "design artifact → execution → review → delivery" lifecycle. Our lifecycle is a hybrid of project management (requirements → planned), CI/CD (ready → delivered), and code review (review-pending → rework → reviewed).

---

## Design Constraints Surfaced

**Review loop and existence-based detection:** The `rework ↔ review-pending` cycle creates ambiguity with pure existence detection. When both `rework.md` and `review-pending.md` exist, priority determines status. Two resolution options:

1. **File deletion in loop:** Delete `rework.md` when re-entering review. Clean but requires active file management.
2. **Priority ordering:** `review-pending > rework` — latest marker wins without deletion. But "latest" is determined by priority chain position, not by recency.

This is a design concern for D-4 (priority ordering). The brief has `defective > review-pending`; if that ordering is preserved as `rework > review-pending`, then rework.md must be deleted on re-review. Reversing to `review-pending > rework` avoids deletion but means rework is only visible when review-pending is absent.

---

## Sources

- [SmartBear Collaborator Review Phases](https://support.smartbear.com/collaborator/docs/working-with/concepts/phases.html) — Primary. Review workflow state machine with Rework phase.
- [Kanban University Official Guide](https://kanban.university/kanban-guide/) — Confirmed Kanban is state-agnostic. Teams define their own.
- [DORA Metrics Guide](https://dora.dev/guides/dora-metrics/) — Delivery performance metrics, no state prescription.
- [DORA Value Stream Management](https://dora.dev/guides/value-stream-management/) — Teams map their own delivery steps.
- [Atlassian VSM Guide](https://www.atlassian.com/continuous-delivery/principles/value-stream-mapping) — "Rework" as standard waste/correction term.
- [Octopus CI/CD Explainer](https://octopus.com/devops/ci-cd/) — Delivered vs deployed distinction.
- [AWS CI/CD Understanding](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-cicd-litmus/understanding-cicd.html) — CD = delivered to repo, manual gate to production.
