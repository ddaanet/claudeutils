# Classification: UserPromptSubmit Topic Injection

- **Classification:** Complex
- **Implementation certainty:** Moderate — scoring algorithm has multiple valid approaches (keyword overlap vs TF-IDF vs BM25) requiring `/ground` research. Integration architecture clear, calibration uncertain.
- **Requirement stability:** High — 7 FRs mechanism-specified with acceptance criteria, 2 NFRs measurable, 3 constraints explicit
- **Behavioral code check:** Yes — new functions (index builder, matcher, resolver wrapper, cache manager), new logic paths (matching tier), conditional branches (cache hit/miss, threshold filtering, code block handling)
- **Work type:** Production — delivers ambient recall injection to agents
- **Artifact destination:** production (`src/` for matching module, `agent-core/hooks/` for integration)
- **Evidence:** Requirements explicitly call for `/ground` research during A.1 (scoring algorithm). Multi-component system (parse→index→match→resolve→cache→inject→feedback) across `src/` and `agent-core/hooks/`. Token budget calibration deferred to design (C-3). Two open questions on edge case behavior.
