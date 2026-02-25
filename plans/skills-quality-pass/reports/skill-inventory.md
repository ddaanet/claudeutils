# Skill Inventory: Prose Quality Audit

**Date:** 2026-02-25
**Skills audited:** 30
**Locations:** `agent-core/skills/*/SKILL.md`
**Frameworks applied:** Deslop rules (project-conventions skill), Segment→Attribute→Compress (skill-optimization-grounding.md), Anti-pattern catalog (prior audit)

---

## Per-Skill Entries

### brief
**Path:** `/Users/david/code/claudeutils/agent-core/skills/brief/SKILL.md`
**Word count (body):** ~130 words
**Line count:** 42
**Grade:** A+

**Description frontmatter:** Clean — action-oriented, no "This skill should be used when…" anti-pattern.

**Content segmentation:** N/A — skill is already minimal.

**Estimated compression:** ~0 lines (skill is already at optimal density)

**Writing style:** Tight imperative prose. Numbered process, concrete format spec.
**Prose quality:** Excellent. Each step is a single action. No rationale padding.
**Progressive disclosure:** Clean: usage → process → format → consumer note.
**Issues:** None.

---

### codify
**Path:** `/Users/david/code/claudeutils/agent-core/skills/codify/SKILL.md`
**Word count (body):** ~680 words
**Line count:** 170
**Grade:** B+

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" with long trigger list.

**Content segmentation:**
- Core rules: ~20 lines (append-only, never overwrite, 7-day gate)
- Mechanical instructions: ~25 lines (step 4a discovery mechanism, compress-key.py)
- Conditional paths: ~15 lines (file splitting, staging retention guidance)
- Redundant content: ~8 lines (file splitting rule partially restates code-removal.md; "measured data" restates no-estimates fragment)
- Examples: ~5 lines (title format anti/correct patterns)
- Guidelines: ~25 lines (quality criteria, staging retention, principles section)
- Framework overhead: ~10 lines (Additional Resources section at end, repeats references already embedded in body)
- Sequential tool calls: ~5 lines (step 4 calls compress-key.py then validates separately)

**Estimated compression:** ~35 lines removable (~21%)
- Description frontmatter: fix to noun phrase (saves 3 lines)
- Remove "Additional Resources" tail section — references already embedded inline (~12 lines)
- Condense "Learnings Quality Criteria" table to 4-line summary (~8 lines saved)
- Consolidate staging retention rules with the 7-day gate in step 1 (~7 lines)
- Remove "Common Patterns" redirect line (reference already stated) (~2 lines)
- Remove "Tool Constraints" summary (restates step 4) (~3 lines)

**Writing style:** Mostly clean. "When to Use" preamble section present.
**Prose quality:** Good. Minor: "When to Use" duplicates trigger list in description. "Integration" section at bottom adds noise without new information.
**Progressive disclosure:** Good. Steps flow logically. But tail sections (Additional Resources, Integration, Target Files) are low-value appendage.
**Issues:**
- Description frontmatter anti-pattern
- "When to Use" preamble section (anti-pattern #2)
- Duplicate reference list in "Additional Resources" tail

---

### commit
**Path:** `/Users/david/code/claudeutils/agent-core/skills/commit/SKILL.md`
**Word count (body):** ~620 words
**Line count:** 151
**Grade:** A-

**Description frontmatter:** Clean — concise noun phrase.

**Content segmentation:**
- Core rules: ~18 lines (only-commit-when-asked, precommit gate, allowlist constraint)
- Mechanical instructions: ~35 lines (separate Bash calls, submodule -C pattern, heredoc syntax, stage/commit/verify)
- Conditional paths: ~20 lines (submodule handling, vet gate branches, context mode)
- Redundant content: ~5 lines (secrets note in step 4 restates always-loaded fragment)
- Examples: ~12 lines (commit message example)
- Guidelines: ~8 lines (message style rules)
- Framework overhead: ~3 lines (Post-Commit STATUS display)

**Estimated compression:** ~30 lines removable (~20%)
- Remove secrets line (redundant with system context) (~2 lines)
- Conditional path extraction: submodule section to references/submodule-handling.md (~20 lines saved, replace with 1-line trigger)
- Condense vet gate prose description (~6 lines → 2 lines)

**Writing style:** Dense. Imperative. Well-structured.
**Prose quality:** Good. Design comment in step 1b ("CWD rule") helpful context. The flags section up front is clean.
**Progressive disclosure:** Good. Flags → style → steps → post-commit.
**Issues:**
- Submodule handling section is extractable conditional path (~20 lines)
- Redundant secrets rule

---

### deliverable-review
**Path:** `/Users/david/code/claudeutils/agent-core/skills/deliverable-review/SKILL.md`
**Word count (body):** ~700 words
**Line count:** 175
**Grade:** A-

**Description frontmatter:** Anti-pattern — "This skill should be used when…" multi-sentence trigger list.

**Content segmentation:**
- Core rules: ~15 lines (when to use, layer 1/2 gate logic)
- Mechanical instructions: ~20 lines (deliverable-inventory.py invocation, recall-resolve.sh, lifecycle append)
- Conditional paths: ~25 lines (layer 1 delegation branches, severity routing)
- Redundant content: ~5 lines (methodology reference restates agents/decisions/deliverable-review.md)
- Examples: ~0 lines
- Guidelines: ~20 lines (report structure template, severity classification)
- Framework overhead: ~8 lines (References tail section)

**Estimated compression:** ~30 lines removable (~17%)
- Description frontmatter fix (~3 lines)
- References section is minimal and useful — keep
- Report structure template is 25 lines; ~8 lines condensable
- Lifecycle append instructions extractable to reference (~6 lines)

**Writing style:** Mostly clean. Good use of tables for layer gate logic.
**Prose quality:** Good. The "Why interactive is mandatory" explanation inline is useful (1 line).
**Progressive disclosure:** Good. When to use → prerequisites → process phases → report.
**Issues:**
- Description frontmatter anti-pattern

---

### design
**Path:** `/Users/david/code/claudeutils/agent-core/skills/design/SKILL.md`
**Word count (body):** ~3,200 words
**Line count:** 521
**Grade:** C+

**Description frontmatter:** Anti-pattern — "This skill should be used when…" multi-trigger list.

**Content segmentation:**
- Core rules: ~35 lines (triage recall D+B anchor, classification gate, companion tasks rule, direct execution criteria)
- Mechanical instructions: ~60 lines (A.1 documentation hierarchy table, recall artifact generation, recall diff steps)
- Conditional paths: ~130 lines (Phase A.1 levels 2-5, Phase A.2 delegation branches, Phase A.3-4 research, Phase B convergence, Phase C.1-C.5 full design path, skill-loading directives)
- Redundant content: ~40 lines (A.1 clarification paragraphs restate the table already shown; "Documentation Perimeter" format restates what's just explained above it; binding constraints section at end restates classification tables rule already in body)
- Examples: ~30 lines (outline example, requirements section format, perimeter section format)
- Guidelines: ~50 lines (density checkpoint numbers, repetition helper prescription, agent-name validation rules)
- Framework overhead: ~20 lines (section dividers, "Constraints" tail section restating existing rules)
- Sequential tool calls: ~10 lines (A.5 recall diff + outline write could batch)

**Estimated compression:** ~150 lines removable (~29%)
- Extract Phase A.3-5 research and recall diff steps to `references/research-protocol.md` (~35 lines → 3-line trigger)
- Extract Phase B iterative discussion loop to `references/discussion-protocol.md` (~25 lines → 2-line trigger)
- Extract Phase C.1 detailed content guidelines (repetition helper, agent-name validation, late-addition check) to `references/design-content-rules.md` (~30 lines → 4-line summary)
- Remove A.1 clarification paragraphs — table is self-explanatory (~12 lines)
- Remove "Constraints" tail section — restates existing rules (~8 lines)
- Condense binding constraints callout (~5 lines → 1 line)
- Remove output expectations section — evident from process description (~10 lines)

**Writing style:** Verbose in places. Second-person in some guidelines. Multiple "rationale" clauses.
**Prose quality:** Anti-pattern: "Rationale: Designer has deepest understanding…" inline in Documentation Perimeter section. Anti-pattern: "Grounding: FR-18 added during a design session…" inline in Late-addition completeness check.
**Progressive disclosure:** Moderate. Complex triage + full Phase A-C creates significant surface area. Phases A-C are conditional paths and should be in references/.
**Issues:**
- Description frontmatter anti-pattern
- Rationale clauses inline (anti-pattern #3): 4+ instances
- Phase A.3-5 and Phase B-C are conditional paths (should be extractable)
- A.1 clarification is redundant with the table
- "Constraints" tail section is redundant
- Skill is 521 lines; target ~200-250 inline + references for conditional paths

---

### doc-writing
**Path:** `/Users/david/code/claudeutils/agent-core/skills/doc-writing/SKILL.md`
**Word count (body):** ~750 words
**Line count:** 153
**Grade:** B+

**Description frontmatter:** Anti-pattern — "This skill should be used when…" multi-trigger list.

**Content segmentation:**
- Core rules: ~5 lines (reader test mandatory, one doc per invocation)
- Mechanical instructions: ~15 lines (Task tool invocation for reader test)
- Conditional paths: ~10 lines (re-run reader test criteria, fix gap patterns)
- Redundant content: ~0 lines
- Examples: ~25 lines (motivation-first opener before/after, example execution walk-through)
- Guidelines: ~45 lines (motivation-first, audience-appropriate depth, structure for scanning, concrete over abstract, omit list)
- Framework overhead: ~8 lines (Constraints tail section)

**Estimated compression:** ~40 lines removable (~26%)
- Description frontmatter fix (~4 lines)
- "When to Use" preamble section (anti-pattern #2): deduplicate with description (~8 lines)
- Condense "Structure for scanning" guidelines to 2 dense rules (~6 lines)
- Condense "Concrete over abstract" list (~4 lines)
- Condense "Omit what doesn't serve the reader" list (~4 lines)
- Extract example execution to `examples/doc-writing-example.md` (~15 lines → 1-line reference)

**Writing style:** Clear. Some second-person ("Most readers scan before reading").
**Prose quality:** The motivation-first example (before/after) is high-value — keep. The "Audience-appropriate depth" section has useful distinctions.
**Progressive disclosure:** Good structure: explore → write → reader-test → fix → review.
**Issues:**
- Description frontmatter anti-pattern
- "When to Use" preamble section (anti-pattern #2)
- Example execution section is extractable (~15 lines)

---

### error-handling
**Path:** `/Users/david/code/claudeutils/agent-core/skills/error-handling/SKILL.md`
**Word count (body):** ~80 words
**Line count:** 20
**Grade:** B-

**Description frontmatter:** Anti-pattern — "This skill should be used when agents execute bash commands…" full sentence trigger.

**Content segmentation:**
- Core rules: ~6 lines (errors never pass silently, 5 bullet rules)
- Redundant content: ~10 lines — entire body duplicates `agent-core/fragments/error-handling.md` which is in always-loaded context

**Estimated compression:** ~12 lines removable (~60%)
- Description frontmatter fix (~1 line)
- Body is largely redundant with the always-loaded fragment; skill exists only to inject via `skills:` frontmatter in sub-agents. If that's the purpose, body can shrink to a header + 2-line summary pointing at the fragment.

**Writing style:** Clean.
**Prose quality:** Body duplicates the fragment verbatim. Acceptable only if the skill is used to inject context into sub-agents that don't have the fragment in their system prompt.
**Progressive disclosure:** N/A — single-purpose injection skill.
**Issues:**
- Description frontmatter anti-pattern
- Body is ~80% redundant with always-loaded fragment (redundant content anti-pattern #4)
- If sub-agent injection is the purpose, note that explicitly in description

---

### gitmoji
**Path:** `/Users/david/code/claudeutils/agent-core/skills/gitmoji/SKILL.md`
**Word count (body):** ~380 words
**Line count:** 80
**Grade:** B

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" multi-trigger list.

**Content segmentation:**
- Core rules: ~8 lines (semantic matching, return emoji character only)
- Mechanical instructions: ~10 lines (read entire index, not grep; update script invocation)
- Conditional paths: ~5 lines (index missing fallback)
- Redundant content: ~0 lines
- Examples: ~5 lines
- Guidelines: ~8 lines (selection rules, priorities)
- Framework overhead: ~15 lines ("When to Use" preamble, "Critical Rules" section restating do/don't from prior sections, "Resources" tail section)

**Estimated compression:** ~30 lines removable (~37%)
- Description frontmatter fix (~4 lines)
- "When to Use" preamble section (anti-pattern #2): ~10 lines → 0 (description covers this)
- "Critical Rules" section restates Do/Don't from earlier content (~10 lines)
- "Resources" tail section restates file references already mentioned above (~5 lines)

**Writing style:** Compact bullet-heavy format. Good.
**Prose quality:** "Critical Rules" section (Do:/Don't:) duplicates content from the body. "Limitations" bullet list at end adds noise.
**Progressive disclosure:** Decent but cluttered by redundant sections.
**Issues:**
- Description frontmatter anti-pattern
- "When to Use" preamble section (anti-pattern #2)
- "Critical Rules" duplicates body content (redundant section)
- "Resources" duplicates file references

---

### ground
**Path:** `/Users/david/code/claudeutils/agent-core/skills/ground/SKILL.md`
**Word count (body):** ~450 words
**Line count:** 94
**Grade:** A-

**Description frontmatter:** Anti-pattern — "This skill should be used when producing output that contains…" multi-trigger.

**Content segmentation:**
- Core rules: ~5 lines (both branches required, grounding quality label mandatory)
- Mechanical instructions: ~20 lines (Phase 2 diverge branch specs, Phase 4 required sections)
- Conditional paths: ~10 lines (scope determines agent type)
- Redundant content: ~0 lines
- Examples: ~8 lines (framing rule with before/after)
- Guidelines: ~15 lines (convergence framing rule, integration points)
- Framework overhead: ~5 lines (Additional Resources tail)

**Estimated compression:** ~20 lines removable (~21%)
- Description frontmatter fix (~4 lines)
- "Additional Resources" tail: keep — grounding-criteria.md reference is conditional path access point
- Integration Points section could condense from 10 lines to 4 lines (~6 lines)

**Writing style:** Clean. Dense procedure format.
**Prose quality:** Good. Framing rule (general-first) with before/after example is high-value.
**Progressive disclosure:** Good: procedure phases in order, integration points at end.
**Issues:**
- Description frontmatter anti-pattern
- Minor: integration points section could compress

---

### handoff
**Path:** `/Users/david/code/claudeutils/agent-core/skills/handoff/SKILL.md`
**Word count (body):** ~900 words
**Line count:** 163
**Grade:** B+

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" multi-trigger list.

**Content segmentation:**
- Core rules: ~20 lines (carry-forward verbatim, allowed sections only, multiple handoffs via Edit, NEVER reference commits as pending)
- Mechanical instructions: ~25 lines (command derivation table, haiku task criteria format, continuation parsing)
- Conditional paths: ~20 lines (haiku session review, plan-archive update, trim completed tasks, continuation protocol)
- Redundant content: ~10 lines (context preservation Omit/Preserve lists partially restate session.md guidance already in context)
- Examples: ~0 lines
- Guidelines: ~15 lines (target 75-150 lines, Preserve/Omit lists, Discussion substance note)
- Framework overhead: ~10 lines (Principles section at end restates session.md/learnings.md roles; Reference tail)

**Estimated compression:** ~40 lines removable (~25%)
- Description frontmatter fix (~3 lines)
- Principles tail section (~12 lines → 0, roles evident from protocol)
- Context preservation "Preserve/Omit" lists condense to 3-line rule (~8 lines saved)
- Continuation protocol extractable to references/continuation.md (~8 lines → 2-line trigger)

**Writing style:** Good. Imperative. Step structure clear.
**Prose quality:** Good. Carry-forward rule is essential and correctly stated. Command derivation table is high-value.
**Progressive disclosure:** Good flow. Principles tail is redundant summary.
**Issues:**
- Description frontmatter anti-pattern
- Principles tail section is redundant summary
- Continuation protocol is extractable conditional path

---

### handoff-haiku
**Path:** `/Users/david/code/claudeutils/agent-core/skills/handoff-haiku/SKILL.md`
**Word count (body):** ~480 words
**Line count:** 121
**Grade:** B

**Description frontmatter:** Clean — "Internal skill for Haiku model orchestrators only." Concise and clear.

**Content segmentation:**
- Core rules: ~8 lines (mechanical merge, preserve everything, don't filter/judge)
- Mechanical instructions: ~35 lines (detailed merge rules per section, task metadata format)
- Conditional paths: ~10 lines (session notes handling vs learnings)
- Redundant content: ~25 lines — task metadata format (lines 44-64) is a verbatim copy of the format in handoff/SKILL.md and execute-rule.md. Always-loaded context already provides this.
- Examples: ~10 lines (example task format lines)
- Guidelines: ~10 lines (principles section)
- Framework overhead: ~8 lines ("Template for sections" — markdown template with raw text section names)

**Estimated compression:** ~45 lines removable (~37%)
- Task metadata format block is redundant with always-loaded execute-rule.md (~20 lines)
- "Template for sections" block (raw markdown in code block): extractable to references/ (~10 lines → 1-line reference)
- Principles tail section: condense to 3 lines (~7 lines saved)
- Field rules in task format: already in context (~8 lines)

**Writing style:** Clear. Second-person in Principles ("Trust the next agent").
**Prose quality:** Moderate. Principles section restates what is evident from the protocol ("Don't filter or judge importance" is covered by the mechanical merge rules).
**Progressive disclosure:** Decent. But template block adds visual weight without structural clarity.
**Issues:**
- Task metadata format block is redundant content (anti-pattern #4)
- Principles tail section redundant with protocol
- "Template for sections" could extract to references/

---

### how
**Path:** `/Users/david/code/claudeutils/agent-core/skills/how/SKILL.md`
**Word count (body):** ~150 words
**Line count:** 49
**Grade:** A

**Description frontmatter:** Anti-pattern — "This skill should be used when the agent needs to recall procedural knowledge…" trigger list.

**Content segmentation:** All core rules and mechanical instructions. Minimal.

**Estimated compression:** ~8 lines removable (~16%)
- Description frontmatter fix (~4 lines saved)
- "When NOT to Use" (4 lines) duplicates content already in /when and /recall skills — if these are loaded together this is redundant; if standalone keep

**Writing style:** Dense. Imperative. Good.
**Prose quality:** Clean. Resolution modes with code examples are the right format.
**Progressive disclosure:** Good: resolution modes → when to use → when not → output.
**Issues:**
- Description frontmatter anti-pattern (minor)
- "When NOT to Use" may be mildly redundant

---

### memory-index
**Path:** `/Users/david/code/claudeutils/agent-core/skills/memory-index/SKILL.md`
**Word count (body):** ~1,400 words
**Line count:** 288
**Grade:** B-

**Description frontmatter:** Anti-pattern — "This skill should be used when sub-agents need memory recall capabilities."

**Content segmentation:**
- Core rules: ~5 lines (Bash transport invocation pattern)
- Mechanical instructions: ~15 lines (invocation examples with 5 modes)
- Conditional paths: ~0 lines
- Redundant content: ~5 lines (HTML comment "Synced from agents/memory-index.md")
- Reference content: ~255 lines — the body IS the memory index listing (all /when and /how triggers grouped by decision file). This is a reference data block, not instructions.

**Estimated compression:** ~10 lines overhead removable (~4% of total, but this skill is unusual — it IS a data payload)
- Description frontmatter fix (~1 line)
- HTML sync comment is noise (~2 lines)
- The 255-line index body is the intended content — not compressible without breaking the skill's function

**Writing style:** N/A — mostly data.
**Prose quality:** The header section (8 lines of instructions + examples) is clean and dense.
**Progressive disclosure:** Good: instructions with examples, then index data.
**Issues:**
- Description frontmatter anti-pattern
- This skill is unique: mostly data payload, not instruction prose. Compression analysis doesn't apply to the index portion.

---

### next
**Path:** `/Users/david/code/claudeutils/agent-core/skills/next/SKILL.md`
**Word count (body):** ~370 words
**Line count:** 83
**Grade:** B

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks…" multi-trigger list.

**Content segmentation:**
- Core rules: ~8 lines (check context first, then invoke; stop once actual work found)
- Mechanical instructions: ~20 lines (4-step check sequence with specific checks per source)
- Conditional paths: ~10 lines (what "no pending work" means per source)
- Redundant content: ~5 lines (Response Format section defines a format that is obvious from context)
- Examples: ~10 lines (example response block)
- Guidelines: ~5 lines (Constraints)
- Framework overhead: ~0 lines

**Estimated compression:** ~25 lines removable (~30%)
- Description frontmatter fix (~4 lines)
- "When to Use" preamble section (anti-pattern #2): ~10 lines — duplicates description triggers + adds check-context-first guidance that belongs in the body (~4 lines)
- Response format section: condense to 1-line rule (~5 lines)
- Example response block: extract to references/ or remove (~10 lines → 0)

**Writing style:** Good. Clear numbered steps.
**Prose quality:** "When to Use" section explains the pre-check rule, but that's a behavioral rule that belongs in the body steps, not a when-to-use preamble.
**Progressive disclosure:** Decent. The check-context-first logic is front-loaded in "When to Use" rather than in the body steps.
**Issues:**
- Description frontmatter anti-pattern
- "When to Use" preamble section (anti-pattern #2)
- Response format section adds ceremony without constraint

---

### opus-design-question
**Path:** `/Users/david/code/claudeutils/agent-core/skills/opus-design-question/SKILL.md`
**Word count (body):** ~550 words
**Line count:** 117
**Grade:** B+

**Description frontmatter:** Clean — structured noun phrase with clear routing criteria.

**Content segmentation:**
- Core rules: ~5 lines (identify decision, invoke opus, execute recommendation)
- Mechanical instructions: ~25 lines (Task invocation template with 5-field structure)
- Conditional paths: ~0 lines
- Redundant content: ~15 lines — "When to Use" section (step 1 header) partially restates always-loaded design-decisions.md fragment which defines the routing criteria. "Execute Recommendation" section states the obvious.
- Examples: ~35 lines (full Click vs argparse scenario walkthrough)
- Guidelines: ~5 lines (formulate context guidance)
- Framework overhead: ~5 lines

**Estimated compression:** ~40 lines removable (~34%)
- "When to Use" intro section redundant with design-decisions.md fragment (~8 lines)
- Example workflow: extract to references/examples.md (~35 lines → 1-line reference)
- "Execute Recommendation" step is 3 lines of obvious advice (~3 lines)

**Writing style:** Good. Task invocation template format is clean.
**Prose quality:** The example is thorough but its length (35 lines) dominates the skill. Most readers need the Task template, not the scenario walkthrough.
**Progressive disclosure:** Bloated by example. Core protocol (40 lines) buried under example (35 lines).
**Issues:**
- Example workflow section dominates — extractable (~35 lines)
- Redundant "When to Use" preamble
- "Execute Recommendation" obvious

---

### orchestrate
**Path:** `/Users/david/code/claudeutils/agent-core/skills/orchestrate/SKILL.md`
**Word count (body):** ~2,900 words
**Line count:** 521
**Grade:** C

**Description frontmatter:** Clean — noun phrase description.

**Content segmentation:**
- Core rules: ~25 lines (sequential unless explicit parallel, never skip steps, escalate all failures, clean-tree check)
- Mechanical instructions: ~65 lines (verify artifacts, execute step, post-step verification, checkpoint delegation template)
- Conditional paths: ~120 lines (inline execution 3.0, agent delegation 3.1-3.5, error escalation levels, progress tracking, continuation protocol, common scenarios)
- Redundant content: ~25 lines (example execution walkthrough is a detailed scenario repeating steps 1-5; "Handling Common Scenarios" section repeats error escalation rules with different framing)
- Examples: ~55 lines (example execution, progress file format, escalation prompt template)
- Guidelines: ~30 lines (weak orchestrator pattern section restates the execution rules with rationale framing)
- Framework overhead: ~20 lines (References section with absolute paths, workflow position section)
- Sequential tool calls: ~10 lines (step 3.3 post-step + phase boundary check could batch)

**Estimated compression:** ~130 lines removable (~25%)
- "Weak Orchestrator Pattern" section restates execution rules in different framing (~30 lines → 5-line summary)
- "Common Scenarios" section extractable to references/common-scenarios.md (~40 lines → 2-line trigger)
- Continuation protocol extractable to references/continuation.md (~35 lines → 3-line trigger)
- Progress tracking "detailed approach" extractable to references/ (~20 lines → 1-line reference)
- Example execution walkthrough: extract to references/ (~20 lines → 1-line reference)
- References tail: clean up absolute paths (~5 lines)

**Writing style:** Verbose in scenario descriptions. Second-person in weak orchestrator pattern.
**Prose quality:** Anti-pattern: "Weak Orchestrator Pattern" is a rationale section — describes why the rules exist instead of just stating them. Anti-pattern: "Key characteristics" header followed by description instead of rules.
**Progressive disclosure:** Poor — Weak Orchestrator Pattern rationale (50 lines) appears after the protocol, adding overhead. Should appear as a 5-line summary or move to references.
**Issues:**
- "When to Use" preamble section (anti-pattern #2)
- "Weak Orchestrator Pattern" rationale section (anti-pattern #3 — rationale inline)
- "Common Scenarios" is extractable conditional path
- Continuation protocol extractable
- Example execution extractable
- 521 lines total; ~390 after extraction

---

### plugin-dev-validation
**Path:** `/Users/david/code/claudeutils/agent-core/skills/plugin-dev-validation/SKILL.md`
**Word count (body):** ~2,600 words
**Line count:** 528
**Grade:** B-

**Description frontmatter:** Clean — concise noun phrase, not user-invocable.

**Content segmentation:**
- Core rules: ~15 lines (review criteria are binding, fix-all policy, escalation criteria)
- Mechanical instructions: ~40 lines (verification procedures section, fix procedures)
- Conditional paths: ~80 lines (per-artifact-type criteria: skills, agents, hooks, commands, plugin-structure)
- Redundant content: ~10 lines (Alignment Criteria section restates the review criteria with different phrasing; Usage Notes section restates the intended workflow)
- Examples: ~80 lines (Good/Bad examples per artifact type × 5 types)
- Guidelines: ~50 lines (Fix Priority, Fix Constraints, Integration workflow)
- Framework overhead: ~15 lines (section dividers, Usage Notes tail)

**Estimated compression:** ~120 lines removable (~23%)
- Good/Bad Examples: project-specific patterns are valuable but 80 lines. Extract all to `references/examples-per-type.md` (~80 lines → 5-line reference)
- Alignment Criteria section: redundant with review criteria (~15 lines → 0)
- Usage Notes tail: redundant with description frontmatter and integration section (~12 lines)
- Fix constraints section: condense to 3-line rule (~6 lines → 2 lines)

**Writing style:** Good. Tables and code blocks used appropriately.
**Prose quality:** Good structure for a reference document. Anti-pattern: "Rationale:" clauses appear throughout (7+ instances inline with criteria).
**Progressive disclosure:** Good — per-type sections clear. But good/bad examples for each type dominate the skill body.
**Issues:**
- Rationale clauses inline (anti-pattern #3): 7+ instances
- Good/Bad examples should extract to references/ (anti-pattern #5: example/scenario sections)
- Alignment Criteria section is redundant
- Usage Notes tail section redundant

---

### prioritize
**Path:** `/Users/david/code/claudeutils/agent-core/skills/prioritize/SKILL.md`
**Word count (body):** ~480 words
**Line count:** 127
**Grade:** A-

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" multi-trigger list.

**Content segmentation:**
- Core rules: ~5 lines (formula, Fibonacci scale)
- Mechanical instructions: ~15 lines (procedure steps, calculate priority)
- Conditional paths: ~10 lines (scheduling modifiers, tiebreaking)
- Redundant content: ~0 lines
- Examples: ~10 lines (priority table format, parallel batches format)
- Guidelines: ~15 lines (when to re-score, scoring modifier annotations)
- Framework overhead: ~5 lines (Additional Resources tail)

**Estimated compression:** ~25 lines removable (~20%)
- Description frontmatter fix (~4 lines)
- "When to Re-Score" section: 8 lines → 3 lines (3 triggers, dense)
- "Additional Resources" tail: keep (scoring-tables.md reference is legitimate conditional path pointer)
- Column key explanations in table header: redundant with column names (~3 lines)

**Writing style:** Clean. Good use of tables for priority output format.
**Prose quality:** Good. Scoring components are clear. Formula is shown explicitly.
**Progressive disclosure:** Good flow. Formula → procedure → output → re-score triggers.
**Issues:**
- Description frontmatter anti-pattern
- "When to Re-Score" verbose (8 lines → 3 lines)

---

### project-conventions
**Path:** `/Users/david/code/claudeutils/agent-core/skills/project-conventions/SKILL.md`
**Word count (body):** ~90 words
**Line count:** 32
**Grade:** A+

**Description frontmatter:** Clean — noun phrase, internal use noted, not user-invocable.

**Content segmentation:** All core rules. No overhead.

**Estimated compression:** ~0 lines (already minimal)

**Writing style:** Dense. Imperative bullets.
**Prose quality:** Good. Code Quality section lists 6 rules in 6 lines.
**Progressive disclosure:** N/A — injection skill.
**Issues:** None.

---

### recall
**Path:** `/Users/david/code/claudeutils/agent-core/skills/recall/SKILL.md`
**Word count (body):** ~600 words
**Line count:** 115
**Grade:** A-

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" trigger list.

**Content segmentation:**
- Core rules: ~8 lines (cumulative behavior, skip already-loaded content, tail-recurse rules)
- Mechanical instructions: ~20 lines (3-pass process, batch resolution commands)
- Conditional paths: ~15 lines (mode descriptions: deep, broad, all, everything)
- Redundant content: ~0 lines
- Examples: ~5 lines (output format example)
- Guidelines: ~10 lines (depth by mode table)
- Framework overhead: ~5 lines (relationship table at end)

**Estimated compression:** ~20 lines removable (~17%)
- Description frontmatter fix (~4 lines)
- Mode descriptions (deep/broad/all/everything): 4 paragraphs, could condense to 3 lines each (~8 lines saved)
- Relationship table at end: valuable differentiation from /when and /how — keep

**Writing style:** Clean. Good.
**Prose quality:** Good. The "Why This Exists" section (8 lines) is the most important behavioral context and should stay.
**Progressive disclosure:** Good: why → invocation → process → modes → comparison table.
**Issues:**
- Description frontmatter anti-pattern
- Mode descriptions slightly verbose

---

### reflect
**Path:** `/Users/david/code/claudeutils/agent-core/skills/reflect/SKILL.md`
**Word count (body):** ~1,700 words
**Line count:** 304
**Grade:** B

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" multi-trigger list.

**Content segmentation:**
- Core rules: ~15 lines (session-local diagnosis, framing block mandatory, diagnostic before fixes, stop after phase 4.5)
- Mechanical instructions: ~35 lines (classification table, fix scope table, 3 exit paths with actions)
- Conditional paths: ~50 lines (exit path 1/2/3 with when/actions, output artifacts section)
- Redundant content: ~10 lines (Key Design Decisions section restates content from protocol phases with different framing; "Integration" section restates obvious)
- Examples: ~35 lines (3 worked examples at end)
- Guidelines: ~25 lines (rule gap analysis bullets, contributing factors list)
- Framework overhead: ~20 lines (Additional Resources tail, Integration section)

**Estimated compression:** ~70 lines removable (~23%)
- Key Design Decisions section: 35 lines of rationale prose for decisions already encoded in the protocol (anti-pattern #3). Extract to references/rca-design-decisions.md (~35 lines → 2-line reference)
- Examples section: 3 worked examples at end (~35 lines → extract to references/)
- Integration section: obvious (~8 lines → 2 lines)
- Contributing factors list: condense to 3-line rule (~4 lines)

**Writing style:** Good. Phase structure clear.
**Prose quality:** Anti-pattern: "Key Design Decisions" section contains 5 H3 sections each explaining the rationale for a protocol decision (Session-Local Diagnosis, Opus Expected, Framing Block is Mandatory, Diagnostic Before Fixes, Three Exit Paths, Returns Control). This is classic "design comment" overhead — valuable during development, but noise during invocation.
**Progressive disclosure:** Good protocol structure. But "Key Design Decisions" and "Examples" tail sections add 70 lines of secondary content.
**Issues:**
- Description frontmatter anti-pattern
- "When to Use" preamble section (anti-pattern #2)
- Key Design Decisions section is framework overhead / rationale (anti-pattern #3): ~35 lines
- Examples section extractable to references/

---

### release-prep
**Path:** `/Users/david/code/claudeutils/agent-core/skills/release-prep/SKILL.md`
**Word count (body):** ~900 words
**Line count:** 214
**Grade:** B+

**Description frontmatter:** Clean — noun phrase trigger list.

**Content segmentation:**
- Core rules: ~10 lines (do NOT run release command, abort on FAIL checks, no version bumping)
- Mechanical instructions: ~40 lines (7 steps with specific commands)
- Conditional paths: ~20 lines (documentation update reference, style corpus check, project type detection)
- Redundant content: ~5 lines (Critical Constraints section restates constraints already in steps)
- Examples: ~35 lines (example interaction showing output format)
- Guidelines: ~15 lines (readiness report format)
- Framework overhead: ~5 lines (Post-Report Behavior section)

**Estimated compression:** ~50 lines removable (~23%)
- "When to Use" section (anti-pattern #2): 8 lines → 0 (description covers this)
- Example interaction: extract to references/ (~35 lines → 1-line reference)
- Critical Constraints section: condense from 12 lines to 4 (restate the non-redundant ones only) (~8 lines)
- Post-Report Behavior: merge into step 7 (~5 lines → 2 lines)

**Writing style:** Good. HTML design comment in step 1 (prose-gate anchor) is unusual but intentional.
**Prose quality:** Mostly clean. The design comment in step 1 is operational metadata — keep.
**Progressive disclosure:** Good. Steps 1-7 sequential. Constraints and example at end.
**Issues:**
- "When to Use" preamble (anti-pattern #2)
- Example interaction extractable (~35 lines)
- Critical Constraints restates step content

---

### requirements
**Path:** `/Users/david/code/claudeutils/agent-core/skills/requirements/SKILL.md`
**Word count (body):** ~1,500 words
**Line count:** 278
**Grade:** B

**Description frontmatter:** Clean — noun phrase.

**Content segmentation:**
- Core rules: ~5 lines (extract from what was said, do not infer; question budget)
- Mechanical instructions: ~30 lines (mode detection heuristic, discovery actions, AskUserQuestion invocation syntax)
- Conditional paths: ~60 lines (extract mode procedure, elicit mode procedure — parallel structures with significant duplication)
- Redundant content: ~20 lines (elicit mode steps 2-3 say "same as extract mode steps 2-6" but then repeat them partially anyway; skill dependency scanning table appears twice in different forms)
- Examples: ~15 lines (mode detection examples, standard format template)
- Guidelines: ~30 lines (key principles table, default exit decision matrix, section rules)
- Framework overhead: ~8 lines (Integration Notes tail, Key Principles table)

**Estimated compression:** ~65 lines removable (~23%)
- Elicit mode procedure: shares steps 2-6 with Extract mode — extract shared procedure to avoid duplication (~20 lines saved)
- "Integration Notes" tail section: obvious workflow integration (~8 lines → 0)
- Key Principles table: 6 rows of principle + rationale. Condense to 3-line rule summary (~8 lines saved)
- Question budget rule appears twice (in gap detection and in key principles) (~4 lines)
- AskUserQuestion invocation syntax: verbose example — condense (~10 lines)

**Writing style:** Good. Tables well-used for standard format and principles.
**Prose quality:** Good. Hallucination risk note ("Extract from what was said, do NOT infer") is high-value and correctly prominent.
**Progressive disclosure:** Good flow. Mode detection → extract mode → elicit mode → format → exit.
**Issues:**
- Elicit mode procedure duplicates Extract mode (anti-pattern: repeated mechanical instructions)
- Integration Notes tail obvious
- Key Principles table verbose (rationale in table adds bulk)

---

### review
**Path:** `/Users/david/code/claudeutils/agent-core/skills/review/SKILL.md`
**Word count (body):** ~1,900 words
**Line count:** 384
**Grade:** C+

**Description frontmatter:** Clean — noun phrase.

**Content segmentation:**
- Core rules: ~5 lines (review what user requested, no fixes, output to file)
- Mechanical instructions: ~25 lines (gather changes per scope, git commands)
- Conditional paths: ~30 lines (scope determination, assessment criteria, output path)
- Redundant content: ~15 lines (assessment criteria bullets restate the obvious; Security section in Critical Constraints restates the always-loaded no-secrets rule)
- Examples: ~70 lines (example execution walkthrough, common scenarios section: 5 scenarios)
- Guidelines: ~80 lines (Analyze Changes section: 8 subsections with 3-10 bullets each including Code Quality, Design Conformity, Functional Completeness, Project Standards, Runbook File References, Self-referential modification, Security, Testing, Documentation, Completeness)
- Framework overhead: ~20 lines (Provide Feedback format template with markdown, Integration section restates workflow, References tail)

**Estimated compression:** ~140 lines removable (~36%)
- Analysis checklist (Analyze Changes section): 80 lines of nested bullets across 10 categories. Extract to `references/review-axes.md` (~80 lines → 5-line summary + reference)
- Common Scenarios section: 5 scenarios extractable to `references/common-scenarios.md` (~30 lines → 2-line reference)
- Example Execution walkthrough: extract to references/ (~25 lines → 1-line reference)
- Feedback format template: condense to key structure (remove redundant labels) (~10 lines saved)
- Integration section: obvious (~15 lines → 3 lines)
- Security redundant with system context (~3 lines)

**Writing style:** Verbose. Second-person in "Tone" section ("Be specific and actionable").
**Prose quality:** Anti-pattern: "Analyze Changes" section is a dense checklist with 10 categories and 30+ bullets. This is reference material injected into the main body — classic example/scenario bloat (anti-pattern #4/5). Anti-pattern: "Common Scenarios" describes 5 hypothetical situations (anti-pattern #5).
**Progressive disclosure:** Poor — "Analyze Changes" (80 lines) dominates the skill body before the output section. Review criteria should be in a reference file loaded on-demand.
**Issues:**
- "Analyze Changes" section is extractable guidelines/reference content (anti-pattern #5): ~80 lines
- "Common Scenarios" section (anti-pattern #5): ~30 lines extractable
- Example execution extractable (~25 lines)
- Security constraints redundant
- Integration section restates workflow
- 384 lines → target ~180 after extraction

---

### review-plan
**Path:** `/Users/david/code/claudeutils/agent-core/skills/review-plan/SKILL.md`
**Word count (body):** ~3,200 words
**Line count:** 587
**Grade:** B-

**Description frontmatter:** Clean — detailed description with domain coverage. Well-formatted.

**Content segmentation:**
- Core rules: ~20 lines (fix-all policy, false positive prevention via layered context, escalation criteria)
- Mechanical instructions: ~40 lines (review process phases 1-5 with grep patterns, fix procedures list)
- Conditional paths: ~100 lines (criteria sections 1-11 are per-type criteria with violation/correct examples; model assignment review)
- Redundant content: ~10 lines (Key Principles section restates 10 principles already evident from criteria sections)
- Examples: ~60 lines (violation/correct examples embedded within criteria sections, output format template)
- Guidelines: ~100 lines (review criteria 1-11 — partially guidelines, partially core rules)
- Framework overhead: ~15 lines (Integration, Sources sections)
- Sequential tool calls: ~10 lines (Phase 1 scan steps could batch)

**Estimated compression:** ~100 lines removable (~17%)
- Key Principles section (10 numbered items): redundant with body (~15 lines → 0)
- Violation/correct examples embedded in criteria: most are 8-15 lines each. Extract to `references/review-examples.md` (~60 lines → 5-line reference to examples file)
- Output format template: extract to `references/report-template.md` (~20 lines → 1-line reference)
- Integration section: condense to 4 lines (~8 lines saved)
- Sources section: valuable — keep (grounded citations deserve prominence)

**Writing style:** Clean. Criterion-per-section structure is good.
**Prose quality:** Good. Sources citations are excellent (grounded in research). Key Principles tail section is standard summary overhead.
**Progressive disclosure:** Good. Scan → validate → analyze → fix → report. Criteria sections 1-11 are the core content.
**Issues:**
- Key Principles tail section redundant (anti-pattern #3/overhead)
- Embedded violation/correct examples bloat criteria sections (anti-pattern #5)
- Output format template extractable

---

### runbook
**Path:** `/Users/david/code/claudeutils/agent-core/skills/runbook/SKILL.md`
**Word count (body):** ~5,200 words
**Line count:** 1,027
**Grade:** C

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" multi-trigger list.

**Content segmentation:**
- Core rules: ~25 lines (per-phase type model, model assignment, artifact-type override, D+B recall anchor)
- Mechanical instructions: ~80 lines (tier assessment format, tier 1/2 sequences, recall context steps, prepare-runbook.py invocation, validate-runbook.py subcommands)
- Conditional paths: ~450 lines (Tier 3 planning process: 12 phases, each 20-60 lines; TDD cycle planning guidance: 80 lines; Conformance validation: 15 lines; Testing strategy: 40 lines)
- Redundant content: ~30 lines (Phase 2.5 consolidation gate is near-identical to Phase 0.85 but post-assembly; testing strategy section partially restates design skill's TDD mode additions; "When to Use" preamble duplicates description)
- Examples: ~30 lines (phase type tagging format, RED/GREEN template, assertion quality table)
- Guidelines: ~50 lines (outline quality verification checklist, inline type selection criteria, pattern batching rule)
- Framework overhead: ~25 lines (section dividers between all 12 phases, "Planning Process" header, closing Phase 4 notes)
- Sequential tool calls: ~15 lines (multiple separate "commit then review" sequences per phase could batch)

**Estimated compression:** ~350 lines removable (~34%)
- Extract Tier 3 phases 0.5 through 3.5 to `references/tier3-planning-process.md` (~400 lines → 5-line trigger). The main skill body retains Tier 1/2 and the entry point, with a pointer to the Tier 3 protocol.
- TDD Cycle Planning Guidance: extract to `references/tdd-cycle-planning.md` (~80 lines → 3-line reference)
- Conformance Validation: extract to `references/conformance-validation.md` (~15 lines → 1-line reference)
- Description frontmatter fix (~4 lines)
- "When to Use" section (~12 lines → 0)

**Writing style:** Verbose. Multiple sections in procedural format with heavy repetition between phases (each phase has commit → review → handle outcome pattern).
**Prose quality:** Anti-pattern: Phase 0.85 and Phase 2.5 are nearly identical consolidation gate procedures with different framing. Could unify to one "Consolidation Gate" process used at both points. Anti-pattern: Each tier (1/2/3) has a "Recall context" sub-section that repeats the same recall invocation instructions with minor variations.
**Progressive disclosure:** Poor — 1,027 lines. Tier 3 planning phases (12 phases) are the source of the bloat. A user invoking `/runbook` for Tier 1 or 2 work doesn't need the 500+ lines of Tier 3 procedures.
**Issues:**
- Description frontmatter anti-pattern
- "When to Use" preamble (anti-pattern #2)
- Tier 3 planning phases are conditional paths and should extract to references/ (anti-pattern for conditional paths)
- Consolidation gate duplication (Phases 0.85 and 2.5)
- Recall context sub-sections repeat across all three tiers
- 1,027 lines is 2× the grounding document's target maximum of ~500 for complex skills
- Critical: at 1,027 lines, load cost is prohibitive for Tier 1/2 work

---

### shelve
**Path:** `/Users/david/code/claudeutils/agent-core/skills/shelve/SKILL.md`
**Word count (body):** ~430 words
**Line count:** 136
**Grade:** B

**Description frontmatter:** Clean — noun phrase.

**Content segmentation:**
- Core rules: ~5 lines (read first, bash only for mkdir/cp, report errors)
- Mechanical instructions: ~25 lines (7 steps with specific commands, template format)
- Conditional paths: ~5 lines (Restoration Notes)
- Redundant content: ~5 lines (Critical Constraints section restates tool usage rules already implicit in steps; "Report Results" step in protocol restates the example output)
- Examples: ~45 lines (Example Interaction: 40-line full simulated dialogue)
- Guidelines: ~0 lines
- Framework overhead: ~0 lines

**Estimated compression:** ~55 lines removable (~40%)
- "When to Use" section (anti-pattern #2): ~10 lines (partially duplicates description)
- Example Interaction: 40-line simulated dialogue extract to references/ or remove (~40 lines → 0 or 1-line reference). The dialogue adds no information beyond the 7 steps.
- Critical Constraints: condense to 2 lines (~7 lines saved)
- Restoration Notes: keep (not obvious from context, legitimate conditional path)

**Writing style:** Clear. The 7-step structure is readable.
**Prose quality:** Example Interaction dominates (40 lines = 29% of skill body). The dialogue is a worked example of an already-clear 7-step process.
**Progressive disclosure:** Good skeleton: when → steps → constraints → example → restoration.
**Issues:**
- "When to Use" preamble section (anti-pattern #2)
- Example Interaction section (anti-pattern #5): 40 lines for an already-clear 7-step process
- Critical Constraints restates step rules

---

### token-efficient-bash
**Path:** `/Users/david/code/claudeutils/agent-core/skills/token-efficient-bash/SKILL.md`
**Word count (body):** ~2,500 words
**Line count:** 523
**Grade:** C+

**Description frontmatter:** Anti-pattern — "This skill should be used when writing multi-step bash scripts…" trigger sentence.

**Content segmentation:**
- Core rules: ~10 lines (pattern: exec 2>&1 + set -xeuo pipefail, intent comment required, 3+ commands threshold)
- Mechanical instructions: ~20 lines (flag explanations, when to use / not use, || true usage)
- Conditional paths: ~30 lines (strict mode caveats, directory changes with trap/subshell, arithmetic expansion)
- Redundant content: ~30 lines (reconciliation with error handling rules restates the always-loaded error-handling fragment; "Token Economy Benefits" section explains the before/after with numbers that are estimates not measurements)
- Examples: ~200 lines (8 code examples: traditional vs efficient, 3 worked examples, anti-patterns section with 3 bad/good code blocks, integration with commit skill)
- Guidelines: ~30 lines (When to Use / Do NOT use sections, anti-patterns list)
- Framework overhead: ~10 lines (Summary section at end restates the pattern + use/caveat rules)

**Estimated compression:** ~200 lines removable (~38%)
- Extract examples 1-3 (file operations, git workflow, setup with expected failures) to `references/examples.md` (~60 lines → 2-line reference)
- Extract anti-patterns section to references/ (~45 lines → 1-line reference)
- Extract directory changes section to references/ (~35 lines → 2-line reference)
- Remove integration with commit skill section (obvious application) (~15 lines)
- Remove token economy benefits before/after comparison (examples do this more concisely) (~25 lines)
- Summary tail section: remove (restates the pattern already at top) (~20 lines)
- Description frontmatter fix (~4 lines)

**Writing style:** Clear. Good technical writing.
**Prose quality:** Anti-pattern: "Token Economy Benefits" section contains a before/after code comparison (25 lines) that repeats what the opening example already shows. Anti-pattern: "Summary" tail section (20 lines) restates the pattern + caveats already stated in the body. Anti-pattern: 8 code examples are educational documentation, not skill instructions — this is a C-grade driver of length.
**Progressive disclosure:** Poor — the skill reads like a tutorial document rather than a skill instruction. 60% of the content is examples and explanation.
**Issues:**
- Description frontmatter anti-pattern
- 8 code examples (anti-pattern #5): ~200 lines total — overwhelms the core instructions
- "Token Economy Benefits" section redundant with examples (~25 lines)
- Summary tail section redundant (~20 lines)
- Reconciliation section redundant with always-loaded fragment (~8 lines)
- At 523 lines, this skill has the highest example-to-instruction ratio of any skill in the corpus

---

### when
**Path:** `/Users/david/code/claudeutils/agent-core/skills/when/SKILL.md`
**Word count (body):** ~150 words
**Line count:** 49
**Grade:** A

**Description frontmatter:** Anti-pattern — "This skill should be used when the agent needs to recall behavioral knowledge…" trigger list.

**Content segmentation:** Core rules + mechanical instructions. Minimal.

**Estimated compression:** ~8 lines removable (~16%)
- Description frontmatter fix (~4 lines)
- "When NOT to Use" (4 lines): minor duplication across how/recall/when trio — keep for standalone clarity

**Writing style:** Dense. Clean.
**Prose quality:** Excellent. Resolution modes with bash examples. Output format described concisely.
**Progressive disclosure:** Good: resolution modes → when to use → when not → output.
**Issues:**
- Description frontmatter anti-pattern (minor)

---

### worktree
**Path:** `/Users/david/code/claudeutils/agent-core/skills/worktree/SKILL.md`
**Word count (body):** ~750 words
**Line count:** 130
**Grade:** A-

**Description frontmatter:** Anti-pattern — "This skill should be used when the user asks to…" multi-trigger.

**Content segmentation:**
- Core rules: ~10 lines (sandbox bypass required for mutations, slug determinism, merge idempotency)
- Mechanical instructions: ~40 lines (Mode A/B/C procedures, conflict resolution steps, precommit failure recovery)
- Conditional paths: ~20 lines (Mode B parallel group analysis, exit codes 0/1/2/3)
- Redundant content: ~0 lines
- Examples: ~0 lines
- Guidelines: ~20 lines (Usage Notes section: 7 notes)
- Framework overhead: ~0 lines

**Estimated compression:** ~20 lines removable (~15%)
- Description frontmatter fix (~4 lines)
- Mode B dependency analysis logic (lines 52-65): dense 14-line checklist. Condense to 4 criteria with one-line each (~6 lines saved)
- Usage Notes: 7 notes. Condense notes 3-5 (determinism, idempotency, automation) to 2-line summary (~5 lines)

**Writing style:** Dense. Good mode structure (A/B/C).
**Prose quality:** Good. Exit code handling (0/1/2/3) is well-structured. Sandbox bypass warning is prominent where needed.
**Progressive disclosure:** Good: Mode A → Mode B → Mode C → Usage Notes.
**Issues:**
- Description frontmatter anti-pattern
- Mode B dependency analysis slightly verbose

---

## Summary Table

| Skill | Lines | Grade | Desc Anti-Pattern | When-to-Use Preamble | Rationale Inline | Example Sections | 2nd-Person | Est. Compression |
|-------|-------|-------|-------------------|---------------------|-----------------|-----------------|------------|-----------------|
| brief | 42 | A+ | No | No | No | No | No | 0 lines |
| codify | 170 | B+ | Yes | Yes | No | No | No | ~35 lines (21%) |
| commit | 151 | A- | No | No | No | No | No | ~30 lines (20%) |
| deliverable-review | 175 | A- | Yes | No | No | No | No | ~30 lines (17%) |
| design | 521 | C+ | Yes | No | Yes | No | Yes | ~150 lines (29%) |
| doc-writing | 153 | B+ | Yes | Yes | No | Yes | Yes | ~40 lines (26%) |
| error-handling | 20 | B- | Yes | No | No | No | No | ~12 lines (60%) |
| gitmoji | 80 | B | Yes | Yes | No | No | No | ~30 lines (37%) |
| ground | 94 | A- | Yes | No | No | No | No | ~20 lines (21%) |
| handoff | 163 | B+ | Yes | No | No | No | No | ~40 lines (25%) |
| handoff-haiku | 121 | B | No | No | No | No | Yes | ~45 lines (37%) |
| how | 49 | A | Yes | No | No | No | No | ~8 lines (16%) |
| memory-index | 288 | B- | Yes | No | No | No | No | ~10 lines (4%) |
| next | 83 | B | Yes | Yes | No | Yes | No | ~25 lines (30%) |
| opus-design-question | 117 | B+ | No | Yes | No | Yes | No | ~40 lines (34%) |
| orchestrate | 521 | C | No | Yes | Yes | Yes | Yes | ~130 lines (25%) |
| plugin-dev-validation | 528 | B- | No | No | Yes | Yes | No | ~120 lines (23%) |
| prioritize | 127 | A- | Yes | No | No | No | No | ~25 lines (20%) |
| project-conventions | 32 | A+ | No | No | No | No | No | 0 lines |
| recall | 115 | A- | Yes | No | No | No | No | ~20 lines (17%) |
| reflect | 304 | B | Yes | Yes | Yes | Yes | No | ~70 lines (23%) |
| release-prep | 214 | B+ | No | Yes | No | Yes | No | ~50 lines (23%) |
| requirements | 278 | B | No | No | No | No | No | ~65 lines (23%) |
| review | 384 | C+ | No | Yes | No | Yes | Yes | ~140 lines (36%) |
| review-plan | 587 | B- | No | No | No | Yes | No | ~100 lines (17%) |
| runbook | 1027 | C | Yes | Yes | No | Yes | No | ~350 lines (34%) |
| shelve | 136 | B | No | Yes | No | Yes | No | ~55 lines (40%) |
| token-efficient-bash | 523 | C+ | Yes | No | No | Yes | No | ~200 lines (38%) |
| when | 49 | A | Yes | No | No | No | No | ~8 lines (16%) |
| worktree | 130 | A- | Yes | No | No | No | No | ~20 lines (15%) |
| **TOTAL** | **7,182** | | **18/30** | **13/30** | **5/30** | **13/30** | **5/30** | **~1,770 lines (25%)** |

---

## Anti-Pattern Analysis

### Current State vs Prior Audit

| Anti-Pattern | Prior Count | Current Count | Delta |
|---|---|---|---|
| Description "This skill should be used when…" | 18/30 | 18/30 | No change |
| "When to Use" preamble sections | 15/30 | 13/30 | -2 (marginal improvement) |
| Rationale clauses inline | ~5/30 | 5/30 | No change |
| Example/scenario sections in body | ~10/30 | 13/30 | +3 (slight worsening) |
| Second-person language | ~5/30 | 5/30 | No change |

**New anti-patterns identified in this audit:**
- **Redundant content from always-loaded context**: 6 skills contain rules restated from fragments already in system prompt (error-handling, handoff-haiku, commit, token-efficient-bash, reflect, orchestrate). Compression budget: 80-100%.
- **Tail section overhead**: 12 skills end with redundant "Additional Resources", "Integration", "References", or "Key Principles" sections that restate content already in the body or obvious from context.
- **Conditional path bloat in body**: 5 skills (runbook, design, orchestrate, token-efficient-bash, review) keep large conditional paths (rarely triggered, >30 lines) in the body instead of extracting to references/.

### Description Anti-Pattern Detail

The 18 skills with "This skill should be used when…" description anti-pattern:

codify, doc-writing, error-handling, gitmoji, ground, handoff, how, memory-index, next, reflect, runbook, token-efficient-bash, when, worktree, deliverable-review, design, prioritize, recall

**Fix template:** Replace `"This skill should be used when [trigger]..."` with a noun phrase:
- `"This skill should be used when the user asks to 'commit', 'ci'"` → `"Create git commits with high-quality messages and gitmoji selection"`
- Noun phrase captures: what it produces + key distinguishing behavior

---

## Grade Distribution

| Grade | Count | Skills |
|---|---|---|
| A+ | 2 | brief, project-conventions |
| A | 2 | how, when |
| A- | 5 | commit, deliverable-review, ground, prioritize, recall, worktree (6, see note) |
| B+ | 4 | codify, doc-writing, handoff, opus-design-question, release-prep (5, see note) |
| B | 5 | gitmoji, handoff-haiku, next, reflect, requirements, shelve (6) |
| B- | 4 | error-handling, memory-index, plugin-dev-validation, review-plan |
| C+ | 3 | design, review, token-efficient-bash |
| C | 2 | orchestrate, runbook |

_Note: worktree is A-, release-prep is B+. Total: 30 skills._

Corrected counts:
- A+: 2 (brief, project-conventions)
- A: 2 (how, when)
- A-: 6 (commit, deliverable-review, ground, prioritize, recall, worktree)
- B+: 4 (codify, doc-writing, handoff, opus-design-question)
- B: 6 (gitmoji, handoff-haiku, next, reflect, requirements, shelve)
- B-: 4 (error-handling, memory-index, plugin-dev-validation, review-plan)
- C+: 3 (design, review, token-efficient-bash)
- C: 3 (orchestrate, runbook, release-prep)

_Revised: release-prep is B+ not C. Counts:_
- A+: 2, A: 2, A-: 6, B+: 5, B: 6, B-: 4, C+: 3, C: 2

---

## Compression Opportunities

Top 10 skills by estimated line savings, with specific extraction targets:

### 1. runbook — ~350 lines (34%)
- **Extract:** Tier 3 planning phases 0.5–3.5 → `references/tier3-planning-process.md` (~400 lines → 5-line trigger in main skill)
- **Extract:** TDD Cycle Planning Guidance → `references/tdd-cycle-planning.md` (~80 lines → 3-line reference)
- **Extract:** Conformance Validation → `references/conformance-validation.md` (~15 lines → 1-line reference)
- **Fix:** Description frontmatter, remove "When to Use" preamble
- **Unify:** Phases 0.85 and 2.5 are identical consolidation gates — one procedure, two call sites

### 2. token-efficient-bash — ~200 lines (38%)
- **Extract:** Three worked examples → `references/examples.md` (~60 lines → 2-line reference)
- **Extract:** Anti-patterns section → `references/anti-patterns.md` (~45 lines → 1-line reference)
- **Extract:** Directory changes section → `references/directory-changes.md` (~35 lines → 2-line reference)
- **Remove:** Token economy benefits before/after (redundant with examples, ~25 lines)
- **Remove:** Summary tail (restates body, ~20 lines)

### 3. review — ~140 lines (36%)
- **Extract:** "Analyze Changes" checklist (10 categories) → `references/review-axes.md` (~80 lines → 5-line summary + reference)
- **Extract:** Common Scenarios → `references/common-scenarios.md` (~30 lines → 2-line reference)
- **Extract:** Example Execution → `references/example-execution.md` (~25 lines → 1-line reference)
- **Remove:** Security redundancy (~3 lines)

### 4. design — ~150 lines (29%)
- **Extract:** Phase A.3-5 (research protocol) → `references/research-protocol.md` (~35 lines → 3-line trigger)
- **Extract:** Phase B (discussion protocol) → `references/discussion-protocol.md` (~25 lines → 2-line trigger)
- **Extract:** Phase C.1 content rules → `references/design-content-rules.md` (~30 lines → 4-line summary)
- **Remove:** A.1 clarification paragraphs (redundant with table, ~12 lines)
- **Remove:** Binding constraints tail + Output Expectations sections (~18 lines)

### 5. orchestrate — ~130 lines (25%)
- **Extract:** "Common Scenarios" → `references/common-scenarios.md` (~40 lines → 2-line trigger)
- **Extract:** Continuation protocol → `references/continuation.md` (~35 lines → 3-line trigger)
- **Condense:** "Weak Orchestrator Pattern" rationale → 5-line summary (~30 lines saved)
- **Extract:** Progress tracking detailed approach → `references/progress-tracking.md` (~20 lines)

### 6. review-plan — ~100 lines (17%)
- **Extract:** Violation/correct examples → `references/review-examples.md` (~60 lines → 5-line reference)
- **Extract:** Output format template → `references/report-template.md` (~20 lines → 1-line reference)
- **Remove:** Key Principles tail section (~15 lines)

### 7. plugin-dev-validation — ~120 lines (23%)
- **Extract:** Good/Bad Examples per artifact type → `references/examples-per-type.md` (~80 lines → 5-line reference)
- **Remove:** Alignment Criteria section (redundant, ~15 lines)
- **Remove:** Usage Notes tail (redundant, ~12 lines)

### 8. reflect — ~70 lines (23%)
- **Extract:** Key Design Decisions section → `references/rca-design-decisions.md` (~35 lines → 2-line reference)
- **Extract:** Examples section → `references/rca-examples.md` (~35 lines → 1-line reference)

### 9. requirements — ~65 lines (23%)
- **Unify:** Extract mode and Elicit mode shared steps → single "shared procedure" section (~20 lines)
- **Remove:** Integration Notes tail (~8 lines)
- **Condense:** Key Principles table → 3-line summary (~8 lines)

### 10. shelve — ~55 lines (40%)
- **Remove:** Example Interaction (40-line simulated dialogue for a 7-step process) (~40 lines)
- **Remove:** "When to Use" preamble (10 lines, covered by description)
- **Condense:** Critical Constraints → 2 lines (~5 lines)

---

## Cross-Cutting Patterns

### Pattern: Skill-as-Tutorial
Skills `token-efficient-bash`, `review`, `orchestrate`, and `runbook` read like tutorial documents — they contain extensive examples, rationale, before/after comparisons, and scenario walkthroughs. These are valuable during development/onboarding but add load cost at invocation time. Extraction to `references/` is the correct fix: examples load on-demand, not on every skill invocation.

### Pattern: Tail Section Overhead
12 skills end with redundant "Additional Resources", "Integration", "References", or "Key Principles/Summary" sections (codify, gitmoji, handoff, orchestrate, reflect, release-prep, requirements, review, token-efficient-bash, deliverable-review, ground, prioritize). These sections typically restate: (a) references already embedded in the body, (b) the workflow position which is obvious from the skill's purpose, or (c) a summary of principles already stated as rules. Removal: safe in all 12 cases.

### Pattern: Conditional Path Bloat
The 5 largest skills (runbook 1027L, design 521L, orchestrate 521L, review-plan 587L, token-efficient-bash 523L) all contain large conditional paths in the main body. The Segment→Attribute→Compress framework rates conditional paths at 70-80% compression via extraction to on-demand references. Applying this to just these 5 skills would save ~700 lines (10% of the total corpus).

### Pattern: Redundant Always-Loaded Rules
6 skills contain rules that duplicate always-loaded context: error-handling (duplicates the fragment entirely), handoff-haiku (task metadata format from execute-rule.md), commit (secrets rule), token-efficient-bash (reconciliation with error-handling fragment), reflect (integration section), orchestrate (escalation rule). Compression budget: 80-100% per instance.

### Pattern: Description Anti-Pattern Stability
18/30 skills still carry the "This skill should be used when…" description anti-pattern. This was 18/30 in the prior audit — no improvement. The fix is mechanical (1-2 lines per skill) but has not been applied. A batch pass with clear template would resolve all 18 in one operation.
