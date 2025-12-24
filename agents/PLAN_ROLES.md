# Agent Role System Architecture

- **Status:** Implemented and tested
- **Last Updated:** 2025-12-20
- **Author:** opus (architecture), haiku (implementation)

---

## Executive Summary

The agent system has been refactored from skill-based (occupation-focused) to role-based
(behavior-mode focused). This document describes the complete architecture, decision
rationale, and operational model.

**Key Change:** Plans can now explicitly conflict with code role constraints. These
conflicts are caught and reported by the code agent rather than silently violated. This
prevents compliance failures and improves transparency.

---

## System Architecture

### Conceptual Model

```
┌─────────────────────────────────────────┐
│         Task Definition (User)          │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      Role Allocation (Strong Agent)     │  ← planning or refactor role
│   - Analyze task requirements           │
│   - Design test specifications          │
│   - Plan implementation steps           │
│   - Create agents/PLAN*.md              │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
    ┌────────────┐ ┌──────────────┐
    │ Code Role  │ │ Refactor Role│  ← Implementation
    │ (haiku)    │ │ (sonnet)     │
    │ - TDD      │ │ - Plan       │
    │ - Tests    │ │ - Design     │
    │ - Minimal  │ │              │
    │   code     │ │              │
    └────┬───────┘ └──────┬───────┘
         │                │
         │                ▼
         │         ┌──────────────┐
         │         │ Execute Role │  ← Execution of refactor plan
         │         │ (haiku)      │
         │         │ - Follow plan│
         │         │ - No judgment│
         │         └──────┬───────┘
         │                │
         └────────┬───────┘
                  ▼
        ┌──────────────────┐
        │ Lint Role        │  ← Cleanup
        │ (haiku)          │
        │ - Fix errors     │
        │ - Type safety    │
        └──────────────────┘
```

### Role Definitions

#### 1. Planning Role

- **File:** `agents/role-planning.md`
- **Model:** Opus or Sonnet
- **Entry Point:** User requests feature design or sprint planning

**Purpose:** Design test specifications and implementation order for other agents to
execute.

**Preconditions:**

- `START.md` loaded (current task)
- `AGENTS.md` loaded (project overview)
- Codebase understanding (may require reading architecture)

**Workflow:**

1. Analyze task requirements and current codebase state
2. Design test specifications (Given/When/Then format)
3. Group tests by capability (discovery → filtering → error handling → recursion)
4. Order tests to force incremental implementation (no over-implementation possible)
5. Create `agents/PLAN.md` with explicit test specs and implementation order
6. Define validation checkpoints every 3-5 tests
7. Hand off to code role for implementation

**Constraints:**

- Each test must require exactly one piece of new code
- No rationale or alternatives (decision already made)
- Explicit checkpoint language: "Run `just role-code tests/...` - awaiting approval"
- Do not execute any code

**Success Criteria:**

- Tests are ordered to prevent early passing
- Implementation order matches capability grouping
- Checkpoints occur at natural boundaries
- Plan is explicit enough for haiku to execute without judgment

---

#### 2. Code Role

- **File:** `agents/role-code.md`
- **Model:** Haiku
- **Entry Point:** User says "continue" at planning checkpoint

**Purpose:** Implement code using Test-Driven Development (TDD). Execute plan exactly as
written.

**Preconditions:**

- `agents/PLAN*.md` exists and is unambiguous
- Tests are ordered to prevent over-implementation
- No linting required (separate session)

**Workflow:**

1. Read plan file completely
2. For each test:
   1. Write ONE new test
   2. Run test → verify FAILS (Red phase is mandatory)
   3. Write minimal code to pass test
   4. Run test → verify PASSES
   5. Refactor if obvious improvement (optional)
3. At checkpoint:
   - Run `just role-code`
   - Report results
   - STOP and await user approval

**Constraints:**

- **Do NOT run `just check`, `just lint`, or any linting command**
- Do NOT add type annotations beyond obvious patterns
- Do NOT anticipate future tests
- Do NOT modify test assertions
- Do NOT skip the RED phase
- Files must stay under 400 lines (split proactively at 300)

**Plan Conflict Handling (New):** If plan instructs you to run a conflicting command:

1. Do not execute it
2. Report: "Plan conflict: [instruction] contradicts [constraint]"
3. Stop and await user guidance

This is a bug in the plan, not an ambiguity. Plans are written by other agents.

**Success Criteria:**

- All tests pass at checkpoints
- Code is minimal and typed
- No lint/type errors introduced (caught in lint role)

---

#### 3. Lint Role

- **File:** `agents/role-lint.md`
- **Model:** Haiku
- **Entry Point:** Code role checkpoints complete; user requests lint cleanup

**Purpose:** Fix lint and type errors in codebase with passing tests.

**Preconditions:**

- All tests pass
- Code role has completed its work
- No refactoring needed (complexity issues are deferred)

**Workflow:**

1. Run `just lint` (format + ruff --ignore=C901 + mypy + pytest)
2. Fix errors reported by ruff and mypy
3. For each error:
   - Fix root cause (not symptoms)
   - Add type annotations where needed
   - Run `just lint` to verify
4. Repeat until clean

**Constraints:**

- **Do NOT fix complexity issues (C901)** - report to user instead
- Do NOT modify test logic or assertions
- Do NOT refactor beyond lint compliance
- Do NOT use suppressions without explanation
- Complex fixes → report and stop

**Lint Recipe Details:**

```
just lint:
  just format                              # Auto-fix formatting
  uv run ruff check -q --ignore=C901      # Skip complexity
  docformatter -c src tests               # Check docstring format
  uv run mypy                             # Type checking
  uv run pytest                           # Verify tests still pass
```

The `--ignore=C901` flag disables complexity checks, which are deferred to refactor
role.

**Success Criteria:**

- `just lint` exits cleanly (no errors)
- All 97 tests pass
- No type errors
- No docstring formatting issues

---

#### 4. Refactor Role

- **File:** `agents/role-refactor.md`
- **Model:** Sonnet
- **Entry Point:** User requests refactoring or optimization

**Purpose:** Plan refactoring changes for handoff to execute role. No implementation.

**Preconditions:**

- `just dev` passes (tests + lint + checks all pass)
- Complexity issues identified or optimization target specified
- Codebase is in clean state

**Workflow:**

1. Analyze codebase for refactoring opportunities (complexity, duplication,
   maintainability)
2. Plan specific changes with clear, atomic steps
3. For each step:
   - Specify exact file and change needed
   - Note expected test impact (should be none for pure refactor)
   - Flag any potential lint implications
4. Create `agents/PLAN.md` with explicit step-by-step changes
5. Hand off to execute role with note: "Execute this plan using role-execute"

**Constraints:**

- Do not execute changes yourself
- Do not modify test assertions
- Do not add new tests (maintain test parity)
- Plan must maintain 100% test pass rate
- Flag complexity issues clearly for execute role

**Plan Format:**

```markdown
### Step N: [Brief description]

**File:** `path/to/file.py`

**Change:** [Exact description of what to change]

**Expected Result:** All tests still pass

**Notes:** [Any lint implications]
```

**Success Criteria:**

- Plan is detailed enough for haiku to execute
- Each step is atomic and clear
- No test modifications required
- Lint implications are documented

---

#### 5. Execute Role

- **File:** `agents/role-execute.md`
- **Model:** Haiku
- **Entry Point:** Refactor plan completed; user says "continue"

**Purpose:** Execute planned changes exactly. No judgment, no improvisation.

**Preconditions:**

- `agents/PLAN.md` exists with refactoring plan
- Plan is clear and atomic (written by sonnet)
- All tests currently pass

**Workflow:**

1. Read the refactor plan completely
2. For each step:
   1. Execute exactly as specified (no variations)
   2. Run `just role-code` to verify tests pass
   3. If tests pass, proceed to next step
   4. If tests fail, stop and report

**Constraints:**

- Follow plan exactly; no improvisation
- Do not refactor beyond what plan specifies
- Do not run `just lint` or `just check`
- Do not modify test assertions
- If step is ambiguous, stop and request clarification

**Lint Issues During Execution:** If `just role-code` passes but you notice lint issues:

- Simple fixes (line length, whitespace) → fix inline
- Complex issues (type errors, cycles) → note in handoff, do not fix

**Success Criteria:**

- All steps executed as planned
- All tests pass after each step
- No ambiguous interpretation needed

---

#### 6. Remember Role

- **File:** `agents/role-remember.md`
- **Model:** Opus
- **Entry Point:** Discovered workflow improvement or compliance violation

**Purpose:** Maintain and evolve agent documentation based on learnings.

**Scope:**

- `AGENTS.md` - Core rules and role definitions
- `START.md` - Current status and handoff info
- `agents/role-*.md` - Role-specific guidelines
- `agents/rules-*.md` - Action-triggered rules

**Do NOT update:**

- `agents/PLAN*.md` - Task artifacts, not rules
- `README.md` - User-facing documentation
- Test files - Implementation artifacts

**Workflow:**

1. Identify pattern (repeated violation, workflow gap, or improvement)
2. Decide: Which file needs updating?
3. Update with precision and examples
4. Tier new rules: Tier 1 (top, critical) → Tier 2 (middle) → Tier 3 (bottom, edge
   cases)

**Rule Budgeting:**

- `AGENTS.md` + role file ≤ 150 total rules
- Fewer is better
- Weak-agent roles (haiku) need explicit, numbered instructions
- Strong-agent roles (opus/sonnet) need less verbosity

**Constraints:**

- One concept per edit
- Always explain ignores/suppressions
- Delete obsolete rules
- Promote rules after repeated violations

**Success Criteria:**

- New rules prevent future violations
- Documentation is clearer and more complete
- Other agents can self-correct using rules

---

### Rules (Action-Triggered)

#### Commit Rule

- **File:** `agents/rules-commit.md`
- **Trigger:** Before any `git commit`

- Read this file before committing
- Verify changes are intentional
- Write concise, meaningful commit messages
- Do not commit secrets or debug code

#### Handoff Rule

- **File:** `agents/rules-handoff.md`
- **Trigger:** Before ending a session

- Document what was completed
- Note any blockers or TODOs
- Prepare for next agent to start cleanly
- Update `START.md` with status

---

## Integration Patterns

### Pattern 1: Feature Implementation (Planning → Code → Lint)

```
User: "Implement feature X"
        ↓
Planning Role (sonnet):
  - Design tests
  - Create PLAN.md
  - Checkpoint: "Awaiting approval"
        ↓
User: "continue"
        ↓
Code Role (haiku):
  - Implement per PLAN.md
  - Hit checkpoint: report results
  - STOP
        ↓
User: "continue"
        ↓
Lint Role (haiku):
  - Fix lint/type errors
  - Verify all tests still pass
        ↓
Done: Feature is implemented, tested, linted
```

### Pattern 2: Refactoring (Refactor → Execute → Lint)

```
User: "Refactor module X (too complex)"
        ↓
Refactor Role (sonnet):
  - Analyze complexity
  - Plan atomic changes
  - Create PLAN.md
  - Checkpoint: "Ready for execution"
        ↓
User: "continue"
        ↓
Execute Role (haiku):
  - Execute plan step-by-step
  - Verify tests pass after each step
  - Report completion
        ↓
Lint Role (haiku):
  - Fix any lint issues from refactoring
  - Verify all tests still pass
        ↓
Done: Code is cleaner, tests pass, lint clean
```

### Pattern 3: Bug Fix (Code → Lint)

```
User: "Fix bug in X"
        ↓
Planning Role (inferred from bug description):
  - Design minimal test for bug
  - Create PLAN.md
        ↓
Code Role (haiku):
  - Implement test and fix
  - Report done
        ↓
Lint Role (haiku):
  - Fix lint/type issues
        ↓
Done: Bug fixed and tested
```

---

## Key Decisions

### Decision 1: Roles vs Skills

**Why Change?**

Old system: Skills were occupation-focused (planner, coder, linter).

Problem: Code role ran `just check` after implementing, violating its own constraints.
Plans could contradict role rules without detection.

New system: Roles are behavior-mode focused (what the agent does, what it never does,
what output it produces).

Result: Code role now detects plan conflicts and reports them instead of silently
violating constraints.

### Decision 2: Plan Conflicts Are Bugs, Not Ambiguities

**Rationale:**

Plans are written by other agents (planning or refactor roles). Plans can be wrong.

When a plan says "run `just check`" but code role prohibits it:

- Old: Code role silently violates its constraint (compliance failure)
- New: Code role detects conflict, reports it, stops (transparency)

User sees the conflict and can fix the plan.

### Decision 3: Complexity Checks Are Deferred to Refactor Role

**Rationale:**

Lint role (haiku) cannot refactor complex functions—it would violate "do not refactor
beyond lint compliance."

Refactor role (sonnet) can plan and reason about complexity.

Solution: Lint recipe disables C901 via `--ignore=C901`. Complexity issues are:

1. Reported by lint role ("Found 3 complexity issues; reporting to user")
2. Addressed by refactor role in next iteration

### Decision 4: Execute Role for Handoff Pattern

**Rationale:**

When refactor role plans changes, who executes them?

- Option A: Refactor role executes itself → violates "do not execute"
- Option B: Code role executes → but code role does TDD, not following a plan
- Option C: New role (execute) follows plans without judgment → clean separation

Chose C: Execute role is haiku agent that follows refactor plans exactly, without TDD.

### Decision 5: Remember Role Owns Agent Documentation

**Rationale:**

Documentation is not user-facing (README), task artifacts (PLAN.md), or implementation
(code).

Separate role for documentation ensures:

- Rules are consistent across system
- Updates are deliberate and principled
- Other agents can read and reference

Only opus can update rules (strong model = careful with fundamental constraints).

---

## Migration Path

### Phase 1: Rename Files (Complete)

Old → New:

- `agents/planning.md` → `agents/role-planning.md`
- `agents/code.md` → `agents/role-code.md`
- `agents/lint.md` → `agents/role-lint.md`
- `agents/remember.md` → `agents/role-remember.md`
- Keep unchanged: `agents/commit.md` → `agents/rules-commit.md`
- Keep unchanged: `agents/handoff.md` → `agents/rules-handoff.md`

### Phase 2: Update AGENTS.md (Complete)

- Replace "Skills" section with "Roles and Rules"
- Update file references
- Document role → model mapping

### Phase 3: Add Role-Specific Recipes (Complete)

- `just role-code` → runs tests only
- `just role-lint` → format + check (no complexity) + test
- `just role-refactor` → full dev cycle

### Phase 4: Update Plans (Complete)

- `agents/PLAN_INLINE_HELP.md` updated with `just role-code` references
- Remove `just check` references (code role never runs it)

### Phase 5: Compliance Enforcement

In code role: Add plan conflict detection:

```
If plan says "run X" and X is prohibited by this role:

  1. Report conflict
  2. Stop and await guidance
  3. (Do not execute X)
```

---

## Testing Checklist

- [x] All help tests pass (5 tests)
- [x] All existing tests pass (97 tests)
- [x] Lint passes with `--ignore=C901`
- [x] Role recipes work: `just role-code`, `just role-lint`, `just role-refactor`
- [x] Plan file updated with new checkpoint references
- [x] AGENTS.md references updated
- [x] No breaking changes to existing workflows

---

## Next Steps

### For Code Role Sessions

1. Read `START.md` first
2. Read `agents/role-code.md`
3. Load current `agents/PLAN*.md`
4. Execute TDD cycle
5. At checkpoint: report and stop

### For Strong Model Sessions (Planning)

1. Read `agents/role-planning.md`
2. Read `AGENTS.md` for project context
3. Design test specifications
4. Create `agents/PLAN.md`
5. Hand off to code role

### For Refactor Sessions

1. Read `agents/role-refactor.md`
2. Analyze complexity/duplication
3. Plan atomic changes
4. Create `agents/PLAN.md`
5. Hand off to execute role

### For Lint Cleanup Sessions

1. Read `agents/role-lint.md`
2. Run `just lint`
3. Fix errors systematically
4. Repeat until clean

---

## Glossary

| Term               | Definition                                                                       |
| ------------------ | -------------------------------------------------------------------------------- |
| Role               | A behavior mode: what the agent does, when it stops, what output it produces     |
| Rule               | Action-triggered guidance (commit, handoff)                                      |
| Plan               | Task artifact created by planning/refactor roles; executed by code/execute roles |
| Checkpoint         | Stopping point in plan; awaiting user approval before continuing                 |
| Red-Green-Refactor | TDD cycle: test fails, code passes test, optional refactor                       |
| Complexity Issue   | C901 function too complex; requires refactoring, not linting                     |
| Plan Conflict      | Plan instruction contradicts role constraint; is a bug, not ambiguity            |

---

## Document History

| Date       | Change                            | Author      |
| ---------- | --------------------------------- | ----------- |
| 2025-12-20 | Initial design and implementation | opus, haiku |
