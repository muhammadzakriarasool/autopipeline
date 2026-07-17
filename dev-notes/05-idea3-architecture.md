# AutoPilot - System Architecture

> Version 1.1 | July 2026 | Updated with OSS/Cloud distinction

## Overview

5-stage closed-loop system built on LangChain + DataHub Agent Context Kit.
Designed to work on BOTH DataHub OSS (Docker) and DataHub Cloud.

## Architecture

  +------------------+
  |   Scheduler      |  (configurable interval, default 300s)
  +--------+---------+
           |
  +--------v---------+     +-----------------------+
  | Detection Engine  |     |    DataHub Graph      |
  | - AssertionPoll   |<--->| - Assertions          |
  | - FreshnessMon    |     | - Datasets/Schemas   |
  | - SchemaWatcher   |     | - Lineage             |
  | - VolumeAnalyzer  |     | - Documents           |
  | - IssueRegistry   |     | - StructuredProps     |
  +--------+----------+     +-----------------------+
           | (IssueRecord)
  +--------v----------+
  |    RCA Engine      |
  | - ContextBuilder   |
  | - LineageTraverser |
  | - SchemaComparator |
  | - LlmDiagnosis     |
  +--------+----------+
           | (DiagnosisRecord)
  +--------v----------+
  |   Fix Generator    |
  | - FixPlanner (LLM)|
  | - CodeGenerator    |
  | - ApprovalGate     |
  +--------+----------+
           | (FixRecord)
  +--------v----------+
  | Validation + WB    |
  | - Revalidation     |
  | - DataHubWriter    |
  | - AuditTrailGen    |
  +-------------------+

## Module Files

| Module | File | Lines Target | Responsibility |
|--------|------|-------------|----------------|
| Detection | detector.py | ~200 | Poll assertions, check freshness/schema/volume |
| Diagnosis | diagnosis.py | ~200 | Lineage traversal, schema compare, LLM RCA |
| Fix Generator | fixer.py | ~150 | Plan fix, generate code, approval gate |
| Validation | healer.py | ~150 | Re-validate, write to DataHub, audit trail |
| Orchestrator | autopilot.py | ~150 | Schedule, orchestrate, config, state |
| CLI | cli.py (extended) | ~50 new | autopilot watch, autopilot heal commands |

## Data Flow Records

IssueRecord: id, dataset_urn, assertion_urn, issue_type, severity, detected_at, description, status
DiagnosisRecord: id, issue_id, root_cause_dataset, root_cause_type, evidence, diagnosis_text, confidence, suggested_fix_type
FixRecord: id, diagnosis_id, fix_type, fix_description, code_patches, requires_approval, approved
HealingRecord: id, fix_id, validation_passed, write_back_results, incident_document_urn, total_duration_seconds

## Technology Stack (100% free)

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Agent Framework | LangChain AgentExecutor | Official DataHub SDK integration |
| DataHub SDK | acryl-datahub>=1.6.0 | Mature entity/search/lineage API |
| Agent Context Kit | datahub-agent-context[langchain] | 22 pre-built tools |
| LLM Primary | OpenRouter free (openrouter/free) | 28+ models, $0, no CC |
| LLM Fallback | Ollama (Phi-4-mini or Llama 3.2 3B) | Local, 4-8GB RAM, works offline |
| Templates | Jinja2 (existing) | Reuse from Phase 2 |
| State | In-memory + DataHub structured properties | No external DB needed |
| CLI | Click (existing) | Extend with autopilot subcommands |
| Config | YAML (existing) | Dataset lists, intervals, thresholds |
| Rich output | Rich (existing) | Terminal output |

## Config Schema (autopilot-config.yaml)

autopilot:
  mode: "shadow"  # shadow | autonomous | disabled
  detection:
    polling_interval_seconds: 300
    enabled_checks: [freshness, volume, column, schema]
    freshness_max_age_hours: 24
    volume_deviation_threshold_percent: 20
    null_threshold_percent: 5
  scope:
    datasets:
      - domain: "healthcare"
  rca:
    max_lineage_hops: 3
    min_confidence_threshold: 0.7
  fixes:
    auto_apply_types: [doc_fix, assertion_update]
    require_approval_types: [dbt_model_patch, sql_patch, dag_update]
  write_back:
    tag_prefix: "AutoPilot"
    create_incident_documents: true
    update_descriptions: true