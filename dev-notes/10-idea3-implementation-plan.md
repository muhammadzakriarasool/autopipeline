# AutoPilot - Implementation Plan

> Execution Order | July 2026 | Deadline: Aug 10, 2026 @ 5pm EDT
> Total: 22 days (July 17 - Aug 8) + 2 day buffer

## Phase 0: Prerequisites (Day 1-2)

- [ ] Load healthcare dataset into DataHub: datahub datapack load healthcare
- [ ] Verify healthcare entities accessible via SDK
- [ ] Plant 5+ quality assertions on healthcare tables
- [ ] Verify all 22 Agent Context Kit tools work
- [ ] Pin dependency versions in pyproject.toml
- [ ] Verify OpenRouter free tier key works
- [ ] Install Ollama + Phi-4-mini as local fallback (optional)
- [ ] Create autopilot-config.yaml with healthcare domain scope

## Phase 1: Detection Engine (Day 3-5)

- [ ] Implement AssertionPoller: query assertion results via GraphQL
- [ ] Implement FreshnessMonitor: check lastModified timestamps
- [ ] Implement SchemaWatcher: compare schemas across hops
- [ ] Implement VolumeAnalyzer: baseline + threshold detection
- [ ] Implement IssueRegistry: dedup and lifecycle tracking
- [ ] Write unit tests for each sub-component
- [ ] Integration test: poll assertions -> detect 3+ failures
- [ ] Commit: feat: detection engine

## Phase 2: RCA Engine (Day 6-8)

- [ ] Implement ContextBuilder: gather full metadata for affected dataset
- [ ] Implement LineageTraverser: recursive upstream BFS, max 3 hops
- [ ] Implement SchemaComparator: field-by-field comparison
- [ ] Implement LlmDiagnosisEngine: evidence -> RCA via LLM
- [ ] Implement RcaDatabase: cache historical patterns
- [ ] Integration test: issue -> diagnosis -> root cause identified
- [ ] Commit: feat: rca engine via lineage traversal

## Phase 3: Fix Generator (Day 9-11)

- [ ] Implement FixPlanner: LLM-based fix strategy
- [ ] Implement CodeGenerator: reuse Phase 2 Jinja2 templates
- [ ] Implement ApprovalGate: shadow vs autonomous mode
- [ ] Integration test: diagnosis -> fix plan -> patch generation
- [ ] Commit: feat: fix generation engine

## Phase 4: Validation + Write-Back (Day 12-14)

- [ ] Implement RevalidationEngine: re-check assertion after fix
- [ ] Extend DataHubWriter: structured properties, documents
- [ ] Implement AuditTrailGenerator: incident report in DataHub
- [ ] Integration test: fix -> re-validate -> write-back complete
- [ ] Commit: feat: validation and write-back

## Phase 5: Scheduler + CLI (Day 15-17)

- [ ] Implement autopilot.py Orchestrator: full cycle orchestration
- [ ] Extend CLI: autopilot watch, autopilot heal, autopilot status
- [ ] Config file parsing: YAML validation with Pydantic
- [ ] Full end-to-end test: detection -> healing cycle
- [ ] Commit: feat: autopilot orchestrator and CLI

## Phase 6: Open-Source Contribution (Day 18-19)

- [ ] Create datahub-self-heal Skill in datahub-skills fork
- [ ] Update PR #1 with new skill + architecture docs
- [ ] Add examples/ with 3+ generated healing artifacts
- [ ] Commit: feat: datahub-self-heal skill contribution

## Phase 7: Demo + Submission (Day 20-22)

- [ ] Record 3-min demo video (show full detection->healing cycle)
- [ ] Write README with architecture diagram + badge
- [ ] Final testing on healthcare dataset
- [ ] Push to GitHub
- [ ] Submit on Devpost: https://datahub.devpost.com/
- [ ] Submit Feedback Survey: free $50 Amazon gift card
- [ ] Deadline: Aug 10, 2026 @ 5:00pm EDT

## Milestone Verification

| Milestone | Day | Proof |
|-----------|-----|-------|
| Detection works | 5 | CLI detects 3+ assertion failures on healthcare data |
| RCA works | 8 | Agent traces lineage and identifies root cause dataset |
| Fix generation works | 11 | Agent generates valid dbt model patch |
| Write-back works | 14 | DataHub shows new tags, description, incident doc |
| Full cycle works | 17 | End-to-end: detect -> diagnose -> fix -> document in <5min |
| Skill contributed | 19 | PR visible on GitHub with datahub-self-heal skill |
| Submitted | 22 | Devpost page shows submission + demo video |