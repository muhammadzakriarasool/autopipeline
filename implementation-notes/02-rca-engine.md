# Step 2: RCA Engine

> Completed: July 2026

## Goals
- Create DiagnosisRecord dataclass
- Implement SchemaComparator, LineageTraverser, RcaDatabase, ContextBuilder
- TDD: 15 tests written and passing
- No regressions in existing 43 tests

## Files Created/Modified

| File | Lines | Action |
|------|-------|--------|
| src/autopipeline/diagnosis.py | 121 | Created — 5 sub-components |
| tests/test_diagnosis.py | 159 | Created — 15 tests |

## Components Implemented

| Component | Purpose | Key Method |
|-----------|---------|------------|
| DiagnosisRecord | Dataclass for RCA results | Auto-UUID, confidence score |
| ContextBuilder | Build evidence dict from IssueRecord + metadata | build_evidence() |
| SchemaComparator | Compare two field lists for additions/removals/types | compare(), compare_with_types() |
| LineageTraverser | BFS upstream traversal with cycle detection | find_root() |
| RcaDatabase | Historical pattern cache by root_cause_type | store(), find_similar() |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| All components take raw data, not DataHubClient | Same pattern as detector.py — trivial unit testing |
| LineageTraverser uses deque for BFS | Efficient traversal, handles wide lineage graphs |
| Cycle detection via visited set | Prevents infinite loops in circular lineage |
| RcaDatabase keyed by root_cause_type | Fast lookup for recurring issue patterns |
| SchemaComparator.compare_with_types separate from compare | Type-aware comparison needs different input format |

## Test Results



## Security Considerations
- No secrets in diagnosis.py
- No external network calls in unit tests
- LineageTraverser bounded by max_hops (default 3)

## Quality Gate Checklist
- [x] All existing tests still pass (43/43)
- [x] New tests written and passing (15/15)
- [x] No file over 300 lines (121 lines)
- [x] No hardcoded tokens/secrets
- [x] All imports resolve
- [x] Type hints on all public methods
- [x] Docstrings on all public classes
- [x] No TODO/TBD/FIXME
- [x] Git commit clean and descriptive
- [x] Phase file written
- [x] No regressions
