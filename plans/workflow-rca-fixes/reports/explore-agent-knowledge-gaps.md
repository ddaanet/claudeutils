# Agent Knowledge Gap Analysis

**Date:** 2026-02-14
**Purpose:** Determine which project knowledge to inject into sub-agents via `skills:` frontmatter

---

## Part 1: What Claude Code Gives Sub-Agents Natively

**Source:** `agent-prompt-task-tool.md`, `agent-prompt-task-tool-extra-notes.md`, `system-prompt-doing-tasks.md`, `system-prompt-tone-and-style.md`

### Native sub-agent system prompt content:

Sub-agents receive a minimal prompt:
- Identity: "You are an agent for Claude Code"
- Task framing: "Do what has been asked; nothing more, nothing less"
- File search guidance: Use Grep/Glob broadly, Read for specific paths
- File creation restriction: "NEVER create files unless absolutely necessary"
- Absolute paths required (cwd resets between bash calls)
- No emojis
- Thorough search guidance

### What sub-agents do NOT receive natively:

- **No code quality guidance** — main agent gets `system-prompt-doing-tasks.md` (avoid over-engineering, don't add unnecessary features, simple focused solutions, delete unused code) but this is NOT confirmed as injected into sub-agents
- **No deslop-equivalent** — main prompt has "avoid over-engineering" but no prose quality rules
- **No error handling philosophy** — no guidance on error suppression patterns
- **No project conventions** — sub-agents get zero project-specific knowledge unless passed via task prompt or `skills:` injection
- **No token economy** — no guidance on minimizing output tokens
- **No tool batching** — parallel tool call guidance is in `system-prompt-tool-usage-policy.md` (main agent), unclear if sub-agents receive it

### Native overlap with our fragments:

| Fragment | CC Native Coverage | Overlap |
|----------|-------------------|---------|
| deslop.md | Partial — "avoid over-engineering", "don't add features beyond what was asked" | ~30% (code deslop partially covered; prose deslop not covered at all) |
| error-handling.md | None | 0% |
| code-removal.md | Partial — "if something is unused, delete it completely", "avoid backwards-compatibility hacks" | ~50% (deletion covered; "don't archive" not covered) |
| token-economy.md | None for sub-agents | 0% |
| no-estimates.md | Main agent has "no time estimates" | ~80% (different framing but similar intent) |

---

## Part 2: Fragment Injection Value Assessment

| Fragment | Lines | Sub-agent defect evidence | CC native coverage | Injection value |
|----------|-------|--------------------------|-------------------|-----------------|
| **deslop.md** | 50 | RCA: vet agents produce verbose reports, plan-reviewer adds unnecessary commentary | 30% prose deslop uncovered | **High** — prose deslop rules absent from CC, directly addresses RCA defects |
| **error-handling.md** | 15 | No direct RCA evidence | 0% | **Medium** — small token cost, prevents `|| true` misuse in sub-agent bash |
| **code-removal.md** | 30 | No direct RCA evidence | 50% deletion covered | **Low** — CC already says "delete unused"; "don't archive" is niche |
| **token-economy.md** | 5 | Vet reports repeat file contents | 0% | **High** — 5 lines, near-zero cost, directly addresses report verbosity |
| **vet-requirement.md** | 40 | N/A (orchestrator-level, not sub-agent) | 0% | **None** — orchestrator concern, sub-agents don't delegate further |
| **commit-skill-usage.md** | 3 | N/A | 0% | **None** — sub-agents don't commit |
| **tool-batching.md** | 15 | Sub-agents don't batch tool calls well | Partial (main agent gets parallel guidance) | **Medium** — but CC may already inject tool-usage-policy into sub-agents |
| **bash-strict-mode.md** | 30 | No evidence | 0% | **Low** — sub-agents rarely write multi-step scripts |
| **sandbox-exemptions.md** | 40 | No evidence | 0% | **None** — main agent concern |
| **execution-routing.md** | 20 | No evidence | 0% | **None** — orchestrator concern |
| **delegation.md** | 30 | N/A | 0% | **None** — orchestrator concern, sub-agents can't spawn sub-agents |
| **communication.md** | 10 | Sub-agents occasionally proceed past boundaries | 0% | **Medium** — "stop at boundaries" useful but partially covered by "nothing more, nothing less" |
| **tmp-directory.md** | 5 | Sub-agents sometimes write to /tmp | 0% | **High** — 5 lines, prevents sandbox violations |

---

## Part 3: Revised Injection Recommendations

### Tier 1: High value, inject into review/fix agents
- **deslop.md** (~300 tokens) — Prose quality absent from CC, direct RCA evidence
- **token-economy.md** (~50 tokens) — Near-zero cost, addresses report verbosity

### Tier 2: High value, inject into all sub-agents
- **tmp-directory.md** (~50 tokens) — Prevents sandbox violations, near-zero cost

### Tier 3: Medium value, consider for specific agents
- **error-handling.md** (~100 tokens) — Small cost, useful for bash-heavy agents
- **communication.md** rules 1,4 only (~50 tokens) — "Stop on unexpected results", "stop at boundaries"

### Tier 4: Low value, skip
- **code-removal.md** — CC already covers deletion; "don't archive" is edge case
- **tool-batching.md** — CC may already inject parallel guidance
- **bash-strict-mode.md** — Sub-agents rarely need multi-step bash

### Not applicable for sub-agents
- vet-requirement.md, commit-skill-usage.md, sandbox-exemptions.md, execution-routing.md, delegation.md, no-estimates.md

---

## Part 4: Design Implications for FR-12

### Original FR-12 plan:
Wrap deslop, error-handling, code-removal as skills → inject into 5 agents

### Revised recommendation:
1. **Keep deslop** — high value, RCA evidence, CC doesn't cover prose deslop
2. **Drop code-removal** — low value, CC already covers "delete unused"
3. **Add token-economy** — high value, near-zero cost (5 lines)
4. **Add tmp-directory** — high value, prevents sandbox violations (5 lines)
5. **Keep error-handling** — medium value but cheap, useful for bash-heavy agents
6. **Consider communication subset** — "stop on unexpected results" + "stop at boundaries" useful for vet/review agents

### Proposed skill bundles:
- **project-conventions skill** (~400 tokens): Combine deslop + token-economy + tmp-directory into single skill. These are universal project rules, not domain-specific. Single injection = single cost.
- **error-handling skill** (~100 tokens): Keep separate for bash-heavy agents only.

### Agent assignments:
| Agent | project-conventions | error-handling |
|-------|-------------------|----------------|
| vet-fix-agent | ✓ | ✓ |
| design-vet-agent | ✓ | — |
| outline-review-agent | ✓ | — |
| plan-reviewer | ✓ (already has review-plan) | — |
| refactor | ✓ | ✓ |

---

## Part 5: Research Grounding

### Anthropic Context Engineering (2025)
- Sub-agents should receive **focused task context** rather than comprehensive information
- "Treating context as a precious, finite resource" — inject only what changes behavior
- Progressive disclosure: agents discover context through exploration, not frontloading
- **Implication:** Our approach of small, targeted skill injections (~300-400 tokens) aligns with Anthropic's recommendation

### ACE Framework (arXiv 2510.04618)
- Structured, incremental knowledge updates prevent information degradation
- 10.6% performance improvement from strategic knowledge injection
- Execution feedback drives effective adaptation without manual annotation
- **Implication:** Skills injected into agents act as "accumulated strategies" — matching ACE's context evolution model

### Context Window & Attention
- Context rot: recall accuracy decreases as token count increases
- **Implication:** Bundling related conventions into single skill (project-conventions) reduces injection points and keeps total overhead minimal (~400 tokens vs ~600 for 3 separate skills)

---

## Sources

- [Effective Context Engineering for AI Agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic, 2025
- [Agentic Context Engineering (ACE)](https://arxiv.org/abs/2510.04618) — arXiv, 2025
- [Context Engineering Guide](https://www.promptingguide.ai/guides/context-engineering-guide) — Prompt Engineering Guide
