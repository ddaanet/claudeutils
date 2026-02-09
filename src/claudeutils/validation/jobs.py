"""Validate jobs.md matches plans/ directory contents.

Checks:
- Plans listed in jobs.md have corresponding directories or files in plans/
- All plan directories/files in plans/ are listed in jobs.md (except complete plans)
- Plans with status 'complete' are exempt from directory existence check
"""

from pathlib import Path


def parse_jobs_md(jobs_path: Path) -> dict[str, str]:
    """Extract plan names and statuses from jobs.md Plans table.

    Args:
        jobs_path: Path to jobs.md file.

    Returns:
        Dictionary mapping plan name to status string.
    """
    content = jobs_path.read_text()
    plans: dict[str, str] = {}

    # Find the Plans table section
    in_table = False
    for line in content.splitlines():
        if line.startswith("## Plans"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if in_table and line.startswith("|") and not line.startswith("| Plan"):
            # Skip header separator
            if line.startswith("|---"):
                continue
            # Parse table row: | plan-name | status | notes |
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                plan_name = parts[1]
                status = parts[2]
                if plan_name and status:
                    plans[plan_name] = status

    return plans


def get_plans_directories(plans_dir: Path) -> set[str]:
    """Get all plan directories and files from plans/.

    Args:
        plans_dir: Path to plans directory.

    Returns:
        Set of plan names (directory names and .md file stems).
    """
    plans: set[str] = set()

    if not plans_dir.exists():
        return plans

    for item in plans_dir.iterdir():
        if item.name.startswith("."):
            continue

        # Skip plans/claude/ (gitignored, ephemeral plan-mode files)
        if item.name == "claude" and item.is_dir():
            continue

        # Regular .md files (one-off documents)
        if item.is_file() and item.suffix == ".md":
            if item.name != "README.md":
                plans.add(item.stem)
            continue

        # Plan directories
        if item.is_dir():
            plans.add(item.name)

    return plans


def validate(root: Path) -> list[str]:
    """Validate jobs.md against plans/ directory.

    Args:
        root: Project root directory.

    Returns:
        List of error messages. Empty list if no errors found.
    """
    jobs_path = root / "agents" / "jobs.md"
    plans_dir = root / "plans"

    if not jobs_path.exists():
        return [f"Error: {jobs_path} not found"]

    jobs_plans = parse_jobs_md(jobs_path)
    dir_plans = get_plans_directories(plans_dir)

    errors: list[str] = []

    # Check for plans in directory but not in jobs.md
    missing_from_jobs = dir_plans - set(jobs_plans.keys())
    errors.extend(
        [
            f"Plan '{plan}' exists in plans/ but not in jobs.md"
            for plan in sorted(missing_from_jobs)
        ]
    )

    # Check for plans in jobs.md but not in directory (excluding complete plans)
    for plan, status in jobs_plans.items():
        if status != "complete" and plan not in dir_plans:
            errors.append(
                f"Plan '{plan}' in jobs.md (status: {status}) but not found in plans/"
            )

    return errors
