# Cooperative Protocol Gaps

Four skills listed as cooperative in `continuation-passing.md` lack full protocol compliance.

## Gaps

| Skill | Missing frontmatter | Missing §Continuation |
|-------|--------------------|-----------------------|
| `/design` | Yes | Yes |
| `/runbook` | Yes | Yes |
| `/worktree` | No | Yes |
| `/commit` | No | Yes |

## Scope

- Add `continuation: cooperative: true` frontmatter to /design and /runbook
- Add §Continuation sections to all 4 skills
- Add /worktree to cooperative skills table in continuation-passing.md
- Update hardcoded tail-calls in /design and /runbook body to reference §Continuation
