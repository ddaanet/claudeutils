## Fix RC14 — Composite Task Classification

**7 active items** (3 dismissed: m-8, m-9, m-10)

- **Classification:** Moderate (composite — m-2 elevates)
- **Implementation certainty:** High — all fixes have clear specs (findings + outline)
- **Requirement stability:** High — findings stable, design delivered
- **Behavioral code check:** Yes — m-2 adds `cwd` param to shared `_git()`, changes caller error-handling default
- **Work type:** Production
- **Artifact destination:** production
- **Evidence:** m-2 modifies `_git()` signature used across 6+ modules; m-3 spans 3 test files. Remaining 5 Simple. Recall: behavioral-code-as-simple, composite-task-decomposition.

### Per-Item

| Finding | Classification | Reason |
|---------|---------------|--------|
| m-1 (hint logic clarity) | Simple | Factor out common assignment, no behavioral change |
| m-2 (`_git_output` dup) | Moderate | Shared API change + error-handling default difference |
| m-3 (submodule helpers) | Moderate | 3-file test infrastructure standardization |
| m-4 (tight assertion) | Simple | Loosen to key fragments |
| m-5 (tight assertion) | Simple | Loosen to key fragments |
| m-6 (test vacuity) | Simple | Add commit setup for different path |
| m-7 (resume state clear) | Simple | Add assertion |

### Dismissed

- **m-8:** design/SKILL.md scope — standalone bugfix, not handoff-cli deliverable
- **m-9:** settings.local.json — POSIX trailing newline only
- **m-10:** .gitignore broadening — handles sandbox artifacts
