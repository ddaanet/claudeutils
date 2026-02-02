# Design: TDD Workflow Skill Improvements

## Problem

The claude-tools-rewrite TDD runbook executed 37 cycles, all GREEN, all tests passing — but features don't work. Root cause: a broken feedback loop across four skills where weak RED phase tests enabled stub implementations that were never caught until final vet review.

Three root causes identified:
- **plan-tdd** generates RED tests that verify structure (exit codes, key existence) not behavior
- **review-tdd-plan** checks GREEN prescriptiveness but not RED test quality
- **tdd-task** encourages stubs and embeds escalation evaluation that belongs at a higher tier

Secondary issues:
- No phase boundary functional review during orchestration
- Vet skill lacks design conformity and functional completeness checks
- No post-commit sanity check (execution reports committed in bulk, not per-cycle)
- Escalation evaluation done by haiku (cheapest model) instead of sonnet

Full analysis: `plans/claude-tools-rewrite/runbook-analysis.md`

## Scope

**In scope:**
- plan-tdd skill (SKILL.md + references)
- review-tdd-plan skill (SKILL.md)
- tdd-task agent template
- orchestrate skill (SKILL.md)
- vet skill (SKILL.md)
- plan-adhoc skill (minor)
- New refactor agent
- prepare-runbook.py (phase boundary markers)

**Out of scope:**
- claude-tools-rewrite recovery (separate design)
- New review-adhoc-plan skill (not justified — vet improvements sufficient)
- design skill changes

## Changes

### 1. plan-tdd SKILL.md

#### 1a. Assertion quality requirements (Phase 3, after line 144)

Add section after RED specification template:

```markdown
**Assertion Quality Requirements:**

RED phase tests MUST verify **behavior**, not just **structure**:

| Weak (structural) | Strong (behavioral) |
|---|---|
| `assert result.exit_code == 0` | `assert "Mode: plan" in result.output` |
| `assert "KEY" in env_vars` | `assert env_vars["KEY"] != ""` or mock keychain |
| `assert hasattr(obj, "method")` | `assert obj.method(input) == expected` |
| `assert isinstance(result, dict)` | `assert result["field"] == expected_value` |

**For I/O-dependent behavior:**
- Mock external dependencies (filesystem, keychain, APIs)
- Use fixtures (tmp_path) for state simulation
- Assert on interaction (mock.assert_called_with) or output content
- Never test I/O behavior with exit-code-only assertions

**Validation rule:** If a RED test can pass with a stub that returns a
constant/empty value, the test is too weak. Add content or mock assertions.
```

#### 1b. Happy path first rule (Phase 3, cycle planning guidance)

Add to Cycle Breakdown Guidance section:

```markdown
**Cycle ordering:**
- Start with simplest happy path, not empty/degenerate case
- Only test empty case if it requires special-casing that wouldn't arise
  naturally from list processing or normal control flow
- Anti-pattern: Cycle 1 tests empty input → GREEN returns `[]` → stub never replaced
```

#### 1c. Integration cycle verification (Phase 3, after dependency assignment)

Add new action:

```markdown
6. **Verify integration coverage:**
   - For each component that reads external state (files, keychain, APIs):
     at least one cycle mocks and tests the real interaction
   - For each CLI command: at least one cycle asserts on output content
   - If components are created separately and need wiring: plan explicit
     integration cycles
   - Metadata cycle count MUST equal actual cycles defined
```

#### 1d. Metadata validation (Phase 5, format verification)

Add to existing verification checklist:

```markdown
- Metadata "Total Steps" matches actual cycle count
- Every CLI command has at least one cycle with content assertions
```

#### 1e. Enhanced checkpoint guidance (Phase: Checkpoints section)

Replace existing two-step checkpoint with three-step:

```markdown
**Process (three steps):**

1. **Fix** - Get tests passing
   - Run `just dev`
   - If failures: sonnet quiet-task diagnoses and fixes
   - Commit when passing

2. **Vet** - Quality review
   - Sonnet reviews accumulated changes (presentation, clarity, design alignment)
   - Fix findings, commit

3. **Functional review** - Behavioral completeness check
   - Sonnet reviews implementations from this phase against design document
   - Checks: Are implementations real or stubs? Do functions compute or return constants?
   - Checks: Are I/O operations mocked and tested, or just exit-code tested?
   - If stubs found: STOP, report which implementations need real behavior
   - If all functional: Proceed to next phase

**Placement:** At every phase boundary (mandatory).
```

### 2. review-tdd-plan SKILL.md

#### 2a. Weak RED phase assertions (new Review Criteria section)

Add after existing "Test Specifications" section (after line 115):

```markdown
### 5. Weak RED Phase Assertions (CRITICAL)

**Violation:** RED test only verifies structure, not behavior

**Indicators:**
- Test only checks `exit_code == 0` or `exit_code != 0`
- Test only checks key existence (`"KEY" in dict`) without value verification
- Test only checks class/method existence (would pass with `pass` body)
- Test has no mocking for I/O-dependent behavior

**Check:** For each RED phase, ask: "Would a stub that returns a constant/empty
value pass this test?" If yes → VIOLATION: weak assertion

**Correct pattern:**
- Assert on output content, mock interactions, or computed values
- Mock external dependencies and verify interaction
- Use fixtures for filesystem state
```

#### 2b. Metadata accuracy check (new Review Criteria section)

```markdown
### 6. Metadata Accuracy

**Check:** `Total Steps` in Weak Orchestrator Metadata matches actual cycle count
- Count all `## Cycle X.Y:` or `### Cycle X.Y:` headers
- Compare to metadata value
- If mismatch → VIOLATION: metadata inaccurate
```

#### 2c. Empty-first anti-pattern check

```markdown
### 7. Empty-First Cycle Ordering

**Warning:** First cycle in a phase tests empty/degenerate case

**Check:** Does Cycle X.1 test empty input, no-op, or missing data?
- If empty case requires special handling → acceptable
- If empty case arises naturally from list processing → WARNING: reorder
  to test simplest happy path first
```

### 3. tdd-task.md

#### 3a. Remove stub guidance

Delete line 61: "Prefer simplest solution (hardcoded values acceptable initially)"

No replacement. The test drives implementation complexity.

#### 3b. Remove escalation evaluation from REFACTOR phase

Remove Steps 4-5 (Refactoring Assessment and Execute Refactoring) including the
handler table and tier table. Replace with:

```markdown
### Step 4: Escalate Refactoring

If quality check found warnings:
- **STOP** execution
- Report warnings to orchestrator
- Orchestrator routes to refactor agent (sonnet)

Do not evaluate warning severity or choose refactoring strategy.
```

#### 3c. Post-commit sanity check (new Step 8)

Add after Step 7 (Amend Commit):

```markdown
### Step 8: Post-Commit Sanity Check

Verify cycle produced a clean, complete commit:

1. Tree must be clean:
   ```bash
   git status --porcelain
   ```
   - If non-empty: stage missing files, amend commit, re-check
   - If still dirty after amend: escalate

2. Last commit must contain both source changes AND execution report:
   ```bash
   git diff-tree --no-commit-id --name-only -r HEAD
   ```
   - Must include at least one file in `src/` or `tests/`
   - Must include the cycle's report file
   - If report missing: STOP — report written but not staged
```

### 4. refactor.md (new agent)

Create `agent-core/agents/refactor.md`. Sonnet agent.

**Purpose:** Evaluate and execute refactoring escalated from tdd-task cycles.

**Receives:** Quality check warnings from tdd-task via orchestrator.

**Escalation table (moved from tdd-task):**

| Warning Type | Handler | Action |
|---|---|---|
| Common (split module, simplify function, reduce nesting) | Sonnet (self) | Design and execute refactoring |
| Architectural (new abstraction, multi-module impact) | Opus | Escalate for design |

**No human escalation** during refactoring. Design decisions are already made.
Opus handles architectural refactoring within design bounds.

**Script-first principle:** Prefer scripted transformations (Tier 1) over manual
edits. Tier evaluation (1: script, 2: simple steps, 3: full runbook) stays here.

**Post-refactoring:** Run `just precommit`, verify passes, amend commit.

### 5. orchestrate SKILL.md

#### 5a. Post-step tree check

Add after step 3.2 (check execution result):

```markdown
**3.3 Post-step tree check:**

After agent returns success:
```bash
git status --porcelain
```
- If clean: proceed
- If dirty: STOP, report "Step N left uncommitted changes" with file list
- Do NOT clean up on behalf of the step — escalate
```

#### 5b. Phase boundary functional review

Add after step 3.3:

```markdown
**3.4 Phase boundary check:**

If the completed step is the last cycle of a phase:
- Delegate functional review to sonnet:
  "Review implementations from Phase N against design at [design-path].
   Check for stub implementations, hardcoded values, missing I/O integration.
   Write report to plans/{name}/reports/phase-{N}-functional-review.md
   Return: 'FUNCTIONAL: [summary]' or 'STUBS_FOUND: [list of stubs]'"
- If STUBS_FOUND: STOP orchestration, report to user
- If FUNCTIONAL: Continue to next phase
```

#### 5c. Route refactoring to refactor agent

Update escalation section: when tdd-task escalates with quality warnings,
route to refactor agent (sonnet) instead of generic sonnet diagnostic.

### 6. vet SKILL.md

#### 6a. Design conformity dimension

Add to "Analyze Changes" (Section 3):

```markdown
**Design Conformity (when design doc available):**
- Implementation matches design specifications
- All design-specified behaviors actually implemented (not stubbed)
- Integration between components matches design architecture
- No hardcoded values where design specifies dynamic behavior
- Check: grep for hardcoded return values in functions that should compute
```

#### 6b. Functional completeness dimension

```markdown
**Functional Completeness:**
- CLI commands produce meaningful output (not just "OK" or empty)
- Functions return computed values (not empty strings or hardcoded constants)
- Components that should read external state actually do so
- Check: look for stub patterns: `return ""`, `return {}`, hardcoded constructors
- Integration: components that exist separately are wired together
```

#### 6c. Scope option for design conformity

Add to scope determination step:

```markdown
6. "Design conformity" - Review changes against design document
```

When selected, prompt for design path or auto-detect from `plans/*/design.md`.

### 7. plan-adhoc SKILL.md

#### Minor: Success criteria guidance

Add to Common Pitfalls "Avoid" list:

```markdown
- Writing success criteria that only check structure ("file exists", "exit code 0")
  when the step should produce functional output. Verify content/behavior, not
  just existence.
```

### 8. references/anti-patterns.md

Add two new rows to the anti-patterns table:

```markdown
| **Weak RED assertions** | `assert result.exit_code == 0` (passes with stub) | Mock filesystem/keychain, assert output content: `assert "Mode: plan" in result.output` |
| **Missing integration cycles** | Components created in isolation, no wiring cycle | Explicit integration cycle: `Cycle 3.16: Wire providers to keychain` with mocked I/O |
| **Empty-first ordering** | Cycle 1: "empty list returns []" → stub committed | Start with simplest happy path. Only test empty case if it requires special handling. |
```

### 9. references/patterns.md

Add to cycle ordering guidance:

```markdown
**Cycle ordering within phase:**
- Start with simplest happy path
- Add complexity incrementally (error handling, edge cases, validation)
- Empty/degenerate case: only if requires distinct code path
- Anti-pattern: empty-first ordering produces stubs that persist
```

### 10. prepare-runbook.py

#### Phase boundary markers

Emit phase boundary markers in orchestrator-plan.md so the orchestrate skill
knows when to insert functional reviews:

```markdown
## Step N (Cycle X.Y) — PHASE_BOUNDARY
[Last cycle of phase X. Insert functional review checkpoint before Phase X+1.]
```

Detection: When cycle numbering changes phase (e.g., 1.13 → 2.1), mark the
preceding step as a phase boundary.

## Design Decisions

**1. No review-adhoc-plan skill**
- plan-adhoc failures haven't produced the same class of problem
- Structural success criteria are often correct for infrastructure work
- Vet improvements (design conformity, functional completeness) cover the gap
- Revisit if a future plan-adhoc execution fails similarly

**2. Human escalation removed from refactoring**
- Design decisions are already made during /design phase
- Opus can handle architectural refactoring within design bounds
- Blocking pipeline for human input during refactoring is expensive
- Human escalation remains for execution blockers (in orchestrate skill)

**3. Escalation evaluation moved from haiku to sonnet**
- Haiku (cheapest) shouldn't evaluate failure severity
- Simplifies tdd-task to pure mechanical execution
- New refactor agent (sonnet) evaluates and handles or escalates to opus

**4. Mandatory phase boundary checkpoints**
- Current checkpoints are optional placement ("natural boundaries")
- Changed to mandatory at every phase boundary
- Cost: ~1 sonnet invocation per phase (typically 2-4 per runbook)
- Benefit: Catches stub implementations before they compound

**5. Post-commit sanity check in both tdd-task and orchestrate**
- tdd-task: owns the commit, can self-heal (stage missing files, amend)
- orchestrate: defense in depth, catches cases where tdd-task fails
- Prevents execution report accumulation across cycles

## Dependencies

**Before:** Analysis in `plans/claude-tools-rewrite/runbook-analysis.md`
**After:** Recovery design (`plans/claude-tools-recovery/design.md`) depends on these improvements being applied first

## Execution

Route: `/plan-adhoc` → `/orchestrate`

Infrastructure/refactoring work on existing skill files. No TDD needed — these are
documentation and agent definition changes, not code with testable behavior.
