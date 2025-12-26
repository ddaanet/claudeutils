# Sonnet Base Agent vs Sub-agent Context Comparison

## Executive Summary

This document compares the system prompts and context provided to the base Claude Code
agent versus sub-agents spawned via the Task tool. The findings reveal that sub-agents
receive a **significantly reduced and simplified instruction set**, focused on task
execution rather than the broader interactive CLI experience.

## Key Findings

### 1. Core Identity Differences

**Base Agent:**

> "I am Claude Code, an interactive CLI tool that helps users with software engineering
> tasks."

**Sub-agent:**

> "I am Claude Code, Anthropic's official CLI for Claude. I am an agent for Claude Code,
> designed to complete tasks using available tools. My directive is to 'do what has been
> asked; nothing more, nothing less.'"

The sub-agent has a more focused, task-oriented identity with an explicit directive to
stay strictly within scope.

### 2. Major Sections Present in Base Agent but ABSENT in Sub-agent

#### A. Professional Objectivity (MISSING)

Base agent has extensive instructions about:

- Prioritizing technical accuracy over validating user beliefs
- Avoiding excessive praise or emotional validation
- Applying rigorous standards and disagreeing when necessary
- Investigating uncertainty rather than confirming beliefs

**Sub-agent:** No such instructions at all.

#### B. Avoid Over-engineering (MISSING)

Base agent has a massive section with detailed rules about:

- Only making directly requested changes
- Not adding features beyond what was asked
- Not adding docstrings/comments/type annotations to unchanged code
- Not creating helpers/utilities/abstractions for one-time operations
- Avoiding backwards-compatibility hacks
- "Three similar lines of code is better than premature abstraction"

**Sub-agent:** No instructions about over-engineering at all.

#### C. Planning Without Timelines (MISSING)

Base agent has instructions to:

- Provide concrete implementation steps without time estimates
- Never suggest timelines like "2-3 weeks"
- Focus on what needs to be done, not when

**Sub-agent:** No such instructions.

#### D. Task Tool and Specialized Agents (CRITICALLY DIFFERENT)

**Base agent has extensive instructions:**

- Proactively use Task tool with specialized agents when task matches description
- When exploring codebase, CRITICAL to use Task tool with subagent_type=Explore
- Prefer Task tool for file searches to reduce context usage
- Maximize use of parallel tool calls

**Sub-agent has minimal, negative-only instructions:**

- "NEVER use TodoWrite or Task tools" (in git commit section)
- "DO NOT use TodoWrite or Task tools" (in PR creation section)
- Brief mention in Grep tool: "Use Task tool for open-ended searches requiring multiple
  rounds"

**Critical difference:** Base agent is told to proactively spawn sub-agents. Sub-agents
are told NOT to spawn further agents (in git/PR contexts).

#### E. Documentation Lookup (MISSING)

Base agent has instructions to use claude-code-guide agent for help questions.

**Sub-agent:** No such instructions.

#### F. Code References (MISSING)

Base agent instructed to use `file_path:line_number` pattern when referencing code.

**Sub-agent:** No such instructions.

#### G. Security Context (MISSING)

Base agent has instructions about authorized security testing, CTF challenges, etc.

**Sub-agent:** No security context instructions.

#### H. Help and Feedback (MISSING)

Base agent knows about /help command and GitHub issues link.

**Sub-agent:** No help/feedback information.

### 3. Sections Present in BOTH (Similar Content)

#### A. Git Commit Protocol

Both have nearly identical, extensive git commit protocols:

- Safety rules (NEVER update config, NEVER force push, etc.)
- Amend rules (very specific conditions)
- NEVER commit unless explicitly asked
- NEVER use -i flag
- Use HEREDOC for commit messages
- Parallel execution of git status/diff/log
- Focus on "why" not "what" in commit messages

**Verdict:** Essentially identical.

#### B. Pull Request Protocol

Both have similar PR creation instructions:

- Use gh command
- Run git commands in parallel
- Analyze ALL commits
- Use HEREDOC for PR body
- Return PR URL

**Verdict:** Very similar.

#### C. Emoji Policy

Both have multiple instructions:

- Only use emojis if explicitly requested
- Avoid adding emojis to files unless asked
- Avoid emojis in communication

**Verdict:** Identical.

#### D. Parallel Tool Calls

Both have extensive instructions:

- Run independent tool calls in parallel
- Wait for dependencies before sequential calls
- Never use placeholders
- Repeated across multiple contexts

**Verdict:** Identical.

#### E. File Creation vs Editing Policy

Both have very strong preferences:

- "ALWAYS prefer editing existing files"
- "NEVER write new files unless explicitly required"
- "NEVER proactively create documentation files"
- Repeated multiple times

**Verdict:** Identical (one of most emphasized instructions).

#### F. Bash Tool Usage

Both have similar policies:

- For terminal operations, not file operations
- Use specialized tools for file operations
- Quote paths with spaces
- Avoid cd, use absolute paths
- Parallel vs sequential command chaining

**Verdict:** Very similar.

### 4. Sub-agent Specific Additions

**Core Strengths Section:** Sub-agent has explicit list of strengths:

- Searching for code, configurations, and patterns
- Analyzing multiple files for architecture
- Investigating complex questions
- Multi-step research tasks

**Base agent:** No such section.

**Notable Absences Section:** Sub-agent explicitly lists what it doesn't have:

- No instructions about "avoiding over-engineering"
- No instructions about "professional objectivity"
- No instructions about planning and timelines
- No mention of Task tool or specialized agents
- No TodoWrite tool available

**Base agent:** No such meta-commentary.

**Explicit Directive:** Sub-agent includes: "My directive is to 'do what has been asked;
nothing more, nothing less.'"

**Base agent:** No such explicit directive (has broader interactive CLI purpose).

### 5. Available Tools Comparison

| Tool       | Base Agent        | Sub-agent |
| ---------- | ----------------- | --------- |
| Task       | ✅ Yes            | ❌ No     |
| TaskOutput | ✅ Yes            | ❌ No     |
| Bash       | ✅ Yes            | ✅ Yes    |
| Glob       | ✅ Yes            | ✅ Yes    |
| Grep       | ✅ Yes            | ✅ Yes    |
| Read       | ✅ Yes            | ✅ Yes    |
| Edit       | ✅ Yes            | ✅ Yes    |
| Write      | ✅ Yes            | ✅ Yes    |
| TodoWrite  | ✅ Yes (implicit) | ❌ No     |

**Critical difference:** Sub-agents cannot spawn other agents (no Task/TaskOutput
tools).

### 6. Context Information Differences

**Base Agent has:**

- Thinking mode: interleaved
- Max thinking length: 31999
- Token budget: 200000
- Todo list status
- Auto-approved tools list

**Sub-agent has:**

- None of the above

### 7. Probing Questions Results

Based on direct questioning of the sub-agent:

| Question                        | Sub-agent Response                                         |
| ------------------------------- | ---------------------------------------------------------- |
| Over-engineering instructions?  | **NO** - None at all                                       |
| Git commit protocol?            | **YES** - Extensive, nearly identical                      |
| Emoji instructions?             | **YES** - Multiple, identical                              |
| Professional objectivity?       | **NO** - None at all                                       |
| Planning/timeline instructions? | **NO** - None at all                                       |
| Task tool instructions?         | **MINIMAL** - Only negative mentions (don't use in git/PR) |
| Parallel tool calls?            | **YES** - Extensive, identical                             |
| File creation policy?           | **YES** - Very strong preference for editing, identical    |

## Implications

### 1. Task Focus

Sub-agents are given a **narrower, more task-focused** instruction set. They lack the
broader guidance about:

- How to interact with users professionally
- Software engineering best practices (avoiding over-engineering)
- Strategic tool usage (when to spawn other agents)

### 2. Recursive Agent Spawning Prevention

Sub-agents **cannot spawn other sub-agents** (no Task tool). This prevents infinite
recursion and keeps the agent hierarchy flat:

- Base agent → Can spawn sub-agents
- Sub-agent → Cannot spawn more agents

The only exception is the mention in Grep tool description about using Task for
open-ended searches, but the tool itself is not available.

### 3. Simplified Decision Space

Sub-agents have **fewer high-level decisions to make**:

- No decisions about when to use specialized agents
- No decisions about over-engineering tradeoffs
- No decisions about professional tone/objectivity

They simply execute the task with the tools available.

### 4. Preserved Core Protocols

Critical operational protocols are **preserved** in sub-agents:

- Git safety and commit protocols
- Pull request creation process
- File operation preferences (edit vs create)
- Parallel tool execution patterns

This ensures sub-agents operate safely and consistently.

### 5. Meta-awareness

Sub-agents include a **"Notable Absences" section** that explicitly lists what they
don't have. This suggests:

- Sub-agents may be aware they're operating with reduced context
- This awareness might help them avoid trying to access unavailable capabilities
- Or this might be part of the experiment's output format

## Architectural Pattern

The observed pattern suggests a **hierarchical agent architecture**:

```
Base Agent (Full Context)
├── Interactive CLI focus
├── Strategic decision-making
├── Can spawn specialized agents
├── Professional guidelines
├── Over-engineering prevention
└── Meta-instructions

Sub-agent (Reduced Context)
├── Task execution focus
├── "Do what has been asked; nothing more, nothing less"
├── Cannot spawn more agents
├── Core operational protocols only
└── No meta-instructions
```

## Conclusion

Claude Code uses a **two-tier context system**:

1. **Base Agent:** Full context with interactive CLI guidelines, strategic tool usage,
   professional standards, and meta-instructions. Designed for direct user interaction
   and complex decision-making.

2. **Sub-agents:** Simplified context focused on task execution. Stripped of
   meta-instructions, strategic guidance, and agent-spawning capabilities. Designed to
   complete specific tasks efficiently without over-thinking or over-engineering.

This architecture:

- ✅ Prevents infinite recursion (sub-agents can't spawn)
- ✅ Reduces token usage (simpler context for sub-tasks)
- ✅ Maintains safety (core protocols preserved)
- ✅ Focuses sub-agents on execution over deliberation
- ✅ Keeps strategic decisions at the base agent level

The design appears intentional and well-suited for a task-delegation architecture where
the base agent handles user interaction and strategy, while sub-agents handle focused
execution.
