# Research: Mechanisms for Notifying Agents About Context Accumulation & Session Handoff

**Date:** January 11, 2026
**Focus:** Discovering how running Claude Code agents can be notified about context limits and enabled to hand off to fresh sessions.

---

## Executive Summary

There are **five primary mechanisms** for managing context accumulation and enabling session handoff in Claude Code agents:

1. **Hook-based context management** (SessionStart/SessionEnd)
2. **Native Claude 4.5 context awareness** via `<budget:token_budget>` tags
3. **Structured handoff protocols** (.claude/handoff.md files)
4. **MCP server notifications** for dynamic capability updates
5. **Community implementations** (claude-mem, token-budget-monitor, Continuous-Claude)

---

## 1. Hook-Based Approaches

### SessionStart and SessionEnd Hooks

Claude Code provides lifecycle hooks that execute at session boundaries, enabling automated context management.

**SessionStart Hook:**
- Runs when Claude Code starts a new session or resumes an existing session
- **Key capability**: Can read and inject context from previous sessions
- Can load development context, install dependencies, set environment variables
- Has access to `CLAUDE_ENV_FILE` for persisting environment variables across bash commands
- Output via stdout is automatically added to Claude's context (unlike other hook types)
- Can emit JSON with `hookSpecificOutput.additionalContext` to explicitly inject context

**SessionEnd Hook:**
- Runs when a session ends (cannot block session termination)
- Useful for cleanup, logging statistics, saving session state
- Receives: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `reason` (e.g., "exit")
- Can capture learnings and create handoff documents

**Configuration Location:**
```
~/.claude/settings.json (global)
.claude/settings.json (project-specific)
.claude/settings.local.json (local overrides)
```

**Example Configuration:**
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Check for .claude/handoff.md. If exists: (1) Read and incorporate into session context, (2) Archive to .claude/session-history/, (3) Present summary"
          }
        ]
      }
    ],
    "SessionEnd": [
      {
        "matcher": "any",
        "hooks": [
          {
            "type": "prompt",
            "prompt": "Review current session state. Write .claude/handoff.md with completed tasks, pending tasks, context notes, and next steps."
          }
        ]
      }
    ]
  }
}
```

**Real-World Implementation Examples:**

- **LaunchDarkly Integration**: Uses SessionStart hooks to dynamically fetch repository-specific instructions from LaunchDarkly's AI Agent Config system. Instructions are dynamically injected based on git context (remote URLs, directory names, custom variables).

- **claude-mem Plugin**: Implements 5 lifecycle hooks (SessionStart, UserPromptSubmit, PostToolUse, Summary, SessionEnd) with async AI processing via Express API on port 37777. Automatically injects relevant context from last 10 sessions at SessionStart.

### Known Issues with Hooks

There's a reported issue (GitHub #10373) where SessionStart hooks execute but their output is **not processed** when starting new conversations. Workarounds:
- SessionStart output works correctly for `/clear`, `/compact`, and URL resume operations
- For brand new sessions, hooks may fail silently
- Workaround: Use explicit `/init` commands to rebuild context

---

## 2. Native Claude 4.5 Context Awareness

### Budget Tracking Mechanism

Claude 4.5 models (Sonnet 4.5 and Haiku 4.5) have **context awareness built-in**, enabling the model to track its own remaining context window throughout a conversation.

**How It Works:**

At conversation start, Claude receives:
```
<budget:token_budget>200000</budget:token_budget>
```

After each tool call, Claude receives a system warning with remaining capacity:
```
<system_warning>Token usage: 35000/200000; 165000 remaining</system_warning>
```

**Context Window Limits:**
- **Standard plans**: 200K tokens
- **Claude.ai Enterprise**: 500K tokens
- **Beta (eligible orgs)**: 1M tokens
- Image tokens are included in these budgets

**Recommended Thresholds:**

Users report the following best practices:
- **70% usage (140K tokens)**: Start preparing to wrap up or plan handoff
- **85% usage (170K tokens)**: Implement aggressive context reduction
- **90-95% usage**: Too late - system auto-compaction triggers, may lose critical context

**Critical Problem with Current Approach:**

Users report receiving **100+ context warnings** throughout a conversation (one after every tool use), starting as early as ~20K tokens. This causes Claude to become "afraid of reading files and making changes."

**Workarounds (Partial):**
```bash
export CLAUDE_CODE_ENABLE_TOKEN_USAGE_ATTACHMENT=0
export CLAUDE_CODE_DISABLE_ATTACHMENTS=1  # Also disables system-reminder, session-memory, shell status
```

These are reportedly **ineffective** according to user reports.

---

## 3. Context Limit Notification Patterns

### Automatic Compaction

Claude Code provides **automatic context management** features:

- **Auto-compact trigger**: Occurs around 95% capacity (considered too late by most users)
- **Recommended threshold**: 85-90% capacity for proactive action
- **Command**: `/compact [optional instructions]` - Summarizes conversation while preserving context
- **Command**: `/clear` - Wipes conversation history for fresh start
- **Command**: `/context` - Shows colored grid visualization of token usage

### Smart Handoff Approach

Users report "Smart Handoff" command that:
- Captures both direction AND details before automatic compaction
- Allows resuming exactly where you left off
- Recommended trigger: When context reaches 70-80% usage

### Notification Levels in Third-Party Systems

The **token-budget-monitor** Claude Skill provides tiered warnings:

**70% usage tier:**
```
💡 Token Usage Check: You've used ~X tokens so far (70% of context).
At current pace, you have ~X hours before hitting limits.
Consider: Save important context, prepare to wrap up, or start fresh chat.
```

**85% usage tier:**
```
⚠️ Token Budget Alert: You're at 85% of context window.
Estimated time remaining: ~X hours at current pace.
Action: Finish critical tasks, save context, prepare new conversation.
```

**95% usage tier:**
```
🚨 URGENT - Token Limit Imminent: You're at 95% of context!
IMMEDIATE ACTION:
1. Save any critical information now
2. Wrap up current task
3. Start fresh conversation
4. Copy important context to new chat
```

---

## 4. Structured Session Handoff Protocol

### The `.claude/handoff.md` Standard (Proposed)

A standardized file format for passing context between sessions, proposed in GitHub Issue #11455:

**File Location:** `.claude/handoff.md` (gitignored by default, optional to commit)

**Structure:**
```markdown
# Session Handoff - [Date]

## Completed This Session
- ✅ Task 1
- ✅ Task 2

## Pending for Next Session
- [ ] Priority 1 task
- [ ] Priority 2 task

## Context Notes
- Key decision made: ...
- Blocker discovered: ...
- Reference files: location/to/file.py:lineX
- Important pattern: ...

## Next Steps
1. First thing to do
2. Second thing to do
3. Validation criteria
```

**Automatic Behavior (Proposed):**

1. **SessionEnd**: Claude automatically writes `.claude/handoff.md` with:
   - Completed tasks
   - Pending tasks
   - Key decisions and blockers
   - Next steps with specific file references

2. **SessionStart**: Claude automatically:
   - Reads `.claude/handoff.md` (if exists)
   - Incorporates content into session context
   - Archives previous handoff to `.claude/session-history/YYYY-MM-DD-HHmm.md`
   - Presents summary to user

**Token Efficiency:**
- Handoff files typically reduce 10,000+ token re-explanations to ~1,000-2,000 tokens
- Weekly savings: 30,000-50,000 tokens for users with 3-5 handoffs/week
- **Cost savings**: $1-5 per week, 10-20 minutes of time

### Implementation Options

**Option A: Automatic (Recommended)**
```json
{
  "hooks": {
    "SessionEnd": {
      "type": "prompt",
      "prompt": "Review current session state. Write .claude/handoff.md..."
    },
    "SessionStart": {
      "type": "prompt",
      "prompt": "Check for .claude/handoff.md. If exists: (1) Read and incorporate..."
    }
  }
}
```

**Option B: Manual CLI Flags**
```bash
$ claude --save-session  # Prompt for handoff at end
$ claude --load-session  # Read handoff at start
```

**Option C: Configuration Setting**
```json
{
  "sessionHandoff": {
    "enabled": true,
    "autoSave": true,
    "autoLoad": true,
    "archiveHistory": true,
    "handoffFile": "handoff.md",
    "archiveDir": "session-history",
    "maxArchiveFiles": 100
  }
}
```

### Real-World Implementations

**Continuous-Claude v3** implements a sophisticated alternative:
- **30 hooks** throughout Claude Code lifecycle (PostToolUse, UserPrompt, Edit tracking, SubagentStop)
- **Ledger system**: YAML-based handoffs in `thoughts/shared/handoffs/`
- **TLDR Code Analysis**: 5-layer AST/call graph/control flow reduction (95% token savings)
- **Memory Recall**: PostgreSQL+pgvector archival memory with daemon extraction
- **Fresh Context Strategy**: `/clear` restarts sessions with preserved state ("Compound, don't compact")

---

## 5. MCP Server Signals

### MCP Notification System

Claude Code supports MCP (Model Context Protocol) servers and can receive notifications about context changes:

**list_changed Notifications:**
- When MCP server sends `list_changed` notification, Claude Code automatically refreshes available capabilities
- Allows dynamic tool/resource/prompt updates without reconnecting
- Useful for notifying agent of new capabilities when context clears

**Output Management:**
- Warning threshold: Claude Code displays warning when MCP tool output exceeds 10,000 tokens
- Maximum default: 25,000 tokens per tool output
- Context window: One user found MCP tools consuming 66,000+ tokens before even starting conversation (33% of 200K window)

### MCP Notification Servers

**Model Context Protocol Notification Server:**
- Sends cross-platform desktop notifications via MCP
- Can play configurable system sounds when tasks complete
- Optional message customization
- Configurable timeout (default 60 seconds)
- Designed to eliminate need for constant visual monitoring

**Limitations:**
- MCP notifications are **not designed for LLM reaction** - they're primarily for user awareness
- LLMs cannot reliably react to notifications
- Better for user-facing alerts than agent-internal logic

### MCP Server Configuration Management

Tools for managing MCP servers in Claude Code:
```bash
claude mcp list           # List configured servers
claude mcp get github     # Get details for specific server
claude mcp remove github  # Remove a server
```

**Context Optimization Tool - McPick:**
- CLI tool for toggling MCP servers on/off before sessions start
- Only enable MCP servers needed for current task
- Significant token savings for large server collections

---

## 6. Claude Agent SDK Session Management

### Session Resume and Forking (Python)

The Claude Agent SDK provides programmatic session management:

**Resume a Session (Continue):**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async for message in query(
    prompt="Continue implementing the authentication system from where we left off",
    options=ClaudeAgentOptions(
        resume="session-xyz",  # Session ID from previous conversation
        model="claude-sonnet-4-5",
        allowed_tools=["Read", "Edit", "Write", "Glob", "Grep", "Bash"]
    )
):
    print(message)
```

**Fork a Session (Branching):**
```python
from claude_agent_sdk import query, ClaudeAgentOptions

# Original session
session_id = None
async for message in query(
    prompt="Help me design a REST API",
    options=ClaudeAgentOptions(model="claude-sonnet-4-5")
):
    if hasattr(message, 'subtype') and message.subtype == 'init':
        session_id = message.data.get('session_id')

# Fork for alternative approach
async for message in query(
    prompt="Now let's redesign this as a GraphQL API instead",
    options=ClaudeAgentOptions(
        resume=session_id,
        fork_session=True,  # Creates new session ID
        model="claude-sonnet-4-5"
    )
):
    print(message)
```

**When to Use Forking:**
- Explore different approaches from same starting point
- Test changes without modifying original history
- Create separate conversation branches
- Maintain multiple experimental paths

### Message and Usage Limits

**Pro Plan:**
- ~45 messages with Claude every 5 hours
- ~10-40 Claude Code prompts every 5 hours
- 40-80 hours of Sonnet 4 per week (varies with codebase size)

**Max Plan:**
- 5x more usage than Pro (225+ messages every 5 hours)
- 20x more usage (900+ messages every 5 hours on highest tier)

**Important Note:** Context window remains 200K across all plans. More messages allowed, not larger windows.

### SDK Cost Tracking

The Agent SDK provides:
- Detailed token usage information per interaction
- Usage data attached to assistant messages
- Capability to track costs and understand usage reporting
- Proper tracking with parallel tool uses and multi-step conversations

---

## 7. Community and Third-Party Solutions

### claude-mem Plugin

**Auto-context loader using 5 lifecycle hooks**

- **SessionStart**: Automatically injects context from last 10 sessions
- **UserPromptSubmit**: Captures user prompts
- **PostToolUse**: Records tool execution observations
- **Summary**: Creates semantic summaries with AI
- **SessionEnd**: Saves session for future retrieval

**How It Works:**
```
Session 1: Work → claude-mem captures observations → summarizes
         ↓
Session 2: SessionStart injects summaries automatically → Continue work
         ↓
Session 3: Access to context from Sessions 1-2
```

**Real-World Usage:**
- Work on feature Monday, close session
- Reopen project Tuesday
- Automatically see Monday's architectural decisions, file changes, recent edits
- "Claude remembers, so you don't re-explain"

**Technical Architecture:**
- TypeScript hooks → ESM modules
- Express API worker on port 37777 (Bun-managed)
- SQLite3 database at `~/.claude-mem/claude-mem.db`
- Modular context builders (TimelineRenderer, FooterRenderer, ObservationCompiler)
- Session IDs for cross-conversation resumption

**Installation:**
```bash
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem
# Restart Claude Code
```

### Continuous-Claude Framework

**Advanced context management using 30 hooks and ledgers**

**Architecture:**
- **Ledger System**: YAML-based state tracking in `thoughts/shared/handoffs/`
- **Smart Hooks**: 30 intervention points (PostToolUse, UserPrompt, Edit tracking, SubagentStop)
- **Code Analysis**: TLDR 5-layer approach reduces 23K tokens to 1.2K (95% savings)
  - L1: AST extraction
  - L2: Call graphs
  - L3: Control flow
  - L4: Data flow
  - L5: Program dependence graphs with slicing
- **Memory System**: PostgreSQL+pgvector for archival memory
- **Fresh Context Philosophy**: "Compound, don't compact" - restart with preserved state

**Cost Reduction:**
- Multiple strategies reduce context pollution
- MCP execution without including full tool output
- Agent orchestration with isolated context windows

---

## 8. Known Challenges and Gaps

### Current Limitations

1. **SessionStart Hook Failures**
   - Hooks execute but output not processed for new conversations
   - Works correctly for `/clear`, `/compact`, URL resume
   - May fail silently for brand new sessions

2. **Excessive Context Warnings**
   - 100+ warnings throughout conversation
   - Warnings start at ~20K tokens (early in 200K window)
   - Causes Claude to be overly cautious about tool usage
   - Environment variables for disabling are reportedly ineffective

3. **Lack of Configurable Thresholds**
   - Users cannot set custom warning thresholds
   - 95% auto-compact is too late (better: 85-90%)
   - No way to disable warnings entirely in some versions

4. **One-Way Web Session Handoff**
   - Can pull web sessions to terminal
   - Cannot push terminal sessions to web
   - Limits flexibility for mixed-mode workflows

5. **Missing Agent-Specific Behaviors**
   - No configurable actions when context limits approaching
   - No graceful degradation for agents
   - Agents need explicit instructions to summarize and restart

---

## 9. Recommended Architecture for Agent Handoff

### Minimal Implementation (Recommended for Quick Adoption)

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup",
        "hooks": [
          {
            "type": "command",
            "command": "sh -c 'test -f .claude/handoff.md && echo \"Handoff found. Loading...\" && cat .claude/handoff.md'"
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
            "command": "sh -c 'if [ -n \"$CLAUDE_SESSION_SUMMARY\" ]; then mkdir -p .claude/session-history && mv .claude/handoff.md .claude/session-history/$(date +%Y-%m-%d-%H%M%S).md; fi'"
          }
        ]
      }
    ]
  }
}
```

### Comprehensive Implementation (Maximum Safety)

Combine multiple mechanisms:

1. **SessionStart Hook**: Load previous handoff + context from claude-mem
2. **Native Context Awareness**: Monitor `<budget:token_budget>` continuously
3. **Token Budget Monitor**: Skill-based monitoring at 70%, 85%, 95% thresholds
4. **Manual Checkpoints**: `/context` command before major operations
5. **SessionEnd Hook**: Automatically create handoff with decisions, blockers, next steps
6. **MCP Notifications**: Alert user when context limit approaching (parallel to agent logic)

### Notification Strategy for Agents

Since agents can't reliably react to MCP notifications, use instead:

1. **In-context budgets**: Pass remaining token count to agent in system message
2. **Ledger-based state**: Track context through YAML files agent reads
3. **Hook-injected warnings**: Inject context warnings as additional context at start
4. **Explicit summarization prompts**: When threshold reached, ask agent to summarize

---

## 10. Recommendations for Implementation

### For Immediate Use (Days 1-3)

1. **Implement SessionStart/SessionEnd hooks** in project `.claude/settings.json`
2. **Create handoff.md generator script** that captures task completion status
3. **Add `/context` monitoring** as manual checkpoint before major operations
4. **Document in AGENTS.md** when handoffs should be triggered (70% context threshold)

### For Short Term (Week 1)

1. **Integrate claude-mem plugin** for automatic context preservation
2. **Set up token-budget-monitor skill** for proactive warnings
3. **Create SessionEnd hook** that archives handoffs with timestamp
4. **Test SessionStart hook** on `/clear` and `/compact` operations (known working paths)

### For Long Term (Month 1+)

1. **Evaluate Continuous-Claude framework** for sophisticated context management
2. **Implement MCP notification server** for user-facing alerts
3. **Build agent-specific logic** for graceful degradation when context approaches limits
4. **Consider contributing** SessionStart hook improvements back to Claude Code
5. **Explore Agent SDK session forking** for parallel task exploration

---

## 11. Key Files and Resources

### Official Documentation
- [Claude Code Hooks Reference](https://code.claude.com/docs/en/hooks)
- [Claude Code Slash Commands](https://code.claude.com/docs/en/slash-commands)
- [Claude Agent SDK Session Management](https://platform.claude.com/docs/en/agent-sdk/sessions)
- [Claude 4.5 Context Windows](https://docs.claude.com/en/docs/build-with-claude/context-windows)

### Open Issues & Feature Requests
- [GitHub #11455: Session Handoff / Continuity Support](https://github.com/anthropics/claude-code/issues/11455) (Primary feature request)
- [GitHub #9239: Context warnings disrupting work](https://github.com/anthropics/claude-code/issues/9239) (Known limitation)
- [GitHub #10373: SessionStart hooks not working for new conversations](https://github.com/anthropics/claude-code/issues/10373) (Known bug)
- [GitHub #13521: Context-Aware Agent with Low-Context Actions](https://github.com/anthropics/claude-code/issues/13521) (Related feature request)

### Community Implementations
- [claude-mem GitHub](https://github.com/thedotmack/claude-mem) - Auto-context loader plugin
- [Continuous-Claude v3 GitHub](https://github.com/parcadei/Continuous-Claude-v3) - Advanced context framework
- [LaunchDarkly Session Start Hook](https://github.com/launchdarkly-labs/claude-code-session-start-hook) - Dynamic config injection
- [claude-code-usage-monitor GitHub](https://github.com/Maciek-roboblog/Claude-Code-Usage-Monitor) - Real-time usage tracking
- [token-budget-monitor skill](https://claude-plugins.dev/skills/@mapachekurt/claude-skills/token-budget-monitor) - Proactive warnings

### Blog Posts & Guides
- [Claude Code Decoded: The Handoff Protocol](https://blackdoglabs.io/blog/claude-code-decoded-handoff-protocol) - Protocol deep dive
- [Never Lose Your Flow: Smart Handoff](https://blog.skinnyandbald.com/never-lose-your-flow-smart-handoff-for-claude-code/) - User strategies
- [Optimising MCP Server Context Usage](https://scottspence.com/posts/optimising-mcp-server-context-usage-in-claude-code/) - Context reduction
- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices) - Official guidance

---

## Summary Table: Mechanisms Comparison

| Mechanism | Real-Time | Automatic | Bidirectional | Token Cost | Implementation Effort | Status |
|-----------|-----------|-----------|---------------|-----------|----------------------|--------|
| SessionStart/SessionEnd Hooks | ✓ | ✓ | ✗ | Low (1-2K) | Low | Stable (some issues) |
| Claude 4.5 Budget Tags | ✓ | ✓ | ✗ | None | None | Stable, noisy |
| Handoff.md Protocol | ✗ | ✓ | ✓ | Low (1-2K) | Medium | Proposed, working |
| MCP Notifications | ✓ | ✓ | ✗ | None | Medium | Stable (limited use) |
| claude-mem Plugin | ✓ | ✓ | ✓ | Medium (3-5K) | Low | Production-ready |
| Continuous-Claude | ✓ | ✓ | ✓ | Low (compression) | High | Experimental |
| Agent SDK Fork/Resume | ✗ | ✗ | ✓ | None | Medium | Production-ready |
| token-budget-monitor | ✓ | ✓ | ✗ | Low | Low | Production-ready |

---

**Generated:** January 11, 2026
**Research Scope:** Comprehensive survey of context management mechanisms in Claude Code and Agent SDK
