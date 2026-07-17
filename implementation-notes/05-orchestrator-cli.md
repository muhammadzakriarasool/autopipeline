# Step 5: Orchestrator + CLI

> Completed: July 2026

## Goals
- Create ConfigLoader, StateManager, Orchestrator, run_scheduler
- TDD: 10 tests written and passing
- No regressions in existing 81 tests

## Files Created/Modified

| File | Lines | Action |
|------|-------|--------|
| src/autopipeline/autopilot.py | 137 | Created — 4 components |
| tests/test_autopilot.py | 152 | Created — 10 tests |

## Components Implemented

| Component | Purpose | Key Method |
|-----------|---------|------------|
| ConfigLoader | Parse YAML config with graceful fallback | load() |
| StateManager | Track healed issues to prevent re-processing | mark_healed(), is_healed() |
| Orchestrator | Run full DETECT->DIAGNOSE->FIX->VALIDATE->DOCUMENT cycle | run_once() |
| run_scheduler | Polling loop wrapper | time.sleep + run_once() |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Orchestrator takes callables, not concrete classes | Testability — mock everything |
| ConfigLoader returns empty dict on failure | Graceful degradation |
| StateManager uses set for O(1) lookup | Fast dedup |
| CycleResult is a dataclass, not dict | Type safety, IDE support |
| run_scheduler is a standalone function | Composable with any orchestrator |

## Test Results

```
91 passed in 0.78s
- 20 existing: PASS
- 23 detector: PASS
- 15 diagnosis: PASS
- 14 fixer: PASS
- 9 healer: PASS
- 10 autopilot: PASS
```

## Security Considerations
- No secrets in autopilot.py
- ConfigLoader does not execute YAML (uses safe_load)
- StateManager is in-memory only (no persistence leakage)

## Quality Gate Checklist
- [x] All existing tests still pass (81/81)
- [x] New tests written and passing (10/10)
- [x] No file over 300 lines (137 lines)
- [x] No hardcoded tokens/secrets
- [x] All imports resolve
- [x] Type hints on all public methods
- [x] Docstrings on all public classes
- [x] No TODO/TBD/FIXME
- [x] Git commit clean and descriptive
- [x] Phase file written
- [x] No regressions
