"""AutoPilot validation and write-back engine — closes the healing loop."""
from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Optional
from uuid import uuid4

from autopipeline.detector import IssueRecord
from autopipeline.fixer import FixRecord

logger = logging.getLogger(__name__)


@dataclass
class HealingRecord:
    fix_id: str
    validation_passed: bool = False
    write_back_results: dict = field(default_factory=dict)
    incident_document_urn: str = ""
    total_duration_seconds: float = 0.0
    status: str = "pending"
    id: str = field(default_factory=lambda: str(uuid4()))


class RevalidationEngine:
    """Re-checks assertions after a fix with retry logic."""

    def __init__(
        self,
        check_fn: Callable[[FixRecord], bool],
        max_retries: int = 3,
        delay: float = 1.0,
    ):
        self.check_fn = check_fn
        self.max_retries = max_retries
        self.delay = delay

    def revalidate(self, fix: FixRecord) -> bool:
        for attempt in range(self.max_retries):
            try:
                if self.check_fn(fix):
                    return True
            except Exception:
                logger.debug("Revalidation attempt %d failed", attempt + 1)
            if attempt < self.max_retries - 1:
                time.sleep(self.delay * (2 ** attempt))
        return False


class AuditTrailGenerator:
    """Generates incident report markdown from healing records."""

    @staticmethod
    def generate(
        issue: IssueRecord, fix: FixRecord, healing: HealingRecord
    ) -> str:
        now = datetime.now(timezone.utc).isoformat()
        lines = [
            "# AutoPilot Incident Report",
            "",
            f"**Dataset:** {issue.dataset_urn}",
            f"**Issue Type:** {issue.issue_type}",
            f"**Severity:** {issue.severity}",
            f"**Detected:** {issue.detected_at.isoformat()}",
            f"**Status:** {healing.status}",
            f"**Generated:** {now}",
            "",
            "## Description",
            issue.description,
            "",
            "## Fix Applied",
            f"**Type:** {fix.fix_type}",
            f"**Description:** {fix.fix_description}",
            "",
            "## Validation",
            f"**Passed:** {healing.validation_passed}",
            f"**Duration:** {healing.total_duration_seconds:.1f}s",
            "",
        ]
        if healing.write_back_results:
            lines.append("## Write-Back Results")
            for key, val in healing.write_back_results.items():
                lines.append(f"- {key}: {val}")
            lines.append("")
        return "\n".join(lines)
