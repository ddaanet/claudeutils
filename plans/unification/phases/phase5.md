# Consolidation: Phase 5

**Context**: Read `consolidation-context.md` for full context before executing this phase.

---

## Phase 5: Build Composition Tooling in claudeutils

### 5.1 Implementation Files

**Create**:
- `src/claudeutils/compose.py` - Core composition engine (extract from tuick/build.py)
- `src/claudeutils/compose_config.py` - YAML config models
- `src/claudeutils/cli_compose.py` - CLI subcommand implementation

**Update**:
- `src/claudeutils/cli.py` - Add `compose` subcommand
- `pyproject.toml` - Ensure claudeutils CLI entry point exists

### 5.2 Core Features

Extract from tuick/build.py:
```python
def increase_header_levels(content: str) -> str:
    """Shift all markdown headers down one level."""
    return re.sub(r'^(#+) ', r'#\1 ', content, flags=re.MULTILINE)

def build_role(output_path: Path, title: str, *sources: Path) -> None:
    """Compose role from fragments with title and separators."""
    sections = []
    for source in sources:
        content = source.read_text()
        elevated = increase_header_levels(content)
        sections.append(elevated)

    result = f"# {title}\n\n" + "\n\n---\n\n".join(sections)
    output_path.write_text(result)
```

### 5.3 YAML Config Parsing

```python
# compose_config.py
from pathlib import Path
from pydantic import BaseModel

class ComposeConfig(BaseModel):
    sources: dict[str, str]  # YAML anchors resolved
    fragments: list[str]      # Fragment paths
    output: str               # Output file path
```

---


---

**Execution Instructions**:
1. Read consolidation-context.md for prerequisites, critical files, and execution notes
2. Execute this phase following the actions listed above
3. Perform validation checks as specified
4. Document results in execution report
5. Stop on any unexpected results per communication rules
