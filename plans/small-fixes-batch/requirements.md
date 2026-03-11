**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Small Fixes Batch

Five small independent fixes batched for efficiency.

## Requirements

### Functional Requirements

**FR-1: Diagnose hook error after clear**
Diagnose "SessionStart:clear hook error" that appears after `/clear` command. Identify root cause and fix.
- Acceptance: `/clear` followed by user message → no hook error in output

**FR-2: Upstream skills field**
File PR or issue against Claude Code for missing `skills` frontmatter field support. Skills currently use `skills:` in frontmatter but it's not documented in upstream spec.
- Acceptance: PR/issue filed with reproduction case and proposed spec addition

**FR-3: Fix prefix tolerance in fuzzy matching**
Zero tolerance for prefix noise in `src/claudeutils/when/fuzzy.py` — one-token mismatch at prefix produces 0.0 score. Should degrade gracefully.
- Acceptance: "when doing X" vs "when X" → non-zero similarity score
- Acceptance: Completely unrelated prefix → still scores near 0.0 (no false positives)

**FR-4: Fix session search CLI**
Make `--project` optional in `session-scraper.py`, support project path globbing.
- Acceptance: `claudeutils _session` without `--project` → searches current project
- Acceptance: `claudeutils _session --project "~/code/*"` → searches matching projects

**FR-5: Test context-fork model**
Create minimal skill with `context: fork` + `AskUserQuestion`, observe and document interaction behavior.
- Acceptance: Test skill created, behavior documented (does fork preserve user interaction? does AskUserQuestion work in forked context?)

### Out of Scope

- Architectural changes — each fix is self-contained
