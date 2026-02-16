"""Vet chain status inference for plan artifacts."""

import re
from pathlib import Path

from .models import VetChain, VetStatus

SOURCE_TO_REPORT_MAP = {
    "outline.md": "reports/outline-review.md",
    "design.md": "reports/design-review.md",
    "runbook-outline.md": "reports/runbook-outline-review.md",
    "runbook-phase-1.md": "reports/phase-1-review.md",
    "runbook-phase-2.md": "reports/phase-2-review.md",
    "runbook-phase-3.md": "reports/phase-3-review.md",
    "runbook-phase-4.md": "reports/phase-4-review.md",
    "runbook-phase-5.md": "reports/phase-5-review.md",
    "runbook-phase-6.md": "reports/phase-6-review.md",
}


def _find_fallback_phase_report(plan_dir: Path, phase_num: int) -> str | None:
    """Glob for phase-level reports when primary pattern not found.

    Searches for reports matching patterns with phase number N in the reports
    directory. Returns the most recent by mtime if multiple matches are found.
    """
    reports_dir = plan_dir / "reports"
    if not reports_dir.exists():
        return None

    # Glob for files containing the phase number and report-like keywords
    pattern = f"*{phase_num}*"
    candidates = []

    for report_file in reports_dir.glob(pattern):
        # Check if filename contains keywords like 'review' or 'vet'
        name = report_file.name
        if "review" in name or "vet" in name:
            candidates.append(report_file)

    if not candidates:
        return None

    # Return highest mtime
    most_recent = max(candidates, key=lambda p: p.stat().st_mtime)
    return f"reports/{most_recent.name}"


def get_vet_status(plan_dir: Path) -> VetStatus | None:
    """Scan plan_dir for recognized source artifacts and map to report paths.

    Returns VetStatus with chains for each source→report pair found. Returns
    None if no source artifacts are found.
    """
    chains = []

    for source_file, report_file in SOURCE_TO_REPORT_MAP.items():
        source_path = plan_dir / source_file
        report_path = plan_dir / report_file

        if source_path.exists():
            stale = False
            source_mtime = 0.0
            report_mtime = 0.0
            actual_report = report_file

            if report_path.exists():
                source_mtime = source_path.stat().st_mtime
                report_mtime = report_path.stat().st_mtime
                stale = source_mtime > report_mtime
            else:
                # Try fallback glob for phase-level reports
                if source_file.startswith("runbook-phase-"):
                    # Extract phase number from runbook-phase-N.md
                    match = re.search(r"runbook-phase-(\d+)", source_file)
                    if match:
                        phase_num = int(match.group(1))
                        fallback = _find_fallback_phase_report(plan_dir, phase_num)
                        if fallback:
                            actual_report = fallback
                            report_path = plan_dir / actual_report
                            if report_path.exists():
                                source_mtime = source_path.stat().st_mtime
                                report_mtime = report_path.stat().st_mtime
                                stale = source_mtime > report_mtime

                if not report_path.exists():
                    source_mtime = source_path.stat().st_mtime

            chain = VetChain(
                source=source_file,
                report=actual_report,
                stale=stale,
                source_mtime=source_mtime,
                report_mtime=report_mtime,
            )
            chains.append(chain)

    if not chains:
        return None

    return VetStatus(chains=chains)
