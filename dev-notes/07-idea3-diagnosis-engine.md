# AutoPilot — Diagnosis Engine Design

> **Component: diagnosis.py** | July 2026

## Purpose

Diagnose root cause of detected issues using lineage traversal, schema comparison, and LLM reasoning.

## Components

### ContextBuilder

Gathers full metadata context for affected dataset:
- Schema fields with types and descriptions
- Ownership and tags
- Glossary terms and domain
- Upstream/downstream lineage list
- Current assertion results

### LineageTraverser

Recursive BFS traversal upstream through DataHub lineage graph:
- Configurable max_hops (default: 3)
- Visited set prevents cycles
- Returns full upstream chain + root cause URN
- Checks each upstream dataset for same issue type

### SchemaComparator

Compares schemas between adjacent datasets in lineage chain:
- Detects added fields (in upstream but not downstream)
- Detects removed fields (in downstream but not upstream)
- Detects type changes (same field, different native_type)
- Returns structured diff dict or None

### LlmDiagnosisEngine

LLM-powered analysis of collected evidence:
- Receives: issue details + upstream chain + schema diffs + evidence
- Determines root cause type: schema_change, stale_upstream, broken_pipeline
- Suggests fix approach: dbt_model_patch, sql_patch, dag_update
- Returns confidence score 0.0-1.0
- Falls back to template-based diagnosis if LLM unavailable

### RcaDatabase

Historical pattern storage:
- Caches previous diagnoses by root_cause_type
- find_similar() returns prior diagnosis for same pattern
- Enables faster RCA for recurring issues

## Sequence: RCA Flow

1. IssueRecord received from Detection Engine
2. ContextBuilder gathers full metadata for affected dataset
3. LineageTraverser walks upstream to find root cause
4. SchemaComparator compares each lineage hop
5. LlmDiagnosisEngine synthesizes evidence into diagnosis
6. RcaDatabase stores pattern for future use
7. DiagnosisRecord emitted to Fix Generator
