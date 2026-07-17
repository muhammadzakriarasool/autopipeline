# AutoPilot - Deep Research Synthesis

> Research Date: July 2026 | Sources: 50+ (docs, GitHub, blogs, communities, academic)

## Critical Finding: We Fill a Gap DataHub Officially Acknowledges

| What DataHub Says | What We Found | Why It Matters |
|-------------------|--------------|----------------|
| Data Quality Agent is 1 of 4 archetypes | No reference implementation exists | We are first movers |
| Will be covered next time (April 2026) | Still not covered July 2026 | Gap confirmed |
| datahub-skills has data-quality skill | Only creates/asserts, does not heal | Our IP is safe |
| Analytics Agent exists (text-to-SQL) | 34 stars, 13 contributors | Pattern is proven |
| Strong submissions go beyond reading | We write back extensively | We win this criterion |

## Industry Validation (July 2026)

| Source | Finding | Our Implication |
|--------|---------|----------------|
| LinkedIn DE Survey (2026) | 59% say pressure to move fast is #1 pain | Speed of resolution critical |
| Qualdo (2026) | Self-healing pipelines replace on-call systems | Market validates production-readiness |
| TDWI (March 2026) | Self-Healing and Intelligent Data Delivery at Scale | Enterprise-grade pattern |
| DataHub Blog (July 2026) | Context Management is the Missing Piece in Agentic AI | Our approach is exactly what they advocate |
| DataHub Context Activation (May 2026) | Pushing accuracy beyond 90% | Our agent leverages this |
| Academic Paper (IJSRST) | Predictive monitoring + self-healing validated | Academic backing |

## Three Architecture Patterns

Pattern 1: Reactive Monitoring - Monte Carlo, Sifflet, Bigeye ($50K+/yr)
Rule-based alerts -> Human investigates -> Manual fix -> Document

Pattern 2: Semi-Autonomous - Databricks Lakehouse Monitoring
ML anomaly detection -> Diagnosis suggested -> Human approves -> Auto-apply

Pattern 3: Fully Autonomous Closed-Loop (OURS)
Assertion monitoring -> AI diagnosis -> Auto-fix -> Validate -> Document
**Nobody in open source** - gap we fill

## DataHub Assertions - OSS vs Cloud

| Feature | OSS (Docker) | Cloud |
|---------|-------------|-------|
| Ingest and display assertion results | Yes (dbt, GE, custom) | Yes |
| Run active assertions against warehouse | No | Yes |
| Anomaly detection | No | Yes |
| Create assertion definitions | Yes (via API) | Yes |
| Report custom assertion results | Yes (via SDK) | Yes |
| Incidents | Yes | Yes (with notifications) |

### Our Strategy for OSS DataHub

Since active assertions require DataHub Cloud, we build our OWN detection engine:
1. Poll assertion results already stored in DataHub (from ingestion)
2. Check freshness by comparing lastModified timestamps on entities
3. Check volume by comparing dataset profile row counts
4. Check schema by comparing stored schemas across lineage hops
5. Report custom assertion results via SDK to simulate Cloud behavior

## GitHub Repo Analysis

| Repo | Stars | What We Learn |
|------|-------|--------------|
| analytics-agent | 34 | LangGraph + FastAPI + React. /improve-context write-back. Context quality scoring. |
| Self-Healing-Data-Pipelines | 3 | Isolation Forest + Gemini. Single-file, no metadata platform. |
| Self-Healing-ML-Pipelines | New | Similar cycle for ML. No DataHub integration. |
| datahub-skills | 30 | Skills format. data-quality skill only creates assertions. |

## Risks and Mitigations

| Risk | Likelihood | Mitigation |
|------|-----------|------------|
| get_dataset_assertions behavior differs | Medium | Fallback to GraphQL; custom tool |
| Healthcare dataset assertions not accessible | Medium | Plant own assertions via SDK |
| LLM hallucinates fixes | High | Schema validation + Shadow Mode approval |
| Agent Context Kit API changes | Low | Pin versions in pyproject.toml |
| OpenRouter rate limits (20 req/min) | Medium | Queue tasks; local Ollama fallback |
| Container state resets | Medium | Setup script; check state first |

## References (July 2026)

- https://docs.datahub.com/docs/dev-guides/agent-context/agent-context
- https://docs.datahub.com/docs/api/tutorials/assertions
- https://docs.datahub.com/docs/features/feature-guides/observe
- https://docs.datahub.com/docs/dev-guides/agent-context/langchain
- https://datahub.com/blog/building-autonomous-data-agents/
- https://datahub.com/blog/datahub-analytics-agent/
- https://github.com/datahub-project/analytics-agent
- https://github.com/datahub-project/datahub-skills
- https://github.com/Pradeepkarra1/Self-Healing-Data-Pipelines
- https://openrouter.ai/collections/free-models