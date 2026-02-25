# How to Prevent Skill Steps From Being Skipped
**Decision Date:** 2026-02-06

**Problem:** Skill steps with only prose judgment (no tool call) get skipped during execution. Manifested in 3 cases: commit skill session freshness (Step 0), commit skill vet checkpoint (Step 0b), orchestrate skill phase boundary (3.4).

**Root cause:** Execution-mode cognition optimizes for "next tool call." Steps without tool calls register as contextual commentary, not actionable work.

**Fix (D+B Hybrid):** Combines Option D (Read/Bash anchor) with Option B (restructure into adjacent step):
1. Eliminate standalone prose gates — merge each gate into its adjacent action step
2. Anchor with tool call — each gate's first instruction is a Read or Bash call providing data for evaluation
3. Explicit control flow — gate evaluation uses if/then with explicit branch targets

**Convention:** Every skill step must open with a concrete tool call (Read/Bash/Glob). Prose-only judgment steps are a structural anti-pattern.

**Design:** `plans/reflect-rca-prose-gates/outline.md`

**Impact:** Prevents prose gates from being skipped; establishes convention for future skill design.

Broader:
/when .Implementation Notes
/when ..implementation-notes.md

Related:
/when using at-sign references
/when placing DO NOT rules in skills
---
# When Placing DO NOT Rules In Skills
**Context:** Multi-phase skill procedures with content generation and cleanup.

**Anti-pattern:** Placing "don't write X" rules in cleanup/trim phases instead of writing phases.

**Problem:** Agent follows phases sequentially; by the time it reaches cleanup, the violation is already written.

**Correct pattern:** Place negative constraints alongside positive content guidance, where decisions are made.

**Example:** "No commit tasks" rule moved from Phase 6 (Trim) to Phase 3 (Context Preservation).

**Generalization:** Any rule about what NOT to produce should be co-located with instructions for WHAT to produce.

**Impact:** Prevents violations rather than detecting them after the fact.

Broader:
/when .Implementation Notes
/when ..implementation-notes.md

Related:
/when using at-sign references
/when prevent skill steps from being skipped
---
# When Selecting Model For Prose Artifact Edits
**Decision Date:** 2026-02-18

**Rule:** Prose edits to skills, fragments, agent definitions, and architectural documents require opus. These artifacts are LLM-consumed instructions — wording directly determines downstream agent behavior.

**Anti-pattern:** Assigning sonnet/haiku to prose edits based on "edit complexity" rather than artifact type.

**Evidence:** Tier 2 plan assigned sonnet to skill/fragment edits, haiku to agent audit. User corrected: all were prose edits to architectural artifacts requiring opus.

**Classification:**
- Skills, fragments, agent definitions, design documents → opus
- Code implementation, test writing, script edits → model by complexity (haiku/sonnet)
- Mechanical execution (copy-paste, config changes) → haiku

Broader:
/when .Pipeline Contracts
/when ..pipeline-contracts.md

Related:
/when choosing review gate
/when routing artifact review
/when review delegation scope template
/when UNFIXABLE escalation
/when declaring phase type
/when reviewing expanded phases
/when outline review produces ungrounded corrections
/when simplifying runbook outlines
/when selecting model for TDD execution
/when reviewing skill deliverable
/when concluding reviews
/when routing implementation findings
/when selecting review model
/when holistic review applies fixes
/when reviewing final orchestration checkpoint
---
# When Refactoring Agents Need Quality Directives
**Decision Date:** 2026-02-12

**Correct pattern:** Include explicit code quality and factorization directives in refactor prompts.

**Rationale:** Refactor agent focuses on warnings (line limits, complexity), doesn't proactively optimize for token efficiency.

Broader:
/when .Operational Practices
/when ..Artifact and Review Patterns
/when ..operational-practices.md
---
# How to Make Skills Discoverable
**Skill discovery layers:**

**Decision Date:** 2026-02-01

**Decision:** Skills require multiple discovery layers, not just good internal documentation.

**Anti-pattern:** Build well-documented skill and assume agents will find it ("build it and they will come")

**Correct pattern:** Surface skills via 4 discovery layers:
1. CLAUDE.md fragment or always-loaded context
2. Path-triggered `.claude/rules/` entry
3. In-workflow reminders in related skills
4. Directive skill description

**Rationale:** Agents only see skill listing descriptions and always-loaded context. Internal skill docs are invisible until invoked.

**Example:** opus-design-question skill had 248-line docs but zero external visibility — agents asked user instead of consulting it. Fixed with 4-layer approach.

**Impact:** Ensures skills are discoverable and used appropriately.

Broader:
/when .Project Configuration
/when ..Skill Discovery
/when ..project-config.md
---
# When Formatting Rules For Adherence
Bullet points outperform prose for discrete task adherence. Connected ideas requiring context benefit from paragraph format.

**Format by content type:**

| Content Type | Best Format | Rationale |
|-------------|-------------|-----------|
| Discrete rules | Bullets | Higher task adherence |
| Connected concepts | Prose paragraphs | Cohesion needed |
| Critical rules | Visually salient markers (⚠️, bold) | Attention capture |
| Examples | Code blocks | Pattern matching |

**Source:** [Effect of Selection Format on LLM Performance (arXiv 2025)](https://arxiv.org/html/2503.06926)

---

Broader:
/when .Prompt Structure Research
/when ..prompt-structure-research.md

Related:
/when ordering fragments in CLAUDE.md
/when writing rules for different models
/when too many rules in context
/when loading context for llm processing
---
# When Writing Rules For Different Models
Different model classes benefit from different instruction density:

| Model Class | Characteristics | Instruction Style |
|------------|----------------|-------------------|
| Opus | Handles complex/detailed prompts, catches nuances | Concise prose, trust inference |
| Sonnet | Handles clear prompts well, balanced | Clear bullets with context |
| Haiku | Needs precise, scoped tasks | Explicit steps, ⚠️ markers, DO NOT examples |

**Source:** [Claude Model Family (Anthropic)](https://www.anthropic.com/news/claude-3-family)

**Expansion ranges:** Same semantic content requires different rule counts:
- Strong (Opus): 3-5 rules per module
- Standard (Sonnet): 8-12 rules per module
- Weak (Haiku): 12-18 rules per module

---

Broader:
/when .Prompt Structure Research
/when ..prompt-structure-research.md

Related:
/when ordering fragments in CLAUDE.md
/when formatting rules for adherence
/when too many rules in context
/when loading context for llm processing
---
# When Designing Quality Gates
**Decision Date:** 2026-02-08

**Decision:** Quality gates should be layered with multiple independent checks to prevent single-point failures. No single gate should be trusted as the sole enforcement mechanism.

**Rationale:**

The statusline-parity RCA documented a cascade of failures where each quality gate—in isolation—passed successfully, yet the combined system failed to catch conformance issues (RC1), test scope limitations (RC2), and file size violations (RC3). This pattern reveals a fundamental design principle: single-layer validation is insufficient for complex work. Multiple, independent defense layers operating on different failure modes are required.

The parity iterations demonstrated:
- **Unit tests passed** (385/385) yet 8 visual parity issues remained undetected because tests verified data flow, not presentation against specification
- **Vet agent reviewed code quality** yet missed systemic conformance gaps because the review mandate did not include external reference comparison
- **File size constraint existed** (400-line limit) yet was either skipped or ignored before commit, requiring retroactive file splits

Each layer failed independently and only by combining them do we achieve adequate coverage.

**Pattern layers (from outer to inner):**

1. **Layer 1 — Outer defense (Execution Flow):** D+B hybrid (merge prose gates with adjacent action steps, anchor with tool call) ensures precommit appears in execution path and is actually executed
   - Prevents: Prose-only validation steps getting optimized/skipped in execution mode
   - Example: Commit skill Step 1 now opens with Read(session.md), not a prose judgment

2. **Layer 2 — Middle defense (Automated Checks):** Precommit catches line limits, lint, test failures via hard validation at commit time
   - Prevents: Oversized files, style violations, broken tests from being committed
   - Mechanism: `just precommit` runs `check_line_limits.sh`, linters, and test suite
   - Execution: Runs always unless in WIP-only modes (see Inner defense)

3. **Layer 3 — Inner defense (Quality Review):** Vet-fix-agent catches quality, alignment, and implementation issues through semantic review before commit
   - Prevents: Logic errors, integration problems, deviations from design
   - Scope: Full alignment verification (output matches design/requirements/acceptance criteria)
   - Note: Only as good as acceptance criteria specification — requires precise test descriptions for conformance work

4. **Layer 4 — Deepest defense (Conformance):** Conformance tests and reference validation catch spec-to-implementation drift
   - Prevents: Implementation that passes all automated checks yet diverges from specification
   - Mechanism: For work with external references (shell scripts, visual mockups, API specs), compare rendered output/behavior directly
   - Example: Conformance validation comparing Python statusline output to shell reference at `scratch/home/claude/statusline-command.sh` would have caught all 8 parity issues immediately

**Gap 3 + Gap 5 interaction:**

These two gaps interact to create a vulnerability:

- **Gap 3 (Prose gates skipping):** Without D+B hybrid fix, prose-only steps (like "run precommit as a judgment") get optimized past in execution mode, leading to the check not running at all.

- **Gap 5 (WIP-only bypass):** The commit skill supports `--test` and `--lint` modes which provide legitimate within-path bypasses of line limits, intended for TDD WIP commits. WIP-only means TDD GREEN phase commits only, before lint/complexity fixes. All other commits must use full `just precommit`. Without this scope restriction, these modes could be misused to bypass validation on final commits.

**Defense-in-depth closes this interaction:**

- **D+B (Outer defense)** ensures precommit runs (fixes Gap 3)
- **WIP-only restriction (Inner defense)** ensures `--test`/`--lint` modes are limited to work-in-progress commits, not final commits (fixes Gap 5)
- **Together:** Even if one layer is partially weak, the others compensate

Example scenario: If an agent were to use `--test` mode on what it perceives as "test-only" work, the outer D+B gate ensures the file size check still runs (because `just precommit` is invoked as a tool call, not skipped as prose). If D+B were not in place, the check could be skipped entirely.

**Example application:**

The statusline-parity failure cascade demonstrates each layer's necessity:

1. **Without outer defense (D+B):** Iteration 3 (aca8371) exceeded line limits and bypassed the precommit check via `--test` mode or prose skipping. The commit succeeded despite violation.

2. **Without middle defense (precommit):** Even with proper execution, files could be committed at any size.

3. **Without inner defense (vet alignment):** The Phase 4 checkpoint found one real issue (duplicate call) but missed the 8 parity issues because acceptance criteria were behavioral prose rather than exact expected strings. With stricter acceptance criteria (exact string matching from shell reference), alignment verification would catch output deviations.

4. **Without deepest defense (conformance):** Even with all three upstream layers perfect, the system could pass all tests and reviews yet still diverge from specification. The original statusline-wiring (Iteration 0) had 100% TDD compliance (28/28 RED-GREEN cycles), clean code, and passing tests—yet lacked all 13 visual indicators.

**Applicability:**

This pattern applies beyond parity tests—use for any quality gate design:
- When adding new quality mechanisms, consider which layer they belong to
- Multiple layers compensate for individual gate weaknesses (e.g., tests can pass but miss visual conformance; vet can review code but miss specification drift)
- No single layer is sufficient
- Each layer has a specific failure mode it prevents

**Related decisions:**

- **DD-1: Conformance tests mandatory for external references** — Deepest defense layer
- **DD-3: WIP-only restriction on `--test`/`--lint`** — Inner defense layer
- **DD-5: Vet alignment verification** — Inner defense layer
- **DD-6: Defense-in-depth pattern** — This decision (all four layers together)
- **Fix (Phase 1 Step 1): Commit skill WIP-only restriction** — Implements inner defense scoping
- **Fix (Phase 1 Step 2): D+B hybrid validation** — Implements outer defense execution flow

Broader:
/when .Defense-in-Depth Pattern
/when ..defense-in-depth.md

Related:
/when reviewing quality gate coverage
/when placing quality gates
/when splitting validation into mechanical and semantic
---
# When Bootstrapping Self-Referential Improvements
**Decision Date:** 2026-02-15

**Decision:** When improving tools/agents, apply each improvement before using that tool in subsequent steps.

**Pattern:** Phase ordering follows tool-usage dependency graph, not logical grouping. Collapses design→plan→execute into design→apply for prose-edit work.

**Rationale:** Unimproved agents reviewing their own improvements creates a bootstrapping problem.

Broader:
/when .Planning Workflow Patterns
/when ..Planning Workflow Patterns
/when ..workflow-planning.md
---
# When Reviewing Skill Deliverable
**Decision Date:** 2026-02-18

**Anti-pattern:** Delegating skill deliverable review to Task agent — agent lacks cross-project context (other skills' allowed-tools, fragment conventions, memory index patterns).

**Correct pattern:** Route to skill-reviewer agent (has cross-skill context) or review interactively in main session. The reviewer needs to compare against project-wide patterns, not just the artifact's internal consistency.

**Evidence:** Task agent found 5 minor issues but missed the major finding (Write missing from allowed-tools). Only detectable by comparing against 18 other skills' allowed-tools fields.

Broader:
/when .Pipeline Contracts
/when ..pipeline-contracts.md

Related:
/when choosing review gate
/when routing artifact review
/when review delegation scope template
/when UNFIXABLE escalation
/when declaring phase type
/when reviewing expanded phases
/when outline review produces ungrounded corrections
/when simplifying runbook outlines
/when selecting model for prose artifact edits
/when selecting model for TDD execution
/when concluding reviews
/when routing implementation findings
/when selecting review model
/when holistic review applies fixes
/when reviewing final orchestration checkpoint
