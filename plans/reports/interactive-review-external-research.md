# Interactive Review: External Research

Research into established frameworks for structured, item-by-item review of software artifacts. Covers formal inspection methodologies, standards, modern code review tool UX, and cognitive load research.

---

## 1. Fagan Inspection (1976)

The foundational structured software inspection method, developed by Michael Fagan at IBM.

### Process Phases

Six sequential phases, with iteration on phases 3-5:

1. **Planning** — Moderator forms team, gathers materials, distributes documents
2. **Overview** — Author describes background; team educated on work product
3. **Preparation** — Individual review; inspectors note potential defects independently
4. **Inspection Meeting** — Structured group defect detection (core phase)
5. **Rework** — Author fixes identified defects
6. **Follow-up** — Moderator verifies all fixes; checks for secondary defects

### Inspection Meeting Mechanics (Item-by-Item)

The meeting is the central innovation. The **reader** paraphrases material section-by-section:
- **Code:** line-by-line
- **Documents:** clause-by-clause

The reader reconstructs the author's intent through paraphrase (not reading verbatim). Inspectors raise defects identified during preparation. Key rules:

- **Detection only, no resolution.** Defects are logged; solutions are deferred to rework.
- **Author cannot defend.** May provide clarification but is prohibited from debating the material.
- **Moderator controls flow.** Enforces time limits, keeps discussion focused on defects.
- **Recorder logs defects in real-time.** Each defect classified and recorded during the meeting.

### Roles

| Role | Responsibility |
|------|---------------|
| Moderator | Schedules, controls meeting, enforces process, verifies rework |
| Author | Creator of the artifact; clarifies but doesn't defend |
| Reader | Paraphrases material to drive discussion |
| Recorder | Documents defects as they are raised |
| Inspector | General role — all participants inspect for defects |

### Defect Classification

Two severity levels:
- **Major** — Incorrect or missing functionality; software will not function correctly if unfixed
- **Minor** — Non-functional issues (spelling, cosmetic, formatting)

### Review Rates and Limits

- **Code:** 150-500 lines/hour (preparation: 150-300 lines/hour)
- **Documents:** 4-6 pages/hour
- **Meeting duration:** Maximum 2-3 hours
- **Re-inspection trigger:** Rework exceeds 5% of inspected material

### Entry/Exit Criteria

**Entry:** Work product complete, stable, compiles cleanly, no unresolved dependencies.
**Exit:** All major defects fixed; minor defects resolved or formally accepted; defect density below established threshold; no secondary defects introduced.

### Effectiveness Data

- 70-85% defect detection rate (>90% in optimized implementations)
- IBM: 82% detection efficiency in initial testing
- 15-20x fewer customer-found defects
- ROI: 3:1 to 30:1

### Relevance to Artifact Review

High. Fagan inspection applies to any software artifact (requirements, design docs, code). The reader-paraphrase + item-by-item mechanics are directly applicable to non-code artifacts. The strict detection-not-resolution rule and author-cannot-defend rule are key ergonomics decisions.

**Sources:**
- [Fagan inspection — Grokipedia](https://grokipedia.com/page/Fagan_inspection)
- [Fagan Inspection — en-academic.com](https://en-academic.com/dic.nsf/enwiki/590590)
- [Fagan Inspection — ProfessionalQA](https://www.professionalqa.com/fagan-inspection)
- [iSixSigma: Fagan Style Software Inspection](https://www.isixsigma.com/dictionary/fagan-style-software-inspection/)

---

## 2. IEEE 1028 Standard for Software Reviews and Audits

IEEE 1028 (versions: 1988, 1997, 2008) defines five review types with procedures for each. It distinguishes review types by formality, leadership, and purpose.

### Five Review Types

| Type | Led By | Purpose | Formality |
|------|--------|---------|-----------|
| **Management Review** | Management | Decision-making on project status | Formal |
| **Technical Review** | Technical lead | Arrive at technically superior version | Semi-formal |
| **Inspection** | Trained moderator | Detect and identify anomalies | Most formal |
| **Walkthrough** | Author | Present work for peer feedback | Least formal |
| **Audit** | Independent auditor | Compliance verification | Formal |

### Key Distinctions

**Inspection vs Walkthrough:**
- Inspection: structured phases, defined roles, checklists, detection-focused. Moderator-led. 1.54x more effective at defect detection than walkthroughs.
- Walkthrough: flexible, author-led, discussion-focused, no predefined steps.

**Inspection vs Technical Review:**
- Inspection: focused on defect detection; cannot suggest alternatives
- Technical review: can suggest direct alterations and alternative approaches; lacks focus on training/process improvement

### Verdict Vocabulary

IEEE 1028 does not define per-item verdicts in the modern tool sense. The inspection outcome is a disposition of the work product:
- Defects logged with classification (major/minor)
- Work product accepted, accepted with rework, or re-inspection required

### Relevance to Artifact Review

The standard's taxonomy of review types is useful for positioning an item-by-item review mode. The inspection type (moderator-led, checklist-driven, detection-focused) is the closest analog. The standard confirms that structured inspection outperforms unstructured walkthrough.

**Sources:**
- [IEEE 1028-2008 Standard](https://standards.ieee.org/ieee/1028/1502/)
- [IEEE 1028-1997 — IEEE Xplore](https://ieeexplore.ieee.org/document/663254/)
- [Software review — Wikipedia](https://en.wikipedia.org/wiki/Software_review)
- [Difference between Inspection and Walkthrough — GeeksforGeeks](https://www.geeksforgeeks.org/software-engineering/difference-between-inspection-and-walkthrough/)

---

## 3. GitHub Pull Request Reviews

GitHub's review system is the most widely-used modern code review UX.

### Verdict Vocabulary (Per-Review, Not Per-Item)

Three actions available when submitting a review:

| Action | Effect | Blocks Merge? |
|--------|--------|---------------|
| **Comment** | General feedback, no status change | No |
| **Approve** | Marks PR as approved | No (enables merge) |
| **Request Changes** | Marks PR as requiring changes | Yes (with branch protection) |

### Per-Item Mechanics

GitHub operates at **two levels**:
1. **Inline comments** — attached to specific lines/ranges in the diff. These are per-item observations.
2. **Review submission** — aggregates all pending inline comments with an overall verdict (Comment/Approve/Request Changes).

Inline comments are initially **drafts** (visible only to author) until the review is submitted. No per-item verdict — the verdict is at the review level.

### Review Lifecycle

1. Reviewer opens diff, leaves inline comments on specific lines
2. Reviewer submits review with overall verdict
3. Author addresses feedback, pushes new commits
4. Stale reviews can be **dismissed** by admins (converts to comment, removes blocking status)
5. Re-review requested after changes

### Navigation

- File-by-file navigation through the diff
- "Viewed" checkbox per file (tracks reviewer progress)
- Files can be reviewed in any order (random access)
- Conversations can be "resolved" individually

### Ergonomics Findings

- No per-item severity classification — all feedback is equal weight
- "Request Changes" used conservatively to avoid slowing development
- Teams often pair "Comment" with minor suggestions rather than blocking
- No built-in checklist or structured inspection flow

### Relevance to Artifact Review

Limited for item-by-item artifact review. GitHub's model is diff-centric (reviewing changes to code), not artifact-centric (reviewing a document's items). The inline-comment-then-aggregate-verdict pattern is relevant. The lack of per-item verdicts is a gap this design could fill.

**Sources:**
- [GitHub PR Reviews: Comment vs. Approve vs. Request Changes — DEV Community](https://dev.to/msnmongare/github-pr-reviews-comment-vs-approve-vs-request-changes-when-to-use-each-1ph2)
- [Reviewing proposed changes — GitHub Docs](https://docs.github.com/articles/reviewing-proposed-changes-in-a-pull-request)
- [Dismissing a pull request review — GitHub Docs](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/dismissing-a-pull-request-review)
- [GitHub PR Review Workflow — Graphite](https://graphite.com/guides/github-pull-request-review-workflow)

---

## 4. Gerrit Code Review

Gerrit uses a numeric voting system with configurable labels, originally developed for the Android Open Source Project.

### Verdict Vocabulary (Numeric Scores)

#### Code-Review Label (default)

| Score | Meaning | Effect |
|-------|---------|--------|
| **-2** | "This shall not be submitted" | Blocks submission (hard veto) |
| **-1** | "I would prefer this is not submitted as is" | Advisory objection (non-blocking) |
| **0** | No opinion | Neutral |
| **+1** | "Looks good to me, but someone else must approve" | Supportive but insufficient |
| **+2** | "Looks good to me, approved" | Enables submission |

Key distinction: **+1/-1 are opinions; +2/-2 are decisions.** A -2 is a hard block that the reviewer must actively remove. Submission requires at least one +2 and zero -2 votes.

#### Verified Label

| Score | Meaning |
|-------|---------|
| **-1** | Fails verification (blocks) |
| **0** | No score |
| **+1** | Verified (passes) |

#### Custom Labels

Projects can define custom labels with arbitrary score ranges and descriptions. Label configuration includes:
- Score values with descriptions (e.g., `-1 Do not approve`, `+1 Approved`)
- Default values
- Branch restrictions

### Label Functions (Vote Combination Logic)

How multiple votes combine for submission:

| Function | Behavior |
|----------|----------|
| **MaxWithBlock** | Highest positive required; any negative blocks |
| **AnyWithBlock** | Negative blocks; positive not mandatory |
| **MaxNoBlock** | Highest positive required; negatives don't block |
| **NoBlock/NoOp** | Informational only |

### Sticky Votes and Patch Sets

Votes can be configured to **carry forward** across patch set updates via copy conditions. Non-copied votes become "outdated." This addresses the stale-review problem: when code changes, do prior verdicts still apply?

### Navigation

- Inline comments on specific lines
- Per-file review with diff view
- Comments carry forward across patch sets with tracking

### Relevance to Artifact Review

High for verdict vocabulary design. The 5-point scale (-2 to +2) with distinct semantics at each level is a proven pattern. The opinion-vs-decision distinction (+1/-1 vs +2/-2) is particularly relevant — it separates "I have a concern" from "this must not proceed." Custom labels show the value of domain-specific verdict dimensions.

**Sources:**
- [Gerrit Code Review — Review Labels](https://gerrit-review.googlesource.com/Documentation/config-labels.html)
- [Gerrit's approach to code review — Graphite](https://graphite.com/guides/gerrits-approach-to-code-review)
- [Gerrit Review Score Cards — Graphite](https://graphite.com/guides/gerrit-review-score-cards-a-unique-approach-to-code-quality)
- [Working with Gerrit: An example](https://gerrit-review.googlesource.com/Documentation/intro-gerrit-walkthrough.html)

---

## 5. Phabricator Differential

Phabricator's code review tool, used by Facebook, LLVM, Wikimedia, and others. Notable for its rich state machine and inline comment model.

### Revision States

| State | Meaning |
|-------|---------|
| **Needs Review** | Initial state; awaiting reviewer action |
| **Accepted** | Reviewer approved; ready to land |
| **Needs Revision** | Reviewer requested changes |
| **Changes Planned** | Author acknowledged feedback; removed from reviewer queues |
| **Abandoned** | Author marked as no longer relevant |
| **Draft** | Not yet submitted for review |

### Reviewer Actions

| Action | Who | Effect |
|--------|-----|--------|
| **Accept** | Reviewer | Moves to Accepted ("can be landed, or at most requires small changes that do not need re-review") |
| **Request Changes** | Reviewer | Moves to Needs Revision |
| **Resign** | Reviewer | Removes self from reviewer list; stops notifications |

### Author Actions

| Action | Who | Effect |
|--------|-----|--------|
| **Request Review** | Author | Resets to Needs Review; prior acceptances become "Accepted Prior Diff" (greyed-out) |
| **Plan Changes** | Author | Removes from reviewer queues temporarily |
| **Abandon** | Author | Marks as no longer relevant |
| **Reclaim** | Author | Reopens an abandoned revision |
| **Reopen** | Author | Reopens a closed revision |

### Special Actions

| Action | Who | Effect |
|--------|-----|--------|
| **Commandeer** | Non-author | Takes over revision authorship |

### Inline Comments

- Click line number to comment on a specific line
- Click-and-drag for range comments on adjacent lines
- Comments are initially **unsubmitted drafts** (marked with "Unsubmitted" badge)
- Published in batch when submitting the review form (alongside optional overall comment and action)
- Inline comments serve as audit trail; can be revisited

### Stale Review Handling

When an author updates a revision after acceptance, the acceptance becomes "Accepted Prior Diff" (shown as a greyed-out checkmark). This makes staleness visible without automatically invalidating the review.

### Relevance to Artifact Review

High. Phabricator's state machine is the most complete of the tools surveyed. Key design insights:
- **Changes Planned** state is unique — lets the author signal "I know, working on it" without requiring reviewer re-engagement
- **Draft comments published in batch** — reduces notification noise, lets reviewer build a complete picture before submitting
- **Accept semantics include "small changes OK"** — avoids the re-review loop for trivial fixes
- **Greyed-out prior acceptance** — makes staleness visible without hard invalidation

**Sources:**
- [Differential User Guide — Phabricator](https://secure.phabricator.com/book/phabricator/article/differential/)
- [Differential: Phabricator's Code Review Application — Graphite](https://graphite.com/guides/differential-phabricators-code-review-application)
- [Differential Inline Comments — Phabricator](https://secure.phabricator.com/book/phabricator/article/differential_inlines/)
- [Mozilla Phabricator User Guide](https://moz-conduit.readthedocs.io/en/latest/phabricator-user.html)

---

## 6. Cognitive Load and Review Effectiveness Research

Empirical research on what makes reviews effective or ineffective, primarily from Cisco/SmartBear and Microsoft studies.

### Optimal Review Parameters

| Parameter | Threshold | Source |
|-----------|-----------|--------|
| Batch size | 200-400 lines of code | Cisco 2006 (2,500 reviews) |
| Review rate | <450 lines/hour | Cisco 2006 |
| Session length | 60 minutes optimal, 90 max | Cisco 2006 |
| Elite team PR size | <219 LOC (75th percentile: <98 LOC) | LinearB 2025 |

### Key Findings

**The cognitive load cliff:** When reviewers exceed 450 lines/hour, 87% of reviews have below-average defect detection. The degradation is "faster than linear" — effectiveness drops sharply, not gradually.

**Qualitative shift with size:** Reviews under 300 lines receive architectural feedback and edge-case discussion. Past 600 lines, comments shift "almost entirely to style issues, typos, and obvious bugs." The reviewer's cognitive capacity is consumed by comprehension, leaving nothing for deep analysis.

**Microsoft's 1.5M comment study:** Approximately one-third of review comments are not useful to the author. As changeset files increase, the proportion of valuable feedback decreases (despite more total comments).

**Checklist effectiveness:** Guided checklists lower cognitive demands through "segmenting and weeding" — breaking the review into focused sub-tasks and filtering out irrelevant concerns per segment. This is the research basis for checklist-driven inspection.

### Implications for Item-by-Item Review

- **Segmentation reduces cognitive load.** Presenting items one at a time rather than as a batch is supported by the segmenting research.
- **Linear presentation prevents skip-ahead bias.** Reviewers who can see all items tend to triage by apparent complexity, skipping "boring" items where defects often hide.
- **Time-boxing matters.** Beyond 60-90 minutes, defect detection drops regardless of review structure.
- **Verdict per item forces engagement.** Requiring a decision on each item prevents passive scanning.

**Sources:**
- [The Cognitive Load Cliff in Code Review — Rishi Baldawa](https://rishi.baldawa.com/posts/pr-throughput/cognitive-load-cliff/)
- [Do explicit review strategies improve code review performance? — Springer](https://link.springer.com/article/10.1007/s10664-022-10123-8)
- [Associating working memory capacity and code change ordering — Springer](https://link.springer.com/article/10.1007/s10664-018-9676-8)
- [Software Inspection Checklist — GeeksforGeeks](https://www.geeksforgeeks.org/software-inspection-checklist/)

---

## 7. Defect Classification Taxonomies

Cross-cutting concern: how defects/findings are classified across frameworks.

### Severity Scales

| Framework | Levels | Scale |
|-----------|--------|-------|
| Fagan Inspection | 2 | Major, Minor |
| IEEE 1028 | 2 | Major, Minor (anomalies) |
| Industry standard (QA) | 3 | Critical, Major, Minor |
| Gerrit (numeric) | 5 | -2, -1, 0, +1, +2 |
| GitHub | 1 | (no severity; all comments equal) |

### Industry Standard 3-Level Classification

- **Critical** — Renders artifact unusable; security breach; core functionality collapse; no workaround
- **Major** — Central functionality impacted; workaround may exist; affects usability or correctness
- **Minor** — Cosmetic, stylistic, or trivial; does not affect functionality

### Code Inspection Fault Categories (Checklist-Driven)

Specialized checklists organize defects by type:
- **Data faults** — initialization, naming, overflow
- **Control faults** — logic, termination, branching
- **Input/Output faults** — variable usage, unexpected input
- **Interface faults** — parameter count/type/ordering
- **Storage management faults** — allocation, deallocation
- **Exception management faults** — error condition coverage

### Relevance to Item-by-Item Review

For artifact review (not code), the 3-level severity (critical/major/minor) is the most common and well-understood. Fagan's 2-level (major/minor) is simpler but loses the "showstopper" distinction. Gerrit's numeric scale is powerful but requires training on score semantics.

**Sources:**
- [Defect Taxonomy — testRigor](https://testrigor.com/blog/what-is-defect-taxonomy/)
- [Critical, Major & Minor Defect Classification — ProQC](https://proqc.com/quality-resources/products-defects-classification/)
- [Software Inspection Checklist — GeeksforGeeks](https://www.geeksforgeeks.org/software-inspection-checklist/)

---

## 8. Synthesis: Verdict Vocabulary Comparison

| Tool/Framework | Per-Item Verdict? | Vocabulary | Blocking Semantics |
|----------------|-------------------|------------|-------------------|
| Fagan Inspection | Yes (defect logged or not) | Major/Minor defect | Re-inspection if >5% rework |
| IEEE 1028 | Yes (anomaly logged) | Anomaly classification | Disposition: accept/rework/re-inspect |
| GitHub | No (review-level only) | Comment / Approve / Request Changes | Request Changes blocks merge |
| Gerrit | No (review-level score) | -2 to +2 numeric | -2 hard blocks; -1 advisory |
| Phabricator | No (review-level action) | Accept / Request Changes / Resign | Request Changes blocks landing |

### Observations

1. **Formal methods (Fagan, IEEE) operate per-item.** Each item gets a defect/no-defect decision during the meeting. The aggregate outcome emerges from the collection of per-item decisions.

2. **Modern tools operate per-review.** Inline comments annotate items, but the verdict is at the review level. No tool requires a per-item verdict.

3. **The gap:** No widely-adopted tool combines per-item verdicts with modern UX. This is the design space for interactive review.

4. **Verdict vocabulary convergence:** Despite different terminology, all systems converge on a 3-state model: pass (approve/accept/no-defect), conditional pass (comment/minor/+1), and block (request changes/major/-2).

5. **Batch-then-submit is universal in modern tools.** GitHub, Gerrit, and Phabricator all use draft-comments-then-submit. This reduces notification noise and lets reviewers build a complete picture.

6. **Staleness handling varies.** Phabricator's "Accepted Prior Diff" is the most nuanced. GitHub dismisses stale reviews. Gerrit uses configurable copy conditions.

---

## 9. Design Implications for Item-by-Item Review Mode

### From Fagan Inspection
- **Reader-paraphrase model:** Present each item with context (not raw text). The "reader" role in Fagan exists because raw text review misses intent.
- **Detection, not resolution:** Per-item verdicts should classify the finding, not prescribe the fix.
- **Author-cannot-defend rule:** In an automated review, this translates to: don't let the review tool rationalize away findings.
- **Rate limits:** Don't present too many items per session. Research supports 60-90 minute sessions max.

### From Modern Tool UX
- **Draft-then-submit:** Accumulate per-item verdicts, then submit the batch. Allow revision of earlier verdicts before final submission.
- **Per-item severity:** Adopt the 3-level (critical/major/minor) classification at the item level, with the review-level outcome derived from the collection.
- **Skip/defer option:** All modern tools allow reviewers to leave items unaddressed. An item-by-item mode needs an explicit "skip" or "defer" action.

### From Cognitive Load Research
- **One item at a time reduces cognitive load** (segmentation principle).
- **Force a verdict per item** to prevent passive scanning.
- **Time-box the session** — reviewer effectiveness degrades after 60-90 minutes regardless of structure.
- **Keep item count manageable** — the 200-400 LOC finding translates roughly to review sessions of bounded scope.

### Candidate Per-Item Verdict Vocabulary

Drawing from all sources surveyed:

| Verdict | Meaning | Analog |
|---------|---------|--------|
| **Pass** | Item is correct | Fagan: no defect; Gerrit: +2 |
| **Minor** | Issue found, non-blocking | Fagan: minor; Gerrit: -1 |
| **Major** | Issue found, must fix | Fagan: major; GitHub: Request Changes |
| **Critical** | Showstopper | Industry QA; Gerrit: -2 |
| **Skip** | Defer judgment | Modern tools: leave unreviewed |

Review-level outcome derived from per-item verdicts:
- Any critical → review blocked
- Any major → rework required
- Only minor/pass → accepted (minor issues noted)
