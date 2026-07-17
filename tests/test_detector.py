"""Tests for AutoPilot detection engine."""
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from autopipeline.detector import (
    IssueRecord,
    FreshnessMonitor,
    SchemaWatcher,
    VolumeAnalyzer,
    IssueRegistry,
)


class TestIssueRecord:
    def test_create_minimal(self):
        issue = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,test,PROD)",
            issue_type="freshness",
            severity="warning",
            description="Table not updated in 24h",
        )
        assert issue.dataset_urn.startswith("urn:li:dataset:")
        assert issue.issue_type == "freshness"
        assert issue.severity == "warning"
        assert issue.status == "open"
        assert issue.id  # auto-generated UUID

    def test_create_with_assertion(self):
        issue = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            assertion_urn="urn:li:assertion:abc",
            issue_type="volume",
            severity="critical",
            description="Row count dropped 50%",
        )
        assert issue.assertion_urn == "urn:li:assertion:abc"

    def test_status_lifecycle(self):
        issue = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="schema",
            severity="warning",
            description="Schema drift",
        )
        assert issue.status == "open"
        issue.status = "diagnosing"
        assert issue.status == "diagnosing"
        issue.status = "healed"
        assert issue.status == "healed"


class TestFreshnessMonitor:
    def test_stale_detection(self):
        monitor = FreshnessMonitor(max_age_hours=24)
        stale_time = datetime.now(timezone.utc) - timedelta(hours=48)
        assert monitor._is_stale(stale_time) is True

    def test_fresh_pass(self):
        monitor = FreshnessMonitor(max_age_hours=24)
        fresh_time = datetime.now(timezone.utc) - timedelta(hours=1)
        assert monitor._is_stale(fresh_time) is False

    def test_exactly_at_threshold(self):
        monitor = FreshnessMonitor(max_age_hours=24)
        threshold_time = datetime.now(timezone.utc) - timedelta(hours=24)
        assert monitor._is_stale(threshold_time) is True

    def test_none_timestamp(self):
        monitor = FreshnessMonitor(max_age_hours=24)
        assert monitor._is_stale(None) is False


class TestSchemaWatcher:
    def test_baseline_storage(self):
        watcher = SchemaWatcher()
        fields = ["id", "name", "email"]
        watcher.set_baseline("urn:test", fields)
        assert watcher._baseline["urn:test"] == fields

    def test_drift_detection_addition(self):
        watcher = SchemaWatcher()
        watcher.set_baseline("urn:test", ["id", "name"])
        current = ["id", "name", "email"]
        result = watcher.check_drift("urn:test", current)
        assert result is not None
        assert "email" in result["added"]

    def test_drift_detection_removal(self):
        watcher = SchemaWatcher()
        watcher.set_baseline("urn:test", ["id", "name", "email"])
        current = ["id", "name"]
        result = watcher.check_drift("urn:test", current)
        assert result is not None
        assert "email" in result["removed"]

    def test_no_drift(self):
        watcher = SchemaWatcher()
        watcher.set_baseline("urn:test", ["id", "name"])
        result = watcher.check_drift("urn:test", ["id", "name"])
        assert result is None

    def test_no_baseline(self):
        watcher = SchemaWatcher()
        result = watcher.check_drift("urn:unknown", ["id"])
        assert result is None


class TestVolumeAnalyzer:
    def test_baseline_storage(self):
        analyzer = VolumeAnalyzer(threshold_percent=20)
        analyzer.set_baseline("urn:test", 1000)
        assert analyzer._baseline["urn:test"] == 1000

    def test_deviation_detection(self):
        analyzer = VolumeAnalyzer(threshold_percent=20)
        analyzer.set_baseline("urn:test", 1000)
        result = analyzer.check_deviation("urn:test", 500)
        assert result is not None
        assert result["deviation_percent"] == 50.0

    def test_within_threshold(self):
        analyzer = VolumeAnalyzer(threshold_percent=20)
        analyzer.set_baseline("urn:test", 1000)
        result = analyzer.check_deviation("urn:test", 950)
        assert result is None

    def test_no_baseline(self):
        analyzer = VolumeAnalyzer(threshold_percent=20)
        result = analyzer.check_deviation("urn:unknown", 500)
        assert result is None

    def test_zero_baseline(self):
        analyzer = VolumeAnalyzer(threshold_percent=20)
        analyzer.set_baseline("urn:test", 0)
        result = analyzer.check_deviation("urn:test", 100)
        assert result is None


class TestIssueRegistry:
    def test_register_new(self):
        registry = IssueRegistry()
        issue = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )
        new_issues = registry.register([issue])
        assert len(new_issues) == 1

    def test_dedup(self):
        registry = IssueRegistry()
        issue1 = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )
        issue2 = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="freshness",
            severity="critical",
            description="still stale",
        )
        registry.register([issue1])
        new_issues = registry.register([issue2])
        assert len(new_issues) == 0  # deduplicated

    def test_different_types_not_deduped(self):
        registry = IssueRegistry()
        issue1 = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )
        issue2 = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="volume",
            severity="warning",
            description="volume drop",
        )
        registry.register([issue1])
        new_issues = registry.register([issue2])
        assert len(new_issues) == 1  # different type, not deduped

    def test_healed_allows_reopen(self):
        registry = IssueRegistry()
        issue = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )
        registry.register([issue])
        registry.update_status("urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)", "freshness", "healed")
        new_issues = registry.register([issue])
        assert len(new_issues) == 1  # healed allows re-detection

    def test_get_open_issues(self):
        registry = IssueRegistry()
        issue = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )
        registry.register([issue])
        open_issues = registry.get_open_issues()
        assert len(open_issues) == 1

    def test_update_status(self):
        registry = IssueRegistry()
        issue = IssueRecord(
            dataset_urn="urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )
        registry.register([issue])
        registry.update_status(
            "urn:li:dataset:(urn:li:dataPlatform:dbt,x,PROD)", "freshness", "diagnosing"
        )
        open_issues = registry.get_open_issues()
        assert len(open_issues) == 0  # status changed, no longer "open"
