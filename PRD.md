Entering **Planner Mode**.

Below is the structured domain breakdown derived strictly from the approved PRD.

---

# 🔍 Feature Classification

**Feature Type:** Operational Recovery Management System
**Domain App:** Remedial / Legal Case Monitoring
**Risk Level:** Medium
**Financial Mutation:** None
**Multi-Tenant Impact:** None (Single bank only)
**RBAC Required:** Yes
**Maker-Checker Required:** No
**Audit Logging Required:** Yes

---

# 🏗 Domain Architecture Breakdown

The system should be divided into the following domain modules:

---

# 1️⃣ Core Domain: Remedial Case Management

### Primary Entity:

`RemedialAccount`

Represents one NPL account under monitoring.

### Responsibilities:

* Store borrower reference data
* Track recovery stage
* Assign responsible officer
* Maintain lifecycle state

### Subdomains:

* Stage Management
* Status Flags
* Escalation Tracking

---

# 2️⃣ Compromise Agreement Domain

### Entity:

`CompromiseAgreement`

Linked to `RemedialAccount` (One-to-Many, but only ONE active allowed)

### Sub-Entities:

* `PaymentSchedule`
* `CompromisePayment`
* `CompromiseStatus`

### Responsibilities:

* Generate installment schedule
* Monitor payments
* Detect default
* Trigger escalation email
* Prevent duplicate active compromise

### Domain Logic:

* Active agreement must auto-monitor due dates
* System-driven state transitions
* No financial mutation to CBS

---

# 3️⃣ Legal Case Domain

### Entity:

`LegalCase`

Linked to `RemedialAccount`

### Types:

* Small Claims
* Regular Collection Case

### Sub-Entities:

* `CourtHearing`
* `LegalStatusHistory`

### Responsibilities:

* Track filing
* Manage hearing calendar
* Email reminders before hearing
* Case lifecycle management

---

# 4️⃣ Foreclosure & Dacion Domain

### Entity:

`RecoveryAction`

Type Enum:

* Foreclosure
* Dacion

### Milestone Tracking:

For Foreclosure:

* Notice Issued
* Publication Dates
* Auction Date
* Redemption Deadline

For Dacion:

* Appraisal
* Board Review
* Completion

### Responsibilities:

* Timeline control
* Escalation if milestone overdue
* Document storage

---

# 5️⃣ Write-Off Endorsement Domain

### Entity:

`WriteOffRequest`

### Lifecycle:

Draft → Recommended → Board Approved → Closed

### Authority:

* Recommend: Branch Manager
* Approve: Board (manual external approval recorded)

System only tracks approval status.

No GL mutation.

---

# 6️⃣ Document Management Domain

### Entity:

`RemedialDocument`

Linked to:

* RemedialAccount
* CompromiseAgreement
* LegalCase
* RecoveryAction

### Requirements:

* Version control
* File size limit
* Upload audit log

---

# 7️⃣ Notification & Escalation Engine

### Entity:

`EscalationRule`
`NotificationLog`

### Triggers:

| Trigger                   | Action           |
| ------------------------- | ---------------- |
| Missed compromise payment | Email escalation |
| Hearing in X days         | Reminder email   |
| Redemption deadline near  | Alert            |
| Milestone overdue         | Escalation       |

System-driven background job required.

---

# 8️⃣ Dashboard & Reporting Domain

### Read-Only Aggregates:

* Total NPL under remedial
* Active compromise
* Defaulted compromise
* Active legal cases
* Upcoming hearings
* Foreclosure status

Filters:

* Date
* Stage
* Assigned officer

Exports:

* CSV
* PDF

---

# 🔐 RBAC Domain

Roles required:

| Role           | Scope              |
| -------------- | ------------------ |
| Loan Officer   | View + Draft       |
| Branch Manager | Approve + Initiate |
| Compliance     | View + Monitor     |
| Auditor        | View + Audit logs  |

No deletion of approved records.

Soft-delete only for draft records.

---

# 📊 Domain Relationships (High-Level)

```
RemedialAccount
    ├── CompromiseAgreement
    │       ├── PaymentSchedule
    │       └── CompromisePayment
    ├── LegalCase
    │       └── CourtHearing
    ├── RecoveryAction (Foreclosure/Dacion)
    ├── WriteOffRequest
    └── RemedialDocument
```

---

# 🧠 Domain Constraints

1. Only one active compromise per account.
2. Legal case cannot be deleted once filed.
3. Write-off requires Board approval status entry.
4. Escalation must not duplicate emails.
5. Approved records immutable.
6. All transitions logged.

---

# ⚙ Technical Classification

| Category                     | Assessment |
| ---------------------------- | ---------- |
| Financial mutation           | None       |
| State machine required       | Yes        |
| Background jobs required     | Yes        |
| Notification system required | Yes        |
| Document storage required    | Yes        |
| Audit trail required         | Yes        |

---

# 🧩 Implementation Complexity Rating

Moderate complexity due to:

* Multiple lifecycle engines
* Escalation logic
* Document management
* Calendar reminder engine

No accounting integration reduces risk.

---

## Architect Mode

Target stack assumption: **Django + PostgreSQL** (standalone), with **background worker** (Celery + Redis) or **cron** if you want minimal infra.

---

# 1) Database Schema (Logical + Django Model Blueprint)

### 1.1 Reference & Security

**User (existing Django auth user)**
Use Django `User` + groups/permissions.

**Role model (optional)**

* Prefer Django Groups: `LOAN_OFFICER`, `BRANCH_MANAGER`, `COMPLIANCE`, `AUDITOR`, `ADMIN`

**AuditLog**

* `id`
* `event_ts`
* `actor_user_id` (FK User, nullable for system jobs)
* `entity_type` (varchar; e.g., "CompromiseAgreement")
* `entity_id` (uuid/int)
* `action` (CREATE/UPDATE/STATE_CHANGE/UPLOAD/EMAIL_SENT)
* `before_json` (jsonb, nullable)
* `after_json` (jsonb, nullable)
* `ip_address` (inet, nullable)
* `notes` (text)

> Every mutation writes an AuditLog row.

---

### 1.2 Core Remedial Domain

**RemedialAccount**

* `id` (uuid)
* `loan_account_no` (varchar, unique)
* `borrower_name` (varchar)
* `borrower_id_ref` (varchar, optional if you have CIF reference)
* `outstanding_balance_ref` (numeric, nullable; informational only)
* `stage` (enum; see states below)
* `status` (enum; ACTIVE/CLOSED/ON_HOLD)
* `assigned_officer_id` (FK User)
* `created_at`, `updated_at`
* `closed_at` (nullable)
* `remarks` (text, nullable)

Indexes:

* `(stage, status)`
* `(assigned_officer_id, stage)`

---

### 1.3 Compromise Agreement Domain

**CompromiseAgreement**

* `id` (uuid)
* `remedial_account_id` (FK RemedialAccount)
* `agreement_no` (varchar, unique or per-account sequence)
* `status` (enum: DRAFT/SUBMITTED/APPROVED/ACTIVE/COMPLETED/DEFAULTED/CANCELLED)
* `settlement_amount` (numeric)
* `start_date` (date)
* `frequency` (enum: WEEKLY/BIWEEKLY/MONTHLY)
* `installment_amount` (numeric, nullable if variable schedule)
* `terms_json` (jsonb; captures special clauses)
* `grace_days` (int default e.g. 0 or 3)
* `default_threshold_days` (int default e.g. 7 or 30; per PRD “missed payment threshold”)
* `approved_by_id` (FK User, nullable until approved)
* `approved_at` (datetime, nullable)
* `created_by_id` (FK User)
* `created_at`, `updated_at`
* `is_active` (bool, derived or enforced)

**Hard constraint (non-negotiable):**

* Only **one active compromise** per RemedialAccount.
  Implementation:
* DB partial unique index (Postgres): `UNIQUE(remedial_account_id) WHERE status IN ('APPROVED','ACTIVE')`

  * OR `is_active=true` maintained by state transitions.

**CompromiseScheduleItem**

* `id` (uuid)
* `compromise_agreement_id` (FK)
* `seq_no` (int)
* `due_date` (date)
* `amount_due` (numeric)
* `amount_paid` (numeric default 0)
* `paid_at` (datetime, nullable)
* `status` (enum: DUE/PAID/PARTIAL/OVERDUE/WAIVED)
* `last_reminder_sent_at` (datetime, nullable)
* `last_escalation_sent_at` (datetime, nullable)

Index:

* `(due_date, status)`
* `(compromise_agreement_id, seq_no)` unique

**CompromisePayment**

* `id` (uuid)
* `compromise_agreement_id` (FK)
* `schedule_item_id` (FK, nullable for unscheduled payments)
* `payment_date` (date)
* `amount` (numeric)
* `reference_no` (varchar, nullable)
* `received_by_id` (FK User)
* `created_at`

Allocation rule (simple): apply to earliest unpaid schedule items unless user explicitly maps.

---

### 1.4 Legal Case Domain

**LegalCase**

* `id` (uuid)
* `remedial_account_id` (FK)
* `case_type` (enum: SMALL_CLAIMS/REGULAR_COLLECTION)
* `status` (enum: DRAFT/FILED/ACTIVE/DECIDED/CLOSED)
* `case_number` (varchar, nullable until filed)
* `court_name` (varchar)
* `court_branch` (varchar)
* `filing_date` (date, nullable)
* `assigned_counsel` (varchar, optional if external counsel tracked as text)
* `next_hearing_date` (date, nullable; denormalized from hearing table)
* `created_by_id` (FK User)
* `created_at`, `updated_at`

**CourtHearing**

* `id` (uuid)
* `legal_case_id` (FK)
* `hearing_date` (date)
* `hearing_type` (varchar; e.g., “Pre-trial”, “Trial”, “Promulgation”)
* `status` (enum: SCHEDULED/DONE/RESET/CANCELLED)
* `notes` (text)
* `reminder_sent_at` (datetime, nullable)
* `escalation_sent_at` (datetime, nullable)

Index:

* `(hearing_date, status)`

---

### 1.5 Recovery Actions (Foreclosure / Dacion)

**RecoveryAction**

* `id` (uuid)
* `remedial_account_id` (FK)
* `action_type` (enum: FORECLOSURE/DACION)
* `status` (enum: DRAFT/INITIATED/IN_PROGRESS/COMPLETED/ON_HOLD/CANCELLED)
* `initiated_by_id` (FK User)
* `initiated_at` (datetime, nullable)
* `created_at`, `updated_at`

**RecoveryMilestone**

* `id` (uuid)
* `recovery_action_id` (FK)
* `milestone_type` (enum; varies by action_type)

  * Foreclosure: NOTICE_ISSUED, PUBLICATION_START, PUBLICATION_END, AUCTION_DATE, REDEMPTION_END
  * Dacion: APPRAISAL_REQUESTED, APPRAISAL_RECEIVED, BOARD_REVIEW, TRANSFER_COMPLETED
* `target_date` (date, nullable)
* `actual_date` (date, nullable)
* `status` (enum: PENDING/DONE/OVERDUE)
* `notes` (text)
* `reminder_sent_at` (datetime, nullable)
* `escalation_sent_at` (datetime, nullable)

Index:

* `(target_date, status)`

---

### 1.6 Write-off Tracking

**WriteOffRequest**

* `id` (uuid)
* `remedial_account_id` (FK)
* `status` (enum: DRAFT/RECOMMENDED/BOARD_APPROVED/REJECTED/CLOSED)
* `recommended_by_id` (FK User)  # Branch Manager
* `recommended_at` (datetime, nullable)
* `board_resolution_ref` (varchar, nullable)
* `board_decision_date` (date, nullable)
* `notes` (text)
* `created_at`, `updated_at`

---

### 1.7 Document Management

**RemedialDocument**

* `id` (uuid)
* `entity_type` (enum: REMEDIAL_ACCOUNT/COMPROMISE/LEGAL_CASE/RECOVERY_ACTION/WRITE_OFF)
* `entity_id` (uuid)
* `doc_type` (varchar; e.g., “Compromise Signed”, “Demand Letter”, “Complaint”, “Sheriff Notice”)
* `file` (FileField)
* `file_hash` (varchar, for integrity)
* `uploaded_by_id` (FK User)
* `uploaded_at`
* `version` (int default 1)
* `is_confidential` (bool default true)

---

### 1.8 Notifications

**NotificationRule** (configurable thresholds)

* `id`
* `rule_code` (e.g., COMPROMISE_DUE_REMINDER, COMPROMISE_DEFAULT_ESCALATION, HEARING_REMINDER)
* `enabled` (bool)
* `days_before` (int, nullable)
* `days_after` (int, nullable)
* `email_to_role` (enum/group name)
* `email_to_specific` (FK User nullable)
* `template_code` (varchar)

**NotificationLog**

* `id`
* `rule_code`
* `entity_type`
* `entity_id`
* `sent_to` (varchar)
* `sent_at`
* `status` (SENT/FAILED)
* `error` (text nullable)

---

# 2) Lifecycle State Machine Design

Below are the authoritative states and transitions. All transitions create `AuditLog(action="STATE_CHANGE")`.

## 2.1 RemedialAccount (Stage)

**Stages**

* `PRE_LEGAL`
* `COMPROMISE`
* `LEGAL`
* `FORECLOSURE`
* `DACION`
* `WRITE_OFF_ENDORSEMENT`
* `CLOSED`

**Transitions**

* PRE_LEGAL → COMPROMISE (when a CompromiseAgreement becomes ACTIVE)
* PRE_LEGAL → LEGAL (when LegalCase becomes FILED)
* PRE_LEGAL → FORECLOSURE (when RecoveryAction FORECLOSURE INITIATED)
* PRE_LEGAL → DACION (when RecoveryAction DACION INITIATED)
* COMPROMISE → LEGAL (when compromise DEFAULTED and manager initiates legal)
* COMPROMISE → CLOSED (when compromise COMPLETED)
* LEGAL → CLOSED (when case CLOSED and recovery concluded)
* FORECLOSURE → CLOSED (when COMPLETED and outcome recorded)
* DACION → CLOSED (when COMPLETED)
* Any → WRITE_OFF_ENDORSEMENT (when WriteOffRequest is RECOMMENDED)
* WRITE_OFF_ENDORSEMENT → CLOSED (when BOARD_APPROVED and closed by admin)

> Stage is derived from the “most advanced active process” unless you want it manually set. Best practice: **derive** + allow override only for Branch Manager.

---

## 2.2 CompromiseAgreement

**States**

* DRAFT → SUBMITTED → APPROVED → ACTIVE → (COMPLETED | DEFAULTED)
* DRAFT → CANCELLED
* SUBMITTED → REJECTED (optional; or back to DRAFT)

**Rules**

* Only Branch Manager can APPROVE.
* On APPROVED: generate schedule items (PaymentSchedule).
* On ACTIVE: system starts monitoring.
* DEFAULTED: triggered by job when missed payment beyond `default_threshold_days`.
* COMPLETED: triggered when all schedule items PAID.

---

## 2.3 LegalCase

**States**

* DRAFT → FILED → ACTIVE → (DECIDED) → CLOSED
* FILED/ACTIVE → ON_HOLD (optional) → ACTIVE

**Rules**

* Branch Manager initiates FILED.
* Hearings are children; `next_hearing_date` is the minimum future SCHEDULED hearing_date.

---

## 2.4 RecoveryAction (Foreclosure/Dacion)

**States**

* DRAFT → INITIATED → IN_PROGRESS → COMPLETED
* Any → ON_HOLD / CANCELLED

**Milestone Rules**

* A milestone becomes OVERDUE if `target_date < today` and not DONE.
* Completion requires all mandatory milestones DONE (per action_type).

---

## 2.5 WriteOffRequest

**States**

* DRAFT → RECOMMENDED → (BOARD_APPROVED | REJECTED) → CLOSED

**Rules**

* Branch Manager can RECOMMEND.
* Board approval is recorded (manual input of resolution reference/date).
* No deletion beyond DRAFT.

---

# 3) Background Task Design (Monitoring + Email Escalation)

You need scheduled tasks. Preferred: **Celery Beat** (daily) + Celery worker. Minimal alternative: **Django management command via cron**.

## 3.1 Task Set

### Task A — `scan_compromise_due_reminders` (daily 7:00 AM)

* For each `CompromiseScheduleItem` with status DUE and `due_date == today + X` (X from rule)
* Send reminder email to borrower? (Not in PRD) → **send to internal** (Loan Officer + Branch Manager)
* Write `NotificationLog`
* Update `last_reminder_sent_at`

### Task B — `scan_compromise_overdue_and_default` (daily 7:10 AM)

* Find schedule items where `due_date + grace_days < today` and not PAID
* Mark item OVERDUE
* If overdue days >= `default_threshold_days`, mark agreement DEFAULTED
* Escalation email to Branch Manager + Compliance
* Update RemedialAccount stage suggestion (do not auto-move to LEGAL; PRD says escalation only)

Idempotency:

* Only send escalation if `last_escalation_sent_at` is null or older than threshold.

### Task C — `scan_upcoming_hearings` (daily 7:20 AM)

* Find `CourtHearing` SCHEDULED where `hearing_date == today + N` (N configurable)
* Email assigned officer + Branch Manager
* Mark `reminder_sent_at`

### Task D — `scan_milestone_overdue` (daily 7:30 AM)

* Find `RecoveryMilestone` PENDING with `target_date < today`
* Mark OVERDUE
* Escalate email to Branch Manager + Compliance
* Set `escalation_sent_at`

### Task E — `rollup_next_hearing_date` (daily or on save signal)

* For each LegalCase, compute `next_hearing_date`
* Keeps dashboard fast

### Task F — `data_quality_checks` (weekly)

* Detect: multiple active compromises, missing loan_account_no, missing assigned officer, etc.
* Email compliance summary

---

## 3.2 Email Delivery & Templates

* Use Django Email backend (SMTP) initially.
* Template codes:

  * `COMPROMISE_REMINDER`
  * `COMPROMISE_DEFAULT_ESCALATION`
  * `HEARING_REMINDER`
  * `MILESTONE_OVERDUE_ESCALATION`

Each email includes:

* Loan account no
* Borrower name
* Action required
* Links to the record

---

# 4) Control & Integrity Design Choices

### 4.1 No Maker-Checker (per PRD)

Still enforce:

* Permission checks
* Immutable approved records
* Audit logs for all changes

### 4.2 Immutability Rules

* If `CompromiseAgreement.status in (APPROVED, ACTIVE, COMPLETED, DEFAULTED)` → terms and schedule cannot be edited; only add payments / upload documents / add notes.
* If `LegalCase.status != DRAFT` → cannot delete, only close.
* If `WriteOffRequest.status != DRAFT` → cannot delete.

### 4.3 Soft Delete

* Only allowed for DRAFT objects.
* Soft delete fields: `is_deleted`, `deleted_at`, `deleted_by`

---

# 5) Recommended Implementation Sequence

1. Models + migrations (schema above)
2. Services layer (domain logic):

   * Schedule generator
   * Payment allocator
   * Default detection
3. State transition endpoints (API + UI)
4. Document upload + linking
5. Background tasks + logs
6. Dashboards + export (CSV/PDF)
7. Hardening: audit coverage + idempotency + data-quality checks

---

Good. That changes the architecture slightly and simplifies risk.

Since the **compromise schedule is NOT system-generated**, but instead consists of **fixed amounts on specific future dates defined manually**, we adjust the model and state logic.

Below is the corrected Architect Mode design.

---

# 🔧 ARCHITECT MODE (Revised – Manual Fixed Schedule)

## Key Change

❌ Remove automatic installment generation logic
❌ Remove frequency-based schedule creation
✅ Schedule items are manually encoded
✅ Each due date + amount is explicitly defined

---

# 1️⃣ Database Schema Adjustments

## 1.1 CompromiseAgreement (Revised)

Remove:

* `frequency`
* `installment_amount`

Keep:

* `settlement_amount`
* `start_date`
* `default_threshold_days`
* `grace_days`
* `terms_json`

No automatic schedule generation.

---

## 1.2 CompromiseScheduleItem (Now Mandatory Manual Entry)

**CompromiseScheduleItem**

* `id`
* `compromise_agreement_id` (FK)
* `seq_no` (int)
* `due_date` (date)
* `amount_due` (numeric)
* `amount_paid` (numeric default 0)
* `status` (DUE / PARTIAL / PAID / OVERDUE)
* `notes` (optional)
* `last_reminder_sent_at`
* `last_escalation_sent_at`

### Hard Validation Rules

When approving compromise:

1. At least one schedule item must exist.
2. Sum of all `amount_due` must equal `settlement_amount`.
3. No duplicate due dates allowed.
4. Due dates must be future dates (unless explicitly allowed).

This validation runs before status can move to APPROVED.

---

# 2️⃣ Revised Compromise Lifecycle Logic

## States

DRAFT → APPROVED → ACTIVE → (COMPLETED | DEFAULTED)

Remove SUBMITTED state (optional unless you want it).

---

## Transition Rules

### DRAFT → APPROVED

Triggered by Branch Manager.

System checks:

* Schedule items exist
* Total matches settlement amount
* No duplicate dates

---

### APPROVED → ACTIVE

Automatic immediately after approval
OR merged into APPROVED (APPROVED = ACTIVE)

Recommended: Merge. Simpler.

---

### ACTIVE → DEFAULTED (System-triggered)

If:

`due_date + grace_days < today`
AND
`amount_paid < amount_due`

→ mark schedule item OVERDUE
→ if overdue_days >= default_threshold_days
→ mark compromise DEFAULTED
→ trigger escalation email

---

### ACTIVE → COMPLETED (System-triggered)

If:
All schedule items status == PAID

→ mark compromise COMPLETED
→ update RemedialAccount stage to CLOSED (if no other active actions)

---

# 3️⃣ Payment Recording Logic (Revised)

When payment is recorded:

### Step 1 — User selects schedule item

OR system auto-allocates to earliest unpaid item.

### Step 2 — Update:

If payment == amount_due:

* status → PAID

If payment < amount_due:

* status → PARTIAL

If cumulative amount_paid >= amount_due:

* status → PAID

### No recalculation of interest.

### No GL integration.

---

# 4️⃣ Background Task Adjustments

## Task: scan_compromise_overdue

Daily:

For each schedule item where:

* status in (DUE, PARTIAL)
* due_date + grace_days < today

Then:

* status → OVERDUE
* send reminder if not yet sent
* check if default_threshold_days exceeded
* if yes:

  * compromise.status → DEFAULTED
  * escalate email to Branch Manager + Compliance

---

# 5️⃣ Data Integrity Constraints

Add database constraints:

### Constraint A

```
Unique(compromise_agreement_id, seq_no)
```

### Constraint B

Partial unique active compromise per account.

### Constraint C

Cannot edit schedule items if compromise status != DRAFT.

Enforced at application layer.

---

# 6️⃣ UI Implication

During compromise drafting:

User must:

1. Input settlement amount
2. Click “Add Schedule Item”
3. Add rows:

   * Due Date
   * Amount
4. System shows running total
5. Validation error if total ≠ settlement amount

This makes encoding explicit and auditable.

---

# 7️⃣ Escalation Logic (Clear Rule)

You must define:

What constitutes DEFAULT?

Example options:

* 7 days overdue?
* 30 days overdue?

Current schema supports both via `default_threshold_days`.

---

# 8️⃣ Risk Impact (Improved)

Manual schedule:

✔ Lower algorithm risk
✔ Clear legal defensibility
✔ Explicit contract encoding
✔ Better audit trail

No financial mutation remains.

---

# 9️⃣ Recommended Additional Safeguard

Add:

`compromise_signed_date`

And require upload of signed document before approval.

This prevents encoding agreements not yet signed.

---

# 🔐 Final Architecture Summary (Revised)

| Component           | Status           |
| ------------------- | ---------------- |
| Schedule generation | Manual           |
| Payment allocation  | Semi-automatic   |
| Default detection   | System monitored |
| Escalation          | Email            |
| GL impact           | None             |
| Audit trail         | Mandatory        |
| Maker-checker       | None             |
| Risk level          | Medium           |

---


