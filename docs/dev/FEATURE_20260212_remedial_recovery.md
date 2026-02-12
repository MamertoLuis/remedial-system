# Feature Plan – Remedial Recovery Management System

## Feature Plan
**Feature Name:** Remedial Recovery Management System
**Type:** CRUD + Workflow + Monitoring + Dashboard/Report
**Domain App:** apps/remedial
**Risk Level:** Medium
**Domain Impact:** Remedial/Legal Case Management (no GL mutation)

### Models Impact
* New models: `RemedialAccount`, `CompromiseAgreement`, `CompromiseScheduleItem`, `CompromisePayment`, `LegalCase`, `CourtHearing`, `RecoveryAction`, `RecoveryMilestone`, `WriteOffRequest`, `RemedialDocument`, `NotificationRule`, `NotificationLog`, shared `AuditLog` from core.
* Indexes: stage/status combos, due dates, partial unique constraint for active compromise per account, indexes on notification/hearing dates, and reminder/escalation timestamps.
* Constraints: one active compromise per RemedialAccount, sum(schedule items) == settlement amount before approval, manual schedule only once (no automatic generation), approved records immutable except allowed actions.

### Services Impact
* Services for stage derivation, compromise approval validation, payment allocation to schedule items, default/completion detection, recovery action milestone tracking, write-off lifecycle updates, document version validation, notification sending, audit log creation.
* Selectors for dashboards/reports with pagination and mandatory filters (date, stage, officer).

### Views/URLs
* CBVs for CRUD on each domain model (RemedialAccount, CompromiseAgreement, LegalCase, RecoveryAction, WriteOffRequest, Document upload/list, dashboards/reports). HTMX partials for filters/status chips.
* FBVs for workflows: approve compromise, record payment, file legal case, initiate recovery action, recommend write-off, record board decision, upload documents, trigger notification/resend.
* URLs follow resource‑oriented nouns under `/remedial/…` as in PLAN matrix.

### Templates
* Server-rendered Django templates with HTMX fragments for filtering lists, inline status chips, notification logs, escalation history, and dashboards (aggregates, tables, exports).
* Reuse UI components per `UI_COMPONENTS.md` for typography, color, and responsive layout; include clear gradients/backgrounds for dashboards.

### Security
* RBAC enforcement per plan: Loan Officer (view/draft), Branch Manager (approve/initiate/recommend), Compliance/Auditor (view/audit logs). Permissions enforced both in views/services.
* Audit logging on all state transitions and critical mutations (using shared audit service).
* Tenant scope = single bank now; design selectors/services to allow future tenant filtering.

### Monitoring & Notifications
* Management commands (initially cron) with locking and logging: `scan_compromise_due_reminders`, `scan_compromise_overdue_and_default`, `scan_upcoming_hearings`, `scan_recovery_milestones_overdue`, `rollup_next_hearing_date`, `run_remedial_data_quality_checks`.
* Jobs send reminder/escalation emails via Django email backend; idempotency ensured by `NotificationLog` and timestamp checks; future migration to Celery is acceptable but not required now.

## TODO – Remedial Recovery Management
- [x] Implement detailed models/migrations + constraints (one active compromise, schedule validation).
- [x] Register models in admin with filters (stage/status, assigned officer, due dates).
- [x] Build services/selectors for transitions, payments, notifications, dashboards.
- [x] Add forms/views for compromise schedules/approvals, legal cases, recovery actions, write-off workflows, documents.
- [x] Implement HTMX-enhanced templates plus dashboards/reports with pagination/filters.
- [x] Create management commands with locking/logging and notifications per cron runbook.
- [x] Enforce RBAC + audit logging for all endpoints and workflows.
- [x] Add document version control (file_hash, version, size limits) and upload audit logs.
- [ ] Add tests for services, transitions, permissions, notification idempotency, report filters.
- [ ] Run AI review checklist + document completion artifacts.

## ✅ Completed
* [x] PRD reviewed and feature classified.
* [x] Architecture plan aligned with governance (AGENTS/GEMINI/AI docs).
* [x] Development plan drafted in `PLAN.md` (models, workflows, cron runbook, RBAC matrix).
* [x] Defaults confirmed (`grace_days=3`, `default_threshold_days=30`).
* [x] Complete models implementation with constraints and relationships
* [x] Services layer with audit logging and business logic
* [x] Selectors layer for optimized queries and dashboard data
* [x] Admin interface with filters and search
* [x] Forms with validation and crispy forms integration
* [x] CBV/FBV views with RBAC enforcement
* [x] Management commands for automated monitoring and notifications
* [x] Dashboard and list templates with responsive design
* [x] URL patterns for all CRUD operations and workflows

## Open Questions
1. Document retention/size policy beyond “limit” is unspecified—need guidance for `RemedialDocument` validation (e.g., retention period, confidentiality tagging).
2. Are there additional email layouts or recipient addresses beyond role groups? (None confirmed; default to role-based emails.)
3. Cron jobs may migrate to Celery in future—need to note planned migration path in documentation.

## Risk Notes
- Workflow integrity risk: invalid transitions when compromise/legal/recovery state machine misused; mitigate via service guards and tests.
- RBAC risk: unauthorized approvals/payments; mitigate with strict permission checks and audit logging.
- Data integrity risk: duplicate active compromises or inconsistent schedule totals; mitigate with DB constraints/pre-save checks.
- Notification spam risk: repeated escalations; mitigate with `NotificationLog` and timestamp thresholds (`last_reminder_sent_at`, `last_escalation_sent_at`).
- Performance risk: growing dashboards/reports; mitigate via indexed selectors, mandatory filters, pagination, and limited exports (CSV first).
