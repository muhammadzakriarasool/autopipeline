"""Tests for AutoPilot validation and write-back engine."""
from datetime import datetime, timezone

from autopipeline.fixer import FixRecord
from autopipeline.detector import IssueRecord
from autopipeline.healer import (
    HealingRecord,
    RevalidationEngine,
    AuditTrailGenerator,
)


def _make_fix() -> FixRecord:
    return FixRecord(
        diagnosis_id="diag-1",
        fix_type="doc_fix",
        fix_description="Update documentation for stale dataset",
        code_patches={"description.md": "# Updated docs"},
    )


def _make_issue() -> IssueRecord:
    return IssueRecord(
        dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,test,PROD)",
        issue_type="freshness",
        severity="critical",
        description="Not updated in 48h",
    )


class TestHealingRecord:
    def test_create_minimal(self):
        rec = HealingRecord(fix_id="fix-1")
        assert rec.fix_id == "fix-1"
        assert rec.validation_passed is False
        assert rec.status == "pending"
        assert rec.id

    def test_create_full(self):
        rec = HealingRecord(
            fix_id="fix-1",
            validation_passed=True,
            write_back_results={"tagged": True, "documented": True},
            incident_document_urn="urn:li:document:ap-001",
            total_duration_seconds=120.5,
            status="healed",
        )
        assert rec.validation_passed is True
        assert rec.status == "healed"


class TestRevalidationEngine:
    def test_success_on_first_try(self):
        check_fn = lambda fix: True
        engine = RevalidationEngine(check_fn=check_fn)
        assert engine.revalidate(_make_fix()) is True

    def test_success_after_retries(self):
        attempts = [False, False, True]
        call_count = [0]

        def check_fn(fix):
            result = attempts[call_count[0]]
            call_count[0] += 1
            return result

        engine = RevalidationEngine(check_fn=check_fn, max_retries=3, delay=0)
        assert engine.revalidate(_make_fix()) is True

    def test_failure_after_all_retries(self):
        check_fn = lambda fix: False
        engine = RevalidationEngine(check_fn=check_fn, max_retries=3, delay=0)
        assert engine.revalidate(_make_fix()) is False

    def test_no_retries_on_success(self):
        call_count = [0]

        def check_fn(fix):
            call_count[0] += 1
            return True

        engine = RevalidationEngine(check_fn=check_fn, max_retries=3, delay=0)
        engine.revalidate(_make_fix())
        assert call_count[0] == 1


class TestAuditTrailGenerator:
    def test_generates_markdown(self):
        issue = _make_issue()
        fix = _make_fix()
        healing = HealingRecord(
            fix_id=fix.id,
            validation_passed=True,
            status="healed",
            total_duration_seconds=45.2,
        )
        md = AuditTrailGenerator.generate(issue, fix, healing)
        assert "# AutoPilot Incident Report" in md
        assert issue.dataset_urn in md
        assert "healed" in md

    def test_includes_diagnosis(self):
        issue = _make_issue()
        fix = _make_fix()
        healing = HealingRecord(fix_id=fix.id)
        md = AuditTrailGenerator.generate(issue, fix, healing)
        assert "freshness" in md
        assert "critical" in md

    def test_includes_validation_status(self):
        issue = _make_issue()
        fix = _make_fix()
        healing = HealingRecord(fix_id=fix.id, validation_passed=False, status="failed")
        md = AuditTrailGenerator.generate(issue, fix, healing)
        assert "failed" in md
