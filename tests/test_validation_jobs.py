"""Tests for jobs validator."""

from pathlib import Path

from claudeutils.validation.jobs import validate


def test_valid_jobs_md_with_matching_plans(tmp_path: Path) -> None:
    """Test that valid jobs.md with matching plans/ returns no errors."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| plan-one | designed | Test plan |
| plan-two | planned | Another test |
""")

    # Create matching plan directories
    (tmp_path / "plans" / "plan-one").mkdir(parents=True, exist_ok=True)
    (tmp_path / "plans" / "plan-two").mkdir(parents=True, exist_ok=True)

    errors = validate(tmp_path)
    assert errors == []


def test_plan_in_directory_but_not_in_jobs_md(tmp_path: Path) -> None:
    """Test: plan in directory but not in jobs.md → error."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| plan-one | designed | Test plan |
""")

    # Create plan directories
    (tmp_path / "plans" / "plan-one").mkdir(parents=True, exist_ok=True)
    (tmp_path / "plans" / "plan-two").mkdir(parents=True, exist_ok=True)

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "plan-two" in errors[0]
    assert "exists in plans/" in errors[0]
    assert "not in jobs.md" in errors[0]


def test_plan_in_jobs_md_but_not_in_directory_non_complete(
    tmp_path: Path,
) -> None:
    """Test: plan in jobs.md but not in directory (non-complete) → error."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| plan-one | designed | Test plan |
| plan-two | planned | Missing plan |
""")

    # Create only plan-one directory
    (tmp_path / "plans" / "plan-one").mkdir(parents=True, exist_ok=True)

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "plan-two" in errors[0]
    assert "in jobs.md" in errors[0]
    assert "not found in plans/" in errors[0]


def test_complete_plans_exempt_from_directory_check(tmp_path: Path) -> None:
    """Test: complete plans exempt from directory check."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| plan-one | designed | Active plan |
| plan-two | complete | Archived plan |
""")

    # Create only plan-one directory (plan-two is complete, not required)
    (tmp_path / "plans" / "plan-one").mkdir(parents=True, exist_ok=True)

    errors = validate(tmp_path)
    assert errors == []


def test_table_parsing_handles_standard_format(tmp_path: Path) -> None:
    """Test: table parsing handles standard format."""
    # Create jobs.md with various formats
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

Some preamble text.

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| plan-alpha | designed | Notes here |
| plan-beta | planned | More notes |
| plan-gamma | complete | Archived |

## Complete (Archived)

Other sections here.
""")

    # Create directories for non-complete plans
    (tmp_path / "plans" / "plan-alpha").mkdir(parents=True, exist_ok=True)
    (tmp_path / "plans" / "plan-beta").mkdir(parents=True, exist_ok=True)

    errors = validate(tmp_path)
    assert errors == []


def test_missing_jobs_md_returns_error(tmp_path: Path) -> None:
    """Test: missing jobs.md → error."""
    # Don't create jobs.md
    (tmp_path / "agents").mkdir(parents=True, exist_ok=True)

    errors = validate(tmp_path)
    assert len(errors) == 1
    assert "not found" in errors[0]


def test_md_file_in_plans_directory(tmp_path: Path) -> None:
    """Test: .md files in plans/ are treated as plans (by stem)."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| my-document | designed | One-off doc |
""")

    # Create .md file (not directory)
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / "my-document.md").write_text("# My Document")

    errors = validate(tmp_path)
    assert errors == []


def test_readme_md_in_plans_ignored(tmp_path: Path) -> None:
    """Test: README.md in plans/ is ignored."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
""")

    # Create README.md (should be ignored)
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / "README.md").write_text("# Plans")

    errors = validate(tmp_path)
    assert errors == []


def test_dotfiles_in_plans_ignored(tmp_path: Path) -> None:
    """Test: dotfiles in plans/ are ignored."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
""")

    # Create dotfiles (should be ignored)
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / ".gitkeep").write_text("")
    (plans_dir / ".test-dir").mkdir()

    errors = validate(tmp_path)
    assert errors == []


def test_plans_claude_directory_ignored(tmp_path: Path) -> None:
    """Test: plans/claude/ directory is ignored."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
""")

    # Create plans/claude/ (should be ignored)
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / "claude").mkdir()

    errors = validate(tmp_path)
    assert errors == []


def test_multiple_errors_reported(tmp_path: Path) -> None:
    """Test: multiple errors are all reported."""
    # Create jobs.md
    jobs_file = tmp_path / "agents" / "jobs.md"
    jobs_file.parent.mkdir(parents=True, exist_ok=True)
    jobs_file.write_text("""# Jobs

## Plans

| Plan | Status | Notes |
|------|--------|-------|
| plan-one | designed | Plan one |
| plan-missing | planned | Missing from directory |
""")

    # Create directories
    plans_dir = tmp_path / "plans"
    plans_dir.mkdir(parents=True, exist_ok=True)
    (plans_dir / "plan-one").mkdir()
    (plans_dir / "plan-extra").mkdir()

    errors = validate(tmp_path)
    assert len(errors) == 2
    assert any("plan-extra" in e and "not in jobs.md" in e for e in errors)
    assert any("plan-missing" in e and "not found in plans/" in e for e in errors)
