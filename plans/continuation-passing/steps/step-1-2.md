# Step 1.2

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.2: Implement Continuation Parser (Modes 1-3)

**Objective:** Parse user input to detect skill references and build continuation chain.

**Execution Model:** Sonnet

**Implementation:**

Create parser function that handles three modes:

**Mode 1 — Single skill (no continuation):**
- Input contains exactly one `/skill` reference
- No other registered skills detected
- Append skill's default exit to continuation

**Example:**
```
Input: "/design plans/foo"
→ current: {skill: "design", args: "plans/foo"}
→ continuation: ["/handoff --commit", "/commit"]
```

**Mode detection order** (resolves ambiguity when patterns overlap):
1. Check Mode 3 pattern first: `and\n- /skill` (more specific)
2. Check Mode 2 pattern: inline `, /` or connecting words (more general)
3. First match wins

**Mode 2 — Inline prose (FR-1, FR-3):**
- Multiple `/skill` references on one line
- Delimiters: `, /` or connecting words (`and`, `then`, `finally`) before `/skill`
- Split into current + continuation

**Example:**
```
Input: "/design plans/foo, /plan-adhoc and /orchestrate"
→ current: {skill: "design", args: "plans/foo"}
→ continuation: [{skill: "plan-adhoc"}, {skill: "orchestrate"}]
```

**Mode 3 — Multi-line list (FR-4):**
- Pattern: `and\n- /skill args` (exact pattern: connecting word + newline + list marker)
- `and` keyword on first line signals continuation
- Subsequent `- /skill` lines are entries

**Example:**
```
Input: "/design plans/foo and
- /plan-adhoc design.md
- /orchestrate foo"
→ current: {skill: "design", args: "plans/foo"}
→ continuation: [{skill: "plan-adhoc", args: "design.md"}, {skill: "orchestrate", args: "foo"}]
```

**Disambiguation (D-7):**
- Scan input for `/word` patterns
- Match each against cooperative registry
- Only registered skills recognized as continuation entries
- Path arguments like `/plans/foo/bar` won't match (not in registry)
- Connecting words in args (e.g., "design and implement") ignored unless followed by registered skill

**Default exit appending (D-3):**
- Identify last skill in chain (user's chain or current skill if solo)
- Look up last skill's `default_exit` from registry
- Append default exit entries to continuation
- Special case: `/handoff` without `--commit` flag is terminal (no default exit)

**Examples:**
```
User: "/design plans/foo"
Last skill: design
Default exit: ["/handoff --commit", "/commit"]
Full chain: ["/handoff --commit", "/commit"]

User: "/design, /plan-adhoc"
Last skill: plan-adhoc
Default exit: ["/handoff --commit", "/commit"]
Full chain: ["/plan-adhoc", "/handoff --commit", "/commit"]

User: "/handoff"
Last skill: handoff (no --commit flag)
Default exit: [] (terminal)
Full chain: [] (terminal)

User: "/commit"
Last skill: commit
Default exit: [] (terminal)
Full chain: [] (terminal)
```

**Mid-chain /handoff without --commit flag:**
- If `/handoff` (no `--commit`) appears mid-chain, user-specified continuation is preserved
- Example: `/design, /handoff, /commit` → chain is `[/handoff, /commit]`
- Rationale: User explicitly specified `/commit`, so `/handoff` terminal default doesn't apply
- Only solo `/handoff` invocation uses empty default exit

**Function signature:**
```python
def parse_continuation(prompt: str, registry: dict) -> Optional[dict]:
    """Parse prompt for continuation.

    Returns:
        None if no skill detected (pass-through)
        {
            "current": {"skill": str, "args": str},
            "continuation": [{"skill": str, "args": str}, ...]
        }
    """
```

**Expected Outcome:**

Parser correctly identifies skill references, splits into current + continuation, and appends default exits.

**Unexpected Result Handling:**
- No registered skills found → return None (silent pass-through)
- Ambiguous parse → resolved by mode detection order (Mode 3 checked first)
- Malformed input → return None (pass-through)
- Empty continuation after default exit appending → return empty list (terminal)

**Validation:**
- Single skill: `/design plans/foo` → continuation = default exit only
- Inline prose: `/design, /plan-adhoc` → correct split
- Multi-line: `and\n- /skill` pattern → correct entries
- Path args: `/design /plans/foo/bar` → path not treated as skill
- Connecting words: "design and implement" → not a continuation
- Flag handling: `/handoff --commit` → parser detects flag, registry returns `["/commit"]` for handoff+flag
- Mid-chain handoff: `/design, /handoff, /commit` → user-specified `/commit` preserved
- Unknown skill: `/design, /nonexistent` → nonexistent ignored
- Terminal skill: `/commit` → empty continuation

**Success Criteria:**
- All 8 test scenarios from design Component 4 pass
- Registry disambiguation works (paths and prose ignored)
- Default exits appended correctly

**Report Path:** `plans/continuation-passing/reports/step-1-2-execution.md`

---
