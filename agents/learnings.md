# Learnings

Institutional knowledge accumulated across sessions. Append new learnings at the bottom.

**Soft limit: 80 lines.** When approaching this limit, use `/remember` to consolidate older learnings into permanent documentation (behavioral rules → `agent-core/fragments/*.md`, technical details → `agents/decisions/*.md` or `agents/decisions/implementation-notes.md`). Keep the 3-5 most recent learnings for continuity.

---
## Tool batching unsolved
- Documentation (tool-batching.md fragment) doesn't reliably change behavior
- Direct interactive guidance is often ignored
- Hookify rules add per-tool-call context bloat (session bloat)
- Cost-benefit unclear: planning tokens for batching may exceed cached re-read savings
- Pending exploration: contextual block with contract (batch-level hook rules)
## Memory index consumption pattern
- Anti-pattern: Skills instructing agents to "scan memory-index.md" (causes grepping already-loaded content)
- Correct pattern: Memory index is loaded via CLAUDE.md @-reference — scan mentally, then Read referenced files
- Fix: Updated plan-tdd, plan-adhoc skills to say "check loaded memory-index context"
- Structure: Sections grouped by target file, file path in heading not per-entry
## Decision file size not enforced
- Current state: architecture.md (821 lines), workflows.md (886 lines) exceed soft 400-line limit
- Line-limits check only applies to Python source (`src/`, `tests/`), not markdown
- Pending: Split large decision files or extend enforcement
## Structural header dot syntax
- Anti-pattern: `.## Title` (dot before markdown marker)
- Correct pattern: `## .Title` (dot is part of title text, after `## `)
- Fix: Added explicit ✅/❌ examples to implementation-notes.md
- Rationale: "Prefix" is ambiguous — examples prevent misinterpretation
## Hard limits vs soft limits
- Anti-pattern: Validators that print warnings but don't fail build
- Correct pattern: Either fail build (hard error) or don't check (no validation)
- Rationale: "Normalize deviance" principle — warnings create false sense of compliance
- Example: memory-index word count changed from warning to hard error, exposed 62 violations
- Trade-off: Hard limits force immediate resolution but may need tuning (word count 8-12 may be too strict)
## Organizational sections and index pollution
- Anti-pattern: Index entries pointing to organizational sections (H2 with only H3 subsections)
- Correct pattern: Mark organizational sections structural (`.` prefix), autofix removes corresponding entries
- Judgment location: Decision happens at source (decision file), not at index — once structural, removal is automatic
- Recursive rule: Applies at all heading levels (H2, H3, H4) — any heading with no direct content before sub-headings
## Index entry key preservation
- Anti-pattern: Shortening index entry by changing key (part before em-dash)
- Correct pattern: Shorten description (after em-dash), preserve key exactly as header title
- Rationale: Validator matches index keys to decision file headers — changed key = orphan entry error
- Example: "Never auto-commit in interactive sessions — ..." → keep full key, shorten description only
## Batch edit token efficiency
- Marker format (`<<<` `>>>` `===`) saves 13% tokens vs JSON
- No quotes, braces, colons, or escaping needed
- Multi-line content handled naturally without escaping
- Script location: `agent-core/bin/batch-edit.py`
