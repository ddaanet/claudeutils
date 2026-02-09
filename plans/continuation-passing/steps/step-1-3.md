# Step 1.3

**Plan**: `plans/continuation-passing/runbook.md`
**Execution Model**: haiku
**Phase**: 1

---

## Step 1.3: Integrate Tier 3 into Existing Hook

**Objective:** Wire continuation parser into userpromptsubmit-shortcuts.py as Tier 3.

**Execution Model:** Sonnet

**Implementation:**

**Tier processing order:**
1. **Tier 1:** Exact match shortcuts (`s`, `x`, `xc`, `r`, `h`, `hc`, `ci`, `?`) — unchanged
2. **Tier 2:** Directive shortcuts (`d:`, `p:`) — unchanged
3. **NEW — Tier 3:** Continuation parsing — if input contains registered skills

**Tier 3 logic:**

```python
# After Tier 1 and Tier 2 checks fail
registry = build_registry()  # Step 1.1 function
parsed = parse_continuation(prompt, registry)  # Step 1.2 function

if parsed is None:
    # No registered skills found
    sys.exit(0)  # Silent pass-through

# Build additionalContext JSON
continuation_entries = [
    f"/{entry['skill']}" + (f" {entry['args']}" if entry.get('args') else "")
    for entry in parsed['continuation']
]
continuation_str = ", ".join(continuation_entries)

current_skill = f"/{parsed['current']['skill']}"
current_args = parsed['current'].get('args', '')
if current_args:
    current_skill += f" {current_args}"

additional_context = f"""[CONTINUATION-PASSING]
Current: {current_skill}
Continuation: {continuation_str}

After completing the current skill, invoke the NEXT continuation entry via Skill tool:
  Skill(skill: "{parsed['continuation'][0]['skill']}", args: "{parsed['continuation'][0].get('args', '')} [CONTINUATION: {', '.join(continuation_entries[1:])}]")

Do NOT include continuation metadata in Task tool prompts."""

output = {
    'hookSpecificOutput': {
        'hookEventName': 'UserPromptSubmit',
        'additionalContext': additional_context
    }
    # No systemMessage — continuation is internal to Claude
}
print(json.dumps(output))
```

**Design reference:** D-2 specifies `additionalContext` format (prose with structured prefix, not raw JSON).

**Key integration points:**
- Tier 3 fires only when Tiers 1/2 don't match
- Requires registry from Step 1.1
- Requires parser from Step 1.2
- No output change for non-skill input (silent pass-through preserved)

**Expected Outcome:**

Hook emits `additionalContext` JSON when skill references detected. No output for non-skill input.

**Unexpected Result Handling:**
- Registry build fails → log warning, fall through to silent pass-through
- Parser raises exception → log error, fall through to silent pass-through
- Empty continuation after parsing → emit terminal format

**Terminal continuation format:**
```json
{
  "hookSpecificOutput": {
    "hookEventName": "UserPromptSubmit",
    "additionalContext": "[CONTINUATION-PASSING]\nCurrent: /commit\nContinuation: (empty)\n\nSkill is terminal. No tail-call needed."
  }
}
```

**Validation:**
- Tier 1 shortcuts still work (`s`, `x`, etc.)
- Tier 2 directives still work (`d:`, `p:`)
- Non-skill input passes through silently
- Skill input emits correct `additionalContext`
- Single-skill invocation includes default exit

**Success Criteria:**
- All existing hook behavior preserved
- Continuation metadata injected for skill inputs
- `additionalContext` format matches design specification (D-2)
- No `systemMessage` emitted (continuation is internal)

**Report Path:** `plans/continuation-passing/reports/step-1-3-execution.md`

---
