# Context Overview Module

---
author_model: claude-opus-4-5-20251101
semantic_type: project_context
expansion_sensitivity: low
target_rules:
  strong: 3-4
  standard: 4-6
  weak: 6-8
---

## Semantic Intent

Provide agent with project purpose and architecture context. This module gives the
"why" and "what" without implementation details.

---

## Project Overview

### Purpose

Extract user feedback from Claude Code conversation history for retrospective analysis.
This enables learning from agent-user interactions to improve agent behavior.

### Architecture

Python CLI tool with two subcommands:

- `list` - Show top-level conversation sessions with titles
- `extract` - Extract user feedback recursively from a session

### Implementation Approach

Test-Driven Development (TDD) with pytest. Discrete implementation steps, each
validated by tests before proceeding.

---

## Key Technologies

- Python 3.14+ with full type annotations (mypy strict mode)
- Pydantic for data validation and serialization
- uv for dependency management (not pip)
- pytest for testing
- ruff for linting and formatting
- just for task running
