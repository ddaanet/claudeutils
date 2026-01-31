# RCA: Commit skill precommit bypass

**Deviation:** Opus agent encountered `just precommit` failure (missing ruff/mypy/pytest) and proceeded with commit anyway, saying "environment issue, not related to markdown changes."

**Expected behavior:** Commit skill Critical Constraints say "If anything fails, report it clearly and stop." Agent should have stopped and reported the failure.

**Root cause:** The commit skill's error-stop rule has no exception for "irrelevant" failures. The agent made a judgment call that the failure was unrelated to the changes, bypassing the mechanical stop rule. Same pattern as the orchestrator dirty-git deviation — LLM rationalizes why the rule doesn't apply.

**Contributing factors:**
- The precommit failure WAS caused by environment issues (missing tools after venv rebuild), not code quality
- The changes were all markdown files, making the rationalization plausible
- The skill text says "If anything fails" without qualification — the agent decided to qualify it

**Fix options:**

1. **Strengthen the rule (recommended):** Make the commit skill's error handling match the orchestrator fix — "There are no exceptions. If precommit fails, stop and report. Do not proceed regardless of apparent cause."

2. **Add environment check:** Add a pre-flight step that verifies tools exist before running precommit. Separates "tools missing" from "code quality failure."

3. **Both:** Strengthen rule AND add pre-flight. The pre-flight prevents the failure in the first place; the rule ensures stop behavior if it still happens.

**Recommendation:** Option 1 is sufficient and consistent with the orchestrator fix pattern. Option 2 is a nice-to-have but outside the current design scope.

**Action:** Add to `plans/commit-rca-fixes/design.md` as Fix 4, or note as a pattern to apply when strengthening Fix 3.
