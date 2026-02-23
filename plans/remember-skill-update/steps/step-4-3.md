# Cycle 4.3

**Plan**: `plans/remember-skill-update/runbook.md`
**Execution Model**: sonnet
**Phase**: 4

---

## Phase Context

Rewrite Click command for one-arg syntax with batched recall.

**Files:** `src/claudeutils/when/cli.py`, `tests/test_when_cli.py`, `agent-core/bin/when-resolve.py`
**Baseline:** 5 existing tests, all passing. Resolver (`src/claudeutils/when/resolver.py`) signature unchanged — CLI parses operator, calls `resolve(operator, query, ...)` as before.

---

## Cycle 4.3: Invalid prefix rejection

**RED:**
- New test: `test_invalid_prefix_rejected`
- Invoke: `["when", "no prefix query"]`
- Assert: exit code != 0, error message mentions "when" or "how" prefix required
- Expected failure: No prefix validation on query strings (old CLI had Click.Choice)

**Verify RED:** `just test tests/test_when_cli.py::test_invalid_prefix_rejected -v`

**GREEN:**
- Add prefix validation: query must start with `when ` or `how ` (case-insensitive)
- Error: state what IS wrong, no recovery suggestions

**Verify GREEN:** `just test tests/test_when_cli.py -v`
**Verify no regression:** `just test -v`

**Stop/Error Conditions:**
- Prefix validation must happen BEFORE resolve() call — invalid prefix should not reach resolver

**Dependencies:** Cycle 4.1 (prefix parsing logic exists before validation added)

**Phase 4 Checkpoint:** `just precommit` passes. Verify dot-prefix modes still work (covered by existing test migration in 4.1).

---

### Phase 5: Recall CLI Docs Update (type: inline, model: opus)

Update invocation examples in 4 skill/decision files from two-arg to one-arg syntax.

Load `/plugin-dev:skill-development` before editing skill files.

- Update `agent-core/skills/when/SKILL.md`: change all examples from `when-resolve.py when <query>` to `when-resolve.py "when <query>"`
- Update `agent-core/skills/how/SKILL.md`: same pattern — `when-resolve.py how <query>` to `when-resolve.py "how <query>"`
- Update `agent-core/skills/memory-index/SKILL.md`: update sub-agent invocation examples to one-arg syntax, add batched recall example
- Update `agents/decisions/project-config.md`: update `when-resolve.py` reference to new invocation convention

---

### Phase 6: Skill Rename to /codify (type: general, model: sonnet)

Mechanical rename — grep-and-replace across codebase. Sonnet sufficient (no architectural judgment, purely mechanical substitution despite touching skill files). Advisory: artifact-type override rule recommends opus for skill file edits, but this phase is pure text substitution with no semantic content changes — sonnet assignment is appropriate exception.
