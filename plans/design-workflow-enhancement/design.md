# Design: Design Workflow Enhancement

## Problem

The design skill produces full design documents in a single pass without user validation of approach. Designers lack systematic documentation loading — they rely on ad-hoc memory discovery and inline exploration. Research artifacts (exploration results, web searches) are discarded into context, unavailable for reuse by planners or future iterations.

## Requirements

**Functional:**
- Design skill produces plan outline first, iterates with user, then generates full design
- Documentation checkpoint replaces and expands current memory discovery
- Documentation hierarchy applied systematically: local knowledge → skills → Context7 → explore → web
- Design documents include documentation perimeter for downstream planner
- quiet-explore agent writes exploration results to files for reuse
- Planner reads documentation perimeter at start, allowed additional research for technical details

**Non-functional:**
- Dense output (token economy for opus designer)
- Exploration delegated (opus never greps/globs directly)
- Outline phase enables early user course-correction before expensive design generation

**Out of scope:**
- Session-log based capture of research artifacts (future work — see Future Work section)
- Custom claude-code-guide wrapper agent
- Custom Context7 wrapper agent
- Changes to plan-tdd or plan-adhoc beyond consuming documentation perimeter

## Architecture

### Design Skill: Three-Phase Workflow

Replace current linear steps 0-7 with phased approach after complexity triage:

**Phase A: Research + Outline**
1. Documentation checkpoint (expanded memory discovery — see below)
2. Codebase exploration (delegate to quiet-explore)
3. Context7 queries if needed (called directly from main session — MCP tools unavailable in sub-agents)
4. Web research if needed (WebSearch/WebFetch direct in main session)
5. Produce **plan outline**: freeform summary of approach, key decisions, open questions, scope boundaries
6. Present outline to user

**Escape hatch:** If user input already specifies approach, decisions, and scope (e.g., detailed problem.md), compress A+B by presenting outline and asking for validation in a single message.

**Phase B: Iterative Discussion**
- User provides feedback on outline
- Designer responds with **incremental deltas only** — not full outline regeneration
- Loop until user validates approach
- This is conversation, not document generation — keep it light
- **Termination:** If user feedback fundamentally changes the approach (not refining it), restart Phase A with updated understanding. Phase B is for convergence, not exploration of new directions.

**Phase C: Generate Design**
1. Write full `design.md` incorporating validated outline + all research
2. Include documentation perimeter section (what planner should read)
3. Vet design (delegate to `vet-agent` sonnet — designer has context to apply fixes per vet-requirement pattern)
4. Apply critical/major fixes from vet review
5. `/handoff --commit` (existing tail-call)

**Step mapping (old → new):**

| Old | New |
|-----|-----|
| Step 0 (triage) | Unchanged (before phases) |
| Step 1 (understand) + Step 1.5 (memory) | Phase A.1 (documentation checkpoint) |
| Step 2 (explore) | Phase A.2 (quiet-explore) |
| Step 3 (research) | Phase A.3-4 (Context7 + web) |
| Step 4 (create design) | Split: Phase A.5 (outline) + Phase C.1 (full design) |
| Step 5 (vet) | Phase C.3 (vet-agent sonnet) |
| Step 6 (fix) | Phase C.4 |
| Step 7 (handoff) | Phase C.5 |

### Documentation Checkpoint

Replaces current Step 1 (understand request) + Step 1.5 (memory discovery). Runs as first action in Phase A.

**Hierarchy (each level is fallback when previous didn't answer):**

| Level | Source | How | When |
|-------|--------|-----|------|
| 1. Local knowledge | `memory-index.md` → referenced files, `agents/design-decisions.md`. Other `agents/decisions/*.md` and `agent-core/fragments/*.md` only when memory-index entries reference them as relevant to the task domain | Direct Read | Always (core), conditional (extended) |
| 2. Key skills | `plugin-dev:*` skills | Skill invocation | When design touches plugin components (hooks, agents, skills, MCP) |
| 3. Context7 | Library documentation via Context7 MCP tools | Designer calls directly from main session (MCP tools unavailable in sub-agents), writes results to report file | When design involves external libraries/frameworks |
| 4. Local explore | Codebase exploration | Delegate to quiet-explore agent | Always for complex designs |
| 5. Web research | External patterns, prior art, specifications | WebSearch/WebFetch (direct in main session) | When local sources insufficient |

**Not all levels needed for every task.** Level 1 is always loaded. Levels 2-5 are conditional on task domain.

**Flexibility:** The checkpoint is domain-aware, not prescriptive. Designer identifies what domain the task touches and loads relevant docs for that domain. No fixed "always read X" list beyond level 1.

### Documentation Perimeter in Design Output

Design documents include a new section specifying what the planner should read before starting:

```markdown
## Documentation Perimeter

**Required reading (planner must load before starting):**
- `agents/decisions/architecture.md` — module patterns, path handling
- `agent-core/fragments/delegation.md` — quiet execution pattern
- `plans/design-workflow-enhancement/reports/explore-design-skill.md` — exploration results

**Context7 references:**
- `/anthropics/claude-code` — hook configuration patterns (query: "PostToolUse hooks")

**Additional research allowed:** Planner may do additional Context7 queries or exploration for technical implementation details not covered above.
```

**Rationale:** Designer has deepest understanding of what knowledge the task requires. Encoding this explicitly prevents planner from either under-reading (missing critical context) or over-reading (wasting tokens on irrelevant docs).

**Integration with planner discovery:** Documentation perimeter is loaded as the first action in the planner's intake/discovery phase, before existing discovery steps. It does NOT replace existing planner discovery — planners still verify paths (Point 0.5 / Phase 2 step 4) and scan memory-index. Perimeter provides the designer's recommended starting context; planner discovery validates and extends it.

### quiet-explore Agent

New agent: `agent-core/agents/quiet-explore.md`

**Based on:** Built-in Explore agent system prompt (read-only specialist with parallel tool usage)

**Key differences from built-in Explore:**
- **Writes report to file** (quiet task pattern) — built-in Explore returns findings in conversation
- **Returns filepath only** — keeps orchestrator context lean
- **Write tool added** — system prompt instructs Write for report output only (not enforced by tool permissions, same pattern as quiet-task.md)

**Agent specification:**

```yaml
name: quiet-explore
description: >
  Use this agent when exploration results need to persist to files for reuse
  across design, planning, and execution phases. Prefer over built-in Explore
  when results will be referenced by downstream agents.
model: haiku
color: cyan
tools: ["Read", "Glob", "Grep", "Bash", "Write"]
```

**System prompt core directives:**
- File search specialist (from built-in Explore prompt)
- Read-only for codebase (Write only for report output)
- Parallel tool calls for speed
- Absolute paths in findings
- **Report format:** Structured findings with file paths, key patterns, relevant code snippets
- **Output:** Write report to caller-specified path, return filepath only
- **Bash:** Read-only operations only (ls, git status, git log, git diff)

**Report location convention:**
- Design phase: `plans/{name}/reports/explore-{topic}.md`
- Ad-hoc: `tmp/explore-{topic}.md`

**Caller specifies report path in task prompt.** Agent writes there, returns path.

### Context7 Usage Pattern

**MCP tools are only available in the main session**, not in sub-agents. The designer calls Context7 directly:

```
1. resolve-library-id(libraryName="...", query="...")
2. query-docs(libraryId="...", query="...")
3. Write results to: plans/{name}/reports/context7-{topic}.md
```

The designer writes results to a report file for reuse by planners. This adds opus tokens for the Write call but ensures results persist.

**Future consideration:** If Claude Code adds MCP tool access to sub-agents, revisit delegation to quiet-task haiku.

## Key Design Decisions

**1. Outline-first, not design-first**
- *Rationale:* Full designs are expensive to generate and expensive to revise. Outlines are cheap. User course-correction at outline stage prevents wasted opus tokens.
- *Trade-off:* Adds one round-trip of user interaction. Worth it for complex designs.

**2. Freeform outline format**
- *Rationale:* Outline communicates approach and decisions, not conforming to structure. Full design.md already has structure guidance. Rigid template would fight the iterative discussion nature.
- *Alternative considered:* Structured template. Rejected — premature formalization at outline stage.

**3. Documentation checkpoint replaces memory discovery**
- *Rationale:* Memory discovery was a subset of what's needed. Expanding it (rather than adding a separate step) keeps the skill simpler and avoids redundant file reads.
- *Impact:* Step 1.5 (memory discovery) is absorbed into the checkpoint. Step 1 (understand request) is absorbed too — reading design-decisions.md is part of level 1.

**4. quiet-explore as haiku, not inherit**
- *Rationale:* Exploration is mechanical (find files, read patterns, report findings). Haiku is sufficient and cheaper. Caller can always override model in Task invocation.
- *Alternative:* `inherit` for caller control. Rejected as default — haiku is the right default, override is always available.

**5. Context7 direct from main session, not delegated**
- *Rationale:* MCP tools unavailable in sub-agents (confirmed empirically). Designer calls Context7 directly and writes results to report file.
- *Trade-off:* Costs opus tokens for the Write call. Acceptable — Context7 queries are infrequent and results persist for planner reuse.
- *Future:* If Claude Code adds MCP tool access to sub-agents, revisit delegation.

**6. No hook-based session capture**
- *Rationale:* PostToolUse hooks don't fire in sub-agents (from claude-config-layout.md). Task matcher fires on ALL Tasks (noisy). Session-log based capture is a better mechanism but requires separate design.
- *Deferred:* Session-log capture as future work item.

## Implementation Notes

**Affected files:**
- `agent-core/skills/design/SKILL.md` — restructure into three-phase workflow, add documentation checkpoint
- `agent-core/agents/quiet-explore.md` — new agent (create)
- `agent-core/skills/plan-adhoc/SKILL.md` — add "read documentation perimeter" step at start
- `agent-core/skills/plan-tdd/SKILL.md` — add "read documentation perimeter" step at start (Phase 1 intake)

**Files NOT changed:**
- `agent-core/agents/quiet-task.md` — no changes needed
- `.claude/settings.json` — no hook changes
- `agents/memory-index.md` — updated naturally as part of handoff

**Symlink management:** After creating `quiet-explore.md`, run `just sync-to-parent` to create symlinks.

**Testing strategy:**
- Manual: Run `/design` on a test task, verify outline-first flow works
- Verify quiet-explore writes report and returns filepath
- Verify Context7 direct calls + Write to report file works
- Verify planner reads documentation perimeter section

## Future Work

- **Session-log based capture:** Extract research artifacts (explore results, web search results, Context7 queries) from session transcripts for reuse. Mechanism TBD — requires separate design.
- **Context7 delegation:** If Claude Code adds MCP tool access to sub-agents, revisit delegation to quiet-task haiku instead of direct calls.
- **Automated perimeter validation:** Hook or script that verifies planner actually read the listed documentation perimeter files.

## Next Steps

- Load `plugin-dev:agent-development` before planning (for quiet-explore agent creation)
- Planning skill: `/plan-adhoc` (general workflow — no TDD needed)
