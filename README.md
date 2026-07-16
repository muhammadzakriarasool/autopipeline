# AutoPipeline — Context-Aware Data Pipeline Generator

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![DataHub](https://img.shields.io/badge/DataHub-1.6.0%2B-orange)](https://github.com/datahub-project/datahub)

**AI agents that read DataHub metadata to generate production-ready pipeline code — and write back to the graph.**

Built for the **Build with DataHub: The Agent Hackathon** — *Metadata-Aware Code Generation & Development* category.

---

## 🏆 Why This Wins

| Criterion | How AutoPipeline Delivers |
|-----------|--------------------------|
| **Use of DataHub** | Reads schemas, lineage, ownership, glossary, tags — **and writes back** tags, descriptions, and lineage to the graph |
| **Technical Execution** | Working CLI, 28 unit tests, 4 template types (dbt/SQL/DAG), end-to-end verified against live DataHub |
| **Originality** | First open-source reference implementation of the "Data Engineering Agent" archetype defined in DataHub's own blog |
| **Real-World Usefulness** | Solves the #1 pain point for data engineers: pipeline code that works on the first try because it's grounded in real metadata |
| **Open-Source Contribution** | New `datahub-pipeline-generate` Skill contributed to `datahub-project/datahub-skills` |

> *"Strong submissions go beyond reading metadata and contribute back to the graph where appropriate."* — Hackathon Judging Criteria

---

## Architecture

```
User Request
    │
    ▼
┌─────────────────────────────────────────────────────────┐
│                    AutoPipeline CLI                       │
│  (autopipeline generate, search, inspect, tag, verify)    │
└────────────────────────┬────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
┌──────────────────────┐  ┌──────────────────────┐
│   ContextCollector    │  │    DataHubWriter      │
│  • Schemas & columns  │  │  • Tags (add/remove)  │
│  • Lineage (up/down)  │  │  • Descriptions       │
│  • Ownership          │  │  • Lineage            │
│  • Tags & Glossary    │  │  • Owners             │
│  • Data Quality       │  │  • Glossary Terms     │
└──────────┬───────────┘  └──────────▲────────────┘
           │                          │
           ▼                          │
┌──────────────────────┐              │
│   ContextComposer     │              │
│  (Structured LLM      │              │
│   prompt assembly)    │              │
└──────────┬───────────┘              │
           │                          │
           ▼                          │
┌──────────────────────┐              │
│   PipelineGenerator   │              │
│  ┌─────────────────┐  │              │
│  │ Jinja2 Templates│  │              │
│  │ • dbt_model.sql │  │              │
│  │ • dbt_schema.yml│  │              │
│  │ • sql_transform │  │              │
│  │ • airflow_dag   │  │              │
│  └─────────────────┘  │              │
└──────────┬───────────┘              │
           │                          │
           ▼                          │
┌──────────────────────┐              │
│   Pipeline Artifacts  │──────────────┘
│  (dbt models, SQL,    │  Write-back to
│   DAGs + tests)       │  DataHub graph
└──────────────────────┘
```

---

## Quickstart

### Prerequisites

- Python 3.11+
- Access to a DataHub instance (GMS endpoint)
- DataHub access token

### Install

```bash
git clone https://github.com/muhammadzakriarasool/autopipeline.git
cd autopipeline
pip install -e .
```

### Configure

```bash
export DATAHUB_SERVER=http://your-datahub-server:8080
export DATAHUB_TOKEN=your-access-token
```

### Verify Connectivity

```bash
autopipeline verify
```

### Search Datasets

```bash
autopipeline search -q "order_details"
```

### Inspect a Dataset

```bash
autopipeline inspect "urn:li:dataset:(urn:li:dataPlatform:dbt,...)"
```

Shows full schema (columns, types, descriptions), upstream/downstream lineage, owners, tags, and glossary terms — all from DataHub.

### Generate a Pipeline

```bash
# Preview the context prompt (no file output)
autopipeline generate -q "Daily revenue report" \
  --target "urn:li:dataset:(...)" \
  --dry-run

# Generate actual pipeline artifacts
autopipeline generate -q "Daily revenue report" \
  --target "urn:li:dataset:(...)" \
  --framework dbt
```

### Write Back to DataHub

```bash
# Tag a dataset
autopipeline tag --urn "urn:li:dataset:(...)" \
  --tag "urn:li:tag:AutoPipeline"
```

The tag, description (with generation metadata), and lineage between upstream sources and the generated model are all written to the DataHub graph.

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `verify` | Test DataHub connectivity |
| `search -q <query>` | Search datasets in DataHub catalog |
| `inspect <urn>` | Full metadata context for a dataset |
| `generate -q <prompt> [-t <urn>] [-o <dir>] [--framework dbt|sql|dag] [--dry-run]` | Generate pipeline code |
| `tag --urn <urn> [--tag <urn>]` | Tag a dataset (write-back test) |

---

## Example Artifacts

Generated from the `showcase-ecommerce` dataset loaded in DataHub:

| Example | Framework | Lines | Output |
|---------|-----------|-------|--------|
| `order_details_revenue/` | dbt | 400+ SQL | [View](examples/order_details_revenue/) |
| `promotion_analysis/` | dbt | 30+ SQL | [View](examples/promotion_analysis/) |
| `customer_orders/` | SQL | 50+ SQL | [View](examples/customer_orders/) |
| `order_inventory_dag/` | Airflow DAG | 40+ Python | [View](examples/order_inventory_dag/) |

Each example directory contains:
- **Generated pipeline code** ready for production
- **Schema documentation** (for dbt models)
- **metadata.json** with context info (source dataset, columns, lineage)

---

## Generated Code Features

| Feature | dbt Model | SQL Transform | Airflow DAG |
|---------|-----------|---------------|-------------|
| CTE-based SQL (WITH clauses) | ✅ | ✅ | N/A |
| Column-level type casting | ✅ | ✅ | N/A |
| dbt `source()` references | ✅ | ❌ | N/A |
| Schema YAML with column docs | ✅ | ❌ | N/A |
| Inferred tests (not_null, unique) | ✅ | ❌ | N/A |
| Jinja2 `config()` block | ✅ | ❌ | N/A |
| Schedule configuration | N/A | N/A | ✅ |
| Retry/alert defaults | N/A | N/A | ✅ |
| AutoPipeline metadata header | ✅ | ✅ | ✅ |

---

## Write-Back to DataHub

AutoPipeline doesn't just read from DataHub — it contributes back. After generating a pipeline:

1. ✅ **Tags** the target dataset with `AutoPipeline`
2. ✅ **Updates the description** with generation metadata (timestamp, model name)
3. ✅ **Adds lineage** from upstream sources to the generated model

This means every generated artifact enriches the DataHub catalog for the next user or agent.

---

## Project Structure

```
autopipeline/
├── pyproject.toml              # Package config (Apache 2.0)
├── README.md                   # This file
├── examples/                   # Generated pipeline artifacts
│   ├── order_details_revenue/   # dbt model (55 columns, 11 sources)
│   ├── promotion_analysis/      # dbt model (6 columns)
│   ├── customer_orders/         # SQL transform (22 columns)
│   └── order_inventory_dag/     # Airflow DAG
├── tests/                      # 28 unit tests
│   ├── test_context.py
│   ├── test_context_composer.py
│   ├── test_generator.py
│   └── test_writer.py
└── src/autopipeline/
    ├── __init__.py
    ├── cli.py                  # Click CLI (5 commands)
    ├── connector.py            # DataHub connection wrapper
    ├── context.py              # Metadata collector + dataclasses
    ├── context_composer.py     # LLM prompt assembly
    ├── generator.py            # Jinja2 template rendering
    ├── writer.py               # DataHub write-back mutations
    └── templates/              # Jinja2 pipeline templates
        ├── dbt_model.sql.j2
        ├── dbt_schema.yml.j2
        ├── sql_transform.sql.j2
        └── airflow_dag.py.j2
```

---

## Development

### Run Tests

```bash
python3 -m pytest tests/ -v
```

### Build

```bash
pip install -e .
```

### DataHub Local Instance

This project was developed against a local DataHub Docker instance:
- **GMS API**: `http://172.17.0.1:8080`
- **Frontend**: `http://localhost:9002` (login: `datahub` / `datahub`)
- **Sample Data**: `showcase-ecommerce` (1,307 entities across Snowflake, dbt, Postgres, Looker, Tableau, PowerBI, S3)

---

## License

[Apache 2.0](LICENSE)

---

## Built For

[Build with DataHub: The Agent Hackathon](https://datahub.devpost.com/) — Deadline: Aug 10, 2026

**Category**: Metadata-Aware Code Generation & Development
