# Empirical Research: AI-Assisted Requirements Elicitation

## Sources

- [AI-based Multiagent Approach for Requirements Elicitation (2024)](https://arxiv.org/html/2409.00038v1)
- [AI for Requirements Engineering: Industry Adoption (2025)](https://arxiv.org/html/2511.01324)
- [Requirements Elicitation Techniques Survey (UCBerkeley)](https://eecs481.org/readings/requirements.pdf)
- [GenAI for Requirements Engineering — Systematic Literature Review (Wiley 2026)](https://onlinelibrary.wiley.com/doi/full/10.1002/spe.70029)

## Key Findings

### Human-AI Collaboration Pattern
- 58.2% of practitioners use AI in requirements engineering
- Only 2% believe AI can handle elicitation independently
- 81.2% use human review of AI suggestions; 71.9% allow human override
- Dominant pattern: collaborative partnership, not automation

### AI Strengths in RE
- Structuring and summarizing existing discussions
- Pattern recognition for missing requirements and inconsistencies
- Routine drafting and documentation generation
- Providing clarifying questions and research augmentation

### AI Weaknesses in RE
- Lacks domain expertise and contextual understanding
- Cannot build stakeholder rapport or interpret non-verbal cues
- Produces overly generic outputs from generalized training
- Struggles with novel problems where requirements are uncertain

### Structured vs Unstructured Elicitation
- Semi-structured interviews (predetermined framework + freedom to explore tangents) most effective
- Structured interviews provide consistency; unstructured capture novel requirements
- Semi-structured balances both — validated as most common technique

### Multi-Agent RE Systems
- Specialized roles (Product Owner, QA, Developer, Manager) improve output quality
- 100 Dollar Allocation prioritization most consistent across techniques
- Human feedback rated LLM outputs between satisfactory and good
- Hallucinations remain problematic — human validation essential

## Design Implications

| Finding | Implication for /requirements |
|---------|------------------------------|
| HAIC pattern (58% adoption, 2% autonomous) | Extract + human gap-fill, not autonomous generation |
| AI excels at structuring | Extract mode is the primary value proposition |
| Semi-structured interviews most effective | Elicit mode uses standard sections as framework, adaptive follow-ups |
| 81% human review | Gap-fill presents extracted requirements for user validation |
| AI struggles with novel/ambiguous | Capture Open Questions explicitly rather than inventing requirements |
| Hallucination risk | Extract from conversation (grounded), don't infer unstated requirements |
