import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

from apps.core.models import AuditLog, TenantAwareModel, TimeStampedModel

User = get_user_model()


def document_upload_path(instance, filename):
    return f"remedial/{instance.entity_type.lower()}/{instance.entity_id}/{filename}"


class RemedialStage(models.TextChoices):
    PRE_LEGAL = "pre_legal", "Pre-legal"
    COMPROMISE = "compromise", "Compromise"
    LEGAL = "legal", "Legal"
    FORECLOSURE = "foreclosure", "Foreclosure"
    DACION = "dacion", "Dacion"
    WRITE_OFF = "write_off", "Write-off"
    CLOSED = "closed", "Closed"


class RemedialStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    ON_HOLD = "on_hold", "On Hold"
    CLOSED = "closed", "Closed"


class CompromiseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    APPROVED = "approved", "Approved"
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    DEFAULTED = "defaulted", "Defaulted"
    CANCELLED = "cancelled", "Cancelled"


class ScheduleStatus(models.TextChoices):
    DUE = "due", "Due"
    PARTIAL = "partial", "Partial"
    PAID = "paid", "Paid"
    OVERDUE = "overdue", "Overdue"
    WAIVED = "waived", "Waived"


class LegalCaseStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    FILED = "filed", "Filed"
    ACTIVE = "active", "Active"
    DECIDED = "decided", "Decided"
    CLOSED = "closed", "Closed"
    ON_HOLD = "on_hold", "On Hold"


class RecoveryActionType(models.TextChoices):
    FORECLOSURE = "foreclosure", "Foreclosure"
    DACION = "dacion", "Dacion"


class RecoveryActionStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    INITIATED = "initiated", "Initiated"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    ON_HOLD = "on_hold", "On Hold"
    CANCELLED = "cancelled", "Cancelled"


class WriteOffStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    RECOMMENDED = "recommended", "Recommended"
    BOARD_APPROVED = "board_approved", "Board Approved"
    REJECTED = "rejected", "Rejected"
    CLOSED = "closed", "Closed"


class NotificationRuleStatus(models.TextChoices):
    ENABLED = "enabled", "Enabled"
    DISABLED = "disabled", "Disabled"


class NotificationLogStatus(models.TextChoices):
    SENT = "sent", "Sent"
    FAILED = "failed", "Failed"


class RemedialAccount(TenantAwareModel, TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan_account_no = models.CharField(max_length=64, unique=True)
    borrower_name = models.CharField(max_length=255)
    borrower_id_ref = models.CharField(max_length=64, blank=True)
    outstanding_balance_ref = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    stage = models.CharField(max_length=20, choices=RemedialStage.choices, default=RemedialStage.PRE_LEGAL)
    status = models.CharField(max_length=20, choices=RemedialStatus.choices, default=RemedialStatus.ACTIVE)
    assigned_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="assigned_remedial_accounts",
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["stage", "status"]),
            models.Index(fields=["assigned_officer", "stage"]),
        ]

    def __str__(self):
        return f"{self.loan_account_no} ({self.get_stage_display()})"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("remedial:account-detail", args=[self.pk])
    
    def get_documents(self):
        """Get all related documents for this account"""
        return RemedialDocument.objects.filter(
            entity_type="remedial_account",
            entity_id=self.id,
            is_deleted=False
        ).order_by("-version", "-uploaded_at")


class CompromiseAgreement(TenantAwareModel, TimeStampedModel):
    remedial_account = models.ForeignKey(
        RemedialAccount,
        on_delete=models.CASCADE,
        related_name="compromise_agreements",
    )
    agreement_no = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=CompromiseStatus.choices, default=CompromiseStatus.DRAFT)
    settlement_amount = models.DecimalField(max_digits=14, decimal_places=2)
    start_date = models.DateField(null=True, blank=True)
    terms = models.TextField(blank=True, default="")
    grace_days = models.PositiveSmallIntegerField(default=3)
    default_threshold_days = models.PositiveSmallIntegerField(default=30)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_compromises",
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_compromises",
    )
    compromise_signed_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["remedial_account"],
                condition=models.Q(status__in=[
                    CompromiseStatus.APPROVED,
                    CompromiseStatus.ACTIVE,
                    CompromiseStatus.DEFAULTED,
                ]),
                name="unique_active_compromise_per_account",
            ),
            models.UniqueConstraint(fields=["remedial_account", "agreement_no"], name="unique_compromise_per_account"),
        ]

    def __str__(self):
        return f"{self.remedial_account.loan_account_no} – {self.agreement_no}"

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("remedial:compromise-approve", args=[self.pk])


class CompromiseScheduleItem(TenantAwareModel, TimeStampedModel):
    compromise_agreement = models.ForeignKey(
        CompromiseAgreement,
        on_delete=models.CASCADE,
        related_name="schedule_items",
    )
    seq_no = models.PositiveIntegerField()
    due_date = models.DateField()
    amount_due = models.DecimalField(max_digits=14, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=ScheduleStatus.choices, default=ScheduleStatus.DUE)
    notes = models.TextField(blank=True)
    last_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    last_escalation_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("compromise_agreement", "seq_no")
        ordering = ["due_date"]

    def __str__(self):
        return f"{self.compromise_agreement} schedule #{self.seq_no}"


class CompromisePayment(TenantAwareModel, TimeStampedModel):
    compromise_agreement = models.ForeignKey(
        CompromiseAgreement,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    schedule_item = models.ForeignKey(
        CompromiseScheduleItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )
    payment_date = models.DateField(default=timezone.now)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    reference_no = models.CharField(max_length=128, blank=True)
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="compromise_payments",
    )

    def __str__(self):
        return f"Payment {self.pk} – {self.amount}"


class LegalCase(TimeStampedModel, TenantAwareModel):
    remedial_account = models.ForeignKey(
        RemedialAccount,
        on_delete=models.CASCADE,
        related_name="legal_cases",
    )
    case_type = models.CharField(max_length=20, choices=[
        ("small_claims", "Small Claims"),
        ("regular", "Regular Collection"),
    ])
    status = models.CharField(max_length=20, choices=LegalCaseStatus.choices, default=LegalCaseStatus.DRAFT)
    case_number = models.CharField(max_length=64, blank=True)
    court_name = models.CharField(max_length=255)
    court_branch = models.CharField(max_length=255)
    filing_date = models.DateField(null=True, blank=True)
    assigned_counsel = models.CharField(max_length=255, blank=True)
    next_hearing_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_legal_cases",
    )

    def __str__(self):
        return f"{self.remedial_account.loan_account_no} – {self.get_status_display()}"


class CourtHearing(TenantAwareModel, TimeStampedModel):
    legal_case = models.ForeignKey(
        LegalCase,
        on_delete=models.CASCADE,
        related_name="hearings",
    )
    hearing_date = models.DateField()
    hearing_type = models.CharField(max_length=64)
    status = models.CharField(max_length=10, choices=[
        ("scheduled", "Scheduled"),
        ("done", "Done"),
        ("reset", "Reset"),
        ("cancelled", "Cancelled"),
    ])
    notes = models.TextField(blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    escalation_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["hearing_date", "status"])]

    def __str__(self):
        return f"Hearing {self.hearing_date} – {self.legal_case}"


class RecoveryAction(TimeStampedModel, TenantAwareModel):
    remedial_account = models.ForeignKey(
        RemedialAccount,
        on_delete=models.CASCADE,
        related_name="recovery_actions",
    )
    action_type = models.CharField(max_length=15, choices=RecoveryActionType.choices)
    status = models.CharField(max_length=20, choices=RecoveryActionStatus.choices, default=RecoveryActionStatus.DRAFT)
    initiated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="initiated_recovery_actions",
        null=True,
        blank=True,
    )
    initiated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.remedial_account.loan_account_no} – {self.action_type}"


class RecoveryMilestone(TenantAwareModel, TimeStampedModel):
    recovery_action = models.ForeignKey(
        RecoveryAction,
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    milestone_type = models.CharField(max_length=50)
    target_date = models.DateField(null=True, blank=True)
    actual_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=15, choices=[
        ("pending", "Pending"),
        ("done", "Done"),
        ("overdue", "Overdue"),
    ], default="pending")
    notes = models.TextField(blank=True)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    escalation_sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["target_date", "status"])]

    def __str__(self):
        return f"{self.recovery_action} – {self.milestone_type}"


class WriteOffRequest(TimeStampedModel, TenantAwareModel):
    remedial_account = models.ForeignKey(
        RemedialAccount,
        on_delete=models.CASCADE,
        related_name="write_off_requests",
    )
    status = models.CharField(max_length=20, choices=WriteOffStatus.choices, default=WriteOffStatus.DRAFT)
    recommended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="recommended_write_offs",
        null=True,
        blank=True,
    )
    recommended_at = models.DateTimeField(null=True, blank=True)
    board_resolution_ref = models.CharField(max_length=255, blank=True)
    board_decision_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Write-off {self.remedial_account.loan_account_no} – {self.get_status_display()}"


class RemedialDocument(TenantAwareModel, TimeStampedModel):
    ENTITY_CHOICES = [
        ("remedial_account", "Remedial Account"),
        ("compromise_agreement", "Compromise Agreement"),
        ("legal_case", "Legal Case"),
        ("recovery_action", "Recovery Action"),
        ("write_off", "Write-off"),
    ]

    entity_type = models.CharField(max_length=50, choices=ENTITY_CHOICES)
    entity_id = models.UUIDField()
    doc_type = models.CharField(max_length=128)
    file = models.FileField(upload_to=document_upload_path)
    file_hash = models.CharField(max_length=128, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="remedial_documents",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    version = models.PositiveIntegerField(default=1)
    is_confidential = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="deleted_remedial_documents",
    )

    class Meta:
        indexes = [models.Index(fields=["entity_type", "entity_id"])]

    def __str__(self):
        return f"{self.doc_type} v{self.version}"


class NotificationRule(TenantAwareModel, TimeStampedModel):
    rule_code = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=10, choices=NotificationRuleStatus.choices, default=NotificationRuleStatus.ENABLED)
    days_before = models.IntegerField(null=True, blank=True)
    days_after = models.IntegerField(null=True, blank=True)
    email_to_role = models.CharField(max_length=64, blank=True)
    email_to_specific = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notification_rules",
    )
    template_code = models.CharField(max_length=64)

    def __str__(self):
        return self.rule_code


class NotificationLog(TenantAwareModel, TimeStampedModel):
    rule_code = models.CharField(max_length=64)
    entity_type = models.CharField(max_length=50)
    entity_id = models.UUIDField()
    sent_to = models.CharField(max_length=255)
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=NotificationLogStatus.choices)
    error = models.TextField(blank=True)

    class Meta:
        indexes = [models.Index(fields=["rule_code", "entity_type", "entity_id"])]

    def __str__(self):
        return f"{self.rule_code} → {self.sent_to}"
