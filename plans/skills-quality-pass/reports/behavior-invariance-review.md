# Behavior Invariance Review

Independent verification of conditional-branch correctness across 6 skills after quality-pass restructuring.

**Method:** Full skill read, enumerate all conditional branches, trace user-visible output per path, compare against execution agent reports.

---

## 1. design skill

**Paths found:** 12 (execution report claimed: 10 + classification block)
**Discrepancies:** Report undercounts by 1 (requirements-clarity routing path omitted)

| # | Path | Trigger | Output/Routing | Status |
|---|------|---------|----------------|--------|
| 1 | Requirements vague | Requirements-clarity gate fails | Route to `/requirements` | OK |
| 2 | Existing design.md | Artifact check finds design.md | Route to `/runbook` (line 37) | OK |
| 3 | Existing outline sufficient | Artifact check, outline meets criteria | Skip to Phase B (line 38) | OK |
| 4 | Existing outline insufficient | Artifact check, outline lacks criteria | Resume A.5 or A.6 (lines 39-40) | OK |
| 5 | Simple classification | Triage criteria + recall | Classification block (lines 74-77) + "Simple -> Check for applicable skills..." (line 81) | OK |
| 6 | Moderate classification | Behavioral code or clear scope | Classification block + "Moderate -> Skip design. Route to /runbook" (line 82) | OK |
| 7 | Complex -> downgrade met | Post-Outline Re-check all criteria hold | Skip A.6, proceed to Phase B sufficiency (line 194) | OK |
| 8 | Complex -> downgrade not met | Post-Outline Re-check criteria fail | Continue to A.6 corrector review (line 197) | OK |
| 9 | Complex -> sufficient -> exec-ready | Sufficiency gate + direct exec criteria met | Present sufficiency, execute edits, corrector, /handoff (lines 242-254) | OK |
| 10 | Complex -> sufficient -> not exec-ready | Sufficiency gate met, exec criteria not met | Route to /runbook (lines 256-258) | OK |
| 11 | Complex -> insufficient -> C -> exec-ready | Sufficiency not met, full design, C.5 exec-ready | Execute edits + review + /handoff (line 330) | OK |
| 12 | Complex -> insufficient -> C -> not exec-ready | Full design, C.5 not exec-ready | Commit design + /handoff, next pending = /runbook (line 331) | OK |

**Additional conditional branches (non-path-level):**
- Companion tasks (line 85): each gets own Phase 0 pass. Routing, not a new terminal path.
- Session state check (line 87): >5 tasks suggests `/shelve`. Advisory, not routing.
- A.0 skill dependency scan (lines 101-116): conditional skill loading. Does not change path.
- A.1 no-requirements case (line 137): wider net on Level 1. Informational.
- A.2 delegate vs direct (lines 166-168): scope-based decision. Informational.
- A.3-5 external research needed vs not (lines 172-174): Read protocol vs skip. Informational.
- A.6 ESCALATION in review outcome (lines 219-221): Address issues vs proceed. Informational.
- C.4 UNFIXABLE issues (lines 312-315): Manual/escalate vs proceed. Informational.

**D+B gate verification (NFR-7 — no new branching):**
- Gate 12 (line 72): Glob/Grep structural check. Produces evidence for existing Simple/Moderate decision. Does not add a new branch. OK.
- Gate 1 (line 184): `Read plans/<job>/outline.md`. Loads data for existing Post-Outline Re-check. Does not add a new branch. OK.
- Gate 2 (line 231): `Read plans/<job>/outline.md`. Loads data for existing Sufficiency Gate. Does not add a new branch. OK.
- Gate 3 (line 319): `Read plans/<job>/design.md`. Loads data for existing C.5 assessment. Does not add a new branch. OK.

**Classification block output:** Lines 74-77 produce visible 3-field output (Classification, Behavioral code check, Evidence) on all triage paths. Verified present before routing section.

**Extraction gap check:** research-protocol.md contains the escape hatch (compress A+B) at line 35 — this is a conditional path within A.3-5. It was also preserved in the main SKILL.md at line 180 ("Escape hatch"). No gap. discussion-protocol.md contains convergence guidance and termination conditions (restart Phase A). These are interaction-level conditionals, not skill routing paths. design-content-rules.md contains no conditional routing — all content rules.

**Verdict:** All paths functional. The execution report's 10 paths correspond to paths 2-12 above (merging downgrade paths 7-8 into path 7). Path 1 (requirements-clarity routing) was not enumerated in the execution report but is present and functional in the skill.

---

## 2. commit skill

**Paths found:** 8 (execution report claimed: 8)
**Discrepancies:** None

| # | Path | Trigger | Output/Routing | Status |
|---|------|---------|----------------|--------|
| 1 | No artifact-prefix matches | Grep output empty | Proceed to validation (line 82) | OK |
| 2 | Trivial changes | <=5 net lines, <=2 files, additive | Self-review via `git diff HEAD` (line 83) | OK |
| 3 | Non-trivial + report exists | Report found in plans/*/reports/ or tmp/ | Proceed to validation (line 84) | OK |
| 4 | Non-trivial + no report | No review report found | STOP, delegate review first (line 84) | OK |
| 5 | Context mode | --context flag | Precommit only, skip git status -vv (lines 95-96) | OK |
| 6 | Submodule modified | git status shows modified submodule | Commit submodule first (lines 103-126) | OK |
| 7 | Precommit fails | just precommit exits non-zero | STOP (line 97) | OK |
| 8 | Nothing to commit | No staged or unstaged changes | ERROR (line 99) | OK |

**D+B gate verification (NFR-7):**
- Gate 4 (lines 76-78): Grep on `git diff --name-only` output for artifact prefixes. The grep classifies into the same three existing branches (no artifacts / trivial / non-trivial). No new branch introduced. OK.

**False positive analysis for Gate 4 Grep:** The grep pattern `'^(agent-core/|plans/|src/|agents/|\.claude/)'` matches any file path starting with these prefixes. Reports themselves (`plans/*/reports/`) would match as artifact-prefix files, but the skill already states "Reports are exempt -- they ARE the verification artifacts" (line 86). This exemption is a classification override applied after the grep, not a new path. The agent must recognize reports during the trivial/non-trivial assessment — this is judgment-level, not routing-level. No false positive risk from the Grep pattern itself creating wrong routing.

**Verdict:** All 8 paths match execution report. No issues.

---

## 3. handoff skill

**Paths found:** 6 (execution report claimed: 6)
**Discrepancies:** None

| # | Path | Trigger | Output/Routing | Status |
|---|------|---------|----------------|--------|
| 1 | Normal handoff (no prior, no --commit) | Standard invocation | Gather -> _worktree ls -> write session.md -> context -> learnings -> plan-archive -> trim -> STATUS | OK |
| 2 | With --commit flag | `/handoff --commit` | Same through step 6 -> skip STATUS -> tail-call `/commit` (lines 143-145) | OK |
| 3 | Prior uncommitted handoff | Date in header != today | Preserve as base state, merge incrementally (line 33) | OK |
| 4 | Haiku session review | Reviewing handoff-haiku session | Process Session Notes for learnings (line 31) | OK |
| 5 | Continuation suffix present | `[CONTINUATION: ...]` in args | Tail-call first entry (line 149) | OK |
| 6 | Empty continuation | No continuation, no --commit | Stop (line 149) | OK |

**Gate 5 verification:** `Bash: claudeutils _worktree ls` (line 77) loads plan lifecycle statuses before the command derivation table. The derivation table (lines 78-85) maps lifecycle status to backtick command. No new derivation rules — same 6 status mappings. Tool call grounds the derivation in filesystem state. NFR-7 satisfied.

**Gate 8 verification:** Prior handoff detection (line 33) uses structural date check: `# Session Handoff:` header with date different from today. Replaces previous conversation-comparison judgment. The decision outcome is the same (merge incrementally vs fresh write). NFR-7 satisfied.

**Continuation section:** Lines 147-151 handle continuation parsing. Two branches: present (tail-call) vs absent (stop). Both produce clear outcomes. The `--commit` flag (line 143-145) is orthogonal to continuation — with --commit, step 7 skips STATUS and hands off to /commit.

**Interaction between --commit and continuation:** The skill has `--commit` as a flag (line 23) AND continuation protocol (line 147-151). These are potentially overlapping. Reading the flow: Step 7 says "Without --commit: display STATUS" / "With --commit: Skip -- /commit displays it." Then the Continuation section says to check args suffix. The `--commit` flag appears to be a specific hardcoded path, while continuation is a general mechanism. `/handoff --commit` would trigger the --commit path (step 7 skips STATUS), then the continuation section checks for additional continuation. Since `--commit` is a flag not a continuation entry, no conflict. The default-exit in frontmatter is `["/commit"]`, so without explicit continuation, `/handoff` chains to `/commit` via default-exit. The `--commit` flag provides a shortcut for this same behavior. No dead branch.

**Verdict:** All 6 paths match execution report. No issues.

---

## 4. codify skill

**Paths found:** 7 (execution report claimed: 7)
**Discrepancies:** None

| # | Path | Trigger | Output/Routing | Status |
|---|------|---------|----------------|--------|
| 1 | Normal flow | Eligible entries exist, route to target file | learning-ages.py -> Grep candidates -> route -> draft -> apply -> discovery -> document | OK |
| 2 | No eligible entries | learning-ages.py shows all entries < 7 days | Stop (implicit — no entries to process) | OK |
| 3 | Superseded entry | Entry superseded by newer on same topic | Drop from staging (line 132) | OK |
| 4 | New fragment created | Consolidation creates new file | Add @-ref to CLAUDE.md OR .claude/rules/ entry (line 80) | OK |
| 5 | Existing fragment updated | Consolidation updates existing file | Verify memory index entry (line 81) | OK |
| 6 | Decision file updated | Consolidation updates decisions/*.md | Verify .claude/rules/ entry (line 82) | OK |
| 7 | File >400 lines after edit | wc -l check | Split by H2/H3 boundaries, validate-memory-index.py --fix (line 65) | OK |

**Gate 7 verification (FR-5):** Step 2 (lines 26-29) adds Grep on `agent-core/fragments/*.md` and `agents/decisions/*.md` for keywords from each eligible learning. The routing table (lines 33-41) is preserved as the classification guide. Grep output grounds the routing but does not override it — the table is described as "fallback classification guide" (per phase-2-report.md). NFR-7 satisfied: the routing table decisions remain the same; Grep provides evidence for choosing among them.

**Routing table completeness check:**
- Behavioral rules -> fragments/*.md (line 33)
- Technical details -> decisions/*.md (line 34)
- Implementation patterns -> implementation-notes.md (line 35)
- Active state -> session.md (line 36)
- Skill references -> .claude/skills/*/references/learnings.md (line 37)
- Agent templates -> agent-core/agents/*.md (line 38)
- Historical -> plan files (line 39)
- Never targets -> README, test, temp (line 40)

All routing targets are present. The Grep grounds which specific file within a category, not which category. No routing decision altered.

**Verdict:** All 7 paths match execution report. No issues.

---

## 5. orchestrate skill

**Paths found:** 7 (execution report claimed: 3 conditional paths)
**Discrepancies:** Execution report undercounts — reported "3 conditional paths" (inline/delegation, success/failure, phase boundary) but did not enumerate full path set. This is a framing difference, not a correctness issue.

| # | Path | Trigger | Output/Routing | Status |
|---|------|---------|----------------|--------|
| 1 | Orchestrator plan missing | ls fails to find orchestrator-plan.md | ERROR, stop (line 37) | OK |
| 2 | Step files missing + all-inline | orchestrator plan has only inline entries | Valid, proceed (line 39) | OK |
| 3 | Step files missing + plan references them | orchestrator plan references step files | ERROR, stop (line 41) | OK |
| 4 | Inline execution (3.0) | Orchestrator plan entry says "Execution: inline" | Orchestrator reads + executes directly (lines 65-78) | OK |
| 5 | Agent delegation (3.1) | Orchestrator plan entry references step file | Task tool dispatch (lines 80-92) | OK |
| 6 | Post-step: clean tree | git status --porcelain empty | Phase boundary check (lines 124-134) | OK |
| 7 | Post-step: dirty tree | git status --porcelain has output | STOP immediately, escalate (lines 116-120) | OK |
| 8 | Phase boundary: same phase | Next step same Phase field | Proceed to 3.4 (line 130) | OK |
| 9 | Phase boundary: phase changed or final | Phase differs or no next step | Delegate to corrector for checkpoint (line 132) | OK |
| 10 | Checkpoint: UNFIXABLE | Corrector reports unfixable issues | STOP, escalate to user (line 141) | OK |
| 11 | Checkpoint: all fixed | Corrector fixes all issues | Commit checkpoint, continue (line 142) | OK |
| 12 | All steps successful | Completion | Corrector review, optional TDD audit, deliverable review task, lifecycle entry, default-exit (lines 249-267) | OK |
| 13 | Blocked (step failure) | Agent reports error | Report failed step, context, completed steps (lines 269-273) | OK |
| 14 | TDD runbook type | Frontmatter `type: tdd` | Additional tdd-auditor delegation (lines 253-255) | OK |

**Extraction gap check:** common-scenarios.md, continuation.md, and progress-tracking.md are purely additive reference content — no conditional routing logic was extracted. All conditional branches remain in the main SKILL.md body.

**Key verification points:**
- Inline phase review-requirement proportionality (lines 74-77): <=5 net lines -> self-review, larger -> corrector. This conditional is preserved inline. OK.
- Inline precommit failure (lines 72-73): fix or escalate. Preserved. OK.
- Final checkpoint lifecycle audit (lines 177-182): additional scope for final phase boundary. Preserved as conditional ("When the phase boundary is the final one"). OK.
- Escalation levels (lines 201-218): three levels with routing. All preserved. OK.

**Continuation protocol:** Extracted to `references/continuation.md` but summarized in SKILL.md lines 290-294. The main SKILL.md says "Read `references/continuation.md`" — the Read instruction is the trigger condition, and the content in the reference file preserves both branches (continuation present / absent / default-exit). No gap.

**Verdict:** All paths functional. Execution report's "3 conditional paths" was a simplification — full enumeration yields 14 paths. No correctness issue.

---

## 6. requirements skill

**Paths found:** 3 (execution report claimed: 3)
**Discrepancies:** None

| # | Path | Trigger | Output/Routing | Status |
|---|------|---------|----------------|--------|
| 1 | Existing artifact | Glob finds plans/<job>/requirements.md | Read existing file, use as base for update/refinement in extract mode -> steps 1-6 -> artifact + next step | OK |
| 2 | Extract (conversation) | Glob finds no file, conversation has substantive discussion | Extract mode -> steps 1-6 -> artifact + next step | OK |
| 3 | Elicit (cold start) | Glob finds no file, no substantive discussion | AskUserQuestion elicitation -> shared steps 2-6 -> artifact + next step | OK |

**Gate 6 verification (FR-5):** `Glob: plans/<job>/requirements.md` added as primary signal in Mode Detection (line 26). Conversation heuristic preserved as fallback (lines 29-31). The Glob determines whether to enter extract-with-existing-base vs fall through to conversation analysis. NFR-7 satisfied: original two-mode detection (extract/elicit via conversation heuristic) is preserved as fallback when no file exists.

**Sub-path verification within each mode:**

Extract mode sub-paths:
- Step 4 Gap Detection (lines 74-86): critical sections empty -> ask (max 3 questions). Non-critical empty -> note absence. These are interaction-level branches, not routing paths.
- Step 5 Present Draft (lines 107-113): user validates -> step 6. User rejects -> implied revision loop.

Elicit mode sub-paths:
- Step 1 (lines 125-127): AskUserQuestion with budget 4-6. Then follows shared steps 2-6.

Default Exit (lines 199-217): 4 suggestion paths based on completeness:
- 0-2 open questions, critical sections populated -> `/design`
- 3+ open questions or empty critical -> standalone
- Very clear scope + simple -> `/runbook` directly
- User stated explicit next step -> use that

These are advisory output, not routing decisions made by the skill. All four suggestions are presented to the user.

**Skill dependency scanning (lines 177-195):** Conditional append to artifact based on indicator presence. Not a routing path — additive content.

**Verdict:** All 3 paths match execution report. No issues.

---

## Summary

| Skill | Paths Found | Report Claimed | Discrepancy | Issues |
|-------|-------------|----------------|-------------|--------|
| design | 12 | 10+1 | +1 (requirements-clarity route) | None |
| commit | 8 | 8 | None | None |
| handoff | 6 | 6 | None | None |
| codify | 7 | 7 | None | None |
| orchestrate | 14 | 3 (simplified) | Framing difference | None |
| requirements | 3 | 3 | None | None |

**Broken paths:** 0
**Dead branches:** 0
**Missing user-visible output:** 0
**NFR-7 violations (new branching from gate additions):** 0
**Extraction gaps (conditional logic lost to references/):** 0

**Design skill note:** The execution report's 10-path enumeration is a reasonable simplification — it groups the Post-Outline downgrade as part of path 7 rather than a separate fork. The requirements-clarity routing (my path 1) is a genuine additional path not in the report, but it existed pre-edit and was not introduced by the quality pass. Not a regression.

**Orchestrate skill note:** The execution report's "3 conditional paths" is a structural summary (inline/delegation, success/failure, phase boundary) rather than a full path enumeration. Full trace reveals 14 paths including error states, TDD branching, and checkpoint outcomes. All are preserved from pre-edit state.
