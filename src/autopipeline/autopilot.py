"""AutoPilot orchestrator — runs the full DETECT -> DIAGNOSE -> FIX -> VALIDATE -> DOCUMENT cycle."""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional

import yaml

from autopipeline.detector import IssueRecord, IssueRegistry
from autopipeline.diagnosis import DiagnosisRecord
from autopipeline.fixer import FixRecord
from autopipeline.healer import HealingRecord

logger = logging.getLogger(__name__)


@dataclass
class CycleResult:
    issues_found: int = 0
    diagnosed: int = 0
    fixed: int = 0
    validated: int = 0
    healed: int = 0
    failed: int = 0
    duration_seconds: float = 0.0


class ConfigLoader:
    """Parses autopilot-config.yaml with graceful fallback."""

    @staticmethod
    def load(path: str) -> dict:
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except (OSError, yaml.YAMLError):
            return {}


class StateManager:
    """Tracks healed issues to prevent re-processing."""

    def __init__(self):
        self._healed: set[str] = set()

    def _key(self, dataset_urn: str, issue_type: str) -> str:
        return f"{dataset_urn}:{issue_type}"

    def mark_healed(self, dataset_urn: str, issue_type: str) -> None:
        self._healed.add(self._key(dataset_urn, issue_type))

    def is_healed(self, dataset_urn: str, issue_type: str) -> bool:
        return self._key(dataset_urn, issue_type) in self._healed

    def healed_count(self) -> int:
        return len(self._healed)


class Orchestrator:
    """Runs one detection-healing cycle using injected dependencies."""

    def __init__(
        self,
        detect_fn: Callable[[], list[IssueRecord]],
        diagnose_fn: Callable[[IssueRecord], Optional[DiagnosisRecord]],
        fix_fn: Callable[[DiagnosisRecord], Optional[FixRecord]],
        validate_fn: Callable[[FixRecord], bool],
        document_fn: Callable[[IssueRecord, FixRecord, HealingRecord], str],
        state: Optional[StateManager] = None,
    ):
        self.detect_fn = detect_fn
        self.diagnose_fn = diagnose_fn
        self.fix_fn = fix_fn
        self.validate_fn = validate_fn
        self.document_fn = document_fn
        self.state = state or StateManager()
        self.registry = IssueRegistry()

    def run_once(self) -> CycleResult:
        start = datetime.now(timezone.utc)
        result = CycleResult()

        issues = self.detect_fn()
        result.issues_found = len(issues)

        new_issues = self.registry.register(issues)
        for issue in new_issues:
            if self.state.is_healed(issue.dataset_urn, issue.issue_type):
                continue

            diagnosis = self.diagnose_fn(issue)
            if not diagnosis:
                continue
            result.diagnosed += 1

            fix = self.fix_fn(diagnosis)
            if not fix:
                continue
            result.fixed += 1

            passed = self.validate_fn(fix)
            healing = HealingRecord(
                fix_id=fix.id,
                validation_passed=passed,
                status="healed" if passed else "failed",
            )
            self.document_fn(issue, fix, healing)

            if passed:
                self.state.mark_healed(issue.dataset_urn, issue.issue_type)
                self.registry.update_status(issue.dataset_urn, issue.issue_type, "healed")
                result.healed += 1
            else:
                result.failed += 1

        result.duration_seconds = (datetime.now(timezone.utc) - start).total_seconds()
        return result


def run_scheduler(orchestrator: Orchestrator, interval_seconds: int = 300) -> None:
    """Polling loop — runs orchestrator.run_once() every interval_seconds."""
    logger.info("AutoPilot scheduler started (interval: %ds)", interval_seconds)
    while True:
        try:
            result = orchestrator.run_once()
            if result.issues_found > 0:
                logger.info(
                    "Cycle: %d issues, %d healed, %d failed (%.1fs)",
                    result.issues_found, result.healed, result.failed,
                    result.duration_seconds,
                )
        except Exception:
            logger.exception("Cycle failed")
        time.sleep(interval_seconds)
