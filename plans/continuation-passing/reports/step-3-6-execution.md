# Step 3.6: Create Continuation Passing Fragment

**Status:** Complete

## Deliverable

Created `agent-core/fragments/continuation-passing.md` — protocol reference for skill developers.

## Content

- Protocol overview with system flow diagram
- Frontmatter schema (`continuation:` block with `cooperative` and `default-exit` fields)
- Consumption protocol template (~5-8 lines replacing hardcoded tail-calls)
- Transport format specification (additionalContext for first invocation, `[CONTINUATION: ...]` suffix for subsequent)
- Sub-agent isolation requirement (convention-based, no continuation in Task prompts)
- Cooperative skills table with default-exit chains
- Guide for adding continuation support to new skills

## Architecture Alignment

Fragment reflects post-architecture-change state:
- Single skills pass through (hook returns None)
- Skills manage own default-exit at runtime
- Hook only activates for multi-skill chains

## Index

Added 4 entries to `agents/memory-index.md` under new `agent-core/fragments/continuation-passing.md` section. Fragment is NOT @-referenced in CLAUDE.md (reference material, not always-loaded).

## Prerequisite

Updated `plans/continuation-passing/design.md` to reflect architecture changes:
- D-1: Added "multi-skill only" qualifier and architecture change note
- D-3: Rewrote to "default exit ownership" — skills manage own default-exit
- D-6: Removed Mode 1, updated to two parsing modes
- Updated parser logic, additionalContext format, frontmatter field descriptions
