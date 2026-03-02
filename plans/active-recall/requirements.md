# Active Recall System

## Requirements

### Functional Requirements

**FR-1: Hierarchical index structure**
Split flat `agents/memory-index.md` (currently 449 lines, 366 entries) into a root index mapping domains to child index files. Root index lists domain names → child file paths. Child indices contain the actual `/when` and `/how` trigger entries scoped to their domain. Lookup traverses root → child → entry using existing tail-recursion primitive in `/recall` skill. Current domain sections in memory-index.md (e.g., `## agents/decisions/cli.md`) become the split boundaries.

Acceptance criteria:
- Root index file exists at `agents/memory-index.md` (same path, different content)
- Child index files exist under a subdirectory (e.g., `agents/recall/` or `agents/memory-index/`)
- `claudeutils _recall resolve "when <trigger>"` works identically pre/post migration (backward compatible)
- `parse_memory_index()` in `src/claudeutils/recall/index_parser.py` handles hierarchical structure
- `/when` and `/how` CLI commands resolve entries through the hierarchy transparently
- O(log_k(N)) lookup with branching factor k = number of child indices

**FR-2: Trigger class distinction**
Formalize the two trigger classes (`when` and `how`) with distinct authoring and automation profiles.

- `when` entries: situational triggers matching agent context/situation. Primarily project decisions from incidents/failures. Hand-curation required. Invalidated by explicit user decision.
- `how` entries: task-descriptive triggers matching agent's current task. Primarily reference documentation. Automation-safe — documentation headings approximate triggers.

Acceptance criteria:
- Trigger class metadata available in `IndexEntry` model (or derivable from prefix)
- `/codify` and future automation tools can distinguish classes for routing decisions
- No behavioral change to resolution — both classes resolve identically via `_recall resolve`

**FR-3: Three learning categories with invalidation rules**
Categorize recall entries into three learning types with distinct invalidation conditions:

- **Internal decisions:** Project choices. Invalidated only by explicit user decision.
- **External environment facts:** Dependency/tool facts. Auto-invalidated on version change. Corpus partitioned by dependency — version bump triggers subtree re-evaluation only.
- **Hybrid:** Internal decisions grounded in external facts. Version change triggers re-evaluation; decision may survive if reasoning still holds.

Acceptance criteria:
- Category metadata representable in index entries or child index structure
- External entries partitioned by dependency (e.g., all pytest entries in one child index)
- Version-change detection mechanism defined (how does the system know a dependency version changed?)
- Re-evaluation triggers subtree-scoped, not full-corpus

**FR-4: Automated documentation conversion pipeline**
Convert external reference documentation (Python stdlib, pytest, pydantic, click, ruff, mypy) into `how` entries via automated pipeline.

Pipeline: source documentation → sonnet-grade extraction agent → corrector pass (validates trigger specificity, deduplication against existing index) → index integration.

Acceptance criteria:
- Pipeline accepts a documentation source (URL, local docs, Context7 library) and produces candidate `how` entries
- Corrector validates each entry: trigger is specific enough, no duplicate with existing entries, content is actionable
- Output integrates into hierarchical index structure (FR-1)
- Pipeline is idempotent — re-running on same source doesn't create duplicates

**FR-5: Memory format grounding**
Ground the recall entry format before bulk conversion (FR-4). Use `/ground` skill to research and formalize:

- Naming conventions for triggers
- Trigger structure (current `/when` and `/how` prefixes, heading alignment)
- `how`/`when` distinction formalization
- Index hierarchy design (root → child navigation, branching factor)

Acceptance criteria:
- Grounding research artifact in `plans/reports/` with external framework references
- Formalized format specification consumable by FR-4's extraction agent
- Existing entries validate against the grounded format (backward compatible)

**FR-6: Recall-explore-recall pattern**
Preserve and formalize the two-pass recall pattern: agent recalls based on initial understanding, explores codebase, recalls again with enriched context. Second pass matches entries invisible from initial request alone.

Acceptance criteria:
- Pattern documented as a retrievable decision entry
- `/recall` skill's tail-recursion primitive supports this naturally (already exists — confirm no regression)
- Pipeline recall points (design A.1, runbook Phase 0.5) implement the pattern

**FR-7: Recall mode simplification**
Reduce formal recall modes from five to three per the grounding report's revised assignment:

- `default`: per-key, two passes, scored selection (8/10 pipeline recall points)
- `all`: per-file, tail-recursive (design A.1, runbook Tier 3 Phase 0.5)
- `everything`: full corpus, no scan (ad-hoc only)

Drop `broad` (absorbed by `all`) and `deep` (absorbed by `default` two-pass).

Acceptance criteria:
- `/recall` skill supports three modes
- `broad` and `deep` either removed or aliased to the canonical modes
- No behavioral regression at existing pipeline recall points

**FR-8: Recall tool consolidation**
Consolidate the two recall CLI modules (`src/claudeutils/recall/` and `src/claudeutils/recall_cli/`) and the when resolver (`src/claudeutils/when/`) into a unified recall interface.

Acceptance criteria:
- Single CLI entry point for recall operations (resolve, check, diff)
- `when` resolver integrated (not a separate module)
- Backward-compatible CLI: `claudeutils _recall resolve` still works
- Test coverage maintained (currently 20+ test files across the three modules)

### Non-Functional Requirements

**NFR-1: Scaling capacity**
Hierarchical index must support thousands of entries (projected from bulk documentation conversion) without degrading lookup performance or agent context budget.

**NFR-2: Backward compatibility**
All existing CLI commands (`claudeutils _recall resolve`, `claudeutils _recall check`, `claudeutils _recall diff`, `claudeutils _when`) must continue working during and after migration. Pipeline recall points across 10+ skills must not break.

**NFR-3: Incremental migration**
Migration from flat to hierarchical index can proceed incrementally — partial hierarchy (some domains split, others still flat) must work correctly.

### Constraints

**C-1: Memory format grounding prerequisite**
FR-5 (memory format grounding) must complete before FR-4 (automated documentation conversion). Bulk conversion without grounded format produces entries that need rework.

**C-2: Hierarchical index before bulk conversion**
FR-1 (hierarchical index) must be operational before FR-4 bulk conversion populates thousands of entries into the system.

**C-3: Existing infrastructure**
Current infrastructure: `src/claudeutils/recall/` (9 modules), `src/claudeutils/recall_cli/` (2 modules), `src/claudeutils/when/` (5 modules), `agents/memory-index.md` (366 entries), `/recall` skill, `/when` and `/how` skills, pretooluse-recall-check hook, 20+ test files. All must be accounted for during consolidation.

**C-4: Agent context budget**
Root index must remain within always-loaded context budget (~5000 tokens for 200 entries currently). Hierarchical structure moves entry-level detail to child indices loaded on-demand.

### Out of Scope

- SWE-ContextBench benchmarking — mentioned in brief as positioning, not implementation work
- Post-resolve scoring / recall usage tracking — noted in grounding report as downstream infrastructure
- Stage provenance tags in recall-artifact.md — grounding report Pattern 1, deferred
- Recall-artifact rejection tracking — grounding report Pattern 2 annotated removal, deferred
- Lifecycle role contract enforcement — grounding report Pattern 3, convention not mechanically enforced
- PreToolUse hook for lint-gated recall — separate from core recall system (defense-in-depth.md)

### Dependencies

- `/ground` skill — required for FR-5 (memory format grounding)
- Context7 MCP — potential source for FR-4 documentation extraction
- Recall lifecycle grounding report (`plans/reports/recall-lifecycle-grounding.md`) — informs FR-7 mode simplification and pipeline integration

### Open Questions

- Q-1: What is the child index directory structure? `agents/recall/<domain>.md` vs `agents/memory-index/<domain>.md` vs keeping children alongside `memory-index.md`
- Q-2: How does version-change detection work for FR-3 external entries? Manual trigger (`just check-deps`), git diff on lockfile, or dependency-version metadata in index?
- Q-3: Which documentation sources are first targets for FR-4? Brief lists Python stdlib, pytest, pydantic, click, ruff, mypy — prioritization needed

### References

- `plans/active-recall/brief.md` — architectural discussion distillation
- `plans/reports/recall-lifecycle-grounding.md` — lifecycle patterns, mode assignments, three-tier model
- `plans/reports/recall-lifecycle-internal-codebase.md` — internal inventory
- `plans/reports/recall-lifecycle-external-research.md` — external frameworks
- Task context: git commit `fc0d9b8a` — session that produced the architectural discussion

### Skill Dependencies (for /design)

- Load `plugin-dev:hook-development` before design (pretooluse-recall-check hook affected by FR-8 consolidation)
- Load `plugin-dev:skill-development` before design (recall skill restructuring in FR-7)
