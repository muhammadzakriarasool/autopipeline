# AutoPilot — Fix Generation Engine Design

> **Component: fixer.py** | July 2026

## Purpose

Generate and stage fixes for diagnosed data pipeline issues.
Reuses Jinja2 templates from Phase 2 code generator.

## Components

### FixPlanner

LLM-powered fix planning based on diagnosis:
- Input: DiagnosisRecord with root cause, confidence, evidence
- Output: structured fix plan with approach, files to modify
- Fix types:
  - dbt_model_patch: UPDATE/INSERT column fixes, NULL handling, schema alignment
  - sql_patch: CTE corrections, type casting, filter adjustments
  - dag_update: Airflow/Dagster retry logic, timeout, dependency fixes
  - assertion_update: Adjust freshness window, volume thresholds
  - doc_fix: Update descriptions, add tags, document known issues
- Falls back to template-based fix plan if LLM unavailable

### CodeGenerator

Generates actual code patches using Jinja2 templates (reused from Phase 2):
- Takes fix plan + original code + metadata context
- Outputs dictionary of filename -> patched content
- Templates available: dbt_model.sql.j2, sql_transform.sql.j2, airflow_dag.py.j2
- Schema-aware: fixes reference actual column names and types

Fix generation strategies per issue type:

| Issue Type | Fix Strategy | Template Used |
|-----------|-------------|---------------|
| Freshness | Add/update freshness assertion; adjust schedule | N/A (mutation) |
| Volume | Adjust volume thresholds; investigate upstream | N/A (mutation) |
| Column (nulls) | Add COALESCE/NVL in transformation | dbt_model.sql.j2 |
| Schema (new cols) | Update downstream model with new columns | dbt_model.sql.j2 |
| Schema (type change) | Add CAST/conversion in model | sql_transform.sql.j2 |

### ApprovalGate

Controls whether fixes are applied automatically or require human approval:

```python
class ApprovalGate:
    def __init__(self, mode='shadow'):
        self.mode = mode  # 'shadow' | 'autonomous'

    def requires_approval(self, fix_record):
        if self.mode == 'autonomous':
            return fix_record.fix_type in CONFIG['require_approval_types']
        return True  # shadow mode always requires approval

    def approve(self, fix_id, approved=True):
        return Approval(approved=approved, approved_at=datetime.now())
```

### Sequence: Fix Flow

1. DiagnosisRecord received from RCA Engine
2. FixPlanner determines fix approach (LLM or template)
3. CodeGenerator produces patched files
4. ApprovalGate checks if approval needed
5. If auto-mode: proceed to Validation & Write-Back
6. If shadow-mode: store FixRecord, emit notification, wait for approval
7. Approved fix proceeds; rejected fix logged with reason
