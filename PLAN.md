# PLAN.md

## Feature Plan

**Feature Name:** Remedial Recovery Management System  
**Type:** CRUD + Workflow + Dashboard + Report + Scheduled Monitoring  
**Domain App:** `apps/remedial` (with shared `core` audit utilities if needed)  
**Users/Roles:** Loan Officer, Branch Manager, Compliance, Auditor  
**Risk Level:** Medium  
**Financial Mutation:** None (no GL/CBS posting)  
**Infra Decision:** cron + Django management commands (no Celery/Redis for MVP)

### Scope

- Track remedial accounts and lifecycle stages.
- Manage compromise agreements with manually encoded payment schedules.
- Track legal cases, hearings, foreclosure/dacion milestones, and write-off endorsements.
- Handle document uploads with versioning and audit traceability.
- Run daily monitoring jobs for reminders, defaults, and escalations.
- Provide role-based dashboards/reports with CSV/PDF export.

### Defaults (Approved)

- `grace_days = 3`
- `default_threshold_days = 30`
- Defaults are prefilled and **editable per agreement**.

## Architecture Decisions

- Django templates + HTMX only (server-rendered).
- Services/Selectors mandatory:
  - `selectors.py` for all reads.
  - `services.py` for all business logic and transitions.
- CRUD = CBVs; workflow transitions/actions = FBVs.
- Forms required for all input (no manual `request.POST` parsing).
- Approved/non-draft records immutable except allowed actions (payments, notes, uploads).
- Soft-delete only for draft records.
- Mandatory audit logging for critical actions and status changes.

## Detailed Backlog (Execution Order)

1. **Schema & Admin**
   - Create models, enums, indexes, and constraints.
   - Register all models in Django admin.

2. **Services & Selectors**
   - Implement transition guards and validation logic.
   - Implement payment allocation and completion/default detection.
   - Centralize audit log creation.

3. **Forms, Views, URLs, Templates**
   - Build CBV CRUD and FBV workflows.
   - Add HTMX partials for list filters/status blocks.
   - Enforce role-based button visibility and backend 403 checks.

4. **Scheduled Monitoring (cron)**
   - Implement management commands:
     - `scan_compromise_due_reminders`
     - `scan_compromise_overdue_default`
     - `scan_upcoming_hearings`
     - `scan_recovery_milestones_overdue`
     - `rollup_next_hearing_date`
     - `run_remedial_data_quality_checks`

5. **Dashboard/Reports**
   - Build aggregate selectors and filtered report screens.
   - CSV first, PDF second.
   - Enforce pagination and mandatory filters for heavy reports.

6. **Testing & Final Review**
   - Service logic, transitions, permissions, idempotency, report filters.
   - Run AI review checklist before completion.

## Role-Permission Matrix (Workflow Mapping)

| Workflow Action | Endpoint | Loan Officer | Branch Manager | Compliance | Auditor |
|---|---|---:|---:|---:|---:|
| Approve Compromise | `/remedial/compromise-agreements/<pk>/approval/` | No | Yes | No | No |
| Record Compromise Payment | `/remedial/compromise-agreements/<pk>/payments/create/` | Yes | Yes | No | No |
| File Legal Case | `/remedial/legal-cases/<pk>/filing/` | No | Yes | No | No |
| Initiate Recovery Action | `/remedial/recovery-actions/<pk>/initiation/` | No | Yes | No | No |
| Recommend Write-off | `/remedial/writeoff-requests/<pk>/recommendation/` | No | Yes | No | No |
| Record Board Decision | `/remedial/writeoff-requests/<pk>/board-decision/` | No | Yes | Yes (recommended) | No |
| Upload Document | `/remedial/documents/upload/` | Yes | Yes | Yes | No |
| View Audit Logs | `/remedial/audit-logs/` | No | No | Yes | Yes |

> Note: all roles listed above have read access to list/detail/report/dashboard pages based on scope.

## Cron Runbook

### Schedule

- `07:00` due reminders
- `07:10` overdue/default scan
- `07:20` hearing reminders
- `07:30` milestone overdue scan
- `07:40` next hearing rollup
- Monday `08:00` weekly data-quality checks

### Lock Strategy

- Layer 1: OS lock via `flock` per command.
- Layer 2: DB advisory lock per command key.
- If lock not acquired, exit as `skipped_lock` (non-fatal).

### Failure Handling

- Exit `0`: success/skipped_lock
- Exit `2`: partial success (record-level failures)
- Exit `1`: fatal failure

Policy:
- Retry once after 5 minutes for fatal failures.
- No retry for lock skips.
- Replay with `--as-of-date` after fix.
- Escalate repeated failures to operations + compliance visibility.

### Log Format (JSON lines)

Required fields:
- `ts`, `level`, `job`, `run_id`, `as_of_date`, `status`, `duration_ms`,
- `records_scanned`, `records_updated`, `notifications_sent`,
- `notifications_failed`, `errors_count`, `host`, `pid`

## TODO List

- [ ] Create `apps/remedial` with canonical structure.
- [ ] Implement all domain models and migrations.
- [ ] Add DB constraints (including one-active-compromise rule).
- [ ] Register admin classes with filters/search.
- [ ] Implement selectors for read paths.
- [ ] Implement services for transitions/validation/audit.
- [ ] Build forms and web endpoints (CBV/FBV split).
- [ ] Implement document versioning and file validation.
- [ ] Implement all cron management commands.
- [ ] Add dashboard/reports and CSV export.
- [ ] Add role/permission assignments and endpoint enforcement.
- [ ] Add automated tests and run final checklist.

## Completed Tasks

- [x] PRD reviewed and feature classified.
- [x] Architecture aligned with governance docs in `REFERENCES/`.
- [x] Development plan finalized.
- [x] Role-permission matrix drafted and mapped to endpoints.
- [x] Cron runbook drafted with locks, retries, and logging format.
- [x] Defaults confirmed (`grace_days=3`, `default_threshold_days=30`).

## Open Questions

- None blocking for implementation start.

## Risk Notes

- **Workflow integrity risk:** invalid transitions; mitigate with service guards + tests.
- **RBAC risk:** unauthorized state changes; mitigate with view + service enforcement and audit logs.
- **Data integrity risk:** duplicate active compromises; mitigate with DB partial unique constraint.
- **Notification spam risk:** duplicate escalations; mitigate with idempotency keys and notification log checks.
- **Performance risk:** report growth over time; mitigate with indexes, required filters, and pagination.
