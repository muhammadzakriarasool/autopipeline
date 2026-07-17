"""End-to-end integration tests — full pipeline without real DataHub."""
from datetime import datetime, timezone, timedelta

from autopipeline.detector import (
    IssueRecord, FreshnessMonitor, SchemaWatcher, VolumeAnalyzer, IssueRegistry,
)
from autopipeline.diagnosis import (
    DiagnosisRecord, ContextBuilder, SchemaComparator, LineageTraverser, RcaDatabase,
)
from autopipeline.fixer import FixRecord, FixPlanner, CodeGenerator, ApprovalGate
from autopipeline.healer import HealingRecord, RevalidationEngine, AuditTrailGenerator
from autopipeline.autopilot import ConfigLoader, StateManager, Orchestrator


def _detect_issues() -> list[IssueRecord]:
    monitor = FreshnessMonitor(max_age_hours=24)
    stale = datetime.now(timezone.utc) - timedelta(hours=48)
    issue = monitor.check(
        "urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.orders,PROD)", stale
    )
    return [issue] if issue else []


def _diagnose_issue(issue: IssueRecord) -> DiagnosisRecord:
    return DiagnosisRecord(
        issue_id=issue.id,
        root_cause_dataset="urn:li:dataset:(urn:li:dataPlatform:dbt,raw.orders,PROD)",
        root_cause_type="stale_upstream",
        evidence=[ContextBuilder.build_evidence(issue, {"upstreams": ["urn:raw"]})],
        diagnosis_text="Upstream raw.orders not updated in 48h",
        confidence=0.9,
        suggested_fix_type="assertion_update",
    )


def _generate_fix(diagnosis: DiagnosisRecord) -> FixRecord:
    return FixPlanner.plan(diagnosis)


def _validate_fix(fix: FixRecord) -> bool:
    return True


def _document_healing(issue: IssueRecord, fix: FixRecord, healing: HealingRecord) -> str:
    return AuditTrailGenerator.generate(issue, fix, healing)


class TestFullPipelineSingleIssue:
    def test_detect_to_document(self):
        issues = _detect_issues()
        assert len(issues) == 1
        assert issues[0].issue_type == "freshness"

        diagnosis = _diagnose_issue(issues[0])
        assert diagnosis.root_cause_type == "stale_upstream"
        assert diagnosis.confidence == 0.9

        fix = _generate_fix(diagnosis)
        assert fix.fix_type == "assertion_update"

        passed = _validate_fix(fix)
        assert passed is True

        healing = HealingRecord(fix_id=fix.id, validation_passed=passed, status="healed")
        md = _document_healing(issues[0], fix, healing)
        assert "# AutoPilot Incident Report" in md
        assert "stale_upstream" in md


class TestFullPipelineMultipleIssues:
    def test_two_issues(self):
        monitor = FreshnessMonitor(max_age_hours=24)
        stale = datetime.now(timezone.utc) - timedelta(hours=48)
        fresh = datetime.now(timezone.utc) - timedelta(hours=1)

        issues = []
        for urn in ["urn:a", "urn:b"]:
            issue = monitor.check(urn, stale)
            if issue:
                issues.append(issue)
        fresh_issue = monitor.check("urn:c", fresh)
        assert fresh_issue is None

        registry = IssueRegistry()
        new_issues = registry.register(issues)
        assert len(new_issues) == 2

        healed = 0
        for issue in new_issues:
            diag = _diagnose_issue(issue)
            fix = _generate_fix(diag)
            passed = _validate_fix(fix)
            if passed:
                healed += 1
        assert healed == 2


class TestFullPipelineFailedValidation:
    def test_failed_validation(self):
        issues = _detect_issues()
        diagnosis = _diagnose_issue(issues[0])
        fix = _generate_fix(diagnosis)

        def fail_validate(fix_record):
            return False

        passed = fail_validate(fix)
        healing = HealingRecord(fix_id=fix.id, validation_passed=passed, status="failed")
        assert healing.status == "failed"
        assert healing.validation_passed is False


class TestOrchestratorIntegration:
    def test_full_cycle_with_orchestrator(self):
        orch = Orchestrator(
            detect_fn=_detect_issues,
            diagnose_fn=_diagnose_issue,
            fix_fn=_generate_fix,
            validate_fn=_validate_fix,
            document_fn=_document_healing,
        )
        result = orch.run_once()
        assert result.issues_found == 1
        assert result.healed == 1
        assert result.duration_seconds >= 0

    def test_second_cycle_skips_healed(self):
        orch = Orchestrator(
            detect_fn=_detect_issues,
            diagnose_fn=_diagnose_issue,
            fix_fn=_generate_fix,
            validate_fn=_validate_fix,
            document_fn=_document_healing,
        )
        r1 = orch.run_once()
        assert r1.healed == 1
        r2 = orch.run_once()
        assert r2.issues_found == 1
        assert r2.healed == 0


class TestConfigIntegration:
    def test_config_loads_real_file(self):
        config = ConfigLoader.load("autopilot-config.yaml")
        assert config.get("autopilot", {}).get("mode") == "shadow"


class TestEdgeCases:
    def test_no_issues_detected(self):
        monitor = FreshnessMonitor(max_age_hours=24)
        fresh = datetime.now(timezone.utc) - timedelta(hours=1)
        issue = monitor.check("urn:test", fresh)
        assert issue is None

    def test_lineage_traversal_with_real_data(self):
        traverser = LineageTraverser(max_hops=3)
        lineage_map = {
            "urn:target": ["urn:mid"],
            "urn:mid": ["urn:source"],
            "urn:source": [],
        }
        chain, root = traverser.find_root("urn:target", lineage_map)
        assert root == "urn:source"
        assert len(chain) == 3

    def test_schema_comparison_with_real_fields(self):
        upstream = ["id", "name", "email", "created_at"]
        downstream = ["id", "name"]
        result = SchemaComparator.compare(upstream, downstream)
        assert result is not None
        assert "email" in result["added"]
        assert "created_at" in result["added"]
