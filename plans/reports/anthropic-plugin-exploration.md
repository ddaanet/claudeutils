# Anthropic Plugin Exploration Report

**Date:** 2026-03-06
**Scope:** All 28 internal plugins from `anthropics/claude-plugins-official`

## Installation Status

All 28 internal plugins installed at project scope (`.claude/settings.json`). `superpowers` confirmed absent from official repo — likely renamed or removed.

## Plugin Inventory by Category

### Safety & Security (2 plugins)

**security-guidance** — PreToolUse hook on Edit/Write/MultiEdit
- Pattern-matching security scanner checking file content and paths
- 8 rules: GitHub Actions injection, child_process.exec, new Function, eval, dangerouslySetInnerHTML, document.write, innerHTML, pickle, os.system
- Session-scoped deduplication (warns once per file+rule per session)
- Blocks first occurrence (exit 2), allows subsequent edits
- **Overlap with custom pipeline:** Our S-3 (output-as-instruction) and Sec-1–Sec-4 criteria cover broader LLM-specific failure modes. security-guidance covers web/JS-specific patterns we don't. Complementary, not redundant.

**hookify** — Configurable hook rule engine
- Declarative `.local.md` rule files with YAML frontmatter
- Events: bash, file, stop, prompt, all
- Actions: warn (default), block
- Regex + conditions (field/operator/pattern)
- Ships examples: dangerous-rm, sensitive-files, console-log, require-tests-stop
- **Safety relevance:** Enables user-defined safety gates without writing Python hooks. Our hooks are Python-based with more logic; hookify is declarative/simpler. Could use hookify for lightweight guards, custom hooks for complex logic.

### Code Quality (3 plugins)

**code-review** — PR review command (`/code-review`)
- 5 parallel Sonnet agents with distinct review angles: CLAUDE.md compliance, shallow bug scan, git history context, prior PR comments, code comment compliance
- Confidence scoring (0-100), threshold >=80 for reporting
- Auto-comments on PRs via `gh`
- **Overlap:** Our `/review` skill is inline (not PR-oriented). code-review is GitHub-integrated. Different use cases.

**code-simplifier** — Simplification guidance (not explored in detail)

**commit-commands** — Commit workflow commands

### Feature Development (1 plugin)

**feature-dev** — 7-phase guided feature development (`/feature-dev`)
- Phases: Discovery, Codebase Exploration, Clarifying Questions, Architecture Design, Implementation, Quality Review, Summary
- 3 specialized agents: code-explorer (yellow/sonnet), code-architect (green/sonnet), code-reviewer (red/sonnet)
- **Overlap with custom pipeline:** Our `/design` + `/runbook` + `/orchestrate` chain covers the same lifecycle with more structure (TDD phases, runbook steps, vet agents). feature-dev is more interactive (asks user at each gate). Different paradigms: our pipeline is autonomous; feature-dev is collaborative.

### Plugin & Skill Development (3 plugins)

**plugin-dev** — Plugin creation guidance (already in our skill set)
**skill-creator** — Skill authoring with eval framework, benchmark scripts, quality grading agents
**hookify** — Also enables hook creation via `/hookify` command

### CLAUDE.md Management (2 plugins)

**claude-md-management** — CLAUDE.md improvement skill + `/revise-claude-md` command
**claude-code-setup** — Initial CLAUDE.md setup guidance

### Output Styles (2 plugins)

**explanatory-output-style** — Explanatory output formatting
**learning-output-style** — Educational output formatting

### Agent SDK (1 plugin)

**agent-sdk-dev** — Agent SDK app scaffolding with TS/Python verifier agents

### IDE/LSP (12 plugins)

pyright-lsp, clangd-lsp, csharp-lsp, gopls-lsp, jdtls-lsp, kotlin-lsp, lua-lsp, php-lsp, rust-analyzer-lsp, swift-lsp, typescript-lsp — All follow same pattern: LSP server integration for language-specific diagnostics. Require system-installed language servers.

### Workflow (2 plugins)

**ralph-loop** — Autonomous loop with stop hook (experimental)
**playground** — SVG visualization templates (code-map, concept-map, data-explorer, design-playground, diff-review, document-critique)

### Other (1 plugin)

**pr-review-toolkit** — PR review utilities
**frontend-design** — Frontend design guidance

## Safety/Security Overlap Analysis

### What official plugins cover that we don't:
- Web-specific security patterns (XSS, innerHTML, eval, GitHub Actions injection)
- Per-file-path pattern matching for sensitive files (.env, credentials)
- Declarative rule engine for lightweight guards (hookify)
- GitHub PR-integrated review with confidence scoring

### What our custom pipeline covers that plugins don't:
- LLM-specific failure modes (S-1 through S-6): exit code optimism, instruction-following from output, happy-path completion bias, cleanup-path destruction
- Chain analysis (C-1 through C-3): destructive operation inventory, error propagation trace, agent-in-the-loop analysis
- Hazard tiering based on reversibility (DO-178C-adapted)
- Safety review integrated into runbook execution pipeline
- Model tier elevation for destructive operations

### Verdict:
**Complementary.** security-guidance adds web/JS-specific pattern detection we lack. Our pipeline adds LLM-behavioral safety analysis they lack. Both should be active. hookify provides a lighter-weight guard mechanism useful for project-specific rules without writing Python hooks.

## Recommendations

- Keep security-guidance enabled — covers patterns our safety criteria don't
- Keep hookify enabled — declarative rule creation supplements our Python hooks
- feature-dev disabled by default (conflicts with our pipeline paradigm), enable for interactive prototyping
- code-review useful for GitHub PR workflows; doesn't conflict with inline `/review`
- LSP plugins: enable only for languages actually used in a project
- skill-creator: useful reference for eval methodology if building new skills
