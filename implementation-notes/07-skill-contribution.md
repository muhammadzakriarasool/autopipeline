# Step 7: Open-Source Skill Contribution

> Completed: July 2026

## Goals
- Create datahub-self-heal Skill for datahub-skills repo
- Push to fork (github.com/muhammadzakriarasool/datahub-skills)
- Follow existing skill format (SKILL.md with YAML frontmatter)

## Files Created/Modified

| File | Lines | Location | Action |
|------|-------|----------|--------|
| skills/datahub-self-heal/SKILL.md | 233 | datahub-skills/ | Created — full skill definition |

## Skill Structure

```
skills/datahub-self-heal/
  SKILL.md    # YAML frontmatter + markdown body
```

## Skill Content

| Section | Purpose |
|---------|---------|
| Multi-Agent Compatibility | Works with Claude Code, Cursor, Codex, etc. |
| Not This Skill | Redirects to datahub-quality, datahub-enrich, etc. |
| Content Trust Boundaries | URN validation, shell metacharacter rejection |
| Step 1: Detect Issues | Search for failing assertions and active incidents |
| Step 2: Diagnose Root Cause | Lineage traversal, root cause classification |
| Step 3: Generate Fix | Fix generation per issue type |
| Step 4: Validate and Document | Re-validation, write-back, incident report |
| Safety Controls | Shadow mode, scope limits, rollback |

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| Follows datahub-quality format | Consistency with existing skills |
| Includes GraphQL examples | Agents can execute directly |
| Safety controls prominent | Self-healing must have guardrails |
| Content trust boundaries | Prevents prompt injection |

## Push Details

- **Repo:** github.com/muhammadzakriarasool/datahub-skills
- **Branch:** feat/datahub-pipeline-generate
- **Commit:** b2aec3f

## Quality Gate Checklist
- [x] Skill follows existing format (YAML frontmatter + markdown)
- [x] Includes Multi-Agent Compatibility section
- [x] Includes Not This Skill section
- [x] Includes Content Trust Boundaries
- [x] Includes step-by-step workflow
- [x] Includes safety controls
- [x] No hardcoded tokens/secrets
- [x] Git commit clean and descriptive
- [x] Phase file written
