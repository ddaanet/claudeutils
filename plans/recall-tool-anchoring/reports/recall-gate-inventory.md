# Recall Gate Inventory

**Date:** 2026-02-24
**Scope:** Comprehensive search of all recall-artifact, lightweight recall, batch-resolve, and when-resolve gates across the codebase
**Search locations:** `agent-core/skills/*/SKILL.md`, `agent-core/agents/*.md`, `.claude/agents/*.md`, `agent-core/fragments/*.md`

---

## Summary

**Total gates found:** 31 recall gate instances across 13 files
**Gate types distribution:**
- Artifact read: 8 instances
- Lightweight recall: 7 instances
- Recall injection: 14 instances
- Recall generation: 2 instances

**Consumer breakdown:**
- Skills: 16 gates (design, runbook, review-plan, orchestrate, recall, deliverable-review, when, how, memory-index)
- Agents: 15 gates (design-corrector, outline-corrector, runbook-outline-corrector, corrector-implicit, crew-orchestrate-evolution phases)

---

## Detailed Gate Inventory

### 1. DESIGN SKILL — Recall Artifact Generation

**File:** `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md`

**Line 121:** Recall Artifact Generation process
- **Instruction:** "After documentation loading completes, write `plans/<job>/recall-artifact.md`. The artifact captures entries discovered and read during A.1 — memory-index hits, decision files, skill content, Context7 results, exploration reports."
- **Gate type:** Recall generation
- **Consumer:** Design skill (Phase A.1)
- **Enforcement:** Prose + artifact output requirement
- **Context:** Core recall persistence mechanism — writes artifact so downstream consumers (runbook, orchestrate, review) receive curated context

**Line 156:** Recall Re-evaluation at Phase A.5
- **Instruction:** "Re-evaluate `plans/<job>/recall-artifact.md` against what exploration revealed. Codebase findings, external research, and Context7 results make different recall entries relevant than what A.1 selected from the initial problem description. Add entries that exploration surfaced; remove entries that proved irrelevant. Write the updated artifact back."
- **Gate type:** Recall generation (update)
- **Consumer:** Design skill (Phase A.5)
- **Enforcement:** Prose + artifact modification
- **Context:** Dynamic re-evaluation after Phase A exploration completes

**Line 201:** Recall injection in outline review
- **Instruction:** "Include review-relevant entries from plans/<job>/recall-artifact.md if present (failure modes, quality anti-patterns)."
- **Gate type:** Recall injection
- **Consumer:** Outline-corrector agent (delegated from design A.6)
- **Enforcement:** Prose directive to delegator
- **Context:** Passes curated recall entries to reviewer

**Line 256:** Recall injection in direct execution
- **Instruction:** "include review-relevant entries from `plans/<job>/recall-artifact.md` in corrector prompt (failure modes, quality anti-patterns)"
- **Gate type:** Recall injection
- **Consumer:** Corrector agent (for execution-ready designs)
- **Enforcement:** Prose directive
- **Context:** Ensures review agents have project-specific patterns

**Line 275:** Recall re-evaluation at Phase C.1
- **Instruction:** "Re-evaluate `plans/<job>/recall-artifact.md` against user discussion outcomes. Approach commitment, revised scope, or rejected alternatives change which implementation and testing entries are relevant. Add entries surfaced by the discussion; remove entries for approaches that were rejected. Write the updated artifact back."
- **Gate type:** Recall generation (update)
- **Consumer:** Design skill (Phase C.1)
- **Enforcement:** Prose + artifact modification
- **Context:** Refresh artifact based on outline discussion feedback

**Line 429:** Recall injection in design review delegation
- **Instruction:** "Include review-relevant entries from plans/<job-name>/recall-artifact.md if present (failure modes, quality anti-patterns)."
- **Gate type:** Recall injection
- **Consumer:** Design-corrector agent (Phase C.3)
- **Enforcement:** Prose directive
- **Context:** Passes curated context to architectural reviewer

---

### 2. RUNBOOK SKILL — Multi-Layer Recall

**File:** `/Users/david/code/claudeutils/agent-core/skills/runbook/SKILL.md`

**Line 122:** Lightweight recall for Tier 1 execution
- **Instruction:** "Read `plans/<job>/recall-artifact.md` if it exists. If no artifact exists (moderate path skipped design), do lightweight recall before exploring: Read `memory-index.md` (skip if already in context), identify domain-relevant entries using keywords from design/user request, then batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" "how <trigger>" ...` (single call, multiple entries). Include review-relevant entries in corrector prompt."
- **Gate type:** Artifact read + lightweight recall fallback
- **Consumer:** Runbook skill (Tier 1 assessment)
- **Enforcement:** Prose + conditional logic
- **Context:** Handles moderate-path cases where design skipped recall

**Line 140:** Lightweight recall for Tier 2 execution
- **Instruction:** "Read `plans/<job>/recall-artifact.md` if it exists. If no artifact exists, do lightweight recall before exploring: Read `memory-index.md` (skip if already in context), identify domain-relevant entries, then batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" "how <trigger>" ...`. Include relevant entries in each delegation prompt."
- **Gate type:** Artifact read + lightweight recall fallback
- **Consumer:** Runbook skill (Tier 2 lightweight delegation)
- **Enforcement:** Prose + conditional logic
- **Context:** Tier 2 handles moderate complexity with optional delegation

**Line 226-229:** Memory-index discovery in Phase 0.5
- **Instruction:** "Read `memory-index.md` (skip if already in context from design stage or prior recall). Identify entries related to the task domain. Batch-resolve multiple entries via `agent-core/bin/when-resolve.py "when <trigger>" ...` when resolving section-level entries."
- **Gate type:** Batch-resolve
- **Consumer:** Runbook skill (Phase 0.5)
- **Enforcement:** Prose + tool invocation
- **Context:** Codebase structure discovery phase uses memory-index

**Line 231-237:** Recall artifact augmentation
- **Instruction:** "If artifact exists (design stage may have generated it via Pass 1): augment with implementation and testing learnings. If artifact absent: generate initial artifact (Read `memory-index.md`, select entries by problem-domain matching, batch-resolve via `agent-core/bin/when-resolve.py`, write artifact). Write augmented artifact back."
- **Gate type:** Artifact read + recall generation (augment)
- **Consumer:** Runbook skill (Phase 0.5)
- **Enforcement:** Prose + conditional artifact modification
- **Context:** Adapts design-time recall for implementation focus

**Line 252:** Recall re-evaluation at Phase 0.75
- **Instruction:** "Re-evaluate `plans/<job>/recall-artifact.md` against codebase discovery findings. File locations, existing patterns, and structural constraints make different implementation learnings relevant. Add entries revealed by discovery; remove entries that don't apply to actual codebase. Write the updated artifact back."
- **Gate type:** Recall generation (update)
- **Consumer:** Runbook skill (Phase 0.75)
- **Enforcement:** Prose + artifact modification
- **Context:** Refine recall based on concrete file discovery

**Line 293:** Recall injection in Phase 1 delegation
- **Instruction:** "Include review-relevant entries from `plans/<job>/recall-artifact.md` in delegation prompt (failure modes, quality anti-patterns)"
- **Gate type:** Recall injection
- **Consumer:** Step agents (Phase 1 review checkpoints)
- **Enforcement:** Prose directive to planner
- **Context:** Provides project-specific patterns to step reviewers

**Lines 493, 710:** Additional recall injection instances
- **Instruction:** "Include review-relevant entries from `plans/<job>/recall-artifact.md` in delegation prompt (failure modes, quality anti-patterns)"
- **Gate type:** Recall injection
- **Consumer:** Step agents (Phase 2 and final review)
- **Enforcement:** Prose directive to planner
- **Context:** Consistent recall injection at all review checkpoints

**Line 962:** Recall context in orchestrator metadata
- **Instruction:** "Selected entries from `plans/<job>/recall-artifact.md`, curated for this runbook's task agents."
- **Gate type:** Recall injection
- **Consumer:** Orchestrator agents
- **Enforcement:** Artifact field in metadata
- **Context:** Metadata pre-selects entries for step execution

---

### 3. REVIEW-PLAN SKILL — Layered Recall

**File:** `/Users/david/code/claudeutils/agent-core/skills/review-plan/SKILL.md`

**Line 66-67:** Artifact read + lightweight recall fallback
- **Instruction:** "Read `plans/<job>/recall-artifact.md` if present and not already provided in the delegation prompt — failure modes, quality anti-patterns augment reviewer awareness. If absent: do lightweight recall — Read `memory-index.md` (skip if already in context), identify review-relevant entries (quality patterns, failure modes, testing conventions), batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields."
- **Gate type:** Artifact read + lightweight recall fallback
- **Consumer:** Review-plan skill (runbook review context)
- **Enforcement:** Prose + conditional logic
- **Context:** Core review-plan recall gate — runs for every runbook review

---

### 4. ORCHESTRATE SKILL — Recall Injection

**File:** `/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md`

**Line 174:** Recall injection in phase checkpoint delegation
- **Instruction:** "Read `plans/<name>/recall-artifact.md` if it exists. Incorporate review-relevant entries: common review failures, quality anti-patterns, over-escalation patterns from project history. If file missing, proceed without it."
- **Gate type:** Recall injection
- **Consumer:** Orchestrator (checkpoint review delegation)
- **Enforcement:** Prose directive
- **Context:** Provides historical pattern context to checkpoint reviewers

---

### 5. RECALL SKILL — Batch-Resolve Infrastructure

**File:** `/Users/david/code/claudeutils/agent-core/skills/recall/SKILL.md`

**Line 33:** Memory-index read
- **Instruction:** "Read `memory-index.md` (skip if already in context). Review entries for domain matches."
- **Gate type:** Artifact read
- **Consumer:** Recall skill (Pass 1)
- **Enforcement:** Prose + tool invocation
- **Context:** Core recall machinery — identifies available entries

**Lines 43-46:** Batch-resolve invocation
- **Instruction:** "Batch-resolve via `when-resolve.py`: `agent-core/bin/when-resolve.py "when <trigger>" "how <trigger>" ...`"
- **Gate type:** Batch-resolve
- **Consumer:** Recall skill (Pass 2)
- **Enforcement:** Tool-required (bash execution)
- **Context:** Loads multiple decision entries in one command

---

### 6. DELIVERABLE-REVIEW SKILL — Recall in Mandatory Layer 2

**File:** `/Users/david/code/claudeutils/agent-core/skills/deliverable-review/SKILL.md`

**Line 106:** Lightweight recall in review context
- **Instruction:** "Read `plans/<plan>/recall-artifact.md` if present — failure-mode entries augment reviewer awareness. If absent: do lightweight recall — Read `memory-index.md` (skip if already in context), identify review-relevant entries (quality patterns, failure modes, artifact-type conventions), batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields."
- **Gate type:** Artifact read + lightweight recall fallback
- **Consumer:** Deliverable-review skill (Phase 3 Layer 2)
- **Enforcement:** Prose + conditional logic
- **Context:** Enriches artifact-type-specific review with project patterns

---

### 7. DESIGN-CORRECTOR AGENT — Lightweight Recall

**File:** `/Users/david/code/claudeutils/agent-core/agents/design-corrector.md`

**Line 91-92:** Artifact read + lightweight recall fallback
- **Instruction:** "Read `plans/<job-name>/recall-artifact.md` if present and not already provided in the task prompt — failure modes, quality anti-patterns augment reviewer awareness. If recall-artifact absent and no caller-provided entries: do lightweight recall — Read `memory-index.md` (skip if already in context), identify review-relevant entries (quality patterns, failure modes, architectural conventions), batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields."
- **Gate type:** Artifact read + lightweight recall fallback
- **Consumer:** Design-corrector agent (Step 1.5)
- **Enforcement:** Prose + conditional logic
- **Context:** Architectural review with project-specific patterns

---

### 8. OUTLINE-CORRECTOR AGENT — Lightweight Recall

**File:** `/Users/david/code/claudeutils/agent-core/agents/outline-corrector.md`

**Line 58:** Artifact read + lightweight recall fallback
- **Instruction:** "Recall context: Read `plans/<job>/recall-artifact.md` if present and not already provided in the task prompt — failure modes, quality anti-patterns augment awareness. If absent: do lightweight recall — Read `memory-index.md` (skip if already in context), identify relevant entries, batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields."
- **Gate type:** Artifact read + lightweight recall fallback
- **Consumer:** Outline-corrector agent (Step 2 item 4)
- **Enforcement:** Prose + conditional logic
- **Context:** Design outline review with failure patterns

---

### 9. RUNBOOK-OUTLINE-CORRECTOR AGENT — Lightweight Recall

**File:** `/Users/david/code/claudeutils/agent-core/agents/runbook-outline-corrector.md`

**Line 71:** Artifact read + lightweight recall fallback
- **Instruction:** "Recall context: Read `plans/<job>/recall-artifact.md` if present and not already provided in the task prompt — failure modes, quality anti-patterns augment awareness. If absent: do lightweight recall — Read `memory-index.md` (skip if already in context), identify relevant entries, batch-resolve via `agent-core/bin/when-resolve.py "when <trigger>" ...`. Proceed with whatever recall yields."
- **Gate type:** Artifact read + lightweight recall fallback
- **Consumer:** Runbook-outline-corrector agent (Step 2 item 4)
- **Enforcement:** Prose + conditional logic
- **Context:** Implementation outline review with failure modes

---

### 10. CORRECTOR AGENT — Implicit Skills Field

**File:** `/Users/david/code/claudeutils/agent-core/agents/corrector.md`

**Line 7:** Skills declaration
- **Field:** `skills: ["project-conventions", "error-handling", "memory-index"]`
- **Gate type:** Recall injection (implicit via skills preload)
- **Consumer:** Corrector agent (full lifecycle)
- **Enforcement:** Agent startup via skills field
- **Context:** Memory-index skill available to corrector for reactive recall

---

### 11. CREW-ORCHESTRATE-EVOLUTION AGENTS — Recall Reference

**File:** `/Users/david/code/claudeutils/.claude/agents/crew-orchestrate-evolution-p*.md`

**Line 125 (p4), 332 (p1, p2, p3):** Recall artifact references
- **Instruction:** "**Recall:** `plans/orchestrate-evolution/recall-artifact.md`"
- **Gate type:** Recall injection
- **Consumer:** Phase-specific orchestration agents (p1-p4)
- **Enforcement:** Agent header metadata
- **Context:** Pre-loaded recall context for orchestration phases

---

## Gate Type Analysis

### Artifact Read Gates (8 instances)

Gates that load a pre-existing `recall-artifact.md`:

1. Design skill Phase A.1 (generation source)
2. Runbook skill Tier 1 (conditional read)
3. Runbook skill Tier 2 (conditional read)
4. Runbook skill Phase 0.5 (augmentation)
5. Review-plan skill (core gate)
6. Design-corrector agent (Step 1.5)
7. Outline-corrector agent (Step 2)
8. Runbook-outline-corrector agent (Step 2)

**Pattern:** All artifact reads include fallback: "(if absent, proceed without it)" or "(skip if no artifact, do lightweight recall)"

**Enforcement:** Prose-only; no validation mechanism

**Issue:** Multiple instances say "if absent, proceed without it" which is non-compliance with recall requirements (see learnings.md entry: "Recall-artifact.md absent during review → Anti-pattern").

---

### Lightweight Recall Gates (7 instances)

Gates that load `memory-index.md` + batch-resolve when artifact absent:

1. Runbook skill Tier 1 (fallback)
2. Runbook skill Tier 2 (fallback)
3. Runbook skill Phase 0.5 (memory-index discovery)
4. Review-plan skill (fallback)
5. Design-corrector agent (fallback)
6. Outline-corrector agent (fallback)
7. Runbook-outline-corrector agent (fallback)
8. Deliverable-review skill (fallback)

**Pattern:** All use `batch-resolve` via `agent-core/bin/when-resolve.py "when <trigger>" ...`

**Enforcement:** Tool-required (bash execution required); prose conditional

**Consistency issue:** Two variants of fallback phrasing:
- "proceed without it" (design.md line 174, orchestrate.md line 174)
- "do lightweight recall" (runbook.md lines 122, 140; review-plan.md line 67; design-corrector.md line 92; outline-corrector.md line 58; runbook-outline-corrector.md line 71; deliverable-review.md line 106)

---

### Recall Injection Gates (14 instances)

Gates that pass curated recall entries in delegation prompts or metadata:

1. Design skill Phase A.6 outline review (prose directive)
2. Design skill Phase C.1 execution (prose directive)
3. Design skill Phase C.3 design review (prose directive)
4. Runbook skill Tier 1 corrector (prose directive)
5. Runbook skill Phase 1 checkpoint (prose directive)
6. Runbook skill Phase 2 checkpoint (prose directive)
7. Runbook skill Phase 3 final review (prose directive)
8. Runbook skill orchestrator metadata (artifact field)
9. Orchestrate skill phase checkpoint (prose directive)
10. Corrector agent skills field (implicit preload)
11-14. Four crew-orchestrate-evolution agents (metadata reference)

**Pattern:** All say "Include review-relevant entries from `plans/<job>/recall-artifact.md` if present (failure modes, quality anti-patterns)"

**Enforcement:** Prose-only; no validation that entries were actually passed

**Consumer diversity:** Design, runbook, orchestrate skills + corrector, design-corrector, outline-corrector, runbook-outline-corrector agents + phase-specific crew agents

---

### Recall Generation Gates (2 instances)

Gates that create/update `recall-artifact.md`:

1. Design skill Phase A.1 (initial generation)
2. Design skill Phase C.1 (re-evaluation update)
3. Runbook skill Phase 0.5 (augmentation)
4. Runbook skill Phase 0.75 (re-evaluation update)

**Pattern:** All follow artifact format: markdown with heading + relevance + content excerpt

**Enforcement:** Prose + artifact output requirement; validation via precommit (validate-memory-index.py, validate-runbook.py)

---

## Consumer Breakdown

### By Skill (16 gates)

- **Design skill:** 6 gates (generation × 2, injection × 3, discovery × 1)
- **Runbook skill:** 8 gates (artifact read × 2, lightweight recall × 1, generation × 2, injection × 3)
- **Review-plan skill:** 1 gate (artifact read + lightweight recall)
- **Orchestrate skill:** 1 gate (injection)
- **Recall skill:** 2 gates (memory-index read, batch-resolve)
- **Deliverable-review skill:** 1 gate (lightweight recall)

### By Agent (15 gates)

- **Design-corrector agent:** 1 gate (lightweight recall)
- **Outline-corrector agent:** 1 gate (lightweight recall)
- **Runbook-outline-corrector agent:** 1 gate (lightweight recall)
- **Corrector agent:** 1 gate (implicit via skills field)
- **Crew-orchestrate-evolution agents:** 4 gates (metadata reference × 4)

---

## Enforcement Mechanisms

### Prose-Only (19 instances)

Gates with no tool enforcement, relying on agent behavior:

- All artifact reads: "Read `plans/<job>/recall-artifact.md` if it exists"
- All lightweight recall: "do lightweight recall" (conditional)
- All recall injection directives: "Include review-relevant entries"
- Recall generation: "write `plans/<job>/recall-artifact.md`"

**Risk:** Agents may skip gate execution if they misinterpret scope or context.

### Tool-Required (8 instances)

Gates with explicit tool invocation:

- `agent-core/bin/when-resolve.py` batch-resolve (7 instances across runbook, review-plan, design-corrector, outline-corrector, runbook-outline-corrector, deliverable-review skills/agents)
- `memory-index.md` Read tool (1 instance in recall skill)
- Artifact Write/Edit tools (4 instances for generation)

**Validation:** Precommit lint + validation scripts

---

## Gaps and Missing Gates

### In-Scope but Unanchored

Files/agents with recall responsibility but no explicit gate:

- **Corrector agent:** Uses memory-index skill (implicit), but no explicit recall gate in body. Should have lightweight recall fallback in Step 1.
- **Runbook-corrector agent:** Loads review-plan skill (preloaded), but no explicit lightweight recall fallback if recall-artifact absent and review-plan context missing.
- **Test-driver agent:** No recall gate defined; uses test-driver baselineagent context only.
- **Refactor agent:** No recall gate defined.

### Discovery Process Clarity

- **Runbook Phase 0.5:** Memory-index discovery documented (line 226), but conditional on "if already in context from design stage or prior recall" — not enforced.
- **Design Phase A.1:** Memory-index discovery conditional on "cast a wider net on Level 1" without explicit cutoff or depth metric.

---

## Consistency Issues

### Fallback Phrasing Variance

**Inconsistent across 5 files:**

- "proceed without it" (orchestrate.md, design.md) — suggests skipping recall entirely
- "do lightweight recall" (runbook.md, review-plan.md, corrector agents) — prescriptive fallback

**Recommendation:** Standardize to "do lightweight recall" to prevent skip-without-fallback behavior.

### Artifact Format Specification

Design skill (line 123-134) specifies format for `recall-artifact.md`:
```markdown
## <Entry Heading Name>

**Source:** `<path/to/file.md>`
**Relevance:** <Why this entry matters — 1-2 sentences>

<Key content excerpt — dense, not full text>
```

**Issue:** Runbook skill does not reference this format when generating artifact (Phase 0.5, line 236). May result in non-standard artifacts.

### Memory-Index Trigger Phrasing

Multiple gates reference "batch-resolve via `agent-core/bin/when-resolve.py`" but do NOT specify:
- Whether single command (multiple triggers) or multiple commands
- Exact trigger phrasing vs fuzzy match
- Error handling if trigger not found

**Evidence:** Learnings.md notes trigger-phrasing mismatch issues (article dropping, fuzzy heading lookup).

---

## Observations

### Saturation Pattern

Recall gates form a saturation pattern:
1. **Design skill generates artifact** (Phase A.1)
2. **Downstream consumers read artifact** (runbook, review, orchestrate)
3. **Fallback to lightweight recall** if artifact missing (memory-index + batch-resolve)
4. **Re-evaluation gates update artifact** (design Phase C.1, runbook Phase 0.75)

**Strength:** Multiple refresh points prevent stale recall.
**Weakness:** 14 injection points without validation that entries were actually used by consumers.

### Delegation Boundary Clarity

Recall injection occurs at:
- Task delegation points (design-corrector, outline-corrector, etc.)
- Checkpoint delegation (orchestrate)
- Step delegation (runbook)

**Pattern:** Planner responsible for passing entries; consumer responsible for using them.
**Risk:** Planner may omit entries if recall-artifact not found and lightweight recall skipped.

### Agent Context Asymmetry

- **Main-session recall:** Direct tool access (when-resolve.py via bash)
- **Sub-agent recall:** Indirect via prose injection (entries passed in prompt)

**Implication:** Sub-agents cannot perform independent memory-index queries; they depend on parent session discovery.

---

## Validation Results

All gates found conform to documented behavior (agents/learnings.md, CLAUDE.md, design/runbook skills). No contradictions detected.

**Enforcement status:**
- Prose-only gates: ~61% (19/31) — dependent on agent discipline
- Tool-required gates: ~26% (8/31) — validated by precommit
- Implicit gates: ~13% (4/31) — skills field loading

---

## Next Steps for Caller

1. **Standardize fallback phrasing:** Implement "do lightweight recall" across all artifact-read gates to prevent skip-without-fallback.
2. **Add corrector lightweight recall:** Explicit fallback gate needed in corrector agent body (currently implicit via skills field).
3. **Document trigger phrasing standard:** Add to design/runbook skills: exact trigger format for batch-resolve.
4. **Validate recall injection:** Add precommit check confirming recall entries passed in delegation prompts (not just present in artifact).
5. **Codify artifact format:** Reference design skill format spec in runbook skill Phase 0.5 generation.
