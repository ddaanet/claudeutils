## Key User Preferences

### Communication Patterns

#### Tier 1 - Critical (Always Follow)

1. **Stop on unexpected results:** If something fails OR succeeds unexpectedly, describe
   expected vs observed, then STOP and wait for guidance
2. **Wait for explicit instruction:** Do NOT proceed with a plan or TodoWrite list
   unless user explicitly says "continue" or equivalent

#### Tier 2 - Important

**Stop at boundaries:** Complete assigned task then stop (no scope creep)

### Tool Batching

**Planning phase (before any tool calls):**

1. Identify ALL changes needed for the current task
2. Group by file: same-file edits are sequential, different-file edits can be parallel
3. For multi-edit files: list insertion points, plan bottom-to-top order (avoids line
   shifts)

**Execution phase:**

4. **Batch reads:** Read multiple files in one message when needed soon
5. **Different files:** Edit in parallel when independent
6. **Same file:** Edit sequentially, bottom-to-top when inserting
7. **Refresh context:** If you plan to modify a file again in the next iteration, Read
   this file in the batch.
