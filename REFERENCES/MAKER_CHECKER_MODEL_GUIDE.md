# MAKER_CHECKER_MODEL_GUIDE.md

## Maker–Checker Controls for Django Banking Systems (Auditable + Practical)

> This guide defines the **maker–checker (4-eyes) control framework** for sensitive banking actions:

* Approvals (loans, restructuring)
* Postings (GL, releases)
* Reversals (transactions, journal entries)
* Write-offs / charge-offs
* Master data changes (products, COA)

It includes:

* Standard data model
* Service-layer enforcement patterns
* UI behavior
* Test requirements
* Audit logging requirements

This system prioritizes **clarity, auditability, and operational safety**.

---

## 0) Principles (Non-Negotiable)

1. **Maker cannot approve their own item.**
2. **Approval is explicit** (no implicit approvals).
3. **Approved records are immutable** (changes require reversal or new version).
4. **Every approval records:**

   * who
   * when
   * decision
   * reason/remarks
5. **All maker–checker actions are logged** in an audit log.

---

## 1) What Requires Maker–Checker?

### Mandatory

* Loan approval
* Loan release (if it affects cash/disbursement)
* GL posting (Draft → Posted)
* Reversal of any posted transaction
* Write-off / charge-off
* Restructuring approval

### Optional (policy-based)

* Large withdrawals
* Interest rate override
* Backdated transaction posting
* Customer profile changes (KYC risk)

---

## 2) Standard Lifecycle States

Use a consistent state machine across approval objects:

| Status          | Meaning                                                 |
| --------------- | ------------------------------------------------------- |
| Draft           | Maker preparing                                         |
| Submitted       | Awaiting checker                                        |
| Approved        | Checker approved                                        |
| Rejected        | Checker rejected                                        |
| Cancelled       | Maker withdrew before approval                          |
| Posted/Executed | System performed final action (optional separate state) |

**Recommendation:** For GL posting and transaction execution, separate:

* approval (Approved)
* execution/posting (Executed)

---

## 3) Canonical Model Pattern

### 3.1 Abstract Base Model: `ApprovalRequest`

Use an abstract model to standardize fields across approvals.

```python
# apps/core/models.py (or apps/approval/models.py)
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ApprovalStatus(models.TextChoices):
    DRAFT = "D", "Draft"
    SUBMITTED = "S", "Submitted"
    APPROVED = "A", "Approved"
    REJECTED = "R", "Rejected"
    CANCELLED = "C", "Cancelled"

class ApprovalRequest(models.Model):
    tenant = models.ForeignKey("tenancy.Tenant", on_delete=models.PROTECT)
    branch = models.ForeignKey("accounts.Branch", on_delete=models.PROTECT, null=True, blank=True)

    status = models.CharField(max_length=1, choices=ApprovalStatus.choices, default=ApprovalStatus.DRAFT)

    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="approvals_created")
    created_at = models.DateTimeField(auto_now_add=True)

    submitted_at = models.DateTimeField(null=True, blank=True)

    decided_by = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name="approvals_decided")
    decided_at = models.DateTimeField(null=True, blank=True)
    decision_remarks = models.TextField(blank=True)

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["tenant", "status"]),
            models.Index(fields=["branch", "status"]),
        ]
```

**Rules**

* `created_by` is maker
* `decided_by` is checker
* `decided_by != created_by` must be enforced in services
* tenant scope is mandatory

---

## 4) Implementations by Domain

### 4.1 Loan Approval

```python
# apps/loans/models.py
class LoanApproval(ApprovalRequest):
    loan = models.OneToOneField("loans.LoanAccount", on_delete=models.PROTECT)
    proposed_amount = models.DecimalField(max_digits=12, decimal_places=2)
    proposed_term = models.IntegerField()
    proposed_rate = models.DecimalField(max_digits=5, decimal_places=2)
```

**Execution**

* Approval changes `LoanAccount.status` from Applied → Approved
* Execution must be done in services, not signals

---

### 4.2 Loan Restructuring Approval (Versioning Approach)

Instead of editing schedule directly:

* Create a `RestructureProposal`
* Approve it
* Generate a new schedule version

```python
class RestructureApproval(ApprovalRequest):
    loan = models.ForeignKey("loans.LoanAccount", on_delete=models.PROTECT)
    new_term = models.IntegerField()
    new_rate = models.DecimalField(max_digits=5, decimal_places=2)
    effective_date = models.DateField()
```

---

### 4.3 Journal Entry Posting Approval

```python
# apps/gl/models.py
class JournalPostApproval(ApprovalRequest):
    journal_entry = models.OneToOneField("gl.JournalEntry", on_delete=models.PROTECT)
```

Execution:

* Checker approves
* Poster executes: Draft → Posted (or approve triggers posting if policy allows)

---

### 4.4 Reversal Approval

Reversal is safest as a *new* transaction referencing original.

```python
class ReversalApproval(ApprovalRequest):
    object_type = models.CharField(max_length=50)  # "DepositTxn", "LoanTxn", "JournalEntry"
    object_id = models.PositiveIntegerField()
    reason = models.TextField()
```

Execution:

* Create reversal txn/JE
* Mark original as reversed (status flag)
* Never delete originals

---

## 5) Service Layer Enforcement (Mandatory)

### 5.1 Submit for Approval

```python
from django.utils import timezone
from django.core.exceptions import PermissionDenied, ValidationError

def submit_for_approval(req, user):
    if req.created_by_id != user.id:
        raise PermissionDenied("Only the maker can submit this request.")
    if req.status != ApprovalStatus.DRAFT:
        raise ValidationError("Only Draft requests can be submitted.")
    req.status = ApprovalStatus.SUBMITTED
    req.submitted_at = timezone.now()
    req.save()
```

---

### 5.2 Approve / Reject (Checker Action)

```python
def approve_request(req, checker, remarks=""):
    if req.status != ApprovalStatus.SUBMITTED:
        raise ValidationError("Only Submitted requests can be approved.")
    if req.created_by_id == checker.id:
        raise PermissionDenied("Maker cannot approve their own request.")
    req.status = ApprovalStatus.APPROVED
    req.decided_by = checker
    req.decided_at = timezone.now()
    req.decision_remarks = remarks
    req.save()
```

```python
def reject_request(req, checker, remarks=""):
    if req.status != ApprovalStatus.SUBMITTED:
        raise ValidationError("Only Submitted requests can be rejected.")
    if req.created_by_id == checker.id:
        raise PermissionDenied("Maker cannot reject their own request.")
    req.status = ApprovalStatus.REJECTED
    req.decided_by = checker
    req.decided_at = timezone.now()
    req.decision_remarks = remarks
    req.save()
```

---

### 5.3 Execute / Post (Controlled Execution)

**Rule:** Approval does not automatically mutate financial objects unless policy permits.

```python
def execute_loan_approval(approval, executor):
    if approval.status != ApprovalStatus.APPROVED:
        raise ValidationError("Approval must be approved before execution.")
    # optional: executor must be checker or specialized role
    loan = approval.loan
    loan.status = loan.Status.APPROVED
    loan.save()
```

For GL posting:

```python
def execute_journal_post(approval, executor):
    if approval.status != ApprovalStatus.APPROVED:
        raise ValidationError("Approval must be approved before posting.")
    je = approval.journal_entry
    # post JE: lock lines, set posted_at, posted_by
    je.post(executor)
```

**Important:** Execution should be idempotent or block double execution.

---

## 6) Permission Rules

### Maker Roles

* Teller, Loan Officer, Bookkeeper, RMU staff

### Checker Roles

* Branch Manager, Credit Approver, GL Poster, Compliance

### Policy Defaults

* Maker cannot approve or execute posted changes alone
* Checker cannot modify proposal content after submission
* If changes required → reject and return to maker

---

## 7) UI Rules (Templates + HTMX)

### Status Badge

Always show status clearly.

### Buttons Visibility

* Draft: `Submit`
* Submitted: `Approve`, `Reject` (checker only)
* Approved: `Execute/Post` (authorized users)
* Rejected: `Edit & Resubmit` (maker)
* Cancelled: read-only

**Never rely on hidden buttons as enforcement** — services must enforce.

---

## 8) Audit Logging Requirements

Every state change logs:

* tenant
* branch
* actor
* action: submit/approve/reject/execute/cancel
* approval request id
* target object type/id
* remarks
* timestamp

Recommended approach:

* call `audit.log()` inside each service function

---

## 9) Data Integrity Rules

* No deletion of financial records
* No modification of posted records
* Corrections happen through:

  * reversal
  * new entry
  * new schedule version

---

## 10) Testing Requirements (Mandatory)

### 10.1 Maker–Checker Rules

* maker cannot approve own request
* cannot approve if not submitted
* cannot execute if not approved
* cannot execute twice

### 10.2 Tenant Isolation

* cannot access another tenant’s approvals
* cannot approve cross-tenant objects

### 10.3 Role Tests

* teller cannot approve
* approver cannot edit draft content

---

## 11) Operational Notes (Bank-Friendly)

* Use “Submitted queue” pages:

  * `/approvals/queue/loans/`
  * `/approvals/queue/gl/`
* Show SLA timers:

  * submitted_at age (hours/days)
* Require reason text for rejections and reversals

---

## 12) Minimal Implementation Set (MVP)

For a safe MVP implement maker–checker only for:

1. Loan approval
2. GL posting
3. Reversals

Expand later to restructuring and write-offs.

---

## Final Principle

Maker–checker is not a UI feature.
It is a **control framework**.

If a feature changes money, status, or ledger — it must be:

* proposed (maker)
* reviewed (checker)
* executed (controlled)
* logged (auditable)

---
