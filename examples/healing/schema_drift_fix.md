# AutoPilot Incident Report

**Incident ID:** ap-20260717-002
**Dataset:** `urn:li:dataset:(urn:li:dataPlatform:dbt,analytics.customer_orders,PROD)`
**Issue Type:** schema
**Severity:** critical
**Detected:** 2026-07-17T11:00:00Z
**Status:** healed

## Description

Schema drift detected. Upstream `raw.customers` added column `loyalty_tier`
that is not present in downstream `customer_orders`.

## Root Cause Analysis

**Root Cause:** schema_change
**Upstream Dataset:** `urn:li:dataset:(urn:li:dataPlatform:dbt,raw.customers,PROD)`
**Confidence:** 0.95
**Schema Diff:** +1 column (`loyalty_tier TEXT`), 0 removed, 0 type changes

## Fix Applied

**Type:** dbt_model_patch
**Description:** Updated dbt model to include `loyalty_tier` column with
COALESCE for NULL handling.

**Code Patch:**
```sql
SELECT
    customer_id,
    order_date,
    total_amount,
    COALESCE(loyalty_tier, 'standard') AS loyalty_tier
FROM {{ ref('raw_customers') }}
```

**Schema YAML Updated:** Added `loyalty_tier` column definition.

## Validation

**Re-check Status:** PASSED
**Duration:** 32.1 seconds

## Write-Back Results

| Action | Status | URN |
|--------|--------|-----|
| Tag added | ✅ | urn:li:tag:auto-healed |
| Description updated | ✅ | urn:li:dataset:(...) |
| Incident document | ✅ | urn:li:document:ap-20260717-002 |
