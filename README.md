# AutoPilot — Self-Healing Data Pipeline Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![DataHub](https://img.shields.io/badge/DataHub-1.6.0%2B-orange)](https://github.com/datahub-project/datahub)
[![Tests](https://img.shields.io/badge/tests-107%20passing-brightgreen)](tests/)
[![Hackathon](https://img.shields.io/badge/Hackathon-DataHub%20Agent%20Hackathon-red)](https://datahub.devpost.com/)

> The first open-source self-healing data pipeline agent that uses DataHub metadata
> to detect quality issues, diagnose root causes via lineage traversal, generate fixes,
> and document everything back to the graph.

## Demo

[![Demo Video](https://img.shields.io/badge/Watch-Demo%20Video-red?style=for-the-badge&logo=youtube)](https://youtube.com/watch?v=YOUR_VIDEO_ID)

## What It Does

AutoPilot monitors DataHub quality assertions in real-time. When something breaks, it autonomously:

1. **Detects** — Polls assertion results, checks freshness/schema/volume
2. **Diagnoses** — Traces lineage upstream to find root cause
3. **Generates Fix** — Produces dbt/SQL patches grounded in real metadata
4. **Validates** — Re-checks assertion to confirm resolution
5. **Documents** — Writes incident report, tags, and descriptions back to DataHub

```
  DETECT → DIAGNOSE → FIX → VALIDATE → DOCUMENT
  (All state stored in DataHub graph)
```

## Quick Start

```bash
# Install
pip install -e .

# Run tests
python -m pytest tests/ -v

# Start dashboard
streamlit run src/autopipeline/ui/app.py
```

Open `http://localhost:8501` in your browser.

## Dashboard

The Streamlit dashboard provides:

- **Overview** — KPI metrics, health chart, detection timeline
- **Monitor** — Live issue feed with diagnose/fix actions
- **History** — Healing cycle log with audit trail

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                 AutoPilot Orchestrator               │
│                                                      │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐           │
│  │ DETECT  │→ │ DIAGNOSE │→ │   FIX    │           │
│  │detector │  │diagnosis │  │  fixer   │           │
│  └─────────┘  └──────────┘  └──────────┘           │
│       │            │              │                   │
│       ▼            ▼              ▼                   │
│  ┌─────────┐  ┌──────────┐  ┌──────────┐           │
│  │VALIDATE │← │ DOCUMENT │← │  APPLY   │           │
│  │ healer  │  │ healer   │  │ healer   │           │
│  └─────────┘  └──────────┘  └──────────┘           │
│                                                      │
│              DataHub Graph (state)                   │
└─────────────────────────────────────────────────────┘
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.11+ |
| Data Platform | DataHub OSS (Docker) |
| Agent Framework | LangChain AgentExecutor |
| LLM | OpenRouter free tier (28+ models) |
| Dashboard | Streamlit + Plotly |
| Templates | Jinja2 |
| CLI | Click |
| Testing | pytest |

## Project Structure

```
autopipeline/
├── src/autopipeline/          # Core modules
│   ├── detector.py            # Detection engine
│   ├── diagnosis.py           # RCA engine
│   ├── fixer.py               # Fix generation
│   ├── healer.py              # Validation + write-back
│   ├── autopilot.py           # Orchestrator
│   └── ui/app.py              # Streamlit dashboard
├── tests/                     # 107 tests
├── dev-notes/                 # Design documents
├── implementation-notes/      # Phase documentation
├── examples/                  # Generated artifacts
└── autopilot-config.yaml      # Configuration
```

## Open Source Contribution

AutoPilot contributes `datahub-self-heal` Skill to the
[datahub-skills](https://github.com/datahub-project/datahub-skills) registry.

## License

[Apache 2.0](LICENSE)

---

*Built for the [Build with DataHub: The Agent Hackathon](https://datahub.devpost.com/) — Deadline Aug 10, 2026*
