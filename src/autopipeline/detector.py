"""AutoPilot detection engine — monitors DataHub for quality violations."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class IssueRecord:
    dataset_urn: str
    issue_type: str
    severity: str
    description: str
    assertion_urn: str = ""
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "open"
    id: str = field(default_factory=lambda: str(uuid4()))


class FreshnessMonitor:
    """Checks if datasets have been updated within the freshness window."""

    def __init__(self, max_age_hours: int = 24):
        self.max_age_hours = max_age_hours

    def _is_stale(self, last_modified: Optional[datetime]) -> bool:
        if last_modified is None:
            return False
        age = datetime.now(timezone.utc) - last_modified
        return age.total_seconds() > self.max_age_hours * 3600

    def check(self, dataset_urn: str, last_modified: Optional[datetime]) -> Optional[IssueRecord]:
        if not self._is_stale(last_modified):
            return None
        age_hours = (datetime.now(timezone.utc) - last_modified).total_seconds() / 3600
        return IssueRecord(
            dataset_urn=dataset_urn,
            issue_type="freshness",
            severity="critical",
            description=f"Not updated in {age_hours:.1f}h (max: {self.max_age_hours}h)",
        )


class SchemaWatcher:
    """Detects schema drift by comparing current vs expected fields."""

    def __init__(self):
        self._baseline: dict[str, list[str]] = {}

    def set_baseline(self, dataset_urn: str, field_paths: list[str]) -> None:
        self._baseline[dataset_urn] = list(field_paths)

    def check_drift(self, dataset_urn: str, current_fields: list[str]) -> Optional[dict]:
        if dataset_urn not in self._baseline:
            return None
        expected = set(self._baseline[dataset_urn])
        current = set(current_fields)
        added = current - expected
        removed = expected - current
        if not added and not removed:
            return None
        return {"added": sorted(added), "removed": sorted(removed)}


class VolumeAnalyzer:
    """Detects anomalous row count deviations from baseline."""

    def __init__(self, threshold_percent: float = 20.0):
        self.threshold_percent = threshold_percent
        self._baseline: dict[str, int] = {}

    def set_baseline(self, dataset_urn: str, row_count: int) -> None:
        self._baseline[dataset_urn] = row_count

    def check_deviation(self, dataset_urn: str, current_count: int) -> Optional[dict]:
        if dataset_urn not in self._baseline:
            return None
        expected = self._baseline[dataset_urn]
        if expected == 0:
            return None
        deviation = abs(current_count - expected) / expected * 100
        if deviation <= self.threshold_percent:
            return None
        return {
            "deviation_percent": round(deviation, 1),
            "expected": expected,
            "actual": current_count,
        }


class IssueRegistry:
    """Deduplicates and tracks issue lifecycle."""

    def __init__(self):
        self._issues: dict[str, IssueRecord] = {}

    def _key(self, dataset_urn: str, issue_type: str) -> str:
        return f"{dataset_urn}:{issue_type}"

    def register(self, issues: list[IssueRecord]) -> list[IssueRecord]:
        new = []
        for issue in issues:
            key = self._key(issue.dataset_urn, issue.issue_type)
            existing = self._issues.get(key)
            if existing is None or existing.status == "healed":
                self._issues[key] = issue
                new.append(issue)
        return new

    def update_status(self, dataset_urn: str, issue_type: str, status: str) -> None:
        key = self._key(dataset_urn, issue_type)
        if key in self._issues:
            self._issues[key].status = status

    def get_open_issues(self) -> list[IssueRecord]:
        return [i for i in self._issues.values() if i.status == "open"]
