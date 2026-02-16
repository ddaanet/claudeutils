"""Plan state inference from directory artifacts."""

from pathlib import Path

from .models import PlanState


def infer_state(plan_dir: Path) -> PlanState | None:
    """Infer plan state from directory artifacts.

    Scans for recognized artifacts and returns PlanState or None if no artifacts
    found.
    """
    if not plan_dir.exists():
        return None

    artifacts = set()

    if (plan_dir / "requirements.md").exists():
        artifacts.add("requirements.md")
    if (plan_dir / "design.md").exists():
        artifacts.add("design.md")
    if (plan_dir / "outline.md").exists():
        artifacts.add("outline.md")
    if (plan_dir / "problem.md").exists():
        artifacts.add("problem.md")

    if not artifacts:
        return None

    name = plan_dir.name
    status = "requirements"
    next_action = f"/design plans/{name}/requirements.md"

    return PlanState(
        name=name,
        status=status,
        next_action=next_action,
        gate=None,
        artifacts=artifacts,
    )


def list_plans(plans_dir: Path) -> list[PlanState]:
    """List all plans in a plans directory, filtering out empty directories."""
    if not plans_dir.exists():
        return []

    plans = []
    for plan_dir in sorted(plans_dir.iterdir()):
        if plan_dir.is_dir():
            state = infer_state(plan_dir)
            if state is not None:
                plans.append(state)

    return plans
