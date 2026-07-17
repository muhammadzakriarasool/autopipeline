# Step 3: Fix Generator

> Completed: July 2026

## Goals
- Create FixRecord dataclass
- Implement FixPlanner, CodeGenerator, ApprovalGate
- TDD: 14 tests written and passing
- No regressions in existing 58 tests

## Files Created/Modified

| File | Lines | Action |
|------|-------|--------|
| src/autopipeline/fixer.py | 99 | Created — 3 sub-components |
| tests/test_fixer.py | 129 | Created — 14 tests |

## Components Implemented

| Component | Purpose | Key Method |
|-----------|---------|------------|
| FixRecord | Dataclass for fix artifacts | Auto-UUID, approval status |
| FixPlanner | Maps root_cause_type to fix_type | plan() |
| CodeGenerator | Generates patches from diagnosis + metadata | generate_patches() |
| ApprovalGate | Shadow vs autonomous mode control | requires_approval(), approve() |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| FixPlanner uses config map, not LLM | Deterministic, testable, no API cost |
| CodeGenerator produces dict of filename->content | Flexible output format |
| ApprovalGate checks fix_type against auto_approve set | Simple, config-driven |
| All components take raw data | Same pattern as detector/diagnosis |

## Test Results



## Security Considerations
- No secrets in fixer.py
- No external network calls
- ApprovalGate prevents auto-apply of dangerous fix types

## Quality Gate Checklist
- [x] All existing tests still pass (58/58)
- [x] New tests written and passing (14/14)
- [x] No file over 300 lines (99 lines)
- [x] No hardcoded tokens/secrets
- [x] All imports resolve
- [x] Type hints on all public methods
- [x] Docstrings on all public classes
- [x] No TODO/TBD/FIXME
- [x] Git commit clean and descriptive
- [x] Phase file written
- [x] No regressions
