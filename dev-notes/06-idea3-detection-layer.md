# AutoPilot — Detection Layer Design

> **Component: detector.py** | July 2026

## Purpose

Continuously monitor DataHub for data quality violations.

## Components

### AssertionPoller

Polls DataHub assertion results periodically. Uses GraphQL to query assertion status. Deduplicates by tracking last-checked timestamps.

### FreshnessMonitor

Checks last_modified timestamps against max_age threshold. Flags datasets that haven't been updated within the expected window.

### SchemaWatcher

Stores expected schema as baseline on first run. On subsequent checks, compares current schema fields to detect additions/removals.

### VolumeAnalyzer

Maintains baseline row counts. Flags deviations beyond configurable threshold percentage.

### IssueRegistry

In-memory deduplication. Keyed by dataset_urn+issue_type. Tracks status lifecycle: open -> diagnosing -> fixing -> healed | failed.

## Sequence: Detection Flow

1. Scheduler triggers poll cycle
2. Each sub-check runs in parallel (thread pool)
3. Results collected into unified list
4. IssueRegistry deduplicates against previously-reported issues
5. New issues enqueued for RCA Engine
