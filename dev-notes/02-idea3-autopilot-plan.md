# AutoPilot - Self-Healing Data Pipeline Agent (Idea 3)

This placeholder has been replaced by detailed multi-page documentation.

## Document Index

| File | Description |
|------|-------------|
| [03-idea3-autopilot-vision.md](03-idea3-autopilot-vision.md) | Vision, concept, why we win, free stack |
| [04-idea3-research-synthesis.md](04-idea3-research-synthesis.md) | 50+ source research, API deep dive, risks |
| [05-idea3-architecture.md](05-idea3-architecture.md) | System architecture, modules, data flow, config |
| [06-idea3-detection-layer.md](06-idea3-detection-layer.md) | Detection engine: assertion polling, freshness, schema, volume |
| [07-idea3-diagnosis-engine.md](07-idea3-diagnosis-engine.md) | RCA via lineage traversal, schema comparison, LLM reasoning |
| [08-idea3-fix-generation.md](08-idea3-fix-generation.md) | Fix generation, Jinja2 templates, approval gate |
| [09-idea3-validation-writeback.md](09-idea3-validation-writeback.md) | Validation, DataHub mutations, audit trail |
| [10-idea3-implementation-plan.md](10-idea3-implementation-plan.md) | 22-day execution plan with milestones |
| [11-idea3-security-analysis.md](11-idea3-security-analysis.md) | Threat model, auth, input validation, safe execution |
| [12-idea3-demo-script.md](12-idea3-demo-script.md) | 3-min demo video script and submission checklist |

## Key Differentiators (from deep research)

1. DataHub promised a Data Quality Agent but hasn't built one - we are first
2. The existing datahub-skills/data-quality only creates assertions - we heal
3. Nobody has built a self-healing agent for DataHub - zero competition
4. Entire stack is free (OpenRouter, Ollama, DataHub Docker, Python SDK)
5. All 22 Agent Context Kit tools used (read + write)
6. Healthcare dataset has planted quality issues = perfect demo