# AutoPilot - Self-Healing Data Pipeline Agent (Idea 3)

> Vision Document | July 2026 | Build with DataHub: The Agent Hackathon
> Category: Metadata-Aware Code Generation & Development (Category 2)

## Elevator Pitch (1 sentence)

AutoPilot is the FIRST open-source Data Quality + Data Engineering Agent that
closes the loop: detect quality failures via DataHub assertions, diagnose root
cause via lineage traversal, generate a fix grounded in real metadata, and write
everything back to the DataHub graph as an auditable incident.

## Why We Are THE Winning Entry

### DataHub literally promised this and hasn't delivered it

DataHub's official blog 'Building Autonomous Data Agents' (April 2026) defines 4 agent
archetypes. For Data Quality Agent, they say:

> A Data Quality Agent: An agent that provisions data quality checks and reports on
> the health of your data estate. This will be covered next time.

They wrote about it in April. It is July. Nobody has built it yet.
The datahub-skills repo has a basic data-quality skill (PR #16) that only creates
and lists assertions. It does NOT detect failures, diagnose root causes, or heal.

We will be the first team to ship a working Data Quality Agent for DataHub.

### The datahub-skills quality skill vs AutoPilot

| Component | datahub-skills/data-quality | AutoPilot (Us) |
|-----------|---------------------------|----------------|
| Function | Creates assertions only | Detects + diagnoses + heals |
| Closed loop | No | Yes |
| Lineage-based RCA | No | Yes |
| Auto-fix generation | No | Yes (dbt/SQL) |
| Incident documentation | No | Yes (writes to DataHub) |
| Write-back scope | Only creates assertions | Tags, docs, lineage, incidents, props |

### We use ALL the tools, not just search

The Agent Context Kit has 22 tools. AutoPilot uses all of them:
- Read: search, get_entities, list_schema_fields, get_lineage, get_dataset_assertions
- Write: add_tags, update_description, save_document, add_structured_properties,
  add_glossary_terms, add_owners, set_domains
  Most entries only use search + get_entities.

## The Closed-Loop Architecture

  DETECT -----> DIAGNOSE -----> FIX -----> VALIDATE -----> DOCUMENT
  Assertions    Lineage+LLM     dbt/SQL    Re-check       Write to graph
  Freshness     Schema diff     Patches    Pass/Fail      Tags+Docs+Incidents
  Volume        Root cause      Generate   Assertion      Structured props

## What is FREE to build and run

| Component | Free Option | Cost |
|-----------|-------------|------|
| DataHub instance | datahub docker quickstart (local) | $0 |
| LLM (cloud) | OpenRouter free tier (28+ models, no CC) | $0 |
| LLM (local backup) | Ollama + Phi-4-mini or Llama 3.2 3B | $0 |
| Python SDK | acryl-datahub (open source) | $0 |
| Agent Context Kit | datahub-agent-context[langchain] | $0 |
| All tools (Jinja2, Click, Rich) | Already in project | $0 |
| Host machine | Laptop (Linux Mint, AMD Ryzen 5, 13.5GB) | $0 |
| License | Apache 2.0 | $0 |

The ENTIRE stack is free. No API keys required for core functionality.

## Guardrails

- Shadow Mode (default): Detects, diagnoses, documents but does NOT apply automatically.
- Autonomous Mode: Auto-apply for low-risk (doc_fix, assertion_update).
- Human-in-loop: Always required for dbt_model_patch, sql_patch, dag_update.
- Rollback: Every fix has enough context to undo.
- Rate limiting: Configurable polling intervals (300s default).
- Scope: Only configured domains/ownership.