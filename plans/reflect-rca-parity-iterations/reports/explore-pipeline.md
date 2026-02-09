# Orchestration & Commit Quality Gate Pipeline

**Date:** 2026-02-06
**Scope:** Validation steps, quality gates, and checkpoint mechanisms in orchestration and commit workflows

## Summary

The quality gate pipeline consists of three integrated layers:
1. **Pre-commit validation** (justfile recipes) — code quality, lint, tests, file sizes
2. **Vet-fix-agent checkpoint** — code review with automated fixes at phase boundaries
3. **Commit workflow with gitmoji** — structured messages with multi-line support

Each layer has clear validation gates, escalation paths, and no bypass modes (validation is hard-fail). The orchestrator uses weak delegation to force error visibility rather than silent handling.

---

## Layer 1: Pre-Commit Validation (Justfile)

**File:** `/Users/david/code/claudeutils-parity-failures/justfile` (lines 23-35)

### Validation Steps (in order)

| Step | Command | What It Checks | Failure Mode |
|------|---------|----------------|--------------|
| 1. Sync | `sync` | Ensures environment is up to date via `uv sync` | Hard fail |
| 2. Tasks validation | `validate-tasks.py agents/session.md agents/learnings.md` | Session.md task format, checkbox states, pending/complete notation | Hard fail |
| 3. Learnings validation | `validate-learnings.py agents/learnings.md` | Learnings format, word count limits (hard limit enforced) | Hard fail |
| 4. Decision files validation | `validate-decision-files.py` | Consistency of all decision files in agents/decisions/ | Hard fail |
| 5. Memory index validation | `validate-memory-index.py agents/memory-index.md` | Memory index entries match backing documentation, no orphaned entries | Hard fail |
| 6. Jobs validation | `validate-jobs.py` | Jobs.md table format, status values, plan directory tracking | Hard fail |
| 7. Agent-core checks | `gmake --no-print-directory -C agent-core check` | Agent-core project-specific validation rules | Hard fail |
| 8. Code style (ruff, docformatter, mypy) | `run-checks` | Type safety, docstring formatting, linting (complexity checks disabled) | Hard fail |
| 9. Tests | `safe pytest-quiet` | Test suite execution (pytest) | Soft fail tracked but continues |
| 10. Line limits | `run-line-limits` | Python files, markdown decision files must not exceed 400 lines | Hard fail |

**Orchestration:** Sequential — each step must pass before next runs. Any hard failure stops precommit.

**Bypass modes:** NONE. All validation is mandatory.

**Token note:** Step 9 (pytest) uses `safe` wrapper to prevent exit on failure, allowing downstream reports to run. This is intentional for visibility (see line 33 and helper at line 325).

### Line Limits Validation

**File:** `/Users/david/code/claudeutils-parity-failures/scripts/check_line_limits.sh`

| Target | Limit | Enforcement |
|--------|-------|-------------|
| `src/**/*.py` | 400 lines | Hard fail exit code 1 |
| `tests/**/*.py` | 400 lines | Hard fail exit code 1 |
| `agents/decisions/**/*.md` | 400 lines | Hard fail exit code 1 |

**Output:** `❌ <file>: <line_count> lines (exceeds 400 line limit)`

No warnings or soft modes. Violation causes immediate precommit failure.

---

## Layer 2: Vet-Fix-Agent Checkpoint (Code Review + Automated Fixes)

**File:** `/Users/david/code/claudeutils-parity-failures/agent-core/agents/vet-fix-agent.md`

### Role & Trigger Points

**Agent definition:**
- Model: sonnet
- Task: Review changes, write detailed report, apply ALL fixes (critical, major, minor)
- Return format: filepath (on success) or structured error

**When invoked:**

1. **Commit skill Gate B** (line 108-122 of `/Users/david/code/claudeutils-parity-failures/agent-core/skills/commit/SKILL.md`):
   - Detects production artifacts (code, scripts, plans, skills, agents)
   - If production artifact changed: requires vet report in `plans/*/reports/` or `tmp/`
   - STOP if no vet report exists — delegate to vet-fix-agent before proceeding to git operations
   - STOP if vet report lists UNFIXABLE issues — escalate to user

2. **Orchestrate skill phase boundary** (line 118-148 of `/Users/david/code/claudeutils-parity-failures/agent-core/skills/orchestrate/SKILL.md`):
   - After each phase completes (when Phase field changes in next step)
   - Delegates checkpoint review to vet-fix-agent
   - Blocked until checkpoint completes or UNFIXABLE issues surface

### Review Criteria

**What vet-fix-agent checks** (lines 115-169):

- **Code quality:** Logic, error handling, readability, abstractions
- **Project standards:** Patterns, codebase style, file locations, dependencies, CLAUDE.md compliance
- **Security:** Hardcoded secrets, input validation, vulnerabilities, auth/authz
- **Testing:** Coverage of main + edge cases, behavior-focused (not implementation-focused), meaningful assertions
- **Documentation:** Comments, updated docs, clear commit messages
- **Completeness:** TODOs addressed, no debug code, related changes included
- **Requirements validation** (if context provided): Verify against stated requirements
- **Design anchoring** (if design reference provided): Verify implementation matches design decisions
- **Integration:** Duplication, pattern consistency, cross-cutting concerns

### Fix Application

**Agent applies ALL fixes automatically** (lines 276-291):

| Priority | Definition | Applied? | Status in Report |
|----------|-----------|----------|------------------|
| Critical | Must fix before commit | YES | FIXED or UNFIXABLE |
| Major | Should fix, strongly recommended | YES | FIXED or UNFIXABLE |
| Minor | Nice to have improvements | YES | FIXED or UNFIXABLE |

**If a fix is unfixable:**
- Mark as `UNFIXABLE — [reason]`
- Reason categories: architectural changes needed, ambiguous approaches, scope creep, introduces new issue
- Unfixable issues block commit progression (escalate to user)

### Report Output

**Location:** `tmp/vet-review-[YYYY-MM-DD-HHMMSS].md` or `plans/[plan-name]/reports/vet-review.md`

**Structure:**
```markdown
# Vet Review: [scope]
## Summary — [Assessment: Ready / Needs Minor / Needs Significant]
## Issues Found
  ### Critical Issues
  ### Major Issues
  ### Minor Issues
## Fixes Applied
## Requirements Validation (if context provided)
## Positive Observations
## Recommendations
```

**Assessment mapping:**
- **Ready:** No critical/major issues (or all fixed), follows project standards
- **Needs Minor Changes:** All critical/major fixed, some minor remain
- **Needs Significant Changes:** Critical issues that are UNFIXABLE

---

## Layer 3: Commit Workflow (Commit Skill with Gitmoji)

**File:** `/Users/david/code/claudeutils-parity-failures/agent-core/skills/commit/SKILL.md`

### Flags & Validation Modes

| Flag | Validation Level | When Used |
|------|------------------|-----------|
| (default) | `just precommit` (full) | General commits, final work |
| `--test` | `just test` only | TDD GREEN phase (before lint) |
| `--lint` | `just lint` only | Post-lint fixes, pre-complexity |
| `--context` | Validation only, skip git discovery | When you know changes from conversation |
| `--no-gitmoji` | Skip emoji selection | When gitmoji not relevant |

### Commit Gates

**Gate A — Session freshness** (line 90-99):
- Read `agents/session.md`
- Verify "Completed This Session" reflects current work
- Check pending tasks and blockers are current
- If stale: run `/handoff` first
- If current: proceed to Gate B

**Gate B — Vet checkpoint** (line 108-122):
1. List changed files: `git diff` + `git status --porcelain`
2. Classify each: production artifact or not?
   - **No production artifacts?** Proceed to validation
   - **Production artifacts exist?** Check for vet report in `plans/*/reports/` or `tmp/`
   - **No vet report?** STOP — delegate to vet-fix-agent first
   - **UNFIXABLE issues in report?** STOP — escalate to user
3. If reports exist: verify no UNFIXABLE issues, continue to validation

**Validation execution** (line 126-141):

```bash
exec 2>&1
set -xeuo pipefail
just precommit  # or: just test (--test) / just lint (--lint)
git status -vv
```

- Preserves staged vs unstaged state (noted in `git status -vv`)
- Fails if nothing to commit (clean working tree)

### Message Format

**Style:** "Short, dense, structured"

```
<Emoji> <Imperative verb> <what changed>

- <detail 1 with quantifiable facts>
- <detail 2 with context>
- <detail 3 with why>
```

**Rules:**
- Title: 50-72 chars, imperative mood (Add, Fix, Update, Refactor), no period
- Blank line after title
- Bullet points: focus on WHAT changed and WHY (not implementation details)
- Include quantifiable info: file counts, line counts, scope

**Example:**
```
🔨 Add OAuth2 authentication module with Google provider

- Add auth service with token management
- Add authentication middleware
- Add unit and integration tests (35 lines)
- Update main.ts to use auth middleware
- Update package.json with OAuth2 dependencies
```

### Gitmoji Selection

**Reference file:** `/Users/david/code/claudeutils-parity-failures/agent-core/skills/commit/references/gitmoji-index.txt` (~78 entries)

**Process:**
1. Read gitmoji index (format: `emoji - name - description`)
2. Analyze commit message semantics (type, scope, impact)
3. Select most specific emoji matching primary intent
4. Prefix commit title with emoji

**Bypass:** `--no-gitmoji` flag skips selection

### Submodule Handling

**Trigger:** `git status` shows modified submodule (e.g., `M agent-core`)

**Process:**
1. Check submodule status: `(cd agent-core && git status)`
2. If submodule has uncommitted changes: commit them in subshell
   ```bash
   (cd agent-core && git add <files> && git commit -m "...")
   ```
3. Stage submodule pointer: `git add agent-core`
4. Continue with parent commit

**Why:** Submodule pointer updates are invisible without committing submodule first

### Stage & Commit Execution

```bash
exec 2>&1
set -xeuo pipefail
git add file1.txt file2.txt
git commit -m "$(cat <<'EOF'
🐛 Fix authentication bug

- Detail 1
- Detail 2
EOF
)"
git status
```

**Rules:**
- Intent comment required as first line
- Stage specific files only (not `git add -A`)
- Include `agents/session.md`, `plans/` files, and submodule pointers if changed
- Use subshell pattern `(cd submodule && ...)` for submodule operations
- Do NOT commit secrets (.env, credentials.json, etc.)

---

## Layer 4: Orchestration Execution (Weak Orchestrator Pattern)

**File:** `/Users/david/code/claudeutils-parity-failures/agent-core/skills/orchestrate/SKILL.md`

### Orchestrator Responsibilities

**Role:** Mechanical step progression with explicit error escalation (NO judgment calls)

**Execution loop:**
1. Read step specification
2. Invoke plan-specific agent with step reference
3. Receive result (filename or error)
4. Verify git tree is clean (hard stop if dirty)
5. Check phase boundary (delegate to vet-fix-agent if phase changed)
6. Continue or escalate

### Step Execution Model

**For each step** (lines 66-151):

**3.1 Invoke plan-specific agent:**
```
Task tool with:
- subagent_type: "<runbook-name>-task"
- prompt: "Execute step from: plans/<runbook-name>/steps/step-N.md"
- model: [from step file header "Execution Model" field]
```

**3.2 Check result:**
- Success: completion message + report file created
- Failure: error message returned
- Unexpected: results differ from specification

**3.3 Post-step verification** (lines 98-147):

```bash
git status --porcelain
```

- **Clean output:** Proceed to phase boundary check
- **ANY output:** STOP immediately
  - Report: "Step N left uncommitted changes: [file list]"
  - HARD STOP — no exceptions
  - Do NOT proceed, do NOT cleanup on behalf of step
  - Escalate to user

**Hard constraint:** Every step MUST leave clean working tree. Report files, artifacts, and changes MUST be committed by step agent.

**Phase boundary check:**
- Read next step file header (first 10 lines)
- Compare Phase field with current step
- If phase changed OR final step: delegate to vet-fix-agent for checkpoint
- Do NOT proceed until checkpoint completes

### Phase Boundary Checkpoint

**Triggered:** When `Phase:` field changes or final phase reached

**Delegation:**
```
Task(subagent_type="vet-fix-agent",
     prompt="Phase N Checkpoint:
       - Run: just dev (fix failures, commit)
       - IN: [list methods/features in this phase]
       - OUT: [list future phases - do NOT flag]
       - Review: test quality, implementation, integration, design anchoring
       - Design reference: plans/<name>/design.md
       - Changed files: [git diff --name-only]
       Write report to: plans/<name>/reports/checkpoint-N-vet.md")
```

**Outcome:**
- All issues fixed: vet-fix-agent commits, orchestrator continues
- UNFIXABLE issues: vet-fix-agent reports, orchestrator STOPS and escalates to user

### Error Escalation

**Escalation levels** (lines 158-198):

| Level | Trigger | Action | Recipient |
|-------|---------|--------|-----------|
| 1 | Quality warnings, recoverable errors | Delegate to sonnet (refactor agent or diagnostic) | Sonnet |
| 1b | File state issues, permission errors, script failures | Delegate to sonnet for diagnostic + fix | Sonnet |
| 2 | Design decisions needed, architectural changes, sonnet cannot fix | STOP execution, escalate to user | User |

**Escalation prompt template:**
```
Diagnose and fix error from step N:
- Error: [message]
- Step objective: [what should happen]
- Expected: [specification]
- Observed: [actual result]
- Read error report: [path]
- Read step: [path]

If fixable: Apply corrections, report success
If not fixable: Explain why, state what input is needed

Write diagnostic to: plans/<name>/reports/step-N-diagnostic.md
Return: "fixed: [summary]" or "blocked: [what's needed]"
```

### Progress Tracking

**Simple approach (default):**
```
✓ Step N: [step name] - completed
✗ Step N: [step name] - failed: [error]
```

**Detailed approach (optional):**
- Maintain progress file: `plans/<runbook-name>/progress.md`
- Update after each step with timestamp and report references

### Completion Handling

**For TDD runbooks:**
1. Delegate to vet-fix-agent for quality review
2. Delegate to review-tdd-process agent for process analysis
3. Report overall success with links to both reports
4. Next: `/commit` to commit changes

**For general runbooks:**
1. Report overall success
2. List created artifacts
3. Suggest next: delegate to vet-fix-agent → `/commit`

---

## Integration Points

### Commit Skill → Vet-Fix-Agent

**Trigger:** Gate B detects production artifact without vet report

**Handoff:**
```
Commit skill (line 108-122) detects artifact
  ↓
Stop execution, delegate to vet-fix-agent
  ↓
Vet-fix-agent reviews, applies all fixes, writes report
  ↓
Commit skill reads report (check for UNFIXABLE)
  ↓
If clean: proceed to validation and git commit
If UNFIXABLE: escalate to user
```

### Orchestrate Skill → Vet-Fix-Agent

**Trigger:** Phase boundary crossing (Phase field changes in next step)

**Handoff:**
```
Orchestrator completes step
  ↓
Verify git tree clean (hard stop if dirty)
  ↓
Check next step's Phase field
  ↓
If phase changed: delegate to vet-fix-agent for checkpoint
  ↓
Vet-fix-agent: run just dev, review, fix, commit
  ↓
If UNFIXABLE: orchestrator stops, escalates to user
If all fixed: orchestrator continues to next step
```

### Orchestrate Skill → Commit Skill

**Workflow:** Post-execution cleanup

```
Orchestrate completes all steps successfully
  ↓
Delegates to vet-fix-agent (if TDD) for final review
  ↓
User or system invokes /commit
  ↓
Commit skill: validation + gitmoji + staging + git commit
```

---

## Validation Failure Modes

### Hard Failures (STOP immediately)

| Gate | Condition | Action |
|------|-----------|--------|
| Precommit validation | Any check fails (lint, test, line limit, tasks validation) | Exit 1, block commit |
| Commit Gate A | Session.md stale | STOP, require `/handoff` first |
| Commit Gate B | Production artifact without vet report | STOP, delegate to vet-fix-agent |
| Commit Gate B | UNFIXABLE issues in vet report | STOP, escalate to user |
| Commit validation | `just precommit` fails | STOP, don't stage/commit |
| Orchestrate 3.3 | Git tree not clean after step | STOP immediately, escalate to user |
| Orchestrate phase boundary | UNFIXABLE issues in checkpoint | STOP, escalate to user |

### Soft Failures (Logged but continue)

| Item | Behavior | Purpose |
|------|----------|---------|
| pytest in precommit (line 33) | Wrapped with `safe` | Allows downstream validation to complete, visibility of all issues at once |

---

## Key Patterns

### No Bypass Modes

The pipeline has **ZERO bypass modes**. Validation is mandatory:

- ❌ `--skip-precommit` — NOT available
- ❌ `--no-lint` in general commit — NOT available (only `--test` for TDD GREEN phase)
- ❌ Force commit without vet report — NOT available
- ❌ Continue after dirty git tree in orchestration — NOT available
- ❌ Suppress UNFIXABLE issues — NOT available

### Escalation Over Silent Failure

**Design principle:** Surface all deviations explicitly rather than silently handling.

- **Weak orchestrator:** No judgment calls by orchestrator. All recovery escalates to sonnet or user.
- **Vet gates:** UNFIXABLE issues stop progression, don't get ignored.
- **Clean tree requirement:** Dirty trees after orchestration steps are HARD STOP, not warning.

### Token Efficiency

**Token cost reduction mechanisms:**

1. **Quiet execution:** Agents write detailed reports to files, return only filepath (success) or error (failure)
2. **Plan-specific agents:** Cached context reuse across multiple steps (~94% token reduction on 3-step plan)
3. **Delegation pattern:** Complex decisions delegated to specialized agents (vet, refactor, design), not repeated in orchestrator

### Minimal Intervention

**Rule:** The orchestrator and commit skill delegate rather than decide.

- Commit skill: Does NOT make message content decisions (user/prompt specifies)
- Orchestrator: Does NOT fix errors on behalf of steps
- Validation: Does NOT warn — either passes (hard) or fails (hard)

---

## Gaps & Unclear Areas

1. **Pytest soft-fail tracking:** Line 33 of justfile uses `safe pytest-quiet` to prevent exit on test failure. While intentional for visibility, **unclear if test failures are escalated or just logged** without blocking precommit.

2. **TDD complexity check bypass:** Line 145 in justfile shows ruff ignores C901 (complexity) during lint. **Unclear if complexity needs separate validation gate or if this is permanent bypass.**

3. **Design reference in vet checkpoint:** Orchestrate skill line 140 references `plans/<name>/design.md` for "design anchoring" validation. **Unclear if this file must exist or if vet-fix-agent validates only if provided.**

4. **UNFIXABLE criteria clarity:** Vet-fix-agent lists UNFIXABLE as: architectural, ambiguous, scope creep, introduces new issue. **Unclear if these are exhaustive or if agent has discretion in classification.**

5. **Phase boundary definition:** Orchestrate skill line 112 reads "first 10 lines" of next step for Phase field. **Unclear if Phase field is always present or if missing Phase should be treated as final phase.**

6. **Submodule depth limit:** Commit skill line 159 notes "Nested submodules not used in this repo." **Unclear if multi-level submodule support is planned or permanently excluded.**

---

## Summary Table

| Layer | Component | Location | Bypass Available? | Escalation Path |
|-------|-----------|----------|------------------|-----------------|
| **Layer 1** | Precommit validation | justfile + scripts/ | NO | Hard fail (exit 1) |
| **Layer 1** | Line limits check | check_line_limits.sh | NO | Hard fail (exit 1) |
| **Layer 2** | Vet-fix-agent review | agent-core/agents/vet-fix-agent.md | NO (invoked at gates) | Unfixable → user escalation |
| **Layer 3** | Commit Gate A (session freshness) | commit/SKILL.md | SOFT (requires /handoff) | User must run /handoff |
| **Layer 3** | Commit Gate B (vet requirement) | commit/SKILL.md | NO (blocks commit) | Hard stop, delegate to vet-fix-agent |
| **Layer 3** | Validation (just precommit) | commit/SKILL.md | SOFT (--test, --lint flags) | Hard fail, blocks git operations |
| **Layer 4** | Orchestrate clean tree check | orchestrate/SKILL.md | NO (hard stop) | Escalate to user |
| **Layer 4** | Phase boundary checkpoint | orchestrate/SKILL.md | NO (hard stop) | Delegate to vet-fix-agent or escalate |
| **Layer 4** | Error escalation | orchestrate/SKILL.md | NO | Sonnet (L1) or user (L2) |
