# Classification: Skill-CLI Integration

## Composite Decomposition

Three sub-problems (SP-3 deferred):

| SP | Description | Classification | Impl. Certainty | Req. Stability | Behavioral Code? | Artifact Dest. |
|----|-------------|---------------|-----------------|----------------|-------------------|----------------|
| SP-H | Stop hook for status display | Moderate | High (spike proven) | High | Yes (bash script) | production |
| SP-1 | execute-rule.md STATUS → trigger convention | Moderate | High | High | No (prose) | agentic-prose |
| SP-2 | /commit skill → `_commit` CLI composition | Moderate | High | High | No (prose) | agentic-prose |
| SP-3 | /handoff skill → `_handoff` CLI (DEFERRED) | -- | -- | -- | -- | -- |

**Work type:** Production
**Evidence:** Both axes high across all SPs. Spike validated hook mechanism. CLI tools exist and tested. Composition pattern clear from spike + CLI exploration.

## SP-3 Deferral Rationale

`_handoff` CLI handles 2 of ~6 session.md mutations (status line, completed section). Skill does full rewrite. Partial CLI composition adds complexity for minimal gain. Revisit when CLI scope expands or batch-vs-incremental model changes.
