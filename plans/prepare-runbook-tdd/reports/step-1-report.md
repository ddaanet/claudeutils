# Step 1 Report: Analyze Current Implementation

## Function Inventory

### `parse_frontmatter(content)` (lines 27-49)
- **Purpose**: Extract YAML frontmatter from markdown content
- **Returns**: Tuple of (metadata_dict, remaining_content)
- **Logic**: Finds --- delimiters, parses key:value pairs
- **Current limitations**: Simple line-based parsing, no nested structures

### `extract_sections(content)` (lines 52-125)
- **Purpose**: Parse runbook into Common Context, Steps, and Orchestrator sections
- **Returns**: Dictionary with 'common_context', 'steps', 'orchestrator' keys
- **Step pattern**: `r'^## Step\s+([\d.]+):\s*(.*)'` (line 74)
- **Logic**: Line-by-line H2 header detection, content accumulation
- **Validation**: Detects duplicate step numbers (lines 96-98)

### `derive_paths(runbook_path)` (lines 128-145)
- **Purpose**: Calculate output paths from runbook location
- **Returns**: Tuple of (runbook_name, agent_path, steps_dir, orchestrator_path)
- **Naming**: Uses parent directory name as runbook_name

### `read_baseline_agent()` (lines 148-157)
- **Purpose**: Load baseline quiet-task agent template
- **Current**: Hardcoded to 'agent-core/agents/quiet-task.md'
- **Extension point**: Needs runbook_type parameter for conditional loading

### `generate_agent_frontmatter(runbook_name, model)` (lines 160-169)
- **Purpose**: Create frontmatter for plan-specific agent
- **Parameters**: runbook_name, model (default 'haiku')
- **Returns**: YAML frontmatter string

### `generate_step_file(step_num, step_content, runbook_path)` (lines 172-182)
- **Purpose**: Create individual step file content
- **Template**: Includes step header, plan reference, and step content
- **Extension point**: Need parallel `generate_cycle_file()` for TDD runbooks

### `generate_default_orchestrator(runbook_name)` (lines 185-192)
- **Purpose**: Create default orchestrator plan if not specified in runbook
- **Returns**: Basic orchestrator instructions

### `validate_and_create(...)` (lines 195-250)
- **Purpose**: Main orchestration for validation and file generation
- **Flow**: Validate → Create dirs → Generate agent → Generate steps → Generate orchestrator
- **Extension point**: Need conditional routing based on runbook type

### `main()` (lines 253-284)
- **Purpose**: CLI entry point
- **Flow**: Parse args → Read runbook → Extract sections → Derive paths → Validate and create

## Current Control Flow

1. Parse CLI arguments
2. Read runbook file
3. Parse frontmatter (extract metadata)
4. Extract sections (Common Context, Steps, Orchestrator)
5. Derive output paths
6. Validate sections (check steps exist)
7. Create directories
8. Generate plan-specific agent (baseline + frontmatter + common context)
9. Generate step files (one per step)
10. Generate orchestrator plan
11. Print summary

## Integration Points for TDD Support

### 1. Frontmatter Type Detection (parse_frontmatter)
- **Location**: Lines 27-49
- **Change**: Add type field extraction, default to 'general'
- **Impact**: Minimal, return type field in metadata dict

### 2. Cycle Pattern Detection (extract_sections)
- **Location**: Lines 52-125
- **Change**: Create new `extract_cycles()` function OR extend extract_sections with conditional logic
- **Pattern needed**: `r'^## Cycle\s+(\d+)\.(\d+):\s*(.*)'`
- **Impact**: Medium, need to handle cycle vs step detection

### 3. Conditional Baseline Selection (read_baseline_agent)
- **Location**: Lines 148-157
- **Change**: Add runbook_type parameter, conditional path selection
- **Paths**: 'agent-core/agents/tdd-task.md' vs 'agent-core/agents/quiet-task.md'
- **Impact**: Minimal, add parameter and if/else logic

### 4. Cycle File Generation (generate_step_file)
- **Location**: Lines 172-182
- **Change**: Create new `generate_cycle_file()` function with cycle-specific template
- **Naming**: cycle-{major}-{minor}.md (e.g., cycle-1-1.md)
- **Impact**: Medium, parallel function needed

### 5. Conditional File Generation Logic (validate_and_create)
- **Location**: Lines 225-233 (step file generation loop)
- **Change**: Route to generate_cycle_file() if TDD runbook
- **Impact**: Medium, need to pass runbook type through call chain

### 6. Help Text and Error Messages (main, validate_and_create)
- **Locations**: Lines 255-260 (help), 198-200 (validation)
- **Change**: Update to mention TDD support, use cycle terminology for TDD runbooks
- **Impact**: Minimal, text updates only

## Shared Logic Opportunities

- **Section parsing pattern**: Both step and cycle extraction follow same H2 detection logic
- **File generation**: Template structure similar between steps and cycles
- **Validation**: Duplicate detection, sequential numbering applicable to both
- **Path derivation**: Same output directory structure

## Code Structure Assessment

**Strengths**:
- Clean separation of concerns (parsing, generation, validation)
- Simple line-based parsing (easy to extend)
- Clear function boundaries

**Extension Strategy**:
- Add `extract_cycles()` as parallel to `extract_sections()`
- Add `generate_cycle_file()` as parallel to `generate_step_file()`
- Thread runbook_type through function calls
- Use conditional routing in `validate_and_create()`

**Estimated Complexity**:
- Step 3 (extract_cycles): ~60 lines
- Step 4 (type detection): ~15 lines
- Step 5 (baseline selection): ~10 lines
- Step 6 (cycle file generation): ~35 lines
- Step 7 (cycle validation): ~50 lines
- Step 8 (help/messages): ~20 lines
- **Total new/modified**: ~190 lines

## Conclusion

The current implementation is well-structured for extension. Key integration points identified:
1. Type field extraction (frontmatter)
2. Cycle detection and parsing (new function)
3. Baseline selection (parameter addition)
4. Cycle file generation (new function)
5. Conditional routing (validate_and_create)
6. Help text updates (minimal changes)

No structural conflicts found. TDD support can be added without breaking existing functionality.
