# Vet Review: test_submodule_safety.py parametrized factorization

**Scope**: `tests/test_submodule_safety.py` — 2 parametrized test functions (17 cases)
**Date**: 2026-02-16
**Mode**: review + fix

## Summary

Clean parametrized test file. 17 cases (10 allowed, 7 blocked) cover FR-1 (cd && pattern), FR-3 (quoting/whitespace variants), and security boundaries (traversal, partial match, subdirectory, semicolon). All tests pass. No issues found.

**Overall Assessment**: Ready

## Issues Found

### Critical Issues

None.

### Major Issues

None.

### Minor Issues

None.

## Fixes Applied

No fixes needed.

## Requirements Validation

| Requirement | Status | Evidence |
|-------------|--------|----------|
| FR-1: Allow `cd <root> && <cmd>` from wrong cwd | Satisfied | `cd-and-single`, `cd-and-chain`, `cd-and-pytest` test IDs |
| FR-3: Quoting and whitespace variants | Satisfied | `dquote-and`, `squote-and`, `no-space-amp`, `extra-space-amp` test IDs |
| Security: path traversal blocked | Satisfied | `path-traversal` test ID |
| Security: partial match blocked | Satisfied | `partial-match` test ID |
| Security: subdirectory blocked | Satisfied | `subdirectory` test ID |
| Security: semicolon separator blocked | Satisfied | `semicolon` test ID |
| 17 test cases preserved | Satisfied | 10 allowed + 7 blocked = 17 total, all pass |

---

## Positive Observations

- Descriptive parametrize IDs make test output readable (`bare-cd-dquote`, `path-traversal`, etc.)
- Helper functions (`_make_hook_input`, `_run`) reduce duplication without over-abstracting
- Security cases are grouped with comments distinguishing wrong-path, traversal, and separator attacks
- `_run` return type (`int | None`) correctly models the three exit states (0, 2, no exit)
