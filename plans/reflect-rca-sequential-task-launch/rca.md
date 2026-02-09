# RCA: Sequential Task Launch Instead of Parallel Batching

**Date:** 2026-02-08
**Session:** Plugin migration runbook vet reviews
**Deviation:** Agent launched Phase 1 vet review sequentially, then attempted Phase 2 before launching remaining phases in parallel

## Executive Summary

Agent read 6 phase files in parallel (correct batching), but then launched vet review tasks sequentially instead of batching all 6 Task invocations in a single message. User interrupted with "parallelize" after Phase 1 completed and Phase 2 started. Root cause: behavioral default to sequential pattern + tool batching rule doesn't explicitly cover Task tool parallelization.

**Impact:** Unnecessary wall-clock delay (sequential vs parallel execution)

**Fix Required:** Update `tool-batching.md` to explicitly cover Task tool, add learning

## Timeline

1. **Initial context load:** Agent read all 6 phase files in parallel (6 Read calls in single message) ✓
2. **Sequential launch begins:** Launched only Phase 1 vet review
3. **Phase 1 completes:** Review found 4 issues, report written
4. **Phase 2 starts:** Agent stated "Phase 2 running in background" and began preparing Phase 3-6
5. **User interrupts:** "parallelize" command issued
6. **Attempted correction:** Agent tried to launch Phase 3-6 in parallel (rejected by user)
7. **User invokes /reflect:** RCA session begins

## Deviation Details

### What Happened

**Observed behavior:**
```
Message 1: Read phase-1.md, phase-2.md, ..., phase-6.md (parallel) ✓
Message 2: Task(vet-fix-agent, phase-1) (sequential) ✗
Message 3: After phase-1 complete, Task(vet-fix-agent, phase-2, run_in_background=true) (sequential) ✗
Message 4: Prepare to launch phase-3 through phase-6 (interrupted by user)
```

**Expected behavior:**
```
Message 1: Read phase-1.md, phase-2.md, ..., phase-6.md (parallel) ✓
Message 2: Task(vet-fix-agent, phase-1)
           Task(vet-fix-agent, phase-2)
           Task(vet-fix-agent, phase-3)
           Task(vet-fix-agent, phase-4)
           Task(vet-fix-agent, phase-5)
           Task(vet-fix-agent, phase-6)
           (all 6 in single message) ✓
```

### Violated Rules

**Primary violation: Tool batching**
- File: `agent-core/fragments/tool-batching.md`
- Section: "Execution phase"
- Rule: "Different files: Edit in parallel when independent"
- Interpretation gap: Does this generalize to Task tool? Not explicitly stated.

**Secondary context: Parallel execution preference**
- Multiple learnings reference parallel agent dispatch
- Session management patterns emphasize parallel worktree setup
- Implication: System values parallel execution when possible

## Root Cause Analysis

### Proximal Cause

**Sequential thinking despite parallel capability.**

The agent identified 6 independent review tasks but defaulted to launching them one at a time. This occurred despite:
- All input files already loaded (context established)
- Identical operation for each task (same prompt template, different file path)
- No dependencies between reviews (Phase 1 doesn't block Phase 2)
- Explicit session context emphasizing parallelism (worktree commands, tool batching)

### Contributing Factors

1. **Tool batching rule scope limitation:**
   - Current rule focuses on Read/Edit operations
   - Task tool parallelization is implied but not explicit
   - Extension principle not documented: "If you batch Reads, you should also batch Tasks"

2. **Anchor task completion pattern:**
   - Phase 1 vet review completed successfully
   - Provided positive reinforcement for sequential pattern
   - Agent saw success and continued same approach for Phase 2

3. **Parallel execution mindset break:**
   - Agent correctly batched 6 Read calls in first message
   - Did not maintain parallel mindset when transitioning to delegation phase
   - Mental model shift: "load context" (parallel) → "execute tasks" (sequential)

4. **Missing explicit trigger:**
   - User prompt said "execute the first pending task" (vet expanded phases)
   - Task description mentioned "retroactive vet of phases 1-6"
   - No explicit "parallelize" instruction until after deviation occurred

### Why This Matters

**Wall-clock time impact:**
- Sequential: 6 × avg_review_time (e.g., 6 × 3 min = 18 min)
- Parallel: max(6 review times) (e.g., ~3-4 min)
- Cost: ~14 min unnecessary delay

**Pattern risk:**
- If sequential becomes default, future multi-task operations will have same issue
- Compounds across sessions (each session wastes time)

## Rule Gap Analysis

### Current State

**`tool-batching.md` current scope:**
- ✓ Read tool parallelization (explicit)
- ✓ Edit tool parallelization for different files (explicit)
- ✓ Edit sequencing for same file (explicit)
- ✗ Task tool parallelization (not mentioned)

**Ambiguity:**
- "Different files: Edit in parallel when independent"
- Does "files" generalize to "tasks/agents/operations"?
- Should reader infer extension principle?

### Proposed Fix

**Add Task tool section to `tool-batching.md`:**

```markdown
## Task Tool Parallelization

**Rule:** Launch all independent Task agents in a single message.

**When to batch Task calls:**
- Multiple agents performing similar operations (e.g., vet reviews of different files)
- No dependencies between tasks (Task A doesn't need Task B's output)
- All task prompts are ready (no waiting for earlier results)

**Example: Vet 6 phase files in parallel**
```
Message with 6 Task tool calls:
  Task(vet-fix-agent, "Review phase-1.md")
  Task(vet-fix-agent, "Review phase-2.md")
  Task(vet-fix-agent, "Review phase-3.md")
  Task(vet-fix-agent, "Review phase-4.md")
  Task(vet-fix-agent, "Review phase-5.md")
  Task(vet-fix-agent, "Review phase-6.md")
```

**Anti-pattern: Sequential launch**
```
Message 1: Task(vet-fix-agent, "Review phase-1.md")
Wait for completion...
Message 2: Task(vet-fix-agent, "Review phase-2.md")
Wait for completion...
(repeats for remaining phases)
```

**Rationale:** Parallel execution minimizes wall-clock time. Sequential launch wastes time waiting for each task to complete before launching the next.
```

## Learning Entry

**Anti-pattern:** Sequential Task launch for independent operations
- Launching vet reviews one at a time (Phase 1 → wait → Phase 2 → wait...)
- Breaks parallelism despite all inputs ready and no dependencies

**Correct pattern:** Batch all independent Task calls in single message
- After reading all phase files, launch all 6 vet reviews in one message
- Maximize parallelism (wall-clock time = max(task_times), not sum)

**Rationale:** Tool batching applies to Task tool same as Read/Edit — when operations are independent, execute in parallel to minimize latency

## Fix Tasks

### Immediate Fixes

1. **Update `agent-core/fragments/tool-batching.md`:**
   - Add "Task Tool Parallelization" section
   - Include explicit example (vet 6 files)
   - Show anti-pattern (sequential launch) vs correct pattern (parallel batch)

2. **Append learning to `agents/learnings.md`:**
   - Anti-pattern / correct pattern / rationale format
   - Reference tool-batching.md for Task tool guidance

3. **Verify memory index:**
   - Check if tool batching entry mentions Task tool
   - Update if needed to reflect expanded scope

### Optional Enhancements

4. **Create hookify rule candidate:**
   - Detect: Multiple Task calls across multiple messages when inputs are ready
   - Warn: "Consider batching all Task calls in single message"
   - Trade-off: Hook overhead vs value (may not be worth it for rare pattern)

5. **Review orchestrate skill:**
   - Check if orchestrator patterns encourage parallel agent launch
   - Ensure no sequential bias in skill content

## Prevention

**Short term:**
- Apply fixes above (tool-batching.md update + learning)
- Tool-batching rule now explicitly covers Task tool

**Long term:**
- Monitor for sequential Task patterns in future sessions
- If pattern recurs, consider structural intervention (hook or template)

## Conclusion

Root cause is behavioral default to sequential execution when tool batching rule doesn't explicitly cover Task tool. Fix is straightforward: extend tool-batching.md to include Task tool section with explicit examples. Learning captures the pattern for future reference.

**Status:** RCA complete, ready for fix implementation in separate session
