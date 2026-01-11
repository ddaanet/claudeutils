# Quick Reference: Context Handoff Implementation Examples

---

## 1. Basic SessionStart Hook (Load Previous Context)

**File:** `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'if [ -f .claude/handoff.md ]; then echo \"=== LOADING PREVIOUS SESSION ===\"  && cat .claude/handoff.md && echo \"\"; fi'"
          }
        ]
      }
    ]
  }
}
```

**What it does:**
- Automatically displays previous handoff file if it exists
- Output is injected into Claude's context automatically
- User sees what was previously completed and what's pending

---

## 2. Basic SessionEnd Hook (Save Context)

**File:** `.claude/settings.json`

```json
{
  "hooks": {
    "SessionEnd": [
      {
        "matcher": "any",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'mkdir -p .claude/session-history && cp .claude/handoff.md .claude/session-history/session-$(date +%Y%m%d-%H%M%S).md 2>/dev/null || true'"
          }
        ]
      }
    ]
  }
}
```

**What it does:**
- Archives previous handoff to timestamped file
- Preserves history for reference
- Allows reviewing multiple session summaries

---

## 3. Smart Handoff Template

**File:** `.claude/handoff.md` (created at session end)

```markdown
# Session Handoff - 2026-01-11 14:30 UTC

## ✅ Completed This Session
- Researched context management mechanisms (5 major categories identified)
- Created CONTEXT_MANAGEMENT_RESEARCH.md (comprehensive reference)
- Analyzed hook systems, MCP notifications, handoff protocols
- Reviewed claude-mem and Continuous-Claude implementations
- Collected official documentation links and GitHub issues

## ⏳ Pending for Next Session
- [ ] Implement SessionStart/SessionEnd hooks in project
- [ ] Test handoff.md auto-generation with actual agent
- [ ] Evaluate claude-mem plugin integration
- [ ] Set up token-budget-monitor skill for warnings
- [ ] Document in AGENTS.md when to trigger handoffs

## 📝 Context Notes
- **Key Decision**: Use hook-based approach + claude-mem for maximum compatibility
- **Blocker Found**: SessionStart hooks don't work for brand new conversations (GitHub #10373)
- **Important Pattern**: Handoff files reduce 10K+ tokens to ~1-2K tokens
- **Recommendation**: Trigger handoff at 70% context usage, not 95%

## 📂 Key Files
- `/home/user/claudeutils/CONTEXT_MANAGEMENT_RESEARCH.md` - Full research document
- `/home/user/claudeutils/AGENTS.md` - Agent system configuration
- `/home/user/claudeutils/START.md` - Handoff entry point

## 🎯 Next Steps
1. Create .claude/settings.json with SessionStart/SessionEnd hooks
2. Install claude-mem plugin for automatic context preservation
3. Test hook execution with `/clear` command (known working path)
4. Create monitoring dashboard for token usage at 70%, 85%, 95% thresholds
5. Document handoff procedure in AGENTS.md for team consistency

## ⚠️ Critical Notes
- Do NOT rely on context warnings after 95% (too late)
- SessionStart hooks are broken for new conversations - use `/clear` workaround
- Token budget warnings are excessive (100+ in one session) - may need disabling
- MCP notifications can't reliably trigger agent actions - use in-context budgets instead
```

---

## 4. Python Agent SDK Session Handoff

**Resuming a Previous Session:**

```python
from claude_agent_sdk import query, ClaudeAgentOptions
import json

# Load previous session ID from handoff file
with open(".claude/handoff.md", "r") as f:
    content = f.read()
    # Parse session_id from handoff (you'll need custom parsing)

# Resume the session
session_id = "session-abc123"
async for message in query(
    prompt="Continue from where we left off. Focus on the pending authentication system.",
    options=ClaudeAgentOptions(
        resume=session_id,
        model="claude-sonnet-4-5",
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep", "Bash"]
    )
):
    print(message)
```

**Creating a Session Fork (for alternative approach):**

```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Fork into a new session to try different approach
async for message in query(
    prompt="Let's refactor this with GraphQL instead. Keep the same database schema.",
    options=ClaudeAgentOptions(
        resume="session-abc123",
        fork_session=True,  # Creates branched session
        model="claude-sonnet-4-5"
    )
):
    print(message)
```

---

## 5. Monitoring Context Budget (Claude 4.5)

**In-Code Context Tracking:**

```python
# Claude receives this automatically at conversation start:
# <budget:token_budget>200000</budget:token_budget>

# After each tool call, Claude sees:
# <system_warning>Token usage: 140000/200000; 60000 remaining</system_warning>

# Agent should check remaining budget and act:
remaining_tokens = 60000
threshold_danger = 200000 * 0.10  # 20% = 40K tokens
threshold_warning = 200000 * 0.15  # 15% = 30K tokens

if remaining_tokens < threshold_danger:
    # Trigger handoff immediately
    print("CRITICAL: Approaching context limit. Creating handoff now.")
elif remaining_tokens < threshold_warning:
    # Warn but continue
    print(f"WARNING: {remaining_tokens} tokens remaining. Plan to handoff soon.")
```

---

## 6. Complete Settings with All Hooks

**File:** `.claude/settings.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'test -d .claude && [ -f .claude/handoff.md ] && echo \"Previous context:\" && cat .claude/handoff.md || echo \"No previous handoff found.\"'"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": "any",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'mkdir -p .claude/logs && date >> .claude/logs/prompts.log && echo \"$CLAUDE_PROMPT\" >> .claude/logs/prompts.log'"
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "any",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'if [ \"$CLAUDE_TOOL\" = \"Write\" ] || [ \"$CLAUDE_TOOL\" = \"Edit\" ]; then git add \"$CLAUDE_TOOL_INPUT_PATH\" 2>/dev/null || true; fi'"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "exit",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'mkdir -p .claude/session-history && if [ -f .claude/handoff.md ]; then cp .claude/handoff.md .claude/session-history/handoff-$(date +%Y%m%d-%H%M%S).md; fi'"
          }
        ]
      }
    ]
  }
}
```

---

## 7. Monitoring Token Usage Manually

**Bash Command for Token Check:**

```bash
# View current token usage
claude /context

# Expected output pattern:
# Token usage: 120000/200000 (60% used)
# Remaining: 80000 tokens
```

**Recommended Actions by Percentage:**

| Usage | Status | Action |
|-------|--------|--------|
| 0-70% | Safe | Continue normally |
| 70-80% | Caution | Plan to wrap up or create handoff |
| 80-90% | Alert | Start aggressive context reduction |
| 90-95% | Critical | Must create handoff NOW |
| 95%+ | Danger | Auto-compact triggers (data loss risk) |

---

## 8. Token-Budget-Monitor Skill Configuration

**Installation:**

```bash
# In Claude Code session:
/plugin marketplace add mapachekurt/claude-skills
# Find and install token-budget-monitor
```

**Configuration (if available):**

```json
{
  "tokenBudgetMonitor": {
    "enabled": true,
    "warningThresholds": [70, 85, 95],
    "checkFrequency": "after-every-tool",
    "alertMode": "progressive",  // Changes from info → warning → urgent
    "autoSummarizeAt": 85,
    "autoHandoffAt": 95
  }
}
```

---

## 9. claude-mem Plugin Setup

**Installation:**

```bash
# In Claude Code session:
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
# Restart Claude Code
```

**Automatic Behavior:**

```
Session 1: Work on feature
  → claude-mem captures observations
  → AI summarizes work
  → Saves to ~/.claude-mem/claude-mem.db

Session 2: Open project
  → SessionStart hook triggers
  → claude-mem injects summary from Session 1
  → "Claude remembers architecture, file changes, recent edits"
```

**Configuration (at ~/.claude-mem/settings.json):**

```json
{
  "aiModel": "claude-sonnet-4-5",
  "workerPort": 37777,
  "dataDirectory": "~/.claude-mem",
  "logLevel": "info",
  "contextInjection": {
    "enabled": true,
    "numSessions": 10,
    "maxTokens": 5000
  }
}
```

---

## 10. Graceful Degradation Pattern

**Agent Logic for Context Limits:**

```python
def handle_context_limit(remaining_tokens: int, total_tokens: int = 200000):
    """Gracefully handle approaching context limits"""

    percentage = (remaining_tokens / total_tokens) * 100

    if percentage > 80:
        # Normal operation
        return "continue"

    elif percentage > 60:
        # Start consolidating
        return "consolidate_progress"

    elif percentage > 40:
        # Stop non-critical operations
        return "wrap_up_critical_only"

    elif percentage > 20:
        # Maximum compression
        return "generate_handoff"

    else:
        # Imminent failure
        return "emergency_summarize_and_exit"

# Usage:
action = handle_context_limit(remaining_tokens=45000, total_tokens=200000)
if action == "generate_handoff":
    # Create .claude/handoff.md
    # Summarize pending work
    # Prepare for session exit
```

---

## 11. Testing Hook Execution

**Known Working Paths (GitHub #10373):**

```bash
# SessionStart hooks WORK for these operations:
claude /clear                    # ✓ Works
claude /compact                  # ✓ Works
claude --resume <session-url>    # ✓ Works

# SessionStart hooks DON'T work for:
claude                          # ✗ Brand new conversation
claude <new-prompt>             # ✗ New prompts
```

**Workaround for New Sessions:**

```bash
# Instead of starting with new conversation:
claude /clear   # Triggers SessionStart hooks correctly
# Then continue work
```

---

## 12. Emergency Context Reset

**When Everything Fails:**

```bash
# Compact the conversation
claude /compact focus on implementation status

# If that fails, start fresh:
claude /clear

# Then immediately inject critical context:
cat .claude/handoff.md
# Share the handoff content with Claude manually
```

---

## Summary: Recommended Setup Order

1. **Immediate (15 min):** Set up basic SessionStart hook to load handoff
2. **Day 1 (30 min):** Add SessionEnd hook to archive handoffs
3. **Day 2 (45 min):** Install claude-mem plugin
4. **Day 3 (30 min):** Add token-budget-monitor for proactive warnings
5. **Week 1 (1 hour):** Implement Agent SDK session forking for complex tasks
6. **Ongoing:** Monitor `/context` output before major operations

---

**Generated:** January 11, 2026
**For questions:** See CONTEXT_MANAGEMENT_RESEARCH.md for full details
