# Interactive Review: Supplementary Grounding Report

**Grounding:** Strong — extends initial grounding with 4 additional domains (backlog refinement, architecture review, defect triage, safety/audit). 20+ named sources across domains. Convergence findings validate outline decisions with one revision (D-8 skip semantics).

---

## Framework Mapping

### Domains Surveyed (Supplementary)

| Domain | Sources | Key Contribution |
|--------|---------|-----------------|
| Backlog refinement (Scrum/Agile) | Agile Alliance, Atlassian, Scrum.org, MoSCoW | 6-7 per-item actions including split/absorb |
| Architecture review (ATAM, ADR, PDR/CDR) | SEI/CMU, Mozilla, AWS, JPL | Classification taxonomy (risk/sensitivity/tradeoff), not action verdicts |
| Process/safety inspection | IEEE 1028, safety checklists, citoolkit | Binary pass/fail/NA per item; no skip state |
| Defect triage | GeeksforGeeks, Atlassian, ThinSys | 5-6 resolution categories (fix/defer/wontfix/duplicate) |
| Cognitive load (per-item) | Cisco/SmartBear, Qualicen, LinearB | No per-item threshold for planning artifacts |
| Audit findings lifecycle | 2 CFR 200.511, AuditFindings.com | No silent deferral; explicit disposition required |

### Internal Patterns Mapped

| Internal Pattern | External Analog | Mapping Tightness |
|-----------------|-----------------|-------------------|
| Per-artifact corrector dispatch (outline→outline-corrector, design→design-corrector) | Per-domain review criteria variation | Tight — same principle (review axes vary by artifact type) |
| Corrector DEFERRED status with report section | Fagan deferred-with-rationale, audit explicit disposition | Tight — both require non-silent tracking |
| Corrector batch pattern (discover→report→fix all) | Fagan detection-then-rework, architecture action-items-after-meeting | Tight — same separation |
| Deliverable-review per-type axes (code vs prose vs agentic) | ATAM per-quality-attribute analysis | Moderate — internal varies review criteria, ATAM varies classification |

---

## Adaptations

### D-1: Verdict Vocabulary — Uniform Across Artifact Types

**General principle:** Review domains converge on 3-6 per-item states, but the *nature* of states differs by domain: checklist domains use binary evaluation (pass/fail), triage domains use routing decisions (action buckets), analysis domains use classification taxonomies (risk/sensitivity). The appropriate model depends on what the reviewer is doing with each item.

**Project adaptation:** Planning artifact review is triage — the reviewer routes items into action buckets (keep, change, remove, defer). The 4-verdict model (a/r/k/s) maps directly to triage vocabulary and is well-calibrated for all planning artifact types.

**Decision: Uniform verdicts, not per-type vocabularies.** The initial outline hypothesized artifact-type-dependent verdict vocabularies (D-1). Supplementary grounding shows the variation across domains is in *review criteria* (what to evaluate), not in *verdict actions* (what to do with findings). The codebase already handles review-criteria variation through per-artifact corrector dispatch (outline-corrector evaluates soundness/completeness, design-corrector evaluates architectural fitness). Verdict vocabulary is orthogonal — it describes the reviewer's *routing decision*, which is the same regardless of artifact type.

**Absorb (kill sub-action):** Well-grounded. Backlog refinement has merge/absorb as a standard action. Defect triage has duplicate (same concept — consolidate into existing item). Present for planning artifacts, absent for code review — but this is a sub-action of kill, not a separate verdict, so it doesn't violate uniformity.

**Split:** Present in backlog refinement (decompose large stories) but excluded from this design. The review disposes existing items; it doesn't create new ones. Split would require the reviewer to define new items during review — a creation action that conflicts with the detection-not-resolution principle (Fagan). If an item needs splitting, `revise` with "split this into X and Y" captures the intent; the rework phase handles the creation.

### D-2: Batch Application — Confirmed

**General principle:** Formal review processes separate detection from resolution. Fagan inspection, architecture review (ATAM, PDR/CDR), and safety audits all produce findings during the review session and apply changes after. Triage sessions (backlog grooming, defect triage) apply decisions immediately because they're modifying metadata (priority, assignment), not artifact content.

**Project adaptation:** Planning artifact review modifies artifact content (text edits, item deletion, content transfer). This places it in the formal review category, not triage. Batch-apply is the correct pattern:
- Artifact unchanged during review (Fagan detection-rework separation)
- Full verdict list available before edit dispatch (prevents 2/2 agent failure pattern)
- Corrector operates on final state, not intermediate states

**No domain-specific batch/immediate variation needed.** The batch pattern is universal for content-modifying review. The immediate pattern applies only to metadata updates (backlog priority, bug assignment) which are outside /proof's scope.

### D-7: Per-Item Size — Ungrounded Threshold, Judgment-Based Splitting

**General principle:** Cognitive load research establishes session-level bounds (200-400 LOC per session, 60-90 minutes, 8-12 pages per inspection) and review speed (150-300 LOC/hr for code, 4-6 pages/hr for documents). No research establishes a per-item size threshold for when a single review item should be split.

**Best available proxies:**
- 10-minute reviewability heuristic (Cisco): if a single item takes >10 minutes of focused review, effectiveness drops — derived from code review, not document review
- Requirements grouping: ~10 items per logical group (Qualicen) — session bound, not per-item
- Working memory: ~4 concurrent items (Cowan) — limits how many sub-concerns an item can contain before comprehension degrades

**Project adaptation:** The auto-split threshold in D-7 cannot be grounded in a specific metric. State this explicitly in the design. Replace metric-based splitting with judgment-based indicators:
- Item contains multiple independent concerns (working memory overload)
- Item requires scrolling past a single screen (visual context loss)
- Item has internal structure (sub-headings, enumerated sub-items) suggesting natural decomposition points

The agent applies these indicators during granularity detection. No hard threshold — the indicators are qualitative cues, not quantitative gates.

### D-8: Skip Semantics — Explicit Deferral, Non-Blocking

**General principle:** No established review process supports silent skipping. Every surveyed domain requires explicit disposition for every item:
- Fagan: deferred items must be "formally accepted with rationale" or resolved
- IEEE 1028: all action items must reach closed status (no deferred state)
- Federal audit (2 CFR 200.511): every prior finding must appear in summary with explicit status
- Safety checklists: items are pass/fail/NA — NA requires justification, is not skip
- Defect triage: defer is an explicit routing decision with implied future timeline

**Convergence:** Skip is not absence of decision — it is an explicit decision to accept the item as-is without evaluation. Four properties:

1. **Explicit disposition** — skip appears in the verdict list with the same structure as other verdicts (V-N: [item] — skip)
2. **Non-blocking** — skipped items do not prevent apply. The review completes with skipped items present (lighter-weight than IEEE 1028's all-closed requirement; consistent with /proof's existing tolerance for partial review)
3. **Summary visibility** — skipped items appear prominently in the apply summary: "N approved, N revised, N killed, **N skipped (unchanged)**"
4. **No tracking obligation** — unlike audit findings, skipped items do not carry forward as open items or become pending tasks automatically. The reviewer sees them in the summary and decides whether to revisit (loop action) or accept as-is. The conversational medium handles follow-up naturally — no formal tracking mechanism needed.

**Semantic definition:** Skip = "I choose not to evaluate this item now. It persists unchanged in the artifact. I acknowledge this explicitly." Not silent omission, not implicit approval, not deferred-with-future-obligation.

---

## Grounding Assessment

**Quality label:** Strong

**Evidence basis:**
- Initial grounding: 4 frameworks (Fagan, IEEE 1028, Gerrit, Phabricator) + cognitive load research — retained, still valid
- Supplementary: 4 additional domains (backlog refinement, architecture review, defect triage, safety/audit) with 20+ named sources
- Cross-domain convergence validates 3 of 4 outline decisions (D-1 verdicts, D-2 batch, D-8 skip)
- D-7 threshold confirmed as ungrounded across all surveyed literature — honest gap, not missing research
- Internal codebase patterns (corrector batch, per-artifact dispatch, DEFERRED tracking) independently confirm external findings

**Gap analysis:**
- Per-item size threshold for planning artifacts: no research exists. 10-minute heuristic (code-derived) is best available proxy. Stated as ungrounded in design.
- Architecture review verdict vocabulary: ATAM uses analytical classification (risk/sensitivity/tradeoff), not action verdicts. This is a different review paradigm — ATAM's contribution is to the corrector's analysis framework, not to the interactive reviewer's verdict vocabulary.

**Design changes from supplementary grounding:**
- D-1: Verdict vocabulary is **uniform**, not artifact-type-dependent (outline hypothesized variation; research shows variation is in review criteria, not verdicts — criteria variation already handled by corrector dispatch)
- D-7: Auto-split threshold stated as **ungrounded**; use judgment-based indicators instead of metric
- D-8: Skip semantics defined: **explicit deferral, non-blocking, visible in summary, no tracking obligation**
- D-2: Confirmed as-is (batch-apply)

---

## Sources

### Primary Sources (Supplementary)

- **Agile Alliance.** Backlog Refinement glossary. Per-item grooming actions. Retrieved via: agilealliance.org
- **Atlassian.** Backlog Refinement, Bug Triage guides. Retrieved via: atlassian.com
- **Scrum.org.** Product Backlog Refinement Explained. Retrieved via: scrum.org
- **SEI/CMU.** ATAM Technical Report (CMU/SEI-2000-TR-004). Architecture evaluation method. Retrieved via: sei.cmu.edu
- **Mozilla.** Firefox Architecture Review Process. Post-meeting action item pattern. Retrieved via: mozilla.github.io
- **AWS.** Well-Architected Review Process. Retrieved via: docs.aws.amazon.com
- **IEEE 1028-1997.** Software Reviews and Audits standard. Action item open/closed states. Retrieved via: silo.tips
- **2 CFR 200.511.** Federal audit finding status categories. No silent deferral. Retrieved via: law.cornell.edu
- **Qualicen.** How-to Requirement Reviews. ~10 items per logical group. Retrieved via: qualicen.de

### Secondary Sources (Supplementary)

- **Cisco/SmartBear** (2006). Extended analysis — 10-minute reviewability proxy. Retrieved via: smartbear.co, Rishi Baldawa
- **LinearB** (2025). 6.1M PRs, 3,000 teams — elite teams <219 LOC. Retrieved via: Rishi Baldawa
- **GeeksforGeeks, SoftwareTestingMaterial, ThinSys, Shakebugs.** Defect triage meeting guides. Retrieved via respective sites
- **SafetyCulture, citoolkit, HSE Coach.** Safety audit checklist patterns. Retrieved via respective sites
- **AuditFindings.com.** Audit findings lifecycle. Retrieved via: auditfindings.com

### Branch Artifacts (Audit Evidence)

- `plans/reports/interactive-review-supplementary-internal.md` — internal codebase exploration (4 gaps)
- `plans/reports/interactive-review-supplementary-external.md` — external domain research (4 gaps)
- `plans/reports/interactive-review-grounding.md` — initial grounding report (retained)
- `plans/reports/interactive-review-internal-codebase.md` — initial internal branch
- `plans/reports/interactive-review-external-research.md` — initial external branch
