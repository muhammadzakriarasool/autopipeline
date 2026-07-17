# AutoPilot — Demo Script & Submission Plan

> **3-Minute Video Script** | July 2026

## Demo Scenario

Setting: Healthcare dataset with planted quality issues loaded in DataHub

## Script (3 minutes)

### 0:00 - 0:30 — The Problem

"Data pipelines break. Schema changes, stale data, null spikes."
Engineers spend 60% of their time firefighting.
Screenshot: Failed assertion in DataHub UI on healthcare.patient_records
"A freshness assertion just failed. The table has not updated in 8 hours."

### 0:30 - 1:00 — Detection

"AutoPilot polls DataHub assertions every 5 minutes."
Split screen:
  Left: terminal running `autopilot watch --domain healthcare`
  Right: DataHub UI showing assertion status
Terminal output shows:
  [DETECT] Freshness failure: patient_records
  [SEVERITY] critical

### 1:00 - 1:30 — Diagnosis

"AutoPilot traces lineage upstream to find the root cause."
Show lineage visualization:
  patient_records <- encounter_data <- etl_job <- source_system
Terminal output:
  [RCA] Traced lineage: patient_records -> encounter_data -> etl_job
  [RCA] Root cause: source_system added column insurance_provider
  [RCA] Schema diff: +1 column, 0 removed, 1 type change

### 1:30 - 2:00 — Fix Generation

"AutoPilot generates a fix: updates the dbt model for the new column."
Show the generated code patch:
  - Model before: missing insurance_provider
  - Model after: includes COALESCE(insurance_provider, Unknown)
Terminal output:
  [FIX] Generated: dbt model patch (+12 lines)
  [FIX] Waiting for approval (shadow mode)...

### 2:00 - 2:30 — Apply & Validate

"With one click, the fix is applied and validated."
Terminal output:
  [APPROVE] Fix approved
  [APPLY] Patch written to models/staging/patient_records.sql
  [VALIDATE] Re-running assertion... PASSED

### 2:30 - 3:00 — Write-Back & Impact

"AutoPilot documents everything back to DataHub."
Show DataHub UI with:
  - New tag: AutoPilot-healed
  - Updated description with incident summary
  - Structured property: last_healed_at
  - Incident document linked to the dataset
Terminal output:
  [WRITE-BACK] Tag added: AutoPilot-healed
  [WRITE-BACK] Description updated
  [WRITE-BACK] Incident doc created: urn:li:document:ap-20260717-001
  [DONE] Cycle complete: 142 seconds

"AutoPilot. Self-healing pipelines, powered by DataHub."

## Recording Checklist

- [ ] Screen recording software (OBS, macOS QuickTime)
- [ ] Terminal with nice theme (Dracula, Monokai)
- [ ] DataHub UI open to assertions page
- [ ] Split terminal view for watch + details
- [ ] No sensitive info visible
- [ ] 1080p resolution, clear font
- [ ] Microphone check (quiet environment)
- [ ] Close all unrelated tabs/windows

## Submission Checklist

- [ ] Public GitHub repo (Apache 2.0 license)
- [ ] Working app with CLI
- [ ] README with architecture diagram
- [ ] 3-minute demo video on YouTube/Vimeo (public)
- [ ] Devpost submission: https://datahub.devpost.com/
- [ ] Feedback survey (free $50 Amazon gift card)
- [ ] Deadline: Aug 10, 2026 @ 5:00pm EDT