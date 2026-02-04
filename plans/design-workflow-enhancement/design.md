# Design: Design Workflow Enhancement (Rev 2)

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

**Example outline** (for planner reference — this is what the designer produces, not a template):
```
Approach: Add rate limiting middleware to API gateway using token bucket algorithm.
Key decisions: Per-user limits (not global), Redis-backed counters, 429 response with Retry-After header.
Open questions: Should rate limits vary by endpoint? Should admin users be exempt?
Scope: API gateway only. Dashboard/monitoring out of scope.
Plugin-topic: Involves hook development (PreToolUse validation) — load plugin-dev:hook-development before planning.
```

**Escape hatch:** If user input already specifies approach, decisions, and scope (e.g., detailed problem.md), compress A+B by presenting outline and asking for validation in a single message.

**Phase B: Iterative Discussion**
- User provides feedback on outline
- Designer responds with **incremental deltas only** — not full outline regeneration
- Loop until user validates approach
- This is conversation, not document generation — keep it light
- **Termination:** If user feedback fundamentally changes the approach (not refining it), restart Phase A with updated understanding. Phase B is for convergence, not exploration of new directions.
- **Convergence guidance:** If after 3 rounds the outline is not converging, ask user whether to proceed with current state or restart with different constraints.

**Phase C: Generate Design**
1. Write full `design.md` incorporating validated outline + all research
2. Include documentation perimeter section (what planner should read)
3. Review design (delegate to `design-vet-agent` — opus model for architectural review)
4. Apply critical/major fixes from review
5. `/handoff --commit` (existing tail-call)

**Step mapping (old → new):**

| Old | New |
|-----|-----|
| Step 0 (triage) | Unchanged (before phases) |
| Step 1 (understand) + Step 1.5 (memory) | Phase A.1 (documentation checkpoint) |
| Step 2 (explore) | Phase A.2 (quiet-explore) |
| Step 3 (research) | Phase A.3-4 (Context7 + web) |
| Step 4 (create design) | Split: Phase A.5 (outline, includes plugin-topic detection) + Phase C.1 (full design with skill-loading directive in Next Steps) |
| Step 5 (vet) | Phase C.3 (design-vet-agent — opus model for architectural review) |
| Step 6 (fix) | Phase C.4 |
| Step 7 (handoff) | Phase C.5 |

### Documentation Checkpoint

Replaces current Step 1 (understand request) + Step 1.5 (memory discovery). Runs as first action in Phase A.

**Hierarchy (each level is fallback when previous didn't answer):**

| Level | Source | How | When |
|-------|--------|-----|------|
| 1. Local knowledge | `memory-index.md` for keyword discovery → read referenced files. `agents/design-decisions.md` always. Other `agents/decisions/*.md` and `agent-core/fragments/*.md` only when memory-index entries reference them. For small doc volumes, quiet-explore or Grep on decision/fragment directories is also valid. | Direct Read, quiet-explore, or Grep | Always (core), flexible method |
| 2. Key skills | `plugin-dev:*` skills | Skill invocation | When design touches plugin components (hooks, agents, skills, MCP) |
| 3. Context7 | Library documentation via Context7 MCP tools | Designer calls directly from main session (MCP tools unavailable in sub-agents), writes results to report file | When design involves external libraries/frameworks |
| 4. Local explore | Codebase exploration | Delegate to quiet-explore agent | Always for complex designs |
| 5. Web research | External patterns, prior art, specifications | WebSearch/WebFetch (direct in main session) | When local sources insufficient |

**Not all levels needed for every task.** Level 1 is always loaded. Levels 2-5 are conditional on task domain.

**Level 1 clarification:** Memory-index is an ambient awareness index — keyword-rich entries that surface relevant knowledge. It is NOT the only way to discover local knowledge. For targeted doc collection (e.g., "what do we know about agent patterns?"), the designer can also:
- Delegate quiet-explore to read and summarize `agents/decisions/` and `agent-core/fragments/`
- Use Grep to search for specific topics across decision/fragment files
- These approaches work well when the doc volume is small enough to read completely

**Flexibility:** The checkpoint is domain-aware, not prescriptive. Designer identifies what domain the task touches and loads relevant docs for that domain. No fixed "always read X" list beyond level 1 core.

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

**Backward compatibility:** If design document lacks a Documentation Perimeter section (older designs), planners proceed with existing discovery steps unchanged. The perimeter is additive, not required.

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

**Agent creation in orchestration:** In orchestrated (runbook) execution, the task agent (sonnet) creates the agent file from the detailed spec in its step file. A subsequent step invokes `plugin-dev:agent-creator` to review and fix the created agent — agent-creator is cooperative in review mode and can identify YAML syntax issues, improve descriptions, etc. The runbook includes `## Orchestrator Instructions` that specifies `plugin-dev:agent-creator` as the subagent_type for the review step (prepare-runbook.py uses custom orchestrator sections when present, no code changes needed). See Runbook Guidance below.

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

**7. Design review uses design-vet-agent (opus)**
- *Rationale:* Vet agents are implementation-focused (code quality, patterns, correctness). Design review requires architectural analysis — completeness, consistency, feasibility, edge cases. The dedicated `design-vet-agent` (opus model) provides specialized review protocol for design documents.
- *Updated:* Phase C.3 now uses `Task(subagent_type="design-vet-agent")`. This agent was created specifically for design review with opus model and artifact-return pattern (detailed report to file).

**8. Agent creation: task agent + agent-creator review**
- *Rationale:* In interactive sessions, `plugin-dev:agent-creator` is the preferred tool for creating agents. In orchestrated execution, the step file IS the spec — task agent creates the file, then agent-creator reviews and fixes (YAML syntax, description quality, prompt structure). Agent-creator is cooperative in review mode and has Write access.
- *Orchestration pattern:* Orchestrator plan specifies per-step agent override for the review step. No prepare-runbook.py changes needed.

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

**Symlink management:** After creating `quiet-explore.md`, run `just sync-to-parent` to create symlinks. This is a single shell command, not a multi-step procedure.

**Design review:** Uses `Task(subagent_type="design-vet-agent")` — dedicated opus agent for architectural analysis. See Decision 7.

**Testing strategy:**
- Manual: Run `/design` on a test task, verify outline-first flow works
- Verify quiet-explore writes report and returns filepath
- Verify Context7 direct calls + Write to report file works
- Verify planner reads documentation perimeter section

## Runbook Guidance

**For the planner — these observations correct issues in the previous runbook:**

- **Agent creation step:** Task agent (sonnet) creates agent file from detailed spec. Follow with a separate step that invokes `plugin-dev:agent-creator` to review and fix the agent. Agent-creator is cooperative when asked to review existing agents. **Mechanism:** Include `## Orchestrator Instructions` section in the runbook that tells the orchestrator to use `subagent_type="plugin-dev:agent-creator"` for the review step (prepare-runbook.py extracts custom orchestrator sections and uses them instead of the default generated plan).

- **Symlink management:** `just sync-to-parent` in `agent-core/` is a two-line operation (cd + just). It does NOT warrant a 50-line runbook step with validation checks. Inline it as a post-creation bash command, or combine with a validation step. Validation = verify symlink exists (`ls -la .claude/agents/quiet-explore.md`).

- **No sequential dependency for agent creation before skill edits:** Skills reference agents by name string. The agent file doesn't need to exist at skill-edit time — it needs to exist at runtime (after `just sync-to-parent`). Steps can execute in any order as long as symlinks happen last.

- **Step count target:** The previous runbook had 6 steps for ~4 actual changes (1 agent, 3 skill edits) plus boilerplate. Aim for fewer, denser steps. Combine related operations where the step agent can handle them in sequence.

## Requirements Alignment Validation (Extension)

This section extends the design to add requirements tracking and validation across the workflow.

### Problem

The original design focuses on outline-first workflow and documentation checkpoint but lacks explicit requirements tracking. Deliverables (designs, runbooks, implementations) should be validated against requirements at each stage to ensure alignment.

### Requirements Checkpoint (Phase A.0)

Add to design skill Phase A, before outline generation:

**A.0. Requirements Checkpoint**

If `requirements.md` exists in job directory (`plans/<job-name>/requirements.md`):
- Read and summarize functional/non-functional requirements
- Note scope boundaries (in/out of scope)
- Carry requirements context into outline and design

If no requirements.md exists:
- Document requirements discovered during research
- Can be inline in design.md or separate requirements.md (designer's judgment)

**Output:** Requirements summary available for Phase A.5 (outline) and Phase C.1 (design).

### Design Document Requirements Section (Phase C.1)

Design documents must include a Requirements section:

```markdown
## Requirements

**Source:** `plans/<job-name>/requirements.md` (or inline if documented during design)

**Functional:**
- FR-1: [requirement] — addressed by [design decision/section]
- FR-2: [requirement] — addressed by [design decision/section]

**Non-functional:**
- NFR-1: [requirement] — addressed by [design decision/section]

**Out of scope:**
- [item] — rationale
```

**Traceability:** Each requirement should map to a design element. This enables downstream validation.

### Design Review: Requirements Alignment (C.3)

Extend design-vet-agent review criteria:

| Check | Question |
|-------|----------|
| **Completeness** | Does design address all functional requirements? |
| **Consistency** | Do design decisions conflict with non-functional requirements? |
| **Scope** | Does design stay within scope boundaries? |
| **Traceability** | Can each requirement be traced to a design element? |

**Review section addition:**

```markdown
## Requirements Alignment

**Requirements Source:** [path or "inline"]

| Requirement | Addressed | Design Reference |
|-------------|-----------|------------------|
| FR-1 | ✓/✗ | Section X / Missing |
| FR-2 | ✓/✗ | Section Y / Missing |
| NFR-1 | ✓/✗ | Decision Z / Missing |

**Gaps:** [List any requirements not addressed by design]
```

### Plan Skills: Requirements Passthrough

**plan-adhoc and plan-tdd changes:**

1. **Read requirements** from design.md `## Requirements` section (or referenced requirements.md)
2. **Include requirements summary** in runbook Common Context section
3. **Vet checkpoint prompt** includes: "Verify implementation satisfies requirements"

**Runbook addition (Common Context):**

```markdown
**Requirements (from design):**
- FR-1: [summary]
- FR-2: [summary]
- NFR-1: [summary]

**Scope boundaries:** [in/out of scope]
```

### Vet Agents: Dual Validation

Extend vet-agent and vet-fix-agent review protocol:

**Current:** Validates against code quality, project standards, security, testing, documentation.

**Extended:** Add requirements validation section:

```markdown
## Requirements Validation

**If design/requirements context provided in task prompt:**

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1 | Satisfied/Partial/Missing | [file:line or explanation] |
| FR-2 | Satisfied/Partial/Missing | [file:line or explanation] |

**Gaps:** [Requirements not satisfied by implementation]
```

**Trigger:** Only when task prompt includes requirements context. Backward compatible — existing vet invocations without requirements context work unchanged.

### Affected Files (Extension)

| File | Change |
|------|--------|
| `agent-core/skills/design/SKILL.md` | Add A.0 requirements checkpoint, C.1 requirements section guidance |
| `agent-core/agents/design-vet-agent.md` | Add requirements alignment checks to review protocol |
| `agent-core/skills/plan-adhoc/SKILL.md` | Read requirements from design, include in runbook, add to vet prompt |
| `agent-core/skills/plan-tdd/SKILL.md` | Same as plan-adhoc |
| `agent-core/agents/vet-agent.md` | Add requirements validation section (conditional on task prompt) |
| `agent-core/agents/vet-fix-agent.md` | Same as vet-agent |

### Design Decisions (Extension)

**9. Requirements checkpoint before outline**
- *Rationale:* Requirements inform outline decisions. Loading them early ensures outline reflects actual constraints.
- *Trade-off:* Adds a step if requirements.md exists. Minimal overhead — Read tool call.

**10. Traceability in design document**
- *Rationale:* Explicit mapping enables automated/manual validation. Missing traceability is a review finding.
- *Alternative considered:* Implicit traceability (assume readers can find connections). Rejected — explicit is verifiable.

**11. Conditional requirements validation in vet agents**
- *Rationale:* Backward compatibility. Existing vet invocations work unchanged. New invocations with requirements context get enhanced validation.
- *Trigger mechanism:* Task prompt includes requirements summary → agent performs requirements validation section.

**12. Requirements in runbook Common Context**
- *Rationale:* Step agents need requirements context for validation. Common Context is loaded by all steps.
- *Alternative:* Pass requirements per-step. Rejected — redundant, increases runbook size.

## Future Work

- **Session-log based capture:** Extract research artifacts (explore results, web search results, Context7 queries) from session transcripts for reuse. Mechanism TBD — requires separate design.
- **Context7 delegation:** If Claude Code adds MCP tool access to sub-agents, revisit delegation to quiet-task haiku instead of direct calls.
- **Automated perimeter validation:** Hook or script that verifies planner actually read the listed documentation perimeter files.
- **Requirements coverage metrics:** Automated scoring of requirements coverage in designs/implementations.

## Next Steps

- Load `plugin-dev:agent-development` before planning (for quiet-explore agent creation)
- Planning skill: `/plan-adhoc` (general workflow — no TDD needed)
