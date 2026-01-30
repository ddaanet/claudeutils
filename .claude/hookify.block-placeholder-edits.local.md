---
name: block-placeholder-edits
enabled: true
event: file
action: warn
conditions:
  - field: new_text
    operator: regex_match
    pattern: (TODO|FIXME|PLACEHOLDER|HACK|XXX|STUB).*\b(later|next|step|phase|batch)\b
---

**[Incomplete Edit Detected]** This edit contains placeholder markers suggesting incremental work.

This pattern indicates you may be making changes piecemeal across multiple messages rather than planning and executing all changes in a single batch.

STOP. Before continuing:
- Plan ALL remaining changes for this task
- Execute ALL edits in ONE parallel batch
- No placeholder content — implement fully or don't edit yet
