"""Plan state inference from directory artifacts."""

from pathlib import Path

from .models import PlanState


def _collect_artifacts(plan_dir: Path) -> set[str]:
    """Collect all recognized artifacts in the plan directory."""
    artifacts = set()

    # Baseline artifacts
    for filename in ["requirements.md", "design.md", "outline.md", "problem.md"]:
        if (plan_dir / filename).exists():
            artifacts.add(filename)

    # Runbook phase files
    for phase_file in sorted(plan_dir.glob("runbook-phase-*.md")):
        artifacts.add(phase_file.name)

    # Ready-state artifacts
    if (plan_dir / "steps").is_dir():
        artifacts.add("steps")
    if (plan_dir / "orchestrator-plan.md").exists():
        artifacts.add("orchestrator-plan.md")

    return artifacts


def _determine_status(plan_dir: Path) -> str:
    """Determine status by priority: ready > planned > designed > requirements."""
    if (plan_dir / "steps").is_dir() and (plan_dir / "orchestrator-plan.md").exists():
        return "ready"
    if list(plan_dir.glob("runbook-phase-*.md")):
        return "planned"
    if (plan_dir / "design.md").exists():
        return "designed"
    return "requirements"


def _derive_next_action(status: str, plan_name: str) -> str:
    """Map status to next action command."""
    match status:
        case "requirements":
            return f"/design plans/{plan_name}/requirements.md"
        case "designed":
            return f"/runbook plans/{plan_name}/design.md"
        case "planned":
            return f"agent-core/bin/prepare-runbook.py plans/{plan_name}"
        case "ready":
            return f"/orchestrate {plan_name}"
        case _:
            return ""


def infer_state(plan_dir: Path) -> PlanState | None:
    """Infer plan state from directory artifacts.

    Scans for recognized artifacts and returns PlanState or None if no artifacts
    found. Status priority: ready > planned > designed > requirements
    """
    if not plan_dir.exists():
        return None

    artifacts = _collect_artifacts(plan_dir)
    if not artifacts:
        return None

    name = plan_dir.name
    status = _determine_status(plan_dir)
    next_action = _derive_next_action(status, name)

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
