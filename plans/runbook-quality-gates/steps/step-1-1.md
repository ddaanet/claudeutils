# Cycle 1.1

**Plan**: `plans/runbook-quality-gates/runbook.md`
**Execution Model**: sonnet
**Phase**: 1

---

## Cycle 1.1: Script scaffold — argparse, importlib, report writer, exit codes

**Execution Model**: Sonnet

**RED Phase:**

**Test:** `test_scaffold_cli`
**Assertions:**
- Running script with `--help` exits with code 0
- Stdout contains all four subcommand names: `model-tags`, `lifecycle`, `test-counts`, `red-plausibility`
- Running script with no subcommand exits with code 1

**Expected failure:** `subprocess.CalledProcessError` or `FileNotFoundError` — script does not exist.

**Why it fails:** `agent-core/bin/validate-runbook.py` does not exist yet.

**Verify RED:** `pytest tests/test_validate_runbook.py::test_scaffold_cli -v`

---

**GREEN Phase:**

**Implementation:** Create `agent-core/bin/validate-runbook.py` with argparse structure, importlib import block, report writer function, and exit-code conventions.

**Behavior:**
- Shebang `#!/usr/bin/env python3` and `if __name__ == '__main__':` guard
- Argparse with 4 subcommands: `model-tags`, `lifecycle`, `test-counts`, `red-plausibility`; each accepts a `path` positional argument
- Missing subcommand → print usage to stderr, exit 1
- Importlib block loads `prepare-runbook.py` from same directory: `parse_frontmatter`, `extract_cycles`, `extract_sections`, `assemble_phase_files`, `extract_file_references`, `extract_step_metadata`
- `write_report(subcommand, path, violations, ambiguous=None)` writes report to `plans/<job>/reports/validation-{subcommand}.md`; `<job>` is `Path(path).parent.name` (directory case) or `Path(path).stem` (single-file case)
- Subcommand handlers are stubs (pass-through to `sys.exit(0)`) after scaffold

**Approach:** Pure argparse (not click). `add_subparsers(dest='subcommand', required=True)` causes exit 2 on missing subcommand — override to exit 1 via error handler or check `args.subcommand is None`. Report directory is created with `mkdir(parents=True, exist_ok=True)`.

**Changes:**
- File: `agent-core/bin/validate-runbook.py`
  Action: Create file with shebang, imports, importlib block, `write_report` function, argparse setup, stub subcommand handlers, `main()`, `if __name__ == '__main__':` guard
  Location hint: New file (~45 lines)

**Verify GREEN:** `pytest tests/test_validate_runbook.py::test_scaffold_cli -v`
**Verify no regression:** `just test tests/test_validate_runbook.py`

---
