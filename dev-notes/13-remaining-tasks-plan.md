# AutoPilot — Remaining Tasks Plan (Steps 8-9 + UI)

> **Created:** July 2026 | **Deadline:** Aug 10, 2026 @ 5pm EDT
> **Status:** Steps 0-7 complete. Steps 8-9 + UI remaining.

---

## Priority Matrix

| Task | Priority | Effort | Impact on Winning |
|------|----------|--------|-------------------|
| Streamlit Web UI | CRITICAL | 2-3 days | +40% submission quality |
| Demo Video | CRITICAL | 1 day | +30% submission quality |
| README with architecture | HIGH | 0.5 day | +15% readability |
| Example healing artifacts | HIGH | 0.5 day | +10% demo evidence |
| Plant quality issues | HIGH | 0.5 day | +20% demo "wow" moment |
| Security audit | MEDIUM | 0.5 day | Required for quality |
| Devpost submission | CRITICAL | 0.5 day | Must submit to compete |
| Feedback survey | LOW | 5 min | Free $50 |

---

## Task 8A: Plant Quality Issues (0.5 day)

**Goal:** Create fake quality problems in showcase-ecommerce data so the demo has a "before" state.

### What to Plant
1. **Freshness violation:** Update a dataset's description to indicate staleness
2. **Schema drift:** Note which datasets have field mismatches in lineage
3. **Volume anomaly:** Use existing datasets with known row counts

### Files
- `scripts/plant_issues.py` (~50 lines) — Plants demo issues via DataHub SDK

---

## Task 8B: Streamlit Web UI (2-3 days)

**Goal:** Build a web dashboard that makes AutoPilot visually impressive for judges.

### Why Streamlit (Not Gradio)
- Dashboard-focused (vs. Gradio's ML-demo focus)
- Built-in: metrics, tables, charts, tabs, sidebar
- Real-time refresh via `st.rerun()` and `st.empty()`
- Plotly integration for interactive charts
- One `pip install streamlit` away
- Judges can try it locally or via Streamlit Cloud (free hosting)

### UI Architecture

```
src/autopipeline/
  ui/
    __init__.py          (5 lines)
    app.py               (200 lines) — Main Streamlit app
    pages/
      dashboard.py       (150 lines) — Overview: health metrics, charts
      monitor.py         (120 lines) — Live monitoring: issues, pipeline
      healing.py         (120 lines) — Healing history, audit trail
      config.py          (80 lines)  — Configuration page
```

### Dashboard Page
- **4 KPI cards:** Datasets Monitored, Issues Found, Healed, Failed
- **Health status chart:** Pie chart (healthy/warning/critical)
- **Timeline:** Issue detection history over time
- **Top affected datasets:** Bar chart

### Monitor Page
- **Live issue feed:** Table with dataset, issue type, severity, timestamp
- **Lineage visualization:** Show upstream chain for selected issue
- **Schema diff view:** Before/after schema comparison
- **Action buttons:** Diagnose, Fix, Validate (per issue)

### Healing Page
- **Healing history table:** All healed issues with duration
- **Audit trail viewer:** Markdown incident reports rendered
- **Performance metrics:** MTTR, success rate, cycle time
- **DataHub write-back status:** Tags, docs, lineage added

### Config Page
- **Mode selector:** Shadow / Autonomous / Disabled
- **Dataset scope:** Domain, platform, include/exclude URNs
- **Detection settings:** Polling interval, thresholds
- **DataHub connection:** Server URL, token status

### Tech Stack
```
streamlit>=1.35
plotly>=5.18
pandas>=2.0
```

### Files
| File | Lines | Purpose |
|------|-------|---------|
| src/autopipeline/ui/app.py | 200 | Main entry, routing, sidebar |
| src/autopipeline/ui/pages/dashboard.py | 150 | Overview metrics + charts |
| src/autopipeline/ui/pages/monitor.py | 120 | Live issue feed + actions |
| src/autopipeline/ui/pages/healing.py | 120 | History + audit trail |
| src/autopipeline/ui/pages/config.py | 80 | Settings page |
| src/autopipeline/ui/__init__.py | 5 | Package init |
| tests/test_ui.py | 80 | Unit tests for UI logic |

---

## Task 8C: Example Healing Artifacts (0.5 day)

**Goal:** Generate real healing artifacts to show judges.

### Files
| File | Purpose |
|------|---------|
| examples/healing/order_staleness_fix.md | Incident report for freshness fix |
| examples/healing/schema_drift_fix.md | Incident report for schema fix |
| examples/healing/volume_anomaly_fix.md | Incident report for volume fix |

---

## Task 8D: README with Architecture (0.5 day)

**Goal:** Professional README that judges can scan in 30 seconds.

### Structure
```
# AutoPilot — Self-Healing Data Pipeline Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)
[![DataHub](https://img.shields.io/badge/DataHub-1.6.0%2B-orange)](https://github.com/datahub-project/datahub)
[![Tests](https://img.shields.io/badge/tests-103%20passing-brightgreen)](tests/)
[![Hackathon](https://img.shields.io/badge/Hackathon-DataHub%20Agent%20Hackathon-red)](https://datahub.devpost.com/)

## What It Does
[1-paragraph elevator pitch]

## Demo
[Link to 3-min video]

## Architecture
[ASCII diagram]

## Quick Start
[3 commands to run]

## How It Works
[5-stage pipeline explanation]

## Tech Stack
[Table]

## Project Structure
[File tree]

## Open Source Contribution
[datahub-self-heal Skill]

## License
[Apache 2.0]
```

---

## Task 8E: Demo Video Script (1 day)

**Goal:** 3-minute screencast with narration.

### Script (from dev-notes/12-idea3-demo-script.md)

| Time | Screen | Narration |
|------|--------|-----------|
| 0:00-0:30 | DataHub UI showing failed assertion | "Data pipelines break. Here's what it looks like." |
| 0:30-1:00 | AutoPilot dashboard detecting issue | "AutoPilot detected the failure immediately." |
| 1:00-1:30 | Lineage visualization tracing upstream | "It traces lineage to find the root cause." |
| 1:30-2:00 | Generated fix code | "It generates a fix grounded in real metadata." |
| 2:00-2:30 | Approval + validation | "With one click, the fix is applied and validated." |
| 2:30-3:00 | DataHub showing write-back | "Everything is documented back to DataHub." |

### Recording Setup
- OBS Studio (free, screen recording + narration)
- Terminal with dark theme
- DataHub UI in browser
- AutoPilot Streamlit dashboard

---

## Task 9A: Security Audit (0.5 day)

**Goal:** Final security review of all files.

### Checklist
- [ ] No secrets in any source file
- [ ] .env gitignored
- [ ] All tokens from environment
- [ ] No hardcoded URLs
- [ ] Input validation on all public methods
- [ ] Exception handling in all external calls
- [ ] Rate limiting configured
- [ ] Scope confinement working

---

## Task 9B: Final Test Run (0.5 day)

**Goal:** Confirm 100% test pass rate.

### Commands
```bash
python3 -m pytest tests/ -v
python3 -m pytest tests/ --cov=autopipeline
```

---

## Task 9C: Devpost Submission (0.5 day)

**Goal:** Submit before deadline.

### Submission Checklist
- [ ] Public GitHub repo: github.com/muhammadzakriarasool/autopipeline
- [ ] 3-min demo video on YouTube (public)
- [ ] README with architecture diagram
- [ ] Working app (Streamlit UI)
- [ ] Written description
- [ ] Submit: https://datahub.devpost.com/
- [ ] Feedback Survey: free $50

---

## Updated File Tree (Target)

```
autopipeline/
├── .env                              # Credentials (gitignored)
├── .gitignore
├── LICENSE                           # Apache 2.0
├── README.md                         # Professional README with badges
├── pyproject.toml                    # Package config
├── autopilot-config.yaml             # AutoPilot configuration
│
├── dev-notes/                        # Design documents (12 files)
│   ├── 01-development-history.md
│   ├── 02-idea3-autopilot-plan.md
│   ├── 03-idea3-autopilot-vision.md
│   ├── 04-idea3-research-synthesis.md
│   ├── 05-idea3-architecture.md
│   ├── 06-idea3-detection-layer.md
│   ├── 07-idea3-diagnosis-engine.md
│   ├── 08-idea3-fix-generation.md
│   ├── 09-idea3-validation-writeback.md
│   ├── 10-idea3-implementation-plan.md
│   ├── 11-idea3-security-analysis.md
│   ├── 12-idea3-demo-script.md
│   └── 13-remaining-tasks-plan.md    # THIS FILE
│
├── implementation-notes/              # Phase documentation (8 files)
│   ├── 00-foundation.md
│   ├── 01-detection-engine.md
│   ├── 02-rca-engine.md
│   ├── 03-fix-generator.md
│   ├── 04-validation-writeback.md
│   ├── 05-orchestrator-cli.md
│   ├── 06-integration-testing.md
│   └── 07-skill-contribution.md
│
├── src/autopipeline/                  # Source code (15 files)
│   ├── __init__.py                   # Package init
│   ├── config.py                     # Environment config
│   ├── context.py                    # DataHub metadata context
│   ├── connector.py                  # DataHub SDK wrapper
│   ├── detector.py                   # Detection engine
│   ├── diagnosis.py                  # RCA engine
│   ├── fixer.py                      # Fix generation
│   ├── healer.py                     # Validation + write-back
│   ├── autopilot.py                  # Orchestrator + config
│   ├── agent.py                      # LangChain agent
│   ├── composer.py                   # LLM prompt assembly
│   ├── generator.py                  # Jinja2 template rendering
│   ├── llm.py                        # LLM client
│   ├── writer.py                     # DataHub mutations
│   ├── cli.py                        # Click CLI
│   ├── templates/                    # Jinja2 templates (4 files)
│   │   ├── dbt_model.sql.j2
│   │   ├── dbt_schema.yml.j2
│   │   ├── sql_transform.sql.j2
│   │   └── airflow_dag.py.j2
│   └── ui/                           # Streamlit Web UI (NEW)
│       ├── __init__.py
│       ├── app.py                    # Main entry
│       └── pages/
│           ├── dashboard.py          # Overview metrics
│           ├── monitor.py            # Live monitoring
│           ├── healing.py            # Healing history
│           └── config.py             # Settings
│
├── scripts/                          # Utility scripts (NEW)
│   └── plant_issues.py               # Plant demo quality issues
│
├── examples/                         # Generated artifacts
│   ├── customer_orders/
│   ├── order_details_revenue/
│   ├── order_inventory_dag/
│   ├── promotion_analysis/
│   └── healing/                      # Healing incident reports (NEW)
│       ├── order_staleness_fix.md
│       ├── schema_drift_fix.md
│       └── volume_anomaly_fix.md
│
├── skills/                           # DataHub Skills
│   └── datahub-pipeline-generate/
│       ├── SKILL.md
│       └── README.md
│
├── tests/                            # Tests (10 files)
│   ├── test_context.py
│   ├── test_composer.py
│   ├── test_generator.py
│   ├── test_detector.py
│   ├── test_diagnosis.py
│   ├── test_fixer.py
│   ├── test_healer.py
│   ├── test_autopilot.py
│   ├── test_integration.py
│   └── test_ui.py                    # NEW
│
└── datahub-skills/                   # Forked repo (separate)
    └── skills/datahub-self-heal/
        └── SKILL.md
```

---

## Estimated Timeline

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| Day 1 | Plant issues + UI scaffold | scripts/plant_issues.py, ui/app.py skeleton |
| Day 2 | UI dashboard + monitor pages | Working dashboard with metrics + issue feed |
| Day 3 | UI healing + config pages + tests | Complete UI, 100+ tests |
| Day 4 | Example artifacts + README | examples/healing/, polished README |
| Day 5 | Security audit + final test run | All tests pass, no security issues |
| Day 6-7 | Record demo video | 3-min screencast with narration |
| Day 8 | Devpost submission | Submit + feedback survey |
| Day 9-10 | Buffer for fixes | Bug fixes, polish, community feedback |

**Total: 10 days (Jul 18-27) + 14 days buffer (Jul 28 - Aug 10)**
