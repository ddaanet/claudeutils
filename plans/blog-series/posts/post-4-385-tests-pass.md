# Post 4: "385 Tests Pass, 8 Bugs Ship"

## Opening Hook

14 TDD cycles. 28 commits. 385/385 tests passing. Zero regressions.

The agent's commit message: "Complete statusline-parity runbook execution. Visual parity validated against shell reference." The celebration summary: "Python implementation now matches shell output exactly."

Human opens the terminal. Compares actual output to the shell prototype.

Eight visual discrepancies. `format_directory()` not extracting basename from full path. `get_python_env()` not wired into CLI. Token count showing decimals (`43.3k`) instead of integers (`43k`). Five more.

The 385 tests validated data flow and structural correctness. Not one test compared rendered output to the shell prototype.

(Commit `45235adf`, Feb 5, 2026. RCA: `bccf08a1`, Feb 8.)

## Core Argument

### The Failure Cascade

The RCA document (commit `bccf08a1`) lays it out:

"The core failure was not specification ambiguity but a multi-layered quality gate failure: the orchestration pipeline declared 'complete' without verifying conformance against the reference, the vet agent reviewed within a narrow scope and missed systemic gaps, tests were added without checking file-level constraints, and `just precommit` was either not run or its output was ignored before committing."

Every gate passed individually. The system failed collectively. The orchestrator declared "complete." The vet agent reviewed within scope. Tests passed. Precommit passed. And the output didn't match the reference.

### Two User Directives

The gap analysis session (session `1fb0b59c`) produced two directives that shaped all subsequent quality infrastructure:

"Script-based diff: sounds like a one-off validation, we must have reproducible validation. Key concept: **tests are executable contracts**."

"Key insight: **warnings do not work.**"

The first eliminated prototype-comparison as a validation approach (one-off, not reproducible). The second eliminated graduated enforcement (advisory warnings, soft checks). Both were grounded in observed failures, not theoretical principles.

### Defense-in-Depth

The defense-in-depth document (commit `e3d26b1e`, Feb 8) established a four-layer model and named the pattern:

| Layer | Mechanism | What it catches |
|-------|-----------|----------------|
| 1. Execution flow | D+B hybrid — prose gates merged with tool calls | Skipped steps, missed prerequisites |
| 2. Automated checks | Tests, lint, precommit | Regressions, style violations |
| 3. Semantic review | Deliverable review with artifact inventory | Drift from design, inter-file inconsistency |
| 4. Conformance validation | Tests as executable contracts | Gap between specification and output |

The 385-test failure hit Layer 4. Tests existed (Layer 2) but tested the wrong thing. No one compared output to spec (Layer 4 absent).

### Building the Review System

The agent proposed six review axes from available context, then admitted: "I'm uncertain whether this is sufficient or well-structured — I haven't looked at methodology literature for this." (Session `90557acc`)

User's one-word response: "search."

The agent searched IEEE 1012 (Verification & Validation), ISO 25010 (software quality characteristics), and agentic AI research. Result: 21 axes across 5 artifact types, grounded in established standards plus agent-specific dimensions:

- **Conformance** (IEEE 1012): does the artifact satisfy the design spec?
- **Functional completeness** (ISO 25010): covers all specified tasks?
- **Constraint precision** (arXiv 2601.03359): are constraints unambiguous? Poorly specified constraints significantly reduce instruction compliance
- **Actionability** (AGENTIF benchmark): can the agent execute without interpretation?

(Commit `e39b2eb2`, Feb 11, 2026)

### The Two-Layer Model

The initial proposal: remove agent delegation from review (agents lack full context). The user corrected: "keep optional agent partitioning (important for large deliverables), add mandatory full-artifact review." (Session `c5b45184`)

Defense-in-depth applied to review itself:

- **Layer 1 (delegated):** Per-file depth — robustness, specificity, conformance against axes. Scales to large deliverables without context overflow. Optional, gated on volume.
- **Layer 2 (interactive):** Cross-cutting patterns — path consistency, fragment conventions, inter-file naming. Requires full session context. Mandatory.

The same principle that created the review system (defense-in-depth) was applied to the review system's own design.

### External Validation

devddaanet (Mar 2026, 63 commits): the full pipeline in production on a real project. Deliverable review finds 1 critical + 3 minor findings → fixed → re-reviewed → delivered.

But the validation is qualified. Post-delivery commits: 3 of the next 5 are bug fixes — sync crash, worktree deletion bug, unison crashes — followed by a discovery mechanism overhaul. The review gate ensures a review happens. It doesn't guarantee the review is comprehensive.

## Evidence Chain

| Claim | Evidence |
|-------|----------|
| 385/385 tests passing, 8 visual discrepancies | Commit `45235adf`, RCA `bccf08a1` |
| "Visual parity validated against shell reference" was false | Session `402efacf` completion commit |
| Tests validated data flow, not presentation | RCA document: "no test compared rendered output to shell prototype" |
| "Tests are executable contracts" directive | Session `1fb0b59c` |
| "Warnings do not work" directive | Session `1fb0b59c` |
| Defense-in-depth: four-layer model | Commit `e3d26b1e` |
| 21 review axes grounded in ISO 25010, IEEE 1012, AGENTIF | Commit `e39b2eb2` |
| Agent admitted methodology gap, user said "search" | Session `90557acc` |
| Two-layer model: user corrected "remove delegation" to "keep + add" | Session `c5b45184` |
| devddaanet: 1C+3Mi found, fixed, re-reviewed | Commits `265c8c7`, `cae9155`, `4ffb1ea` |
| Post-delivery: 3 of 5 next commits are bug fixes | devddaanet commit history |

## Transition to Post 5

Tests as executable contracts. Grounded review methodology. Defense-in-depth. Each of these solutions shares a structural property: they constrain what the agent can produce, rather than advising the agent to be careful. The final post names this pattern explicitly and traces it back to the earliest agent instructions.
