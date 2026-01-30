---
name: batch-edit-reminder
enabled: true
event: file
action: warn
conditions:
  - field: file_path
    operator: regex_match
    pattern: agent-core/(skills|fragments|agents)/
---

**[Tool Batching Required]** You are editing a file in agent-core/ where changes typically span multiple files.

BEFORE proceeding with individual edits:
- Have you identified ALL files that need changes for this task?
- Are you executing ALL edits in a SINGLE parallel batch?
- If this is one edit in a multi-file task, STOP and plan ALL edits first, then execute them all in one message.

Required pattern: Read all files → Plan all edits → Execute all in one batch.
Do NOT make sequential single-file edits across multiple messages.
