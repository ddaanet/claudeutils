# Topic 1: Memory System Evolution — Evidence Bundle

## 1. Git Timeline

Commits ordered chronologically, tracing the full arc from initial implementation through evaluation and redesign.

### Phase A: Foundation — Memory Index & Always-Loaded Context (Feb 1)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-01 | `9a5f9f71` | Implement ambient awareness with memory index and path-scoped rules |
| 2026-02-01 | `6e88a294` | Move memory index to project-level, seed with 46 entries |

Commit `9a5f9f71` body: "Import memory-index.md in CLAUDE.md for always-loaded discovery. Add 2 path-scoped rules. Document memory index pruning design problem."

Commit `6e88a294` body: "Create agents/memory-index.md with seeded entries (4 sections). Entry format: keyword-rich summaries with arrow separator. Seeding: behavioral rules (5), workflows (7), decisions (9), tools (7)."

### Phase B: /when and /how Skills — Active Lookup (Feb 8–13)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-08 | `00b8ec35` | Add memory index recall analysis tool |
| 2026-02-13 | `1a9b2c4b` | Cycle 11.1: Update recall index parser for /when format |
| 2026-02-13 | `fc0f293f` | Cycle 11.3: Verify recall analysis with new /when format |
| 2026-02-13 | `8df92e27` | Fix recall path matching and rerun baseline analysis |
| 2026-02-13 | `fb16d94e` | Refactor complex parsing functions to reduce complexity |
| 2026-02-13 | `f2715734` | Merge when-recall worktree |

The when-recall worktree implemented fuzzy matching for `/when` and `/how` skill invocations — TDD cycles 0.1 through 1.x covering word-overlap tiebreaker, minimum score threshold, section navigation, and file navigation.

### Phase C: Recall Infrastructure — Measurement & Tooling (Feb 13–23)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-13 | `8df92e27` | Fix recall path matching and rerun baseline analysis |
| 2026-02-23 | `c7a55dd5` | Finalize remember-skill-update outline with 6 phases and 13 FRs |
| 2026-02-23 | `ebbc7936` | Rename /remember skill to /codify (step 6.1) |
| 2026-02-23 | `ed951bc1` | Ground recall pass: 4-pass pipeline memory model |

### Phase D: The 4.1% Inflection Point (Feb 20)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-20 | `c4b1e043` | Evaluate /when recall: 4.1% usage, unblock memory-index demotion |
| 2026-02-20 | `917122ba` | Context optimization analysis and hook batch scoping |

Commit `c4b1e043` body: "801 sessions scanned across 71 project dirs: 22 /when calls in 8/193 post-merge sessions. Direct decision file reads unchanged (21.2% to 21.8%), 1.1x improvement (noise). Root cause: metacognitive recognition bottleneck, not tool awareness. Unblock memory-index.md (3.7k tokens) demotion in context-optimization brief."

### Phase E: Recall Gate Anchoring — Tool-Based Enforcement (Feb 24–Mar 1)

| Date | Hash | Message |
|------|------|---------|
| 2026-02-24 | `7ee9d0c0` | Design recall gate tool-anchoring (31 gates, 61% prose-only) |
| 2026-02-24 | `66f58df0` | Runbook for recall-tool-anchoring (promoted from outline) |
| 2026-02-24 | `b982c69f` | Phase 2: Convert recall-artifact to reference manifest format |
| 2026-02-25 | `4ecd09b7` | Wire memory-index validation into precommit, fix orphans and duplicates |
| 2026-02-28 | `fc7d94e1` | Cycle 2.1: Check succeeds on valid artifact (recall CLI) |
| 2026-02-28 | `ff71a254` | Cycle 3.1: Resolve artifact mode — happy path |
| 2026-02-28 | `0ad15370` | Phase 5: Integration, cleanup, prototype deletion |
| 2026-03-01 | `0d867a23` | Cycle 1.1: Build inverted index from parsed entries |
| 2026-03-01 | `f4de036b` | Cycle 3.1: Topic detector block in hook |

### Phase F: Active Recall System — Architectural Redesign (Mar 2–6)

| Date | Hash | Message |
|------|------|---------|
| 2026-03-02 | `fc0d9b8a` | Create active recall system plan from architectural discussion |
| 2026-03-02 | `60de1237` | Capture requirements for active recall system |
| 2026-03-03 | `cff6fd79` | (session) Design inputs: metacognitive analysis, forced injection, Context7 |
| 2026-03-06 | `43abd7fe` | Design active recall system: outline + 7 architectural decisions |
| 2026-03-06 | `de5ddfdd` | Redraft outline with decomposition methodology (8 sub-problems, DAG) |

---

## 2. Session Excerpts

### Excerpt 1: The 4.1% Discovery — Recognition Bottleneck Diagnosed

**Session:** `f9e199ea-312e-4fa8-aec0-3316312f5c1b`
**Project:** when-recall-evaluation
**Date:** 2026-02-20

The pivotal moment where measurement data revealed the fundamental failure of agent-initiated recall.

> **Agent:** `/when` is barely used and hasn't moved the needle.
>
> - 801 sessions scanned across 71 project directories
> - 22 total `/when`/`/how` invocations in 8 of 193 post-merge sessions (4.1%)
> - Direct decision file reads unchanged: 21.2% to 21.8%
> - Total recall improvement: 1.1x (essentially noise)
>
> **Root cause:** `/when` changed the action mechanism (Read -> Skill -> Bash) but not the recognition step. Agents still need to recognize they're in a decision-relevant situation to invoke it — the same cognitive step the passive index relied on.

> **User:** so we are back to relying on explicit exploration steps and grep?

> **Agent:** For decisions that matter during execution, yes. The data confirms the recognition problem: giving agents a lookup tool doesn't help if they don't recognize when to use it — same failure mode as the passive index, different mechanism.
>
> What actually works, by the evidence:
> - **Always-loaded fragments** — 100% "recall" by definition, but token-expensive.
> - **Explicit paths in prompts** — orchestrator/vet delegation templates that name specific files.
> - **Grep during exploration** — design and planning phases where agents actively search.
>
> `/when` occupies a dead zone: cheaper than always-loaded, but requires the same recognition step that fails at 0.2%.
>
> Two paths forward that the data supports:
>
> **Hook-based injection** (already in hook batch Phase 1). UserPromptSubmit detects topic keywords and injects relevant decision content — same as forced-eval hook pattern from learnings (84% activation vs 20% baseline). Moves recognition from agent to script.
>
> **Structural embedding** — put decisions where agents already look.

### Excerpt 2: Metacognitive vs Procedural Recognition

**Session:** `f9e199ea-312e-4fa8-aec0-3316312f5c1b` (continued)
**Date:** 2026-02-20

User challenges the agent to evaluate its own diagnosis.

> **User:** d: agents do not recognize "/when" as actionable

> **Agent:** Partially agree, but the diagnosis is imprecise in a way that matters for choosing the fix.
>
> **Reason 2: `/when`'s trigger is metacognitive, not procedural.** Compare with skills that work:
> - `/commit` — trigger is a clear action boundary ("commit this")
> - `/handoff` — trigger is a clear action boundary ("end session")
> - `/when` — trigger is "you might be wrong about how to handle this situation"
>
> The first two require recognizing an *action*. `/when` requires recognizing *uncertainty about a decision you're currently making confidently*. LLMs don't introspect on their own confidence well. An agent that's about to handle errors incorrectly doesn't think "I should check the error handling decision" — it just handles errors the way it would by default.
>
> **Verdict:** The mechanism that fails is not "recognition of /when as a tool" but "recognition of uncertainty as a state requiring action." No amount of skill description tuning fixes that because the bottleneck is metacognition, not tool awareness.

### Excerpt 3: From Agent-Invoked to Script-Invoked Resolution

**Session:** `f9e199ea-312e-4fa8-aec0-3316312f5c1b` (continued)
**Date:** 2026-02-20

The conceptual pivot from agent recall to forced injection.

> **Agent:** The memory index and `/when` could still serve as the *backing store* for hook-based injection — the hook script matches topics against index entries and injects content. The agent never needs to recognize the situation; the hook does it mechanically.

> **Agent:** Brief updated. memory-index.md (3.7k tokens) moved from "blocked — waiting for usage data" to demotable, with the evaluation data as evidence. Key addition: the index's future role is as hook infrastructure (queried by scripts), not agent-visible context.

### Excerpt 4: Recall Gate Inventory — 61% Prose-Only Gates

**Session:** `3a299440-3acb-4de4-91fb-5f88466327fc`
**Project:** recall-tool-anchoring
**Date:** 2026-02-24

Design session that grounded the enforcement problem.

> **Agent:** All three plan files loaded:
> - **outline.md** — Design document: reference manifest format, 3 prototype scripts, D+B restructure of 8 skills/agents, PreToolUse hook. 9 prototype steps.
> - **recall-artifact.md** — 11 entries in current content-dump format (will be converted to reference manifest)
> - **reports/recall-gate-inventory.md** — 31 gates across 13 files; 61% prose-only, 26% tool-required, 13% implicit

From the outline itself (commit `7ee9d0c0`): "31 recall gates across 13 files. 61% (19/31) prose-only. Documented bypasses: deliverable-review ran without recall; recall-artifact summary treated as full recall pass. Root cause codified: 'Execution-mode cognition optimizes for next tool call. Steps without tool calls register as contextual commentary.'"

### Excerpt 5: TDD Execution of /when Fuzzy Matching

**Session:** `d2a626b7-44dc-49b7-93ca-6ba82e7a12a1`
**Project:** when-recall
**Date:** 2026-02-12–13

Orchestrated TDD execution building the recall matching engine.

> **Agent:** Resuming when-recall execution. Current state: 4/47 cycles complete (0.1, 0.2, 0.3 skip, 0.4).
>
> **Blocker identified:** Cycle 0.5 has a known test flaw. The assertions pass due to boundary bonuses (212 vs 202) even though the word-overlap tiebreaker feature is absent. The test needs rewriting with inputs that produce genuinely tied fzz scores.
>
> **Blast radius protocol:** "Fix test flaws before continuing. Test flaws are deliverable defects."

> **Agent:** Cycle 0.5 complete — Word-overlap tiebreaker implemented
> **Agent:** Cycle 0.6 complete — Minimum score threshold implemented

### Excerpt 6: Recall Fix — Path Normalization Bug

**Session:** `7304d4b5-c924-4565-8e5c-52b1b2b8460e`
**Project:** recall-fix
**Date:** 2026-02-13

Post-deliverable-review fix that revealed systematic zero recall from path mismatches.

> **Agent:** Now I can see the issue. The fixture has 1 Grep + 2 Reads = 3 tool calls.
>
> **M-2: Path normalization** - The issue is that `Path.__eq__` requires exact match. Real sessions use absolute paths while index entries use relative paths. Need to normalize by comparing path suffixes.
>
> **M-1: e2e test** - The assertion expects 4 tool calls but the fixture has 3.

This bug (commit `8df92e27`) caused the recall analysis to show 0% recall for entries where agents actually did read the relevant files — absolute vs relative path comparison failure masked real usage.

### Excerpt 7: Active Recall Architecture — Forced Injection as Core Design

**Session:** `ae5d319e-c0ca-4769-ab4e-1e70b863a50e`
**Project:** active-recall-system
**Date:** 2026-03-06

Requirements capture session that defined the active recall system vision.

> From the brief (loaded in session): "Replace training-data reliance for operational methodology with grounded recall. Training provides reasoning capability; recall provides authoritative inputs to reason over. Interaction structure (skills, tool gates, PreToolUse hooks) enforces application at the right moments."

The requirements document (commit `60de1237`) formalized:
- FR-1: Hierarchical index structure (split flat 449-line index into domain tree)
- FR-2: Broaden trigger classes beyond project decisions
- FR-3: External environment facts with version-keyed invalidation
- FR-4: Bulk conversion from documentation sources

### Excerpt 8: Context7 as Query-Keyed Cache, Not Bulk Import

**Session:** `cff6fd79-3377-4f84-a030-86e08a49c6d5`
**Project:** active-recall-system
**Date:** 2026-03-03

Design discussion that refined how external knowledge enters the system.

> **User:** d: no bulk import, evaluate context7 as query-keyed memory class

> **Agent:** Bulk import (FR-4 style) produces entries that may never be queried. The recall system already has a recognition problem [...]. Cached queries, by contrast, are self-selecting: they were needed once, and the cache serves as replay for the next occurrence.

> **User:** Stop repeating the "4.1%" number, it pertained agent-initiated passive recall, and included user-initiated recall. Not very accurate, and not relevant to active recall.

> **Agent:** Fair point. The 4.1% figure measured `/when` skill invocations across all sessions — it conflates agent-initiated and user-initiated usage, and it measured the passive lookup tool, not the recognition problem itself. Citing it as evidence for the demand-driven argument was sloppy.

---

## 3. Key Inflection Points

### Inflection 1: Always-Loaded to Active Lookup

**When:** Feb 1 -> Feb 8-13
**What changed:** memory-index.md started as an always-loaded `@`-reference in CLAUDE.md (3.7k tokens consumed every session). The `/when` and `/how` skills were built to make recall on-demand, reducing token cost.
**Evidence:** Commits `9a5f9f71`, `6e88a294` (creation), then `00b8ec35` through `f2715734` (when-recall implementation).
**Trigger:** Token cost concern — 3.7k tokens for an index that grew with every codified learning.

### Inflection 2: The 4.1% Measurement

**When:** Feb 20
**What changed:** Quantitative evaluation revealed `/when` was invoked in only 4.1% of post-merge sessions. The tool changed the retrieval mechanism but not the recognition step. Decision file reads were unchanged (21.2% -> 21.8%).
**Evidence:** Commit `c4b1e043`, session `f9e199ea`.
**Trigger:** Context optimization work needed usage data to justify demoting memory-index from always-loaded.
**Consequence:** Unblocked memory-index.md demotion. Shifted design direction from "better tools for agents" to "forced injection by infrastructure."

### Inflection 3: Metacognitive Recognition Bottleneck Named

**When:** Feb 20
**What changed:** The failure was diagnosed not as tool-awareness (agent doesn't know `/when` exists) but as metacognition (agent doesn't recognize it's in a situation where it should doubt its defaults). This distinction matters because it rules out an entire class of fixes (better descriptions, more prominent placement).
**Evidence:** Session `f9e199ea` — "The mechanism that fails is not 'recognition of /when as a tool' but 'recognition of uncertainty as a state requiring action.'"
**Consequence:** Procedural triggers (action boundaries) work; metacognitive triggers (uncertainty recognition) don't. This explains why `/commit` and `/handoff` succeed but `/when` fails.

### Inflection 4: Prose-Only Gates to Tool-Anchored Gates

**When:** Feb 24
**What changed:** Inventory revealed 61% of recall gates were prose-only — no tool call to enforce execution. Root cause: "Execution-mode cognition optimizes for next tool call. Steps without tool calls register as contextual commentary."
**Evidence:** Commit `7ee9d0c0`, session `3a299440`, `recall-gate-inventory.md`.
**Trigger:** Documented bypasses where deliverable-review ran without recall.

### Inflection 5: Forced Injection Architecture

**When:** Feb 20 (conceptualized) -> Mar 1 (implemented) -> Mar 6 (redesigned as active recall)
**What changed:** Recognition shifted from agent to deterministic code. UserPromptSubmit hooks detect topic keywords and inject relevant decision content. The memory-index becomes a backing store queried by scripts, not by agents.
**Evidence:** Commit `f4de036b` (topic detector hook), `43abd7fe` (active recall design with 7 architectural decisions).
**Trigger:** The 4.1% data plus the 84% activation rate for forced-eval hooks (from prior learnings) made the design choice obvious — forced injection at 84% beats voluntary recall at 4.1%.

### Inflection 6: From Flat Index to Hierarchical Domain Tree

**When:** Mar 2-6
**What changed:** The flat memory-index.md (449 lines, 366 entries) was recognized as unsustainable. Active recall system design introduced hierarchical index: `agents/memory/index.md` -> `agents/memory/<domain>.md` -> sub-domains. Prefix-free key structure with colon-delimited domains.
**Evidence:** Commit `60de1237` (FR-1), session `cff6fd79` (domain discussion), commit `de5ddfdd` (8 sub-problems DAG).
**Trigger:** Index growth from codify cycles (24-50 learnings consolidated per session) made flat file unwieldy for both token cost and navigation.
