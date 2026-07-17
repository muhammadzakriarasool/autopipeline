# AutoPilot - Security Analysis

> Security Review | July 2026 | Top-tier security for AI agent

## Threat Model

| Threat | Vector | Impact | Likelihood | Mitigation |
|--------|--------|--------|-----------|------------|
| Compromised DataHub token | .env file leak | Full DataHub access | Low | .gitignore; file permissions 600; never log token |
| LLM prompt injection | Crafted issue descriptions | Hallucinated fixes | Medium | Input validation; fix must match actual schema; approval gate |
| Scope escape | Misconfigured config | Healing unintended datasets | Low | Domain/ownership filtering; exclude URNs list; validation |
| Token in LLM context | Token passed to LLM as text | API keys exposed | Low | Tokens never enter LLM context; read from env at runtime only |
| Cascade bad fix | Auto-apply wrong patch | Data corruption | Low | Shadow mode default; patches are suggestions, not auto-executed |
| API flooding | Aggressive polling | DataHub performance degradation | Low | 300s default interval; configurable; respects 429 responses |
| Dependency supply chain | Compromised pip package | Code execution | Low | Pin versions; use pip-audit; no unusual dependencies |
| Memory exposure | Sensitive data in debug logs | Information leak | Medium | Structured logging; no PII in logs; redact tokens |

## Security Controls (Layered Defense)

### Layer 1: Authentication and Authorization
- DataHub token stored in .env only (in .gitignore)
- Token loaded from environment at runtime, never hardcoded
- Configurable scope: only datasets in specified domains/ownership
- Exclude URNs list prevents healing blacklisted datasets
- Token never passed to LLM as context or history

### Layer 2: Input Validation
- Dataset URNs validated against DataHub before any operation
- Configuration YAML validated with strict Pydantic model
- LLM outputs constrained to structured fix plans (not freeform SQL)
- All generated code checked against actual schema before write-back
- Lineage traversal bounded by max_hops (default 3, max 5)

### Layer 3: Safe Execution
- Default mode is SHADOW: human approval required for all fixes
- Autonomous mode restricted to non-destructive fix types only
- Code patches written to filesystem only, never auto-executed
- Every write-back stores rollback information
- Rate limiting: configurable polling intervals respect API limits

### Layer 4: Data Protection
- Reads ONLY metadata: schemas, types, descriptions, lineage
- Never reads actual data content (rows, values, records)
- No data warehouse credentials needed (queries DataHub graph only)
- Incident documents contain technical metadata only, no PII
- All mutations logged in DataHub audit trail

### Layer 5: Operational Security
- No external services contacted except DataHub + OpenRouter
- OpenRouter requests use HTTPS; tokens in headers only
- Local Ollama fallback available for air-gapped execution
- All state in-memory (no SQLite/postgres with sensitive data)
- Debug mode disabled by default; only enabled with explicit flag

## Dependency Security
| Package | Version Pin | Known Issues |
