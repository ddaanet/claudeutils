# Interactive Review: Supplementary External Research

Supplementary grounding for 4 domain-specific gaps identified during outline review. Initial grounding covered code review tools (GitHub, Gerrit, Phabricator) and formal inspection (Fagan, IEEE 1028). This report covers planning-artifact review domains.

---

## Gap D-1: Per-Domain Verdict Vocabularies

### Backlog Refinement / Issue Triage

**Sources:**
- [Agile Alliance: Backlog Refinement](https://agilealliance.org/glossary/backlog-refinement/)
- [Atlassian: Backlog Refinement](https://www.atlassian.com/agile/scrum/backlog-refinement)
- [Scrum Institute: Grooming Meeting](https://www.scrum-institute.org/scrum-grooming-meeting-the-scrum-framework.php)
- [Scrum.org: Product Backlog Refinement Explained](https://www.scrum.org/resources/blog/product-backlog-refinement-explained-23)
- [Public Agile: Story Refinement](https://publicagile.org/agile-playbook/scrum-events/story-refinement/)
- [MoSCoW Method (Wikipedia)](https://en.wikipedia.org/wiki/MoSCoW_method)

**Per-item actions (convergent across sources):**
- **Accept/Ready** — item meets Definition of Ready, approved for sprint
- **Revise** — needs clarification, better acceptance criteria, re-estimation
- **Split** — too large for a sprint; decompose into smaller stories
- **Defer** — acknowledged but pushed to future sprint (MoSCoW "Won't Have this time")
- **Remove/Kill** — no longer relevant, dropped from backlog
- **Merge/Absorb** — combine with another item (duplicate or subset)
- **Reprioritize** — reorder relative to other items (RICE/WSJF rescoring)

**State count:** 6-7 distinct per-item actions. Notably includes **split** and **absorb/merge** — actions that create or consolidate items, not just classify them. These are absent from code review vocabularies.

### Architecture / Design Review

**Sources:**
- [SEI ATAM Technical Report (CMU/SEI-2000-TR-004)](https://www.sei.cmu.edu/documents/629/2000_005_001_13706.pdf)
- [ATAM (Wikipedia)](https://en.wikipedia.org/wiki/Architecture_tradeoff_analysis_method)
- [Mozilla Firefox Architecture Review Process](https://mozilla.github.io/firefox-browser-architecture/text/0006-architecture-review-process.html)
- [AWS Prescriptive Guidance: ADR Process](https://docs.aws.amazon.com/prescriptive-guidance/latest/architectural-decision-records/adr-process.html)
- [JPL Review Process (Chapter 5)](https://parts.jpl.nasa.gov/asic/Sect.1.5.html)
- [CadChat: Engineering Design Review Process](https://cadchat.com/articles/engineering-design-review-process/)

**Per-item classifications (ATAM):**
- **Risk** — potentially problematic architectural decision
- **Non-risk** — sound architectural decision (explicit or implicit)
- **Sensitivity point** — decision with significant impact on a quality attribute
- **Tradeoff point** — decision where improving one quality attribute harms another

ATAM does not produce approve/reject verdicts per item. Instead, it classifies each architectural decision into the above taxonomy. The whole-evaluation outcome is a risk theme synthesis, not a per-item pass/fail.

**Per-item classifications (ADR lifecycle):**
- **Proposed** — under consideration
- **Accepted** — approved and immutable
- **Deprecated** — no longer relevant
- **Superseded** — replaced by a newer decision

ADR statuses are lifecycle states, not review verdicts. But the transition Proposed -> Accepted/Deprecated maps to the approve/kill distinction.

**Per-item actions (engineering design reviews — PDR/CDR):**
- **Action item** — concern requiring team response before review completion
- **Proceed** — design approved to advance (holistic, not per-item)
- **Alter/revise** — questions reformulated, subsequent review needed
- **Drop** — proposal abandoned entirely

Engineering design reviews (PDR, CDR, Mozilla) operate at whole-proposal level, not per-item. The reviewer produces action items (enumerated concerns), and the team responds. The reviewer then decides the overall outcome. Per-item verdicts are action items, not disposition categories.

**State count:** ATAM has 4 classifications (but they're analytical categories, not action verdicts). ADR has 4 lifecycle states. Engineering design reviews use 2-3 holistic verdicts plus per-item action items without formal disposition.

### Process Review / Checklist Inspection

**Sources:**
- [IEEE 1028-1997 (via silo.tips)](https://silo.tips/download/ieee-standard-for-software-reviews)
- [Fagan Inspection (Grokipedia)](https://grokipedia.com/page/Fagan_inspection)
- [Safety Audit Checklist (citoolkit)](https://citoolkit.com/templates/safety-audit-checklist/)
- [HSE Coach: Safety Audit Checklist Template](https://thehsecoach.com/safety-audit-checklist-template/)

**Per-item states (IEEE 1028 inspection):**
- **Valid** vs **Invalid** — whether the anomaly is real
- **Major** vs **Minor** — severity classification
- **Systemic** — flagged separately for process improvement

**Whole-product disposition (IEEE 1028):**
- **Accept with no or minor rework** — product accepted as-is or with trivial changes requiring no further verification
- **Accept with rework verification** — product proceeds after designated team members confirm corrections
- **Re-inspect** — complete re-examination required; triggered when rework exceeds 5% of inspected material

**Per-item states (safety/audit checklists):**
- **Pass** / **Fail** / **Not Applicable** — the universal 3-state checklist vocabulary
- **Open** (corrective action needed) / **Closed** (resolved)

**State count:** Inspection has 2-3 per-item severity categories plus a 3-state whole-product disposition. Safety checklists use a strict 3-state (pass/fail/NA) per-item model.

### Defect Triage

**Sources:**
- [GeeksforGeeks: Defect Triage Meeting](https://www.geeksforgeeks.org/defect-triage-meeting/)
- [SoftwareTestingMaterial: Defect Triage](https://www.softwaretestingmaterial.com/defect-triage-meeting/)
- [Atlassian: Bug Triage](https://www.atlassian.com/agile/software-development/bug-triage)
- [Helloskillio: Bug Triage Guide](https://helloskillio.com/bug-triage-in-software-testing/)
- [ThinSys: Bug Triage Meeting Process](https://thinksys.com/qa-testing/complete-bug-triage-meeting-process/)

**Per-item resolution categories (convergent across sources):**
- **Fix now** — high severity/priority, immediate action
- **Fix later / Defer** — acknowledged, scheduled for future release
- **Won't fix** — acknowledged, not worth the cost
- **Duplicate** — same as another defect (link and close)
- **Not a defect / By design** — working as intended
- **Cannot reproduce** — insufficient evidence to act on

**State count:** 5-6 per-item resolution categories. This is the most granular per-item vocabulary across all four domains.

### Cross-Domain Convergence

| Domain | Per-item states | Action-oriented? | Key distinction |
|--------|----------------|------------------|-----------------|
| Backlog refinement | 6-7 | Yes — actions change items | Has split/absorb (item-creating actions) |
| Architecture review | 4 (ATAM) | No — analytical classification | Risk taxonomy, not action verdicts |
| Process/checklist | 3 (pass/fail/NA) | Yes — binary+NA | Simplest vocabulary |
| Defect triage | 5-6 | Yes — routing decisions | Most granular disposition |
| Code review (prior) | 3-5 | Yes — approve/request-changes | Whole-PR, not per-item (except comments) |

**Convergence finding:** 3-6 per-item states across all domains (consistent with initial grounding's 3-5 finding). But the nature of states differs fundamentally:
- **Checklist domains** (process, safety): binary pass/fail — items are evaluated against criteria
- **Triage domains** (backlog, defect): routing decisions — items are sorted into action buckets
- **Analysis domains** (architecture): classification — items are categorized for synthesis

**Implication for D-1:** The outline's 4-verdict model (a/r/k/s) maps well to triage domains but poorly to checklist and analysis domains. For planning artifacts (requirements, outlines, designs), the triage model is the best fit — the reviewer is routing items into action buckets, not evaluating pass/fail against criteria.

The **absorb** action (kill sub-action in outline D-1) is well-grounded: backlog refinement's merge/absorb and defect triage's duplicate are the same concept. It is natural for planning artifact review.

The **split** action is present in backlog refinement but absent from the outline. Whether to add it depends on whether the review should create new items or only disposition existing ones. The outline's current position (review disposes, doesn't create) is defensible.

---

## Gap D-2: Batch vs Immediate Application by Domain

### Backlog Refinement — Immediate

**Sources:**
- [Plane: Backlog Grooming Best Practices](https://plane.so/blog/backlog-grooming-best-practices-for-agile-teams)
- [Atlassian: Backlog Grooming](https://www.atlassian.com/agile/project-management/backlog-grooming)

Oral decisions decay quickly. If you agree to change scope, adjust priority, or add a dependency, document it immediately in the ticket. The recommendation is **immediate documentation and application** during the session. Backlog tools (Jira, Azure DevOps) are typically open during refinement and updated in real time.

### Architecture Review — Batch (Action Items)

**Sources:**
- [Mozilla Architecture Review Process](https://mozilla.github.io/firefox-browser-architecture/text/0006-architecture-review-process.html)
- [AWS Well-Architected Review Process](https://docs.aws.amazon.com/wellarchitected/latest/framework/the-review-process.html)
- [JPL Review Process](https://parts.jpl.nasa.gov/asic/Sect.1.5.html)

Architecture reviews produce action items during the meeting, but the team implements them **after the review session**. The reviewer validates responses and decides the outcome post-meeting. Mozilla's process explicitly states "reviewers don't need to make a decision at the meeting." This is **batch by design** — the review produces a list, implementation follows.

### Defect Triage — Immediate Assignment, Batch Resolution

**Sources:**
- [ThinSys: Bug Triage Meeting Process](https://thinksys.com/qa-testing/complete-bug-triage-meeting-process/)
- [Atlassian: Bug Triage](https://www.atlassian.com/agile/software-development/bug-triage)
- [Shakebugs: Bug Triage Meetings Guide](https://www.shakebugs.com/blog/bug-triage-meetings-guide/)

Triage makes **immediate assignments** during the meeting — bug trackers are updated in real time. But resolution (actual fixing) is obviously batched. The critical recommendation: update trackers immediately, don't rely on verbal agreements. Bugs discussed but not updated in the tracker are a known failure mode.

### Safety/Audit — Batch (Report)

**Sources:**
- [HSE Coach: Safety Walkthrough vs Safety Audit](https://thehsecoach.com/safety-walkthrough-vs-safety-audit/)
- [SafetyCulture: Corrective Action](https://safetyculture.com/topics/corrective-action/)
- [AuditFindings: Audit Findings Lifecycle](https://www.auditfindings.com/audit-findings-lifecycle/)

Safety walkthroughs are immediate ("fix the missing toe board now"). Audits produce batch reports with findings and corrective action plans. The distinction maps to severity: immediate hazards get immediate correction; systemic findings get batched into reports. Corrective action plans include timelines, owners, and follow-up verification.

### Fagan Inspection — Batch (Rework Phase)

Already covered in initial grounding. Detection during inspection meeting, resolution deferred to rework phase. Separation of detection and correction is a core Fagan principle.

### Cross-Domain Pattern

| Domain | Decision timing | Application timing |
|--------|----------------|-------------------|
| Backlog refinement | Immediate | Immediate |
| Architecture review | During meeting | After meeting (batch) |
| Defect triage | Immediate (assignment) | After meeting (resolution) |
| Safety walkthrough | Immediate | Immediate |
| Safety audit | During audit | After audit (batch report) |
| Fagan inspection | During meeting | After meeting (rework phase) |

**Convergence finding:** Two patterns emerge:
1. **Triage/grooming sessions** — decisions and recording are immediate (tools open during meeting)
2. **Formal reviews/audits** — decisions recorded during meeting, implementation batched after

The outline's batch-apply design (D-2) aligns with the formal review pattern. This is the correct choice for /proof because: (a) the artifact under review shouldn't change while being reviewed (Fagan principle), (b) batch application prevents the 2/2 agent failure pattern, and (c) planning artifact review is closer to formal review than to triage.

The backlog refinement "immediate" pattern is not a counterargument — in backlog refinement, the reviewed items are metadata (priority, estimates) that can be updated without changing the artifact's content. In /proof, verdicts change the artifact's text.

---

## Gap D-7: Per-Item Cognitive Load Threshold

### Existing Session-Level Data (Summary)

- Cisco/SmartBear: 200-400 LOC per review session, 60-90 min sessions, effectiveness drops past 400 LOC/hr review speed
- Fagan: 150-300 LOC/hr preparation rate, 8-12 pages per inspection for documents

### Per-Item / Per-Segment Data

**Sources:**
- [Cognitive Load Cliff (Rishi Baldawa)](https://rishi.baldawa.com/posts/pr-throughput/cognitive-load-cliff/)
- [Cisco/SmartBear Case Study](https://static0.smartbear.co/support/media/resources/cc/book/code-review-cisco-case-study.pdf)
- [Fagan Inspection (Grokipedia)](https://grokipedia.com/page/Fagan_inspection)
- [Qualicen: How-to Requirement Reviews](https://www.qualicen.de/how-to-requirement-reviews/)

**Code review per-chunk data:**
- LinearB 2025 analysis (6.1M PRs, 3,000 teams): elite teams average under 219 LOC per PR, 75th percentile under 98 LOC
- Below 300 lines: meaningful architectural feedback. Past 600 lines: only style/typo comments
- Working memory constraint: ~4 items simultaneously (consistent with Miller's 7+/-2 for chunks, Cowan's 4 for unrelated items)
- Optimal review target: reviewable in ~10 minutes per segment for maximum defect detection

**Document review per-item data:**
- Fagan: 4-6 pages/hour for documentation preparation, material scope limited to 8-12 pages per inspection session
- Requirements review: "not more than about ten per group" for logical requirement groupings (Qualicen)
- Requirements review sessions: max 2 hours recommended
- Legal document review (e-discovery, different domain but calibrating): 44-50 documents/hour for simple relevance decisions, 25/hour with redaction
- Pre-trip inspection checklists: 30-50 items optimal, 15-20 minutes

**Gap: No direct per-item size threshold for planning artifacts.**

The research provides session-level bounds (items per session, pages per session) and per-item review speed (pages/hour, LOC/hour), but not a "maximum size for a single review item before it should be split." The closest data points:

- Fagan's 5% reinspection threshold (if rework exceeds 5% of inspected material, reinspect) is about rework scope, not item size
- The 10-minute reviewability target (Cisco) is the best proxy: if a single item takes longer than ~10 minutes of focused review, it may be too large
- Requirements grouping of ~10 items per group (Qualicen) gives a per-group bound but not per-item

**Implication for D-7:** The outline's hierarchical granularity detection (large items auto-split into sub-items) is grounded in the general principle that working memory limits (~4 concurrent items) constrain comprehension. But a specific LOC or page threshold for "when to split" cannot be grounded in existing research for planning artifacts. The 10-minute reviewability heuristic from Cisco is the best available proxy, though it was derived from code review, not document review.

**Recommendation:** State the auto-split threshold as ungrounded in the design. Use the 10-minute reviewability heuristic as a design rationale (not a measured threshold). The agent can apply judgment about item size without a hard threshold — the design should describe when splitting is appropriate (item requires scrolling, item has multiple independent concerns) rather than specifying a metric.

---

## Gap D-8: Skip/Deferred Item Outcome Semantics

### Fagan Inspection

**Sources:**
- [Fagan Inspection (Grokipedia)](https://grokipedia.com/page/Fagan_inspection)
- [IEEE 1028-1997 (via silo.tips)](https://silo.tips/download/ieee-standard-for-software-reviews)

**Deferred items in Fagan:** The rework report documents "any unresolved issues deferred for later resolution." In follow-up, "minor defects addressed or formally accepted with rationale." The moderator audits "any unresolved items to determine appropriate resolution paths."

Key principle: **deferred items require explicit disposition.** They don't silently persist — they must be "formally accepted with rationale" or scheduled for resolution. The moderator is responsible for verifying resolution of ALL items, including deferred ones.

**IEEE 1028 action item tracking:** Action items have two states: **open** or **closed**, with ownership and target date (if open) or completion date (if closed). The inspection leader must verify that all action items are closed. There is no "deferred" state in the formal tracking — items are either open (unresolved) or closed (resolved).

### Audit Findings

**Sources:**
- [AuditFindings: Audit Findings Lifecycle](https://www.auditfindings.com/audit-findings-lifecycle/)
- [2 CFR 200.511 (via law.cornell.edu)](https://www.law.cornell.edu/cfr/text/2/200.511)

**Federal audit finding status categories (2 CFR 200.511):**
- **Corrected** — fully resolved, summary lists finding and states corrective action taken
- **Not corrected / Partially corrected** — must describe reasons for recurrence, planned corrective action, and partial actions taken
- **No longer valid / Does not warrant further action** — auditee must describe reasons; valid only after 2 years have passed and the federal agency is not currently following up

Key principle: **there is no silent deferral.** Every prior finding must appear in the summary schedule with an explicit status. The "no longer valid" category requires affirmative justification, not mere omission.

### Safety/Audit Checklists

**Sources:**
- [Safety Audit Checklist (citoolkit)](https://citoolkit.com/templates/safety-audit-checklist/)
- [SafetyCulture: Corrective Action](https://safetyculture.com/topics/corrective-action/)

Per-item states: Pass / Fail / Not Applicable. There is no "skip" or "deferred" state. Items are either evaluated or marked N/A with justification. N/A is not skip — it means the item is inapplicable to this context, not that the reviewer chose not to evaluate it.

### Defect Triage

**Sources:**
- [SoftwareTestingMaterial: Defect Triage](https://www.softwaretestingmaterial.com/defect-triage-meeting/)
- [Atlassian: Bug Triage](https://www.atlassian.com/agile/software-development/bug-triage)

Every defect gets a disposition: fix now, defer, won't fix, duplicate, not a defect, or cannot reproduce. **Defer** is an explicit action with intended future handling, not an absence of decision. The defer category routes to a future release — it has an implied timeline.

### Cross-Domain Convergence

| Domain | "Skip" equivalent | Handling |
|--------|-------------------|----------|
| Fagan inspection | Deferred in rework report | Must be "formally accepted with rationale" or resolved |
| IEEE 1028 | No skip state | All action items must reach closed status |
| Federal audit | "No longer valid" | Requires affirmative justification + 2-year waiting period |
| Safety checklist | N/A | Must provide justification; N/A != skip |
| Defect triage | Defer | Explicit routing to future release |
| ADR lifecycle | Deprecated | Explicit transition with rationale |

**Convergence finding:** No established review process supports silent skipping. Every domain requires:
1. **Explicit disposition** — every item gets a status, even if that status is "deferred" or "not applicable"
2. **Justification for non-action** — deferral/NA requires stated reasons
3. **Tracking obligation** — deferred items carry forward and must be resolved eventually (audit) or formally accepted (Fagan)
4. **Completeness requirement** — reviews are not complete until all items have a disposition

**Implication for D-8:** The outline's `skip` verdict needs clearer semantics. Based on this research:

- Skip should NOT mean "silently ignored." It should mean "explicitly deferred with tracking."
- Skipped items should appear in the apply summary with a distinct status (not lumped with approved items).
- Skipped items do NOT block apply — the review can complete with skipped items (unlike IEEE 1028 which requires all items closed, /proof is a lighter-weight process).
- The summary should surface skipped items prominently so the user can decide whether to revisit them or accept them as-is.
- "Accept as-is without review" is the closest semantic: the item persists unchanged, and the reviewer has acknowledged they chose not to evaluate it.

---

## Summary of Findings

| Gap | Key finding | Design implication |
|-----|------------|-------------------|
| D-1 | 3-6 per-item states across domains; triage model (routing to action buckets) is best fit for planning artifacts | Outline's 4-verdict model (a/r/k/s) is well-calibrated. Absorb (kill sub-action) grounded in backlog refinement merge + defect duplicate. Split action not needed (review disposes, doesn't create). |
| D-2 | Formal reviews batch; triage sessions are immediate. Planning artifact review is closer to formal review. | Outline's batch-apply (D-2) is the correct pattern. Artifact should not change during review (Fagan principle). |
| D-7 | No per-item size threshold exists in literature for planning artifacts. Best proxy: 10-minute reviewability heuristic (Cisco, code-derived). Requirements grouped ~10 per group. | State auto-split threshold as ungrounded. Use judgment-based splitting (multiple independent concerns, requires scrolling) rather than a metric. |
| D-8 | No established process supports silent skipping. All require explicit disposition + justification for non-action. | Skip = "explicitly deferred, accept as-is without review." Must appear in summary. Does not block apply. |
