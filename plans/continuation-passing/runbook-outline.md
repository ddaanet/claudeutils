# Runbook Outline: Continuation Passing

**Design:** plans/continuation-passing/design.md
**Type:** general

## Requirements Mapping

| Requirement | Phase | Steps/Cycles | Coverage | Notes |
|-------------|-------|--------------|----------|-------|
| FR-1: Prose continuation syntax | 1 | 1.1-1.3 | Complete | Hook parser with delimiter detection + registry lookup |
| FR-2: Sequential execution | 1 | 1.2 | Complete | Peel-first-pass-remainder protocol in parser |
| FR-3: Continuation consumption | 2 | 2.1-2.6 | Complete | Cooperative skill protocol implementation |
| FR-4: Structured continuation (multi-line) | 1 | 1.3 | Complete | `and\n- /skill` list marker detection (simplified from requirements) |
| FR-5: Prose-to-explicit translation | 1, 3 | 1.2, 3.5 | Complete | Registry matching + empirical validation (D-7) |
| FR-6: Sub-agent isolation | 2 | 2.1-2.6 | Complete | Convention + explicit prohibition in skill protocol (D-5) |
| FR-7: Cooperative skill protocol | 2 | 2.1-2.6 | Complete | Frontmatter declaration + consumption protocol (D-2) |
| FR-8: Uncooperative skill wrapping | — | — | Out of scope | Explicitly optional in requirements, deferred |
| NFR-1: Light cooperation | 2 | 2.1-2.6 | Complete | Skills understand protocol, not specific downstream skills |
| NFR-2: Context list for cooperation detection | 1 | 1.1, 1.4 | Complete | Frontmatter scanning + registry cache (D-1) |
| NFR-3: Ephemeral continuations | 1, 2 | 1.2, 2.1-2.6 | Complete | Passed through execution, never persisted (D-4) |
| C-1: No sub-agent leakage | 2 | 2.1-2.6 | Complete | Continuation stripped from Task tool prompts (D-5) |
| C-2: Explicit stop | 1, 2 | 1.2, 2.1-2.6 | Complete | Empty continuation = terminal (no tail-call) |

## Phase Structure

### Phase 1: Hook Implementation
**Objective:** Build continuation parser and registry in userpromptsubmit-shortcuts.py
**Complexity:** High
**Model:** Sonnet (registry + parser logic requires semantic analysis)
**Note:** Design recommends frontmatter-first ordering (safe/inert without hook), but this phase builds the hook infrastructure that skills will consume. Frontmatter additions in Phase 2 are safe regardless of ordering — they are inert without the hook.
**Steps:**
- 1.1: Implement cooperative skill registry builder (3-source discovery: project-local, plugins, built-in)
- 1.2: Implement continuation parser (Modes 1-3: single skill, inline prose, multi-line list)
- 1.3: Integrate Tier 3 into existing hook (after Tier 1/2 shortcut processing)
- 1.4: Add registry caching (mtime-based invalidation, NFR-2)

### Phase 2: Skill Modifications
**Objective:** Add frontmatter declarations and consumption protocol to 6 skills
**Complexity:** Medium
**Model:** Sonnet (interpreting design intent for protocol text)
**Steps:**
- 2.1: Update /design skill (frontmatter + protocol + remove hardcoded tail-call + add `Skill` to allowed-tools)
- 2.2: Update /plan-adhoc skill (frontmatter + protocol + remove hardcoded tail-call)
- 2.3: Update /plan-tdd skill (frontmatter + protocol + remove hardcoded tail-call)
- 2.4: Update /orchestrate skill (frontmatter + protocol + add continuation handling + add `Skill` to allowed-tools)
- 2.5: Update /handoff skill (frontmatter + protocol + conditional default exit per --commit flag)
- 2.6: Update /commit skill (frontmatter only — already terminal, default-exit: [])

### Phase 3: Testing and Validation
**Objective:** Unit tests for parser/registry/consumption + integration + empirical validation
**Complexity:** Medium-High
**Model:** Haiku for unit test implementation (3.1-3.3), Sonnet for integration test and empirical validation (3.4-3.5)
**Steps:**
- 3.1: Unit tests for continuation parser (8 scenarios per design Component 4)
- 3.2: Unit tests for registry builder (3 scenarios: frontmatter scanning, non-cooperative exclusion, cache invalidation)
- 3.3: Unit tests for consumption protocol (3 scenarios: peel first, last entry, empty)
- 3.4: Integration test (2-skill chain: hook parse -> additionalContext -> args -> terminal)
- 3.5: Empirical validation against session corpus (FR-5/D-7: 0% false positive target)

### Phase 4: Documentation
**Objective:** Create fragment and update decision files
**Complexity:** Low
**Model:** Haiku
**Note:** Depends on Phases 1+2 for accurate content but not for structure. Can run in parallel with Phase 3 unit tests (3.1-3.3) but should follow Phase 2 completion.
**Steps:**
- 4.1: Create agent-core/fragments/continuation-passing.md (protocol reference for skill developers)
- 4.2: Update agents/decisions/workflow-optimization.md (add continuation passing decision entries)
- 4.3: Update plugin-dev:skill-development references (mention continuation frontmatter schema)

## Key Decisions Reference

- **D-1 (Hook as parsing layer)** → affects Phase 1 (userpromptsubmit-shortcuts.py extension)
- **D-2 (Explicit passing via Skill args)** → affects Phase 2 (consumption protocol format)
- **D-3 (Default exit appending)** → affects Phase 1.2 (parser logic) and Phase 2 (frontmatter declarations)
- **D-4 (Ephemeral continuation lifecycle)** → affects Phase 2 (no persistence in skills)
- **D-5 (Sub-agent isolation by convention)** → affects Phase 2 (protocol prohibition statement)
- **D-6 (Parsing strategy)** → affects Phase 1.2 (three parsing modes)
- **D-7 (Prose-to-explicit translation)** → affects Phase 1.2 (registry matching) and Phase 3.5 (empirical validation)

## Complexity Notes

**Phase 1 (High):**
- Registry builder scans 3 sources (project-local, plugins, built-in)
- Parser handles 3 modes with disambiguation
- Integration with existing Tier 1/2 shortcut logic
- Cache invalidation based on file mtime

**Phase 2 (Medium):**
- 6 skill files to modify
- Requires interpreting design intent for protocol text (sonnet)
- /orchestrate special case (no hardcoded tail-call to remove, just add protocol)
- /handoff special case (flag-dependent default exit)
- Design constraint: All skill modifications use exact protocol text from design

**Phase 3 (Medium-High):**
- Standard TDD test implementation for unit tests (haiku, 3.1-3.3)
- Integration test spans hook → skill → tail-call → skill (sonnet, 3.4)
- Empirical validation requires corpus extraction, parser execution, and manual review (sonnet, 3.5)
- Step 3.5 is fundamentally different from standard testing — involves real user data analysis

**Phase 4 (Low):**
- Documentation updates are straightforward
- No complex logic or analysis

## Dependencies

**Inter-phase:**
- Phase 2 depends on Phase 1 (skills need continuation metadata format from hook; frontmatter additions are safe/inert without hook but protocol text references hook output format)
- Phase 3 depends on Phases 1+2 (tests validate complete system)
- Phase 4 depends on Phases 1+2 for accurate content; can run in parallel with Phase 3 unit tests (3.1-3.3)

**Intra-phase:**
- Phase 1: Steps 1.1-1.3 sequential (registry → parser → integration)
- Phase 1: Step 1.4 (caching) can follow 1.1 but benefits from integration testing feedback
- Phase 2: All steps independent (different skill files, same protocol text from design)
- Phase 3: Steps 3.1-3.3 parallel (different test modules), 3.4 depends on 3.1-3.3, 3.5 independent (corpus-based)

## Parallelization Opportunities

**Phase 2:** All 6 skill modifications can be done in parallel (different files, no shared state)

**Phase 3:** Unit test modules (3.1-3.3) can be implemented in parallel

**Phase 4:** Documentation updates can run in parallel with Phase 3

## Expansion Guidance

The following recommendations should be incorporated during full runbook expansion:

**Consolidation candidates:**
- Steps 2.1-2.3 (/design, /plan-adhoc, /plan-tdd) share identical pattern: add frontmatter, add protocol, remove hardcoded tail-call. Consider merging into single step with per-skill sub-tasks. Note: 2.1 also needs `Skill` added to allowed-tools.
- Phase 4 (3 doc steps, all Low complexity) is a strong merge candidate with adjacent work. Consider inlining 4.1-4.3 as a single documentation step at end of Phase 3.
- Step 1.4 (registry caching) could inline into 1.1 if registry builder naturally includes caching.

**Cycle expansion:**
- Phase 1 cycles should reference design sections D-1 (hook as parsing layer), D-6 (parsing strategy), D-7 (prose-to-explicit). Each cycle should include the specific design section for implementation guidance.
- Phase 2 cycles should embed the exact consumption protocol text from design "Consumption Protocol" section. Protocol text is verbatim, not interpreted.
- Step 3.5 (empirical validation) needs its own cycle with clear procedure: extract prompts, run parser, classify results, report metrics. Reference D-7 validation protocol.

**Checkpoint guidance:**
- Phase 1 -> Phase 2 boundary: Verify hook outputs correct additionalContext JSON for all 3 modes before proceeding to skill modifications.
- Phase 2 -> Phase 3 boundary: Verify all 6 skill files have correct frontmatter YAML and protocol sections. Run `just precommit` to catch formatting issues.
- Phase 3.4 (integration test) serves as natural system checkpoint before empirical validation.

**References to include:**
- Design "Affected skills and their current tail-call locations" section (line references for each skill's hardcoded tail-call)
- Design "Skills requiring Skill tool addition" — /design and /orchestrate specifically
- Design "Handoff --commit Special Case" for Step 2.5 implementation
- Design "additionalContext Format" for Phase 1.3 integration work

**Design ordering note:**
- Design recommends: frontmatter first -> skill protocol -> hook -> tests -> docs -> empirical validation
- Outline orders: hook first -> skills -> tests -> docs
- Both orderings are safe (frontmatter is inert without hook, protocol is no-op without hook injecting continuations). Outline ordering is implementation-natural (build infrastructure consumers depend on first).

**Model assignments:**
- Phase 2 requires sonnet (interpreting design intent for protocol text, not mechanical edits)
- Phase 3.1-3.3 can use haiku (standard test implementation)
- Phase 3.4-3.5 require sonnet (integration logic, corpus analysis)
