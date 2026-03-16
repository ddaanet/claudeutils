# Outline Review 2: remove-fuzzy-recall

**Artifact**: plans/remove-fuzzy-recall/outline.md
**Date**: 2026-03-15
**Mode**: review + fix-all (incremental — focuses on D3 changes, cli.py scope addition, and prior-fix verification)

## Summary

D3 artifact-form error message (added in prior review) is well-specified with correct STOP directive usage per recall entry "when cli error messages are llm-consumed." The `recall_cli/cli.py` scope item was added but lacked implementation detail in Affected Functions and test coverage in Test Changes. Both gaps fixed. Prior review fixes (D3 artifact-form, D4 title, scope OUT rationale, affected functions table reference) all hold.

**Overall Assessment**: Ready

## Requirements Traceability

Requirements extracted from brief.md (no numbered FR-* identifiers; mapped from Proposed Change section):

| Requirement | Outline Section | Coverage | Notes |
|-------------|-----------------|----------|-------|
| Keyword-form error message | D3, Affected Functions (resolver.py, recall_cli/cli.py) | Complete | Message matches brief; cli.py wraps per context |
| Artifact-form error message | D3, Affected Functions (recall_cli/cli.py) | Complete | STOP directive + rationale; no index-read guidance per brief |
| Remove `_get_suggestions()` | Affected Functions (resolver.py) | Complete | Marked for deletion |
| Remove `_handle_no_match()` | Affected Functions (resolver.py) | Complete | Marked for deletion |
| Hard failure + guidance | D1, D2, D3 | Complete | Exact matching with context-differentiated errors |
| Update tests expecting "Did you mean:" | Test Changes | Complete | 3 rewritten, 2 deleted, 2 new cli.py tests added |

**Traceability Assessment**: All requirements covered.

## Scope-to-Component Traceability

| Scope IN Item | Implementation Section | Notes |
|---------------|----------------------|-------|
| `resolver.py` -- 3 fuzzy paths | Affected Functions: resolver.py | D1 trigger, D2 heading, deleted functions |
| `memory_index_checks.py` -- 1 fuzzy path | Affected Functions: validation/memory_index_checks.py | D4, D5 |
| `memory_index.py` -- 1 fuzzy path | Affected Functions: validation/memory_index.py | D5 |
| `recall_cli/cli.py` -- error wrapping | Affected Functions: recall_cli/cli.py | Added this review -- was orphan |
| `test_when_resolver.py` -- 3 tests | Test Changes: test_when_resolver.py | All 3 addressed |
| `test_when_resolver_errors.py` -- 3 tests | Test Changes: test_when_resolver_errors.py | 1 rewrite, 2 delete |
| `test_validation_memory_index_formats.py` -- 2 tests | Test Changes: test_validation_memory_index_formats.py | Both addressed |
| `agents/memory-index.md` -- data fixes | Sequencing step 2, D6 | Pre-flight + data fix phase |
| `agents/decisions/*.md` -- heading fixes | Sequencing step 2, D6 | Pre-flight + data fix phase |

**Scope Assessment**: All items assigned after fix. `recall_cli/cli.py` was orphan -- now has Affected Functions subsection.

## Cross-Component Interface Check

| Producer | Consumer | Interface | Status |
|----------|----------|-----------|--------|
| `resolver.py` raises `ResolveError` | `cli.py` catches and wraps | Exception type | Compatible -- both reference `ResolveError` |
| `cli.py` argument parsing | `cli.py` error wrapping | Call context (keyword vs artifact) | Compatible -- cli.py determines context from argument type |

No interface mismatches found.

## Recall Entries Checked

| Entry | Relevance | Assessment |
|-------|-----------|------------|
| when cli error messages are llm-consumed | D3 error design | D3 correctly applies: facts-only for keyword-form, STOP for unrecoverable artifact-form |
| when writing memory-index trigger phrases | D6 data check | D6 correctly references this for article alignment |
| when design proposes removing functions | `_get_suggestions()`, `_handle_no_match()` deletion | Outline specifies exact functions. Implementer should verify all callers per this recall entry. |
| when grounding recall system behavior | Fuzzy matcher known issues | Background context -- no action needed in outline |
| when testing CLI tools | Test approach | New cli.py tests should use Click CliRunner per this entry |
| when triaging behavioral code changes as simple | Complexity assessment | Background -- already triaged as moderate |

## Prior Review Fix Verification

| Prior Fix | Location | Status |
|-----------|----------|--------|
| D3 artifact-form error message added | Line 35 | Intact |
| D4 title "simplified to exact-only" | Line 37 | Intact |
| Scope OUT fuzzy.py rationale expanded | Line 21 | Intact |
| Affected Functions `_resolve_trigger()` references D3 | Line 51 | Intact |

All prior fixes hold.

## Review Findings

### Critical Issues

None.

### Major Issues

1. **`recall_cli/cli.py` in Scope IN but missing from Affected Functions**
   - Location: Affected Functions section (between validation/memory_index.py and Test Changes)
   - Problem: Scope IN lists `recall_cli/cli.py` for "differentiated error wrapping per D3" but no Affected Functions subsection existed. D3 describes WHAT the error messages are but not WHERE the differentiation is implemented. The implementer would have to guess whether the branching happens in `resolver.py` (which doesn't know call context) or `cli.py` (which does). This is the kind of architectural ambiguity that causes implementation rework.
   - Fix: Added `### recall_cli/cli.py` subsection to Affected Functions. Specifies that cli.py catches `ResolveError` from resolver.py and wraps with context-appropriate message. Includes rationale for cli.py as the correct location (knows call context from argument parsing).
   - **Status**: FIXED

### Minor Issues

1. **No test coverage specified for artifact-form error message**
   - Location: Test Changes section
   - Problem: D3 specifies two distinct error messages (keyword-form and artifact-form) but Test Changes only rewrites `test_trigger_not_found_suggests_matches` for keyword-form. No test verifies the artifact-form STOP message. Without explicit test specification, the implementer may only test the keyword path and miss the artifact path entirely.
   - Fix: Added two new test specifications (`test_keyword_form_error_message`, `test_artifact_form_error_message`) for cli.py error differentiation, with specific assertion criteria for each form.
   - **Status**: FIXED

## Fixes Applied

- Affected Functions -- Added `### recall_cli/cli.py` subsection with function table showing keyword-path and artifact-path error wrapping, plus rationale for implementation location
- Test Changes -- Added cli.py error differentiation test specifications (keyword-form and artifact-form) between resolver_errors and validation_memory_index_formats sections

## Positive Observations

- D3 artifact-form message correctly uses STOP directive per "when cli error messages are llm-consumed" recall entry (unrecoverable = STOP)
- D3 includes explicit rationale for WHY the STOP should halt the agent (context was judged relevant by planning skill; missing context is definitively lost)
- Brief's two-failure-mode distinction (keyword = recoverable via index read; artifact = upstream problem) is faithfully preserved
- Sequencing rationale remains sound -- validator before resolver prevents mismatches from becoming runtime errors
- Function-level detail with line numbers gives implementer precise targets
- Scope OUT items comprehensively enumerated with reasons

## Recommendations

- The recall entry "when testing CLI tools" specifies Click CliRunner for in-process testing. New cli.py tests should follow this pattern.
- The recall entry "when design proposes removing functions" applies to `_get_suggestions()` and `_handle_no_match()`. Implementer should Grep for all callers before deletion -- not just the fuzzy path identified in this outline.

---

**Ready for user presentation**: Yes
