# Recall Tool Anchoring — Outline

## Problem

31 recall gates across 13 files. 61% (19/31) prose-only. Documented bypasses: deliverable-review ran without recall; recall-artifact summary treated as full recall pass (both in learnings.md).

Root cause codified: "Execution-mode cognition optimizes for next tool call. Steps without tool calls register as contextual commentary." (implementation-notes.md, D+B Hybrid)

Two distinct failure classes:
- **Read-side (19 gates):** Consumers (correctors, reviewers) skip loading recall content. High frequency, documented.
- **Write-side (3 gates):** Producers (designer, planner) skip re-evaluating artifact after exploration. Lower frequency, no documented instances — but prose-only, so predictably fragile.

## Approach

### Format change: reference manifest

Recall-artifact becomes a thin reference list, not a content dump.

```
when designing quality gates — layered enforcement for recall gates
how to prevent skill steps from being skipped — core pattern being applied
when sub-agent rules not injected — correctors need explicit recall
```

Each line: trigger phrase + one-line relevance annotation (designer's curation).

**Why this solves read-side tool-anchoring structurally:**
- References contain no content → consumers MUST call a resolution tool to get usable content
- Tool call forced by format, not by prose instruction
- Staleness eliminated: references resolve to current decision file content
- Token efficient: ~15 lines vs ~200 lines for content dump

### Layer 1 (Outer): D+B restructure of recall gates

Apply existing convention: every skill step opens with a concrete tool call.

**Read-side gates (correctors, reviewers):**
- Step opens with: `Bash: agent-core/bin/recall-resolve.sh <artifact-path>`
- Resolution is the tool anchor — can't get content without calling it
- Format makes this structural, not behavioral

**Write-side gates (design A.5, C.1, runbook 0.75):**
- Step opens with: `Bash: agent-core/bin/recall-diff.sh <job>`
- Shows what changed in plan directory since last artifact update
- Gives designer/planner data to evaluate, rather than relying on them to remember to evaluate
- Judgment still required (which entries to add/remove) — but the data-gathering is tool-anchored

### Layer 2 (Middle): Prototype scripts

Throwaway scripts in `agent-core/bin/`. Validate the concept before claudeutils integration.

**`agent-core/bin/recall-check.sh <job-name>`**
- Validates `plans/<job>/recall-artifact.md` exists, is non-empty
- Exit 0 / exit 1 + diagnostic

**`agent-core/bin/recall-resolve.sh <artifact-path>`**
- Reads reference manifest, strips `—` annotations, feeds triggers to when-resolve.py
- Outputs resolved content to stdout
- Thin wrapper around existing when-resolve.py

**`agent-core/bin/recall-diff.sh <job-name>`**
- Lists files changed in plan directory since recall-artifact.md mtime
- git-based (`git diff --name-only` against mtime or last commit touching artifact)

No TDD, no Click CLI, no module structure. Scripts are disposable — learnings feed the eventual claudeutils integration.

### Layer 3 (Inner): PreToolUse hook on Task delegation

Soft enforcement at delegation boundary:
- PreToolUse hook on Task matcher
- Detects `plans/<job>` path in prompt, checks recall-artifact.md existence
- Missing → injects additionalContext warning
- Warning, not block — different failure mode than Layer 1/2

Hooks fire in main session only — correct, the delegator is in main session.

## Key Decisions

**D-1: Reference manifest over content dump.** Solves read-side tool-anchoring structurally (format forces resolution call). Eliminates staleness. Preserves curation via one-line relevance annotations.

**D-2: Throwaway prototype, not production CLI.** Validate format + resolution mechanics with shell scripts before investing in claudeutils module, TDD, Click integration. Scripts are `agent-core/bin/recall-*.sh` — disposable, no test suite, learn from real pipeline usage.

**D-3: Three scripts.** `check` (exists?), `resolve` (expand references → content), `diff` (what changed since last update?). `resolve` is the read-side anchor. `diff` is the write-side anchor. `check` is the validation layer.

**D-4: `generate` deferred.** Entry selection is cognitive (designer chooses which decisions matter for this task). Can't script without viable heuristic. Prototype resolution side first.

**D-5: `diff` anchors write-side gates.** The 3 re-evaluation gates are judgment gates — designer must decide what to update. `diff` provides data for that judgment. D+B: merge re-evaluation prose into adjacent step, open with `diff` as tool call.

**D-6: Injection gates (14) stay prose.** Can't be tool-anchored without fragile text matching. Hook (Layer 3) catches missing artifacts. D+B restructure ensures reading happens; injection into prompt text remains delegator's responsibility.

**D-7: Resolution caching deferred.** `.resolved` companion file adds complexity. Skip for prototype — measure whether repeated resolution is actually a problem before solving it.

## Scope

**IN:**
- Reference manifest format for recall-artifact.md
- Three prototype scripts (`recall-check.sh`, `recall-resolve.sh`, `recall-diff.sh`)
- PreToolUse hook on Task (soft warning)
- D+B restructure of read-side gates in 5 skills + 3 corrector agents
- D+B restructure of write-side gates in design/runbook skills
- Permission and hook registration in settings.json

**OUT:**
- claudeutils CLI integration (deferred to post-prototype)
- TDD / test suite for prototype scripts
- `_recall generate` (entry selection is cognitive)
- Resolution caching (measure first)
- Recall injection validation (stays prose)
- Hard blocking on missing recall (warning only)
- Changes to prepare-runbook.py or when-resolve.py
- crew-orchestrate-evolution agents (plan-specific, regenerated)

## Affected Files

**New (prototype):**
- `agent-core/bin/recall-check.sh`
- `agent-core/bin/recall-resolve.sh`
- `agent-core/bin/recall-diff.sh`
- `agent-core/hooks/pretooluse-recall-check.py`

**Modified (D+B restructure):**
- `agent-core/skills/design/SKILL.md` — A.1 generation, A.5/C.1 re-eval → `recall-diff.sh`
- `agent-core/skills/runbook/SKILL.md` — Phase 0.5 check, 0.75 re-eval → `recall-diff.sh`
- `agent-core/skills/review-plan/SKILL.md` — recall gate → `recall-resolve.sh`
- `agent-core/skills/deliverable-review/SKILL.md` — recall gate → `recall-resolve.sh`
- `agent-core/skills/orchestrate/SKILL.md` — checkpoint recall → `recall-resolve.sh`
- `agent-core/agents/design-corrector.md` — Step 1.5 → `recall-resolve.sh`
- `agent-core/agents/outline-corrector.md` — Step 2 item 4 → `recall-resolve.sh`
- `agent-core/agents/runbook-outline-corrector.md` — Step 2 item 4 → `recall-resolve.sh`

**Config:**
- `.claude/settings.json` — hook registration, `Bash(agent-core/bin/recall-*:*)` permission

## Prototype Steps

1. Write `recall-check.sh` — trivial file-existence check
2. Write `recall-resolve.sh` — parse manifest, feed to when-resolve.py
3. Write `recall-diff.sh` — git diff against artifact mtime
4. Convert one recall-artifact to reference manifest format (this plan's artifact as guinea pig)
5. Convert design-corrector to D+B pattern with `recall-resolve.sh`
6. Run through real pipeline, observe behavior
7. Roll out D+B restructure to remaining skills/agents
8. Add PreToolUse hook
9. Assess: what worked, what needs claudeutils integration, what to discard

## Open Questions

None. Prototype-first derisks before committing to production code.
