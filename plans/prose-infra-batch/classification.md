# Prose Infrastructure Batch — Classification

## FR-1: Remove opus-design-question skill
- **Classification:** Simple
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** No
- **Work type:** Production
- **Artifact destination:** agentic-prose

## FR-2: Magic-query skill
- **Classification:** Moderate
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** No
- **Work type:** Production (agentic-prose)
- **Artifact destination:** agentic-prose

## FR-3: Handoff merge-incremental fix
- **Classification:** Moderate
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** Yes — changes conditional logic
- **Work type:** Production (agentic-prose)
- **Artifact destination:** agentic-prose

## FR-4a: Rule fragment
- **Classification:** Simple
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** No
- **Work type:** Production (agentic-prose)
- **Artifact destination:** agentic-prose

## FR-4b: Validator
- **Classification:** Moderate
- **Implementation certainty:** High
- **Requirement stability:** High
- **Behavioral code check:** Yes — new function with conditional logic
- **Work type:** Production
- **Artifact destination:** production (src/claudeutils/validation/)

## Routing
- FR-1, FR-2, FR-3, FR-4a: agentic-prose → /inline
- FR-4b: production → /runbook (TDD)
- Batch routing: /runbook (coordinates commit+restart constraint C-1)
