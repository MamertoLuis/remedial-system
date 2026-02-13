from datetime import date, timedelta
from django.db.models import Prefetch, Q, Count, Sum, Avg, Max, Case, When, F
from django.utils import timezone

from . import models


# ===== BASIC QUERYSET SELECTORS =====

def remedial_accounts_for_tenant(tenant):
    return (
        models.RemedialAccount.objects.filter(tenant=tenant)
        .select_related("assigned_officer")
        .order_by("loan_account_no")
    )


def active_compromise_agreements(tenant):
    return (
        models.CompromiseAgreement.objects.filter(tenant=tenant, status__in=[
            models.CompromiseStatus.APPROVED,
            models.CompromiseStatus.ACTIVE,
        ])
        .select_related("remedial_account", "approved_by")
        .prefetch_related("schedule_items")
    )


def defaulted_compromise_agreements(tenant):
    return models.CompromiseAgreement.objects.filter(
        tenant=tenant,
        status=models.CompromiseStatus.DEFAULTED,
    )


# ===== DASHBOARD SELECTORS =====

def dashboard_accounts_overview(tenant, officer=None, stage=None, status=None, days=None):
    """Remedial accounts for dashboard with filters and counts"""
    queryset = remedial_accounts_for_tenant(tenant)
    
    if officer:
        queryset = queryset.filter(assigned_officer=officer)
    if stage:
        queryset = queryset.filter(stage=stage)
    if status:
        queryset = queryset.filter(status=status)
    
    if days:
        since_date = timezone.now().date() - timedelta(days=days)
        queryset = queryset.filter(created_at__gte=since_date)
    
    return queryset


def get_dashboard_overview_data(tenant):
    """Get overview data for the dashboard."""
    return {
        'accounts_count': models.RemedialAccount.objects.filter(tenant=tenant).count(),
        'compromises_count': models.CompromiseAgreement.objects.filter(tenant=tenant).count(),
        'legal_cases_count': models.LegalCase.objects.filter(tenant=tenant).count(),
        'hearings_count': models.CourtHearing.objects.filter(tenant=tenant).count(),
        'recovery_actions_count': models.RecoveryAction.objects.filter(tenant=tenant).count(),
        'milestones_count': models.RecoveryMilestone.objects.filter(tenant=tenant).count(),
        'write_offs_count': models.WriteOffRequest.objects.filter(tenant=tenant).count(),
    }

def dashboard_compromise_summary(tenant):
    """Compromise agreements summary with status counts and amounts"""
    return (
        models.CompromiseAgreement.objects.filter(tenant=tenant)
        .values("status")
        .annotate(
            count=Count("id"),
            total_settlement=Sum("settlement_amount"),
            total_paid=Sum("payments__amount", filter=Q(payments__status="success")),
            avg_days=Avg(
                models.F("payments__payment_date") - 
                models.F("created_at")
            )
        )
        .order_by("status")
    )


def dashboard_legal_cases_summary(tenant):
    """Legal cases summary by type and status"""
    return (
        models.LegalCase.objects.filter(tenant=tenant)
        .values("case_type", "status")
        .annotate(
            count=Count("id"),
            upcoming_hearings=Count(
                "hearings",
                filter=Q(
                    hearings__status="scheduled",
                    hearings__hearing_date__gte=timezone.now().date()
                )
            )
        )
        .order_by("case_type", "status")
    )


# ===== REPORT SELECTORS =====

def report_accounts_by_stage(tenant, start_date=None, end_date=None):
    """Accounts grouped by stage for reporting"""
    queryset = remedial_accounts_for_tenant(tenant)
    
    if start_date:
        queryset = queryset.filter(created_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(created_at__lte=end_date)
    
    return (
        queryset.values("stage", "status")
        .annotate(
            count=Count("id"),
            total_balance=Sum("outstanding_balance_ref")
        )
        .order_by("stage", "status")
    )


def report_compromise_performance(tenant, start_date=None, end_date=None):
    """Compromise agreement performance report"""
    queryset = models.CompromiseAgreement.objects.filter(tenant=tenant)
    
    if start_date:
        queryset = queryset.filter(compromise_signed_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(compromise_signed_date__lte=end_date)
    
    return (
        queryset.values("status")
        .annotate(
            agreements=Count("id"),
            total_settlement=Sum("settlement_amount"),
            total_paid=Sum("payments__amount", filter=Q(payments__status="success")),
            completion_rate=Sum(
                Case(
                    When(schedule_items__status="paid", then=1),
                    default=0
                )
            ) / Count("schedule_items")
        )
        .order_by("status")
    )


def report_payments_summary(tenant, start_date=None, end_date=None):
    """Compromise payments summary report"""
    queryset = models.CompromisePayment.objects.filter(
        compromise_agreement__tenant=tenant
    )
    
    if start_date:
        queryset = queryset.filter(payment_date__gte=start_date)
    if end_date:
        queryset = queryset.filter(payment_date__lte=end_date)
    
    return (
        queryset.values("compromise_agreement__status")
        .annotate(
            count=Count("id"),
            total_amount=Sum("amount"),
            avg_amount=Avg("amount")
        )
        .order_by("compromise_agreement__status")
    )


# ===== BUSINESS LOGIC SELECTORS =====

def accounts_pending_compromise(tenant):
    """Accounts that need compromise consideration"""
    return remedial_accounts_for_tenant(tenant).filter(
        stage=models.RemedialStage.PRE_LEGAL,
        status=models.RemedialStatus.ACTIVE
    )


def accounts_in_compromise_stage(tenant):
    """Accounts currently in compromise stage"""
    return remedial_accounts_for_tenant(tenant).filter(
        stage=models.RemedialStage.COMPROMISE,
        status=models.RemedialStatus.ACTIVE
    )


def accounts_needing_hearing_reminders(tenant, days_ahead=7):
    """Accounts with scheduled hearings in next N days"""
    return (
        models.CourtHearing.objects.filter(
            legal_case__tenant=tenant,
            status="scheduled",
            hearing_date__lte=timezone.now().date() + timedelta(days=days_ahead),
            hearing_date__gte=timezone.now().date(),
        )
        .select_related("legal_case")
        .order_by("hearing_date")
    )


def accounts_with_overdue_milestones(tenant):
    """Accounts with recovery milestones that are overdue"""
    return (
        models.RecoveryMilestone.objects.filter(
            recovery_action__tenant=tenant,
            status="overdue",
        )
        .select_related("recovery_action")
        .order_by("target_date")
    )


# ===== MONITORING & ALERT SELECTORS =====

def active_compromises_needing_reminders(tenant, grace_days=3, default_threshold=30):
    """Compromises that need reminder notifications"""
    today = timezone.now().date()
    
    due_items = (
        models.CompromiseScheduleItem.objects.filter(
            compromise_agreement__tenant=tenant,
            compromise_agreement__status__in=[
                models.CompromiseStatus.APPROVED,
                models.CompromiseStatus.ACTIVE,
            ],
            status__in=[models.ScheduleStatus.DUE, models.ScheduleStatus.PARTIAL],
        )
        .filter(
            # Items due soon (grace period)
            due_date__lte=today + timedelta(days=grace_days),
            last_reminder_sent_at__isnull=True,
        )
        .select_related("compromise_agreement")
    )
    
    overdue_items = (
        models.CompromiseScheduleItem.objects.filter(
            compromise_agreement__tenant=tenant,
            compromise_agreement__status__in=[
                models.CompromiseStatus.APPROVED,
                models.CompromiseStatus.ACTIVE,
            ],
            status=models.ScheduleStatus.DUE,
        )
        .filter(
            # Items overdue (past threshold)
            due_date__lt=today - timedelta(days=default_threshold),
            last_escalation_sent_at__isnull=True,
        )
        .select_related("compromise_agreement")
    )
    
    return {"due_items": due_items, "overdue_items": overdue_items}


def upcoming_hearings(tenant, days_ahead=14):
    """Hearings scheduled in next N days"""
    return (
        models.CourtHearing.objects.filter(
            legal_case__tenant=tenant,
            status="scheduled",
            hearing_date__lte=timezone.now().date() + timedelta(days=days_ahead),
            hearing_date__gte=timezone.now().date(),
        )
        .select_related("legal_case")
        .order_by("hearing_date")
    )


def accounts_for_reconsideration(tenant):
    """Accounts that need action reconsideration"""
    return (
        models.RemedialAccount.objects.filter(
            tenant=tenant,
            stage=models.RemedialStage.COMPROMISE,
            status=models.RemedialStatus.ACTIVE,
        )
        .annotate(
            overdue_payments=Count(
                "compromise_agreements__schedule_items",
                filter=Q(
                    compromise_agreements__schedule_items__status="overdue"
                )
            )
        )
        .filter(overdue_payments__gt=0)
        .select_related("assigned_officer")
    )


# ===== DATA QUALITY SELECTORS =====

def accounts_missing_data(tenant):
    """Accounts with missing required data"""
    return (
        models.RemedialAccount.objects.filter(tenant=tenant)
        .filter(
            Q(borrower_name="") | Q(borrower_name__isnull=True)
        )
        .order_by("loan_account_no")
    )


def compromises_inconsistent(tenant):
    """Compromises with inconsistent data"""
    return (
        models.CompromiseAgreement.objects.filter(tenant=tenant)
        .select_related("remedial_account")
        .filter(
            # Check if total scheduled items match settlement amount
            schedule_items__amount_due__sum__lt=models.F("settlement_amount")
        )
    )


# ===== UTILITY SELECTORS =====

def notification_log_for_entity(tenant, entity_type, entity_id):
    """Notification log for specific entity"""
    base = models.NotificationLog.objects.filter(
        Q(entity_type=entity_type)
        & Q(entity_id=entity_id)
        & Q(status=models.NotificationLogStatus.SENT)
    )
    if tenant:
        base = base.filter(rule_code__startswith=tenant.code)
    return base


def document_history_for_entity(tenant, entity_type, entity_id):
    """Document upload history for entity"""
    return (
        models.RemedialDocument.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
            is_deleted=False,
        )
        .select_related("uploaded_by")
        .order_by("-version", "-uploaded_at")
    )


def audit_trail_for_entity(tenant, entity_type, entity_id):
    """Audit trail for specific entity"""
    return (
        models.AuditLog.objects.filter(
            entity_type=entity_type,
            entity_id=entity_id,
        )
        .select_related("actor")
        .order_by("-created_at")
    )


# ===== STATISTICAL SELECTORS =====

def summary_statistics(tenant):
    """High-level statistics for tenant"""
    return {
        "total_accounts": remedial_accounts_for_tenant(tenant).count(),
        "active_compromises": active_compromise_agreements(tenant).count(),
        "total_settlement": active_compromise_agreements(tenant).aggregate(
            total=Sum("settlement_amount")
        )["total"] or 0,
        "legal_cases": models.LegalCase.objects.filter(tenant=tenant).count(),
        "recovery_actions": models.RecoveryAction.objects.filter(tenant=tenant).count(),
        "write_off_requests": models.WriteOffRequest.objects.filter(tenant=tenant).count(),
    }


def trend_data(tenant, days=30):
    """Trend data for the last N days"""
    since_date = timezone.now().date() - timedelta(days=days)
    
    return {
        "accounts_created": remedial_accounts_for_tenant(tenant).filter(
            created_at__gte=since_date
        ).count(),
        "compromises_signed": models.CompromiseAgreement.objects.filter(
            tenant=tenant,
            compromise_signed_date__gte=since_date
        ).count(),
        "payments_received": models.CompromisePayment.objects.filter(
            compromise_agreement__tenant=tenant,
            payment_date__gte=since_date
        ).count(),
    }


def get_dashboard_metrics(tenant):
    """Get comprehensive dashboard metrics"""
    return {
        "summary": summary_statistics(tenant),
        "trends": trend_data(tenant, 30),
        "quality_issues": DataQualityService.run_data_quality_checks(tenant)
    }
