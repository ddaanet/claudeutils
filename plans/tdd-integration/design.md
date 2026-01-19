# Design: TDD Workflow Integration

## Problem Statement

pytest-md has TDD-specific skills that need to be integrated into the agent-core workflow system. The goal is to unify the execution engines while preserving TDD methodology, using the weak orchestrator and plan-specific agent patterns already established in agent-core.

## Requirements

### Functional

- Merge `/design` and `/plan-design` into unified design skill with TDD mode support
- Merge `/execute-tdd` and `/orchestrate` into unified runbook execution engine
- Support TDD cycles as a runbook type with RED/GREEN/REFACTOR phases
- Integrate lint, refactoring, and commit into TDD cycle execution
- Update all plan references after refactoring
- Update agent documentation after refactoring
- Keep `/review-analysis` separate for TDD process review (uses claudeutils session extraction)
- Add `/vet` and fix application at end of TDD execution, before process review
- pytest-md consumes agent-core via submodule with sync recipe

### Non-Functional

- Precommit-validated states only in commit history
- Script-first refactoring to prevent token churn
- Escalate architectural refactoring to opus
- New abstractions require human approval

### Out of Scope

- Session extraction tooling (defer)
- Project-specific test command configuration (TODO, use hardcoded `just` recipes initially)
- Line limits for agent docs (TODO, when markdown processing fixed)
- Documentation refactoring support (TODO)

## Design

### Unified Workflow Entry Point

```
/oneshot
  ↓ (complexity + methodology detection)
  │
  ├── TDD path (feature development):
  │     /design (TDD mode) → /plan-tdd → /orchestrate (TDD runbook)
  │                        → /vet → apply fixes → /review-analysis
  │
  └── General path (oneshot work):
        /design → /plan-adhoc → /orchestrate → /vet
```

**Methodology detection signals:**

| TDD Methodology | General Methodology |
|-----------------|---------------------|
| Project has test-first culture | Infrastructure/migration work |
| User mentions "test", "TDD", "red/green" | Refactoring without behavior change |
| Feature requires behavioral verification | Prototype/exploration |
| Project is pytest-md or similar | |

### Merged /design Skill

The unified design skill supports both general and TDD modes.

**Mode selection:** Automatic based on methodology detection, or explicit via context.

**Shared sections (both modes):**
- Problem statement
- Requirements (functional, non-functional, out of scope)
- Key design decisions with rationale
- High-level phases

**TDD mode additions:**
- Spike Test section (verify current behavior, document framework defaults)
- `(REQUIRES CONFIRMATION)` markers for decisions needing user input
- Flag reference table (if adding CLI options)
- "What might already work" analysis

**General mode additions:**
- Integration points
- Edge cases
- Risks and mitigations
- Detailed implementation notes

**Output:** Design document consumed by `/plan-tdd` (TDD) or `/plan-adhoc` (general).

### Merged Execution Engine

Both `/execute-tdd` and `/orchestrate` become a unified `/orchestrate` skill that handles different runbook types.

**Runbook types:**
1. **General runbook** - Steps executed sequentially via plan-specific agent
2. **TDD runbook** - Cycles executed with RED/GREEN/REFACTOR protocol

**Orchestrator behavior:**
- Read runbook type from metadata
- Load appropriate plan-specific agent (`<name>-task.md` or `tdd-task.md`)
- Execute steps/cycles sequentially
- Handle errors via escalation (haiku → sonnet → user)
- Produce execution reports

**TDD-specific logic lives in:**
1. Runbook structure (cycles instead of steps)
2. TDD task agent (RED/GREEN/REFACTOR protocol)

### TDD Runbook Structure

TDD plan produced by `/plan-tdd`:

```markdown
---
name: feature-auth
type: tdd
model: haiku
---

## Weak Orchestrator Metadata

**Runbook Type**: TDD
**Total Cycles**: 5
**Execution Model**: Haiku (tdd-task agent)
**Step Dependencies**: Sequential
**Error Escalation**: Haiku → Sonnet → User
**Report Locations**: plans/<name>/reports/

## Common Context

[Shared knowledge for all cycles - design decisions, file paths, conventions]

## Cycle 1.1: User can authenticate

**Dependencies**: None

### RED Phase
**Test**: `test_user_can_authenticate` in `tests/test_auth.py`
**Assertions**:
- `assert response.status_code == 200`
- `assert "token" in response.json()`
**Expected Failure**: `AssertionError: assert 404 == 200`

### GREEN Phase
**Implementation**: Add `/auth` endpoint returning token
**Files**: `src/routes/auth.py`
**Minimal**: Return hardcoded token initially

### Stop Conditions
- If RED passes unexpectedly: Check if `[REGRESSION]`, else investigate
- If GREEN fails after 2 attempts: STOP, document, await guidance

---

## Cycle 1.2: Token includes user ID
...
```

### TDD Task Agent

**Location:** `agent-core/agents/tdd-task.md` (baseline template)

**Integration with prepare-runbook.py:**

The TDD task agent is NOT a standalone shared agent. Instead, `prepare-runbook.py` uses it as a baseline template that gets combined with runbook-specific context to create plan-specific agents.

```
prepare-runbook.py (TDD runbook)
       ↓
Reads:
  - tdd-task.md (baseline protocol)
  - Runbook common context (design decisions, paths, conventions)
       ↓
Creates:
  - .claude/agents/<runbook-name>-task.md (plan-specific agent)
    = TDD protocol + common context
  - plans/<runbook-name>/steps/cycle-X-Y.md (one per cycle)
    = Specific cycle definition
```

**Why agent-per-cycle pattern:**
- Implementation agents benefit from broader context (design decisions, conventions)
- Each cycle gets fresh context (no accumulation from previous cycles)
- Solves TDD adherence issues through context isolation
- Consistent with general orchestration pattern

**Baseline template contains full TDD cycle execution protocol:

#### RED Phase
1. Write test exactly as specified in cycle
2. Run `just test`
3. Verify failure matches expected message
4. If passes unexpectedly → check `[REGRESSION]` marker → if not, STOP

#### GREEN Phase
1. Write minimal implementation
2. Run `just test` → verify passes
3. Run full suite → handle regressions individually (never batch)
4. If stuck after 2 attempts → STOP, mark BLOCKED, await guidance

#### REFACTOR Phase (mandatory per cycle)

**Step 1: Format & Lint**
```bash
just lint  # includes reformatting
```
Fix lint errors. Ignore complexity warnings and line limits (addressed next).

**Step 2: Intermediate Commit**
```bash
git commit -m "WIP: Cycle X.Y [name]"  # rollback point
```

**Step 3: Quality Check**
```bash
just precommit  # validates green BEFORE refactoring
```
Surfaces complexity warnings and line limit issues.

**Step 4: Refactoring Assessment (if warnings)**

| Warning Type | Handler |
|--------------|---------|
| Common (split module, simplify function) | Sonnet designs, executes |
| Architectural (new abstraction, multi-module impact) | Opus designs, decides escalation |
| New abstraction introduced | Opus, always escalate to human |

**Refactoring tiers:**

| Tier | Criteria | Execution |
|------|----------|-----------|
| 1: Script-based | Mechanical, single pattern, no judgment | Sonnet writes script, execute directly |
| 2: Simple runbook | 2-5 steps, minor judgment | Inline step list, sequential execution |
| 3: Full runbook | 5+ steps, design decisions embedded | prepare-runbook.py, /orchestrate |

**Script-first principle:** Prefer scripted transformations to prevent token churn.

**Step 5: Execute Refactoring**
- Use scripts proactively
- Verify with `just precommit` after
- If fails: STOP, keep state for diagnostic (no auto-reset)

**Step 6: Post-Refactoring Updates**

Update all references to refactored code:
1. **Plans** - All designs and runbooks (`grep -r "old_ref" plans/`)
2. **Agent documentation** - Files in `agents/` (architecture, patterns, implementation)
3. **CLAUDE.md** - Only if behavioral rules affected (keep focused on behavior)
4. **Regenerate step files** if runbook.md changed

Verification: `grep` to confirm old references gone.

**Step 7: Amend Commit**

Safety check before amending:
```bash
current_msg=$(git log -1 --format=%s)
if [[ "$current_msg" != WIP:* ]]; then
  echo "ERROR: Expected WIP commit, found: $current_msg"
  exit 1
fi
```

Amend and reword:
```bash
git commit --amend -m "Cycle X.Y: [name]"
```

Goal: Only precommit-validated states in commit history.

#### Structured Log Entry

After each cycle, append to execution report:
```markdown
### Cycle X.Y: [name] [timestamp]
- Status: RED_VERIFIED | GREEN_VERIFIED | STOP_CONDITION | REGRESSION
- Test command: `[exact command]`
- RED result: [FAIL as expected | PASS unexpected | N/A]
- GREEN result: [PASS | FAIL - reason]
- Regression check: [N/N passed | failures]
- Refactoring: [none | description]
- Files modified: [list]
- Stop condition: [none | description]
- Decision made: [none | description]
```

### TDD Execution Escalation

| Result | Action |
|--------|--------|
| `success` | Proceed to next cycle |
| `quality-check: warnings found` | Escalate to sonnet for refactoring design |
| `architectural-refactoring` | Escalate to opus (opus decides human escalation) |
| `blocked: [reason]` | Standard escalation (sonnet → user) |
| `error: [details]` | Standard escalation |
| `refactoring-failed` | STOP, write diagnostic report, keep state |

### Post-TDD Execution Flow

After all cycles complete:

```
All cycles complete
       ↓
/vet (sonnet)
  - Review uncommitted changes
  - Identify issues (critical/major/minor)
       ↓
Apply fixes (if critical/major)
  - Agent or user fixes issues
  - Re-run /vet if significant changes
       ↓
/review-analysis (TDD process review)
  - Compare plan vs execution
  - Assess TDD compliance
  - Produce recommendations
  - Uses claudeutils session extraction (when available)
```

### Command Reference

| Command | Purpose | Used In |
|---------|---------|---------|
| `just test` | Run test suite | TDD iteration (RED/GREEN) |
| `just lint` | Lint + reformat | Post-GREEN cleanup |
| `just precommit` | Check + test (no reformat) | Refactor validation |

**TODO:** Project-specific configuration (future).

### prepare-runbook.py Updates

Support TDD cycle format in addition to generic steps:

**Cycle detection:**
- `## Cycle X.Y:` headers (in addition to `## Step N:`)
- TDD metadata in frontmatter (`type: tdd`)

**TDD runbook processing:**

1. **Read baseline:** Load `agent-core/agents/tdd-task.md` template
2. **Read runbook:** Parse common context and cycles
3. **Generate plan-specific agent:**
   - Combine TDD baseline protocol with runbook common context
   - Output: `.claude/agents/<runbook-name>-task.md`
4. **Generate cycle files:**
   - One file per cycle: `plans/<name>/steps/cycle-X-Y.md`
   - Contains: RED spec, GREEN spec, stop conditions
5. **Generate orchestrator plan:**
   - TDD-specific instructions (cycle execution, escalation rules)
   - Output: `plans/<name>/orchestrator-plan.md`

**Key difference from general runbooks:**
- General: baseline from `quiet-task.md`
- TDD: baseline from `tdd-task.md`
- Both: combine baseline + common context → plan-specific agent

### Documentation Structure

```
CLAUDE.md
├── Behavioral rules (how agent should act)
├── Communication rules
├── Error handling principles
├── Tool usage constraints
└── References to agents/ for details

agents/
├── session.md              ← Current work state
├── context.md              ← Active task context
├── design-decisions.md     ← Architectural patterns
├── oneshot-workflow.md     ← Oneshot workflow documentation
├── tdd-workflow.md         ← TDD workflow documentation
├── [implementation.md]     ← Implementation patterns (optional)
└── [other as needed]
```

**Progressive disclosure:** CLAUDE.md references agents/ for details.

### pytest-md Integration

1. Add agent-core as git submodule
2. Use existing sync recipe in agent-core to install skills/agents
3. Remove project-specific skills from pytest-md/.claude/skills/
4. Remove project-specific agents from pytest-md/.claude/agents/

**Stopgap until:** agent-core converted to Claude plugin.

## Implementation Notes

### File Changes

**New files:**
- `agent-core/agents/oneshot-workflow.md` - Moved from claudeutils/agents/workflow.md
- `agent-core/agents/tdd-workflow.md` - New TDD workflow documentation
- `agent-core/agents/tdd-task.md` - Shared TDD task agent baseline

**Modified files:**
- `agent-core/skills/design/skill.md` - Add TDD mode support
- `agent-core/skills/oneshot/skill.md` - Add TDD methodology detection
- `agent-core/skills/orchestrate/skill.md` - Add TDD runbook type support
- `agent-core/bin/prepare-runbook.py` - Add TDD cycle format support

**New files (pytest-md integration):**
- `plans/tdd-integration/runbook.md` - Implementation runbook

**Deleted files:**
- `claudeutils/agents/workflow.md` - Moved to agent-core
- `pytest-md/.claude/skills/*` - Replaced by agent-core submodule
- `pytest-md/.claude/agents/*` - Replaced by agent-core submodule

### Testing Strategy

1. Create sample TDD runbook for pytest-md feature
2. Execute via updated /orchestrate
3. Verify cycle execution follows protocol
4. Verify refactoring phase triggers correctly
5. Verify post-execution /vet and /review-analysis flow

### Risks and Mitigations

**Risk:** TDD cycle format parsing in prepare-runbook.py
**Mitigation:** Add comprehensive tests for cycle detection

**Risk:** Refactoring tier selection incorrect initially
**Mitigation:** Start conservative (Tier 2), refine cutoffs with real-world use

**Risk:** Amend safety check false positives
**Mitigation:** Clear WIP prefix convention, documented in tdd-task.md

## Next Steps

1. Write `agent-core/agents/tdd-workflow.md` - Full TDD workflow documentation
2. Write `agent-core/agents/tdd-task.md` - Shared TDD task agent
3. Move `claudeutils/agents/workflow.md` → `agent-core/agents/oneshot-workflow.md`
4. Update `/design` skill with TDD mode
5. Update `/oneshot` skill with TDD methodology detection
6. Update `/orchestrate` skill with TDD runbook support
7. Update `prepare-runbook.py` with TDD cycle format
8. Create `/plan-tdd` skill (adapted from pytest-md)
9. pytest-md integration: submodule + sync + remove project skills

## Design Decisions

### Decision 1: TDD Task Agent as Baseline Template

**Problem:** Should TDD task agent be shared baseline or generated per-runbook?
**Options:**
1. Standalone shared agent invoked directly
2. Baseline template combined with runbook context to generate plan-specific agent
**Choice:** Baseline template (option 2)
**Rationale:** Implementation agents benefit from broader context (design decisions, conventions). Agent-per-cycle pattern solves TDD adherence issues through context isolation. Consistent with general orchestration pattern.

### Decision 2: Refactoring Execution Without Orchestrator

**Problem:** When can refactoring skip weak orchestrator overhead?
**Options:**
1. Always use orchestrator for consistency
2. Allow direct execution for simple refactoring
**Choice:** Tiered approach - Tier 1 (script-based) skips orchestrator
**Rationale:** Script-based refactoring is mechanical and verified by precommit. Orchestrator overhead not justified.

### Decision 3: Documentation Location Split

**Problem:** Where should workflow documentation live?
**Options:**
1. Single workflow.md with sections
2. Separate oneshot-workflow.md and tdd-workflow.md
**Choice:** Separate files
**Rationale:** "Flat is better than nested." Each workflow is substantial enough to warrant own file.

### Decision 4: Commit Strategy

**Problem:** How to handle commits during TDD cycle?
**Options:**
1. Single commit after all refactoring
2. WIP commit then amend
3. Multiple granular commits
**Choice:** WIP commit as rollback point, amend after precommit passes
**Rationale:** Provides rollback safety while maintaining clean history with only validated states.

## Dependencies

**Before this runbook:**
- Current agent-core workflow infrastructure complete
- pytest-md TDD skills available as reference

**After this runbook:**
- pytest-md can use agent-core for TDD workflow
- TDD process review uses session extraction (future)
- Project-specific command configuration (future)

## TODOs (Deferred)

- [ ] Project-specific test command configuration
- [ ] Line limits for agent docs (when markdown processing fixed)
- [ ] Documentation refactoring support (when docs exceed limits)
- [ ] Session extraction integration for /review-analysis

---

**Created:** 2026-01-19
**Status:** Ready for planning
