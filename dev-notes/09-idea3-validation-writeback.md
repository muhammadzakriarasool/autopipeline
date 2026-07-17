# AutoPilot — Validation & Write-Back Engine

> **Component: healer.py** | July 2026

## Purpose

Apply fixes, re-validate assertions, document everything back to DataHub.
This is the final stage that closes the loop.

## Components

### RevalidationEngine

Re-checks the failed assertion after fix is applied:
- Re-runs the same assertion via DataHub API
- Compares new result with pre-fix baseline
- Returns validation_passed: bool
- Timeout after 3 attempts with exponential backoff

```python
class RevalidationEngine:
    def __init__(self, client, max_retries=3):
        self.client = client
        self.max_retries = max_retries

    def revalidate(self, fix_record):
        for attempt in range(self.max_retries):
            result = self._check_assertion(fix_record)
            if result.get('status') == 'SUCCESS':
                return True
            time.sleep(2 ** attempt)
        return False
```

### DataHubWriter

Reuses and extends existing DataHubWriter from Phase 2:

| Action | Method | Purpose |
|--------|--------|---------|
| Tag | add_tag() | Mark as AutoPilot-healed |
| Description | update_description() | Append fix summary |
| Lineage | add_lineage() | Record upstream->fix lineage |
| Document | save_document() | Full incident report |
| Structured Prop | add_structured_properties() | last_healed_at, healing_count |
| Glossary | add_glossary_terms() | data_quality, auto_remediated |

### AuditTrailGenerator

Creates comprehensive incident documentation in DataHub:

```markdown
# AutoPilot Incident Report

**Incident ID:** ap-20260717-001
**Dataset:** urn:li:dataset:(...)
**Issue Type:** freshness
**Severity:** critical
**Detected:** 2026-07-17T10:00:00Z
**Resolved:** 2026-07-17T10:02:30Z
**Duration:** 150 seconds

## Diagnosis
Root cause: Upstream source table not updated in 12 hours.
Lineage chain: target -> intermediate -> source

## Fix Applied
Type: assertion_update
Description: Adjusted freshness window from 6h to 12h for upstream source.

## Validation
Re-check passed: source table now within freshness window.
```

### Sequence: Healing Flow

1. Approved FixRecord received
2. Code patches written to filesystem (optional)
3. DataHubWriter applies mutations:
   a. Tag dataset with AutoPilot-healed
   b. Update description with fix summary
   c. Add structured property: last_healed_at
   d. Increment structured property: healing_count
4. RevalidationEngine re-checks the original assertion
5. AuditTrailGenerator creates incident document
6. HealingRecord returned with full results
7. IssueRegistry updated: status -> healed
