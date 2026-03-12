# Small Fixes Batch

Three small independent fixes batched for efficiency.

## Requirements

### Functional Requirements

**FR-1: Diagnose hook error after clear**
Diagnose "SessionStart:clear hook error" that appears after `/clear` command. Identify root cause and fix.
- Acceptance: `/clear` followed by user message → no hook error in output

**FR-2: Fix session search prototype**
Make `--project` optional in `plans/prototypes/session-scraper.py`, support project path globbing. This is a standalone prototype script, not part of `claudeutils` CLI.
- Acceptance: `plans/prototypes/session-scraper.py` without `--project` → searches current project
- Acceptance: `plans/prototypes/session-scraper.py --project "~/code/*"` → searches matching projects

**FR-3: Test Skill tool context parameter**
Investigate the `context` parameter on the Skill tool (e.g., `context: fork`). Create a minimal test skill, invoke it with different `context` values, observe and document behavior differences.
- Acceptance: Behavior documented — what does `context: fork` do vs default? Does AskUserQuestion work? What context is visible to the skill?

**FR-4: Remove bottom-to-top edit ordering references**
Grep and remove all references to "bottom-to-top" edit ordering from documents. The concept is unfounded — the Edit tool is not line-number dependent.
- Acceptance: `grep -ri "bottom.to.top" agent-core/ agents/ plans/` returns no matches

### Out of Scope

- Architectural changes — each fix is self-contained
