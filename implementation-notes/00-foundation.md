# Step 0: Foundation

> Completed: July 2026 | Duration: ~15 minutes

## Goals
- Create implementation-notes/ documentation folder
- Create autopilot-config.yaml
- Update pyproject.toml with new dependencies
- Verify DataHub connection and dataset accessibility
- Confirm all existing tests still pass
- Security review

## Files Created/Modified

| File | Lines | Action |
|------|-------|--------|
| autopilot-config.yaml | 36 | Created — YAML config for AutoPilot with healthcare/DBT scope |
| pyproject.toml | 33 | Modified — added pydantic>=2.0 and schedule>=1.2 |
| implementation-notes/00-foundation.md | This file | Created |

## Problems Solved

1. **Healthcare dataset not available** — `datahub datapack load healthcare` returns "Unknown data pack". Only bootstrap and showcase-ecommerce are available. Adapted to use showcase-ecommerce (1113 datasets) and will plant our own quality assertions for demo.

2. **pytest not installed** — Installed via `pip3 install pytest`. 9.1.1 now available.

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Use showcase-ecommerce instead of healthcare | Healthcare datapack doesn't exist in this DataHub version. 1113 DBT datasets from showcase-ecommerce are sufficient. |
| Add pydantic for config validation | YAML config needs validation. Pydantic v2 is industry standard. |
| Add schedule for polling | Lightweight scheduler for detection engine polling. |
| Config targets DBT platform only | scope.platforms: ["dbt"] — focuses AutoPilot on DBT datasets where we have lineage. |
| Shadow mode default | Safety first — all fixes require human approval by default. |

## Test Results

```
============================== 20 passed in 0.63s ==============================
```

All 20 existing tests pass. No regressions.

## Verification Results

| Check | Status | Evidence |
|-------|--------|----------|
| DataHub connection | PASS | curl 200 OK, SDK search returns 1113 datasets |
| Config parsing | PASS | yaml.safe_load returns correct structure |
| SDK imports | PASS | DataHubClient.from_env() works |
| Dependencies install | PASS | pydantic 2.x, schedule 1.2.2 installed |
| Existing tests | PASS | 20/20 passed in 0.63s |
| No secrets in code | PASS | grep scan clean |
| .env gitignored | PASS | .gitignore contains .env |
| All files under 300 lines | PASS | Max is 176 lines (cli.py) |

## Security Considerations

- Tokens loaded from .env via os.environ.get() — never hardcoded
- .env is in .gitignore
- Config file (autopilot-config.yaml) contains no secrets
- No print/logging of token values

## Quality Gate Checklist

- [x] All existing tests still pass (20/20)
- [x] No hardcoded tokens/secrets
- [x] All imports resolve
- [x] No TODO/TBD/FIXME in production code
- [x] Git commit clean and descriptive
- [x] Phase file written
- [x] No regressions in existing functionality
