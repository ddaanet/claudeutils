# Interactive Review: Design Outline

## Approach

Extend /proof with an item-by-item review mode. The current /proof validates artifacts as wholes (reword-accumulate-sync). Interactive review adds structured iteration over discrete items within an artifact, with per-item recall context and verdict accumulation before batch application.

**Architectural decision:** Extend /proof (not a separate skill). C-1 requires extension, not replacement. Item-by-item is the default when artifact has detectable items; whole-artifact is the fallback. One skill, adaptive behavior based on artifact structure. Both paths share terminal actions and corrector dispatch.

**Grounding:** Design grounded in Fagan inspection (per-item detection, reader-paraphrase, detection-not-resolution), Phabricator (draft-then-submit, state machine), and cognitive load research (segmentation, forced verdict). Full grounding report: `plans/reports/interactive-review-grounding.md`.

## Key Decisions

### D-1: Verdict Vocabulary — artifact-type-dependent (NEEDS GROUNDING)

**FR-4 deviation:** FR-4 specifies 5 verdicts (approve, revise, kill, discuss, absorb). This design reduces to 4 explicit verdicts (a/r/k/s): `discuss` becomes implicit (D-4), `absorb` becomes a kill sub-action, and `skip` is added. Justified by user review session decisions and Fagan/Phabricator convergence research.

Initial grounding covered code review tools (GitHub, Gerrit, Phabricator) and formal inspection (Fagan, IEEE 1028). But /proof primarily reviews planning artifacts — requirements, outlines, designs — which belong to different review domains:

| Artifact type | Review domain | Examples |
|--------------|--------------|---------|
| requirements.md | Backlog refinement / issue triage | RICE, WSJF, grooming ceremonies |
| outline.md / design.md | Architecture / design review | ADRs, design critiques |
| runbook-phase-*.md | Process review / checklist inspection | Fagan, IEEE 1028 |
| Deliverable review findings | QA / defect triage | Bug triage meetings |
| Source files / diffs | Code review (future) | GitHub, Gerrit, Phabricator |

**Design direction:** Verdict vocabulary varies by artifact type. D-7 already varies granularity by type — verdict vocabulary is a second axis of artifact-type adaptation. `absorb` is natural for requirements/backlog review but meaningless for code review.

**Supplementary grounding required:** Research review patterns in each domain before finalizing per-type verdict vocabularies. The initial grounding's convergence finding (3-5 per-item states) may hold across domains, but the specific verdicts may differ.

**Kill sub-actions:** After `k`, prompt: "Delete only, or absorb into another artifact?" If absorb: user names target, content transferred before deletion. (Absorb availability is artifact-type-dependent — present for planning artifacts, absent for code review.)

### D-2: Batch-Apply (not immediate)

Verdicts accumulate in-memory during iteration. Applied as a batch on terminal action ("apply"). File on disk unchanged until apply.

**Rationale:** FR-5 lifted by user — session resume handles interruption. Draft-then-submit is universal across GitHub/Gerrit/Phabricator. Batch application is a single atomic operation in the skill — structurally prevents the 2/2 agent failure pattern (lost track of edits) by encoding the full verdict list before dispatching edits.

**Accumulation format:**

```
- V-1: [item identifier] — approve
- V-2: [item identifier] — revise: "[user's stated fix]"
- V-3: [item identifier] — kill (absorb → plans/foo/requirements.md)
- V-4: [item identifier] — skip
```

### D-3: Orientation Phase (Fagan Overview analog)

Before item iteration, present:

1. **Preamble:** What artifact is being reviewed, total item count, artifact-type granularity
2. **TOC:** Numbered list with per-item title + agent-generated one-line summary (not table — dogfooding feedback)
3. **Checkpoint:** Wait for user response before first item. User may: reorder items, skip sections, adjust scope, or proceed as-is.

**Grounding:** Fagan inspection has Overview phase before Inspection Meeting. Cognitive load research: advance organizers activate schema before detail processing. Dogfooding confirmed gap — jumping to Item 1 without context was disorienting.

### D-4: Per-Item Presentation Format

Each item presented as:

```
**Item N of M: [item title]**

[item content — plain text, not blockquote]

Recall: [domain-relevant context if any, or omitted if none]

Verdict? (a)pprove (r)evise (k)ill (s)kip [skip is a design addition beyond FR-4, grounding-justified]
```

**Plain text, not blockquote** — dogfooding feedback: blockquote renders dim.

**Non-verdict input is implicit discussion.** No explicit `d` verdict needed. If the user responds with anything that isn't a recognized verdict shortcut, treat it as discussion — enter sub-loop naturally. The conversational medium makes explicit "discuss" actions unnecessary (unlike GUI-based tools where buttons are the only input).

**Recall per item (FR-3):** Before presenting each item, resolve domain-relevant recall entries for that item's topic. Null recall is silent (no "no relevant context found" noise).

### D-5: Linear Iteration with Revisit

Items presented in document order. No random-access preview of upcoming items.

**Revisit allowed:** After completing iteration, user can revisit any item. Identification is flexible — by number, title, or content. Model handles semantic matching.

**Grounding:** Cognitive load research shows linear presentation prevents skip-ahead bias. Fagan inspection is sequential (reader paraphrases in order). Revisit after completion mirrors Phabricator's "edit draft comment before submitting."

### D-6: Discussion and Iteration Guards

**Implicit discussion:** Non-verdict input enters a discussion sub-loop for the current item. Uses existing /proof reword-accumulate-sync mechanics scoped to one item (C-2 satisfied). Returns to verdict prompt with accumulated understanding.

**No direct edits during iteration.** The skill refuses execution-oriented requests (file edits, skill chains to /runbook, /deliverable-review, /codify, external plugins). This gate prevents bare-directive bypass of the review workflow.

**Normal loop actions** available throughout iteration, resume review after:
- **learn** — capture insight to `agents/learnings.md`
- **pending** — capture task for handoff (`p:` semantics)
- **brief** — transfer context to worktree

**Terminal actions:** apply, discard. No suspend → /design chain — if review surfaces a design issue, capture as pending and keep reviewing.

**Cross-item outputs (FR-6):** learnings, pending tasks, and new artifacts produced during discussion are captured via the normal loop actions above. These are immediate side effects (written during iteration), distinct from verdict application which is batched (D-2). Absorb transfers (kill sub-action in D-1) are also deferred to batch-apply — the transfer target is recorded in the verdict list, executed alongside other edits.

### D-7: Artifact-Type Granularity Detection

Automatic granularity detection (FR-2):

| Artifact type | Pattern | Item granularity |
|--------------|---------|-----------------|
| requirements.md | `**FR-N:**` / `**NFR-N:**` / `**C-N:**` | Individual requirement/constraint |
| outline.md | `### Sub-problem` / `## Section` headings | Section or sub-problem |
| design.md | `## Section` headings | Design section |
| runbook-phase-*.md | Cycle/step markers | Individual cycle or step |
| Source files | Function/class definitions | Function or class |
| Diff output | Hunk markers (`@@`) | Individual hunk |

**Hierarchical granularity:** Items above a size threshold auto-split into sub-items (large classes → methods, large diffs → per-function hunks). Per-item size threshold requires grounding — add to supplementary research scope (cognitive load per review segment, not per session).

**User override (FR-2):** Natural conversation handles granularity changes — no explicit override mechanism needed.

### D-8: Terminal Actions

**"apply":**
1. Display full verdict summary (FR-7): N approved, N revised, N killed, N skipped, cross-item outputs
2. User confirms
3. Apply all verdicts as batch edits to artifact (revise edits, kill deletions, absorb transfers)
4. Dispatch lifecycle-appropriate corrector (reuse /proof's existing corrector dispatch table)
5. Present corrector findings
6. Planstate: reuses /proof's existing entry/exit transitions (review-pending on entry, reviewed on exit) — no separate planstate logic needed

**"discard":** Abandon all verdicts. Artifact unchanged.

**"revisit"** (loop action, not terminal): Change verdict for a previously-reviewed item. Identification is flexible (number, title, content). Re-enter verdict prompt for that item. Returns to iteration — does not exit the loop.

### D-9: No Mode Selection

There is no separate "whole-artifact mode." The item-by-item loop is the only path. When an artifact has no detectable sub-items, it is one item — the loop runs once. Orientation shows "1 item", presents it, asks for verdict. The degenerate case is a single-iteration loop, not a different mode.

## Scope

### IN

- Item-by-item iteration mode in /proof skill
- Artifact-type-dependent verdict vocabulary (+ kill sub-actions)
- Orientation phase (preamble + TOC + checkpoint)
- Batch-apply with accumulation
- Per-item recall context (FR-3)
- Artifact-type granularity detection (hierarchical — large items auto-split)
- Implicit discussion via non-verdict input, using existing /proof mechanics
- Iteration guards (no direct edits, no execution-oriented chaining) — behavioral instruction in SKILL.md (same enforcement pattern as existing /proof anti-patterns section)
- Normal loop actions during iteration (learn, pending, brief)
- Cross-item outputs (learnings, tasks, artifacts)
- Review summary
- Single loop path (degenerate single-iteration for whole artifacts, no mode selection)
- Linear iteration with post-completion revisit (flexible item identification)
- Multi-file single artifact support (runbook phases as composite review target) — inherited from existing /proof glob handling (SKILL.md line 37), no new implementation needed; granularity detection (D-7) applies per-file within the composite

### OUT

- Automated review (agent-driven verdicts) — human-in-the-loop only
- Multi-artifact review in single invocation (distinct from multi-file single artifact like runbook phases, which is in-scope)
- Persistent review state across sessions (session resume handles)
- Time-boxing or automatic checkpoints
- Random-access navigation during iteration (deliberate exclusion per cognitive load research; post-completion revisit is in-scope)
- Per-item severity classification (reviewer decides importance via verdict, not label)
- Corrector integration changes (reuses existing dispatch table)
- New corrector types

## Affected Files

| File | Change |
|------|--------|
| `agent-core/skills/proof/SKILL.md` | Add item-by-item mode section, mode selection, verdict vocabulary, orientation phase |
| `agent-core/skills/proof/references/item-review.md` | New reference: detailed item presentation format, granularity patterns, accumulation format |

## Open Questions

**Grounding report divergence:** The grounding report (sections 1, 4) reflects pre-review analysis. This outline incorporates review findings that expand the grounding scope: artifact-type-dependent verdict vocabularies (D-1), skip outcome semantics (D-8), per-item cognitive load threshold (D-7), batch-apply by domain (D-2). Outline is authoritative; supplementary grounding will update the report.

**Skip outcome:** What happens to skipped items after apply? Persist unchanged and list in summary? Become pending tasks? Block apply? Needs grounding — established review processes handle deferred/unreviewed items differently by domain.

## Risk

**Batch-apply edit reliability:** User identified 2/2 agent failure on batched edits. Mitigation: skill encodes explicit accumulation format (V-N list) with structured dispatch. The agent has an explicit list to work from rather than trying to remember what was discussed — structure prevents the failure mode.

**SKILL.md size:** Adding item-by-item mode to /proof SKILL.md. Current SKILL.md is ~135 lines. Item-by-item adds substantial content. Mitigation: progressive disclosure — core loop mechanics in SKILL.md, detailed format/granularity in `references/item-review.md`.

## References

- `plans/reports/interactive-review-grounding.md` — grounding report (Fagan, Gerrit, Phabricator, cognitive load)
- `plans/reports/interactive-review-internal-codebase.md` — internal codebase patterns
- `plans/reports/interactive-review-external-research.md` — external framework research
- `plans/interactive-review/requirements.md` — FR-1 through FR-7 (FR-5 lifted)
- `plans/interactive-review/brief.md` — dogfooding feedback
- `agent-core/skills/proof/SKILL.md` — current /proof skill (extension target)
