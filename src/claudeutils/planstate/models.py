"""Data models for plan state."""

from dataclasses import dataclass


@dataclass
class PlanState:
    """Plan state inferred from directory artifacts."""

    name: str
    status: str
    next_action: str
    gate: str | None
    artifacts: set[str]
