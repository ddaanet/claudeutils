**⚠ UNREVIEWED — Agent-drafted from session.md task descriptions. Validate before design.**

# Gate Batch

Mechanical checkpoints at skill entry/exit/transition points. Prevent stale artifacts, missing context, and uncommitted state from propagating through the workflow pipeline.

## Requirements

### Functional Requirements

**FR-1: Artifact staleness gate**
Verify plan artifacts (design.md, outline.md, runbook files) are current relative to their inputs before skill execution. Gate fires at skill entry for `/runbook`, `/orchestrate`, and `/inline`.
- Acceptance: Stale artifact detected → skill halts with message identifying which artifact is stale and what changed since it was written

**FR-2: Entry gate propagation**
Propagate gate checks across skill boundaries when one skill chains to another (e.g., `/design` → `/runbook` → `/orchestrate`). Downstream skill inherits upstream's gate results rather than re-running.
- Acceptance: Chain of 3 skills runs gate once at entry, not 3 times

**FR-3: Design context gate**
Validate design context (recall artifact, requirements, outline) is loaded before planning phases. Prevents planning against stale or absent design artifacts.
- Acceptance: `/runbook` invoked without recall artifact → gate blocks with "run recall pass first"

**FR-4: Pre-inline plan commit**
Commit plan state (requirements, design, outline) before `/inline` execution begins. Prevents plan artifacts from being lost if inline execution fails or is interrupted.
- Acceptance: `/inline` entry commits plan directory changes if working tree is dirty for plan files

### Out of Scope

- Runtime validation during execution (these are entry/exit gates only)
- Modifying the skill execution model — gates are pre/post checks, not middleware

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (gates may be implemented as hooks)
