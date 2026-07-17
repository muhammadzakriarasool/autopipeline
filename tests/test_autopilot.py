"""Tests for AutoPilot orchestrator and config."""
import os
import tempfile

from autopipeline.autopilot import ConfigLoader, StateManager, Orchestrator
from autopipeline.detector import IssueRecord, FreshnessMonitor, IssueRegistry
from autopipeline.diagnosis import DiagnosisRecord, ContextBuilder
from autopipeline.fixer import FixRecord, FixPlanner, ApprovalGate
from autopipeline.healer import HealingRecord, RevalidationEngine, AuditTrailGenerator


class TestConfigLoader:
    def test_load_valid_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("autopilot:\n  mode: shadow\n  detection:\n    polling_interval_seconds: 300\n")
            f.flush()
            config = ConfigLoader.load(f.name)
            os.unlink(f.name)
        assert config["autopilot"]["mode"] == "shadow"
        assert config["autopilot"]["detection"]["polling_interval_seconds"] == 300

    def test_load_missing_file(self):
        config = ConfigLoader.load("/nonexistent/path.yaml")
        assert config == {}

    def test_load_invalid_yaml(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: {{{}}}")
            f.flush()
            config = ConfigLoader.load(f.name)
            os.unlink(f.name)
        assert config == {}


class TestStateManager:
    def test_track_healed(self):
        sm = StateManager()
        sm.mark_healed("urn:test", "freshness")
        assert sm.is_healed("urn:test", "freshness") is True

    def test_not_healed(self):
        sm = StateManager()
        assert sm.is_healed("urn:test", "freshness") is False

    def test_different_type_not_healed(self):
        sm = StateManager()
        sm.mark_healed("urn:test", "freshness")
        assert sm.is_healed("urn:test", "volume") is False

    def test_get_healed_count(self):
        sm = StateManager()
        sm.mark_healed("urn:a", "freshness")
        sm.mark_healed("urn:b", "volume")
        assert sm.healed_count() == 2


class TestOrchestrator:
    def test_run_once_with_no_issues(self):
        def mock_detect():
            return []
        def mock_diagnose(issue):
            return None
        def mock_fix(diagnosis):
            return None
        def mock_validate(fix):
            return True
        def mock_document(issue, fix, healing):
            return "report"

        orch = Orchestrator(
            detect_fn=mock_detect,
            diagnose_fn=mock_diagnose,
            fix_fn=mock_fix,
            validate_fn=mock_validate,
            document_fn=mock_document,
        )
        result = orch.run_once()
        assert result.issues_found == 0
        assert result.healed == 0

    def test_run_once_with_issue(self):
        issue = IssueRecord(
            dataset_urn="urn:test",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )
        diagnosis = DiagnosisRecord(
            issue_id=issue.id,
            root_cause_dataset="urn:upstream",
            root_cause_type="stale_upstream",
        )
        fix = FixRecord(diagnosis_id=diagnosis.id, fix_type="doc_fix")

        def mock_detect():
            return [issue]
        def mock_diagnose(iss):
            return diagnosis
        def mock_fix(diag):
            return fix
        def mock_validate(fx):
            return True
        def mock_document(iss, fx, healing):
            return "report"

        orch = Orchestrator(
            detect_fn=mock_detect,
            diagnose_fn=mock_diagnose,
            fix_fn=mock_fix,
            validate_fn=mock_validate,
            document_fn=mock_document,
        )
        result = orch.run_once()
        assert result.issues_found == 1
        assert result.healed == 1

    def test_skips_already_healed(self):
        issue = IssueRecord(
            dataset_urn="urn:test",
            issue_type="freshness",
            severity="warning",
            description="stale",
        )

        call_count = [0]

        def mock_detect():
            call_count[0] += 1
            return [issue] if call_count[0] <= 1 else []

        def mock_diagnose(iss):
            return DiagnosisRecord(issue_id=iss.id, root_cause_dataset="urn:x", root_cause_type="stale_upstream")

        def mock_fix(diag):
            return FixRecord(diagnosis_id=diag.id, fix_type="doc_fix")

        def mock_validate(fx):
            return True

        def mock_document(iss, fx, healing):
            return "report"

        orch = Orchestrator(
            detect_fn=mock_detect,
            diagnose_fn=mock_diagnose,
            fix_fn=mock_fix,
            validate_fn=mock_validate,
            document_fn=mock_document,
        )
        orch.run_once()
        result = orch.run_once()
        assert result.issues_found == 0
