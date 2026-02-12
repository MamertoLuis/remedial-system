import logging
from datetime import timedelta
from django.core.exceptions import ValidationError, PermissionDenied
from django.utils import timezone

from apps.core.models import AuditLog

from . import models

logger = logging.getLogger(__name__)


# ===== AUDIT LOGGING UTILITIES =====

def _record_audit(actor, tenant, entity, entity_id, action, notes="", before=None, after=None):
    """Create audit log entry with metadata"""
    return AuditLog.objects.create(
        tenant=tenant,
        actor=actor,
        entity_type=entity,
        entity_id=str(entity_id),
        action=action,
        notes=notes,
        before_json=before,
        after_json=after,
    )


def _record_model_change(actor, tenant, model_instance, action, notes=""):
    """Record model change in audit log"""
    before_data = {}
    after_data = {}
    
    if hasattr(model_instance, '_orig_data'):
        before_data = model_instance._orig_data
    
    model_data = {}
    for field in model_instance._meta.fields:
        if not field.primary_key:
            model_data[field.name] = getattr(model_instance, field.name)
    
    after_data = model_data
    
    _record_audit(
        actor=actor,
        tenant=tenant,
        entity=model_instance._meta.model_name,
        entity_id=model_instance.pk,
        action=action,
        notes=notes,
        before_json=before_data,
        after_json=after_data,
    )


# ===== REMEDIAL ACCOUNT SERVICES =====

class RemedialAccountService:
    """Service for managing remedial account lifecycle"""
    
    @staticmethod
    def create_remedial_account(tenant, loan_account_no, borrower_name, officer=None, **kwargs):
        """Create new remedial account"""
        if models.RemedialAccount.objects.filter(loan_account_no=loan_account_no).exists():
            raise ValidationError("Account with this loan number already exists.")
        
        account = models.RemedialAccount.objects.create(
            tenant=tenant,
            loan_account_no=loan_account_no,
            borrower_name=borrower_name,
            assigned_officer=officer,
            **kwargs
        )
        
        _record_audit(
            actor=None,  # Will be set by view
            tenant=tenant,
            entity="RemedialAccount",
            entity_id=account.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Created account for {borrower_name}",
        )
        
        return account
    
    @staticmethod
    def update_stage(account: models.RemedialAccount, new_stage: str, user, notes=""):
        """Update account stage with validation"""
        if new_stage not in dict(models.RemedialStage.choices):
            raise ValidationError("Invalid stage")
        
        old_stage = account.stage
        account.stage = new_stage
        
        # Handle stage transitions
        if new_stage == models.RemedialStage.CLOSED:
            account.status = models.RemedialStatus.CLOSED
            account.closed_at = timezone.now()
        
        account.save(update_fields=["stage", "status", "closed_at"])
        
        _record_audit(
            actor=user,
            tenant=account.tenant,
            entity="RemedialAccount",
            entity_id=account.pk,
            action=AuditLog.Action.STATE_CHANGE,
            notes=f"Stage changed from {old_stage} to {new_stage}. {notes}",
        )
        
        return account
    
    @staticmethod
    def assign_officer(account: models.RemedialAccount, officer, user):
        """Assign account to officer"""
        old_officer = account.assigned_officer
        account.assigned_officer = officer
        account.save(update_fields=["assigned_officer"])
        
        _record_audit(
            actor=user,
            tenant=account.tenant,
            entity="RemedialAccount",
            entity_id=account.pk,
            action=AuditLog.Action.UPDATE,
            notes=f"Officer changed from {old_officer} to {officer}",
        )
        
        return account


# ===== COMPROMISE AGREEMENT SERVICES =====

class CompromiseAgreementService:
    """Service for managing compromise agreements"""
    
    @staticmethod
    def create_compromise(tenant, remedial_account, agreement_no, settlement_amount, user, **kwargs):
        """Create new compromise agreement"""
        if models.CompromiseAgreement.objects.filter(
            tenant=tenant, 
            remedial_account=remedial_account,
            agreement_no=agreement_no
        ).exists():
            raise ValidationError("Compromise with this agreement number already exists.")
        
        # Validate stage
        if remedial_account.stage != models.RemedialStage.PRE_LEGAL:
            raise ValidationError("Compromises can only be created for pre-legal accounts")
        
        compromise = models.CompromiseAgreement.objects.create(
            tenant=tenant,
            remedial_account=remedial_account,
            agreement_no=agreement_no,
            settlement_amount=settlement_amount,
            created_by=user,
            **kwargs
        )
        
        _record_audit(
            actor=user,
            tenant=tenant,
            entity="CompromiseAgreement",
            entity_id=compromise.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Created compromise {agreement_no} for {remedial_account.loan_account_no}",
        )
        
        return compromise
    
    @staticmethod
    def approve_compromise(compromise: models.CompromiseAgreement, checker_user):
        """Approve compromise agreement with maker-checker validation"""
        if compromise.status != models.CompromiseStatus.DRAFT:
            raise ValidationError("Only drafts can be approved.")
        
        if compromise.created_by_id == checker_user.id:
            raise PermissionDenied("Maker cannot approve their own compromise.")
        
        compromise.status = models.CompromiseStatus.APPROVED
        compromise.approved_by = checker_user
        compromise.approved_at = timezone.now()
        compromise.is_active = True
        compromise.save()
        
        _record_audit(
            actor=checker_user,
            tenant=compromise.tenant,
            entity="CompromiseAgreement",
            entity_id=compromise.pk,
            action=AuditLog.Action.STATE_CHANGE,
            notes="Approved compromise agreement",
        )
        
        return compromise
    
    @staticmethod
    def record_compromise_payment(
        compromise: models.CompromiseAgreement,
        amount: float,
        user,
        schedule_item: models.CompromiseScheduleItem | None = None,
        reference_no: str | None = None,
    ):
        """Record payment against compromise agreement"""
        if amount <= 0:
            raise ValidationError("Payment amount must be positive.")
        
        if compromise.status not in {models.CompromiseStatus.APPROVED, models.CompromiseStatus.ACTIVE}:
            raise ValidationError("Cannot record payment for inactive compromise.")
        
        if schedule_item and schedule_item.compromise_agreement_id != compromise.pk:
            raise ValidationError("Schedule item does not belong to this compromise.")
        
        payment = models.CompromisePayment.objects.create(
            compromise_agreement=compromise,
            schedule_item=schedule_item,
            payment_date=timezone.now().date(),
            amount=amount,
            reference_no=reference_no or "",
            received_by=user,
        )
        
        # Update schedule item if provided
        if schedule_item:
            schedule_item.amount_paid += amount
            if schedule_item.amount_paid >= schedule_item.amount_due:
                schedule_item.status = models.ScheduleStatus.PAID
            else:
                schedule_item.status = models.ScheduleStatus.PARTIAL
            schedule_item.save(update_fields=["amount_paid", "status"])
        
        _record_audit(
            actor=user,
            tenant=compromise.tenant,
            entity="CompromisePayment",
            entity_id=payment.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Recorded payment of {amount}",
        )
        
        return payment
    
    @staticmethod
    def check_compromise_completion(compromise: models.CompromiseAgreement):
        """Check if compromise agreement is fully completed"""
        total_paid = sum(
            payment.amount for payment in compromise.payments.all()
            if payment.status != "failed"
        )
        
        total_due = sum(item.amount_due for item in compromise.schedule_items.all())
        
        if total_paid >= total_due:
            compromise.status = models.CompromiseStatus.COMPLETED
            compromise.save(update_fields=["status"])
            
            _record_audit(
                actor=None,
                tenant=compromise.tenant,
                entity="CompromiseAgreement",
                entity_id=compromise.pk,
                action=AuditLog.Action.STATE_CHANGE,
                notes="Compromise marked as completed",
            )
            
            return True
        return False


# ===== SCHEDULE ITEM SERVICES =====

class ScheduleItemService:
    """Service for managing compromise schedule items"""
    
    @staticmethod
    def create_schedule_item(compromise: models.CompromiseAgreement, seq_no, due_date, amount_due, user):
        """Create schedule item for compromise"""
        if models.CompromiseScheduleItem.objects.filter(
            compromise_agreement=compromise,
            seq_no=seq_no
        ).exists():
            raise ValidationError("Schedule item with this sequence number already exists.")
        
        # Validate total doesn't exceed settlement amount
        total_existing = sum(
            item.amount_due for item in compromise.schedule_items.all()
        )
        
        if total_existing + amount_due > compromise.settlement_amount:
            raise ValidationError("Total scheduled amount exceeds settlement amount.")
        
        schedule_item = models.CompromiseScheduleItem.objects.create(
            compromise_agreement=compromise,
            seq_no=seq_no,
            due_date=due_date,
            amount_due=amount_due,
        )
        
        _record_audit(
            actor=user,
            tenant=compromise.tenant,
            entity="CompromiseScheduleItem",
            entity_id=schedule_item.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Created schedule item #{seq_no}",
        )
        
        return schedule_item
    
    @staticmethod
    def detect_schedule_default(schedule_item: models.CompromiseScheduleItem):
        """Detect if schedule item is default and update status"""
        if schedule_item.amount_paid >= schedule_item.amount_due:
            return False
        
        overdue_days = (timezone.now().date() - schedule_item.due_date).days
        
        if overdue_days > schedule_item.compromise_agreement.grace_days:
            schedule_item.status = models.ScheduleStatus.OVERDUE
            schedule_item.save(update_fields=["status"])
            
            _record_audit(
                actor=None,
                tenant=schedule_item.compromise_agreement.tenant,
                entity="CompromiseScheduleItem",
                entity_id=schedule_item.pk,
                action=AuditLog.Action.STATE_CHANGE,
                notes=f"Marked overdue ({overdue_days} days)",
            )
            
            # Check if compromise should be marked as defaulted
            if overdue_days >= schedule_item.compromise_agreement.default_threshold_days:
                compromise_service = CompromiseAgreementService()
                compromise_service.mark_as_defaulted(schedule_item.compromise_agreement)
                
            return True
        return False


# ===== LEGAL CASE SERVICES =====

class LegalCaseService:
    """Service for managing legal cases"""
    
    @staticmethod
    def create_legal_case(tenant, remedial_account, case_type, court_name, user, **kwargs):
        """Create new legal case"""
        legal_case = models.LegalCase.objects.create(
            tenant=tenant,
            remedial_account=remedial_account,
            case_type=case_type,
            court_name=court_name,
            created_by=user,
            **kwargs
        )
        
        _record_audit(
            actor=user,
            tenant=tenant,
            entity="LegalCase",
            entity_id=legal_case.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Created legal case for {remedial_account.loan_account_no}",
        )
        
        return legal_case
    
    @staticmethod
    def file_legal_case(legal_case: models.LegalCase, case_number, filing_date, user):
        """File legal case with court"""
        if legal_case.status != models.LegalCaseStatus.DRAFT:
            raise ValidationError("Only draft cases can be filed.")
        
        legal_case.case_number = case_number
        legal_case.filing_date = filing_date
        legal_case.status = models.LegalCaseStatus.FILED
        legal_case.save()
        
        _record_audit(
            actor=user,
            tenant=legal_case.tenant,
            entity="LegalCase",
            entity_id=legal_case.pk,
            action=AuditLog.Action.STATE_CHANGE,
            notes=f"Filed case {case_number}",
        )
        
        return legal_case


# ===== RECOVERY ACTION SERVICES =====

class RecoveryActionService:
    """Service for managing recovery actions"""
    
    @staticmethod
    def initiate_recovery_action(tenant, remedial_account, action_type, user, **kwargs):
        """Initiate recovery action"""
        recovery_action = models.RecoveryAction.objects.create(
            tenant=tenant,
            remedial_account=remedial_account,
            action_type=action_type,
            initiated_by=user,
            initiated_at=timezone.now(),
            **kwargs
        )
        
        # Update account stage
        if action_type == models.RecoveryActionType.FORECLOSURE:
            RemedialAccountService().update_stage(
                remedial_account, 
                models.RemedialStage.FORECLOSURE, 
                user,
                notes="Initiated foreclosure action"
            )
        elif action_type == models.RecoveryActionType.DACION:
            RemedialAccountService().update_stage(
                remedial_account,
                models.RemedialStage.DACION,
                user,
                notes="Initiated dacion action"
            )
        
        _record_audit(
            actor=user,
            tenant=tenant,
            entity="RecoveryAction",
            entity_id=recovery_action.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Initiated {action_type} action",
        )
        
        return recovery_action
    
    @staticmethod
    def create_recovery_milestone(
        recovery_action: models.RecoveryAction,
        milestone_type: str,
        target_date: str,
        user,
        **kwargs
    ):
        """Create recovery milestone"""
        milestone = models.RecoveryMilestone.objects.create(
            recovery_action=recovery_action,
            milestone_type=milestone_type,
            target_date=target_date,
            **kwargs
        )
        
        _record_audit(
            actor=user,
            tenant=milestone.recovery_action.tenant,
            entity="RecoveryMilestone",
            entity_id=milestone.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Created milestone {milestone_type}",
        )
        
        return milestone


# ===== WRITE-OFF SERVICES =====

class WriteOffService:
    """Service for managing write-off requests"""
    
    @staticmethod
    def recommend_write_off(tenant, remedial_account, user, notes="", **kwargs):
        """Recommend write-off for account"""
        write_off = models.WriteOffRequest.objects.create(
            tenant=tenant,
            remedial_account=remedial_account,
            recommended_by=user,
            recommended_at=timezone.now(),
            **kwargs
        )
        
        _record_audit(
            actor=user,
            tenant=tenant,
            entity="WriteOffRequest",
            entity_id=write_off.pk,
            action=AuditLog.Action.CREATE,
            notes=f"Recommended write-off for {remedial_account.loan_account_no}",
        )
        
        return write_off
    
    @staticmethod
    def record_board_decision(write_off: models.WriteOffRequest, approved: bool, user, board_resolution_ref=None):
        """Record board decision on write-off"""
        if write_off.status != models.WriteOffStatus.RECOMMENDED:
            raise ValidationError("Only recommended write-offs can have board decisions.")
        
        if approved:
            write_off.status = models.WriteOffStatus.BOARD_APPROVED
            notes = "Board approved"
            if board_resolution_ref:
                write_off.board_resolution_ref = board_resolution_ref
        else:
            write_off.status = models.WriteOffStatus.REJECTED
            notes = "Board rejected"
        
        write_off.board_decision_date = timezone.now().date()
        write_off.save()
        
        _record_audit(
            actor=user,
            tenant=write_off.tenant,
            entity="WriteOffRequest",
            entity_id=write_off.pk,
            action=AuditLog.Action.STATE_CHANGE,
            notes=f"{notes} write-off",
        )
        
        return write_off


# ===== NOTIFICATION SERVICES =====

class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    def send_notification(rule: models.NotificationRule, entity_type: str, entity_id, sent_to: str, message: str):
        """Send notification with error handling"""
        status = models.NotificationLogStatus.SENT
        error_text = ""
        
        try:
            logger.info("[Notification] %s → %s (%s)", rule.rule_code, sent_to, message)
            # TODO: Implement actual email sending here
        except Exception as exc:
            status = models.NotificationLogStatus.FAILED
            error_text = str(exc)
            logger.error("Notification failed: %s", exc, exc_info=True)
        
        notification_log = models.NotificationLog.objects.create(
            rule_code=rule.rule_code,
            entity_type=entity_type,
            entity_id=entity_id,
            sent_to=sent_to,
            status=status,
            error=error_text,
        )
        
        return notification_log
    
    @staticmethod
    def send_scheduled_reminders(tenant):
        """Send scheduled reminder notifications"""
        from .selectors import active_compromises_needing_reminders
        
        reminders = active_compromises_needing_reminders(tenant)
        
        for item in reminders["due_items"]:
            # TODO: Implement reminder logic
            pass
        
        for item in reminders["overdue_items"]:
            # TODO: Implement escalation logic
            pass


# ===== DOCUMENT SERVICES =====

class DocumentService:
    """Service for managing documents"""
    
    @staticmethod
    def upload_document(
        tenant, 
        entity_type: str, 
        entity_id, 
        doc_type: str, 
        file_obj, 
        uploaded_by,
        is_confidential=True
    ):
        """Upload document with version control"""
        # Calculate file hash
        import hashlib
        file_hash = hashlib.sha256(file_obj.read()).hexdigest()
        file_obj.seek(0)
        
        # Check for existing version
        latest_doc = (
            models.RemedialDocument.objects
            .filter(entity_type=entity_type, entity_id=entity_id, doc_type=doc_type)
            .order_by("-version", "-uploaded_at")
            .first()
        )
        
        version = (latest_doc.version + 1) if latest_doc else 1
        
        # Create new document version
        document = models.RemedialDocument.objects.create(
            tenant=tenant,
            entity_type=entity_type,
            entity_id=entity_id,
            doc_type=doc_type,
            file=file_obj,
            file_hash=file_hash,
            uploaded_by=uploaded_by,
            version=version,
            is_confidential=is_confidential,
        )
        
        _record_audit(
            actor=uploaded_by,
            tenant=tenant,
            entity="RemedialDocument",
            entity_id=document.pk,
            action=AuditLog.Action.UPLOAD,
            notes=f"Uploaded {doc_type} v{version}",
        )
        
        return document
    
    @staticmethod
    def delete_document(document: models.RemedialDocument, user):
        """Soft delete document"""
        if document.is_deleted:
            raise ValidationError("Document is already deleted.")
        
        document.is_deleted = True
        document.deleted_at = timezone.now()
        document.deleted_by = user
        document.save()
        
        _record_audit(
            actor=user,
            tenant=document.tenant,
            entity="RemedialDocument",
            entity_id=document.pk,
            action=AuditLog.Action.UPDATE,
            notes="Document deleted",
        )
        
        return document


# ===== DATA QUALITY SERVICES =====

class DataQualityService:
    """Service for data quality checks"""
    
    @staticmethod
    def run_data_quality_checks(tenant):
        """Run comprehensive data quality checks"""
        issues = []
        
        # Check accounts missing data
        missing_data = models.RemedialAccount.objects.filter(
            tenant=tenant,
            borrower_name=""
        )
        
        if missing_data.exists():
            issues.append({
                "type": "missing_borrower_name",
                "count": missing_data.count(),
                "severity": "high"
            })
        
        # Check compromises with inconsistent data
        inconsistent = models.CompromiseAgreement.objects.filter(
            tenant=tenant,
            schedule_items__amount_due__sum__gt=models.F("settlement_amount")
        )
        
        if inconsistent.exists():
            issues.append({
                "type": "inconsistent_compromise_totals",
                "count": inconsistent.distinct().count(),
                "severity": "medium"
            })
        
        return issues


# ===== STATISTICS SERVICES =====

class StatisticsService:
    """Service for generating statistics and metrics"""
    
    @staticmethod
    def get_dashboard_metrics(tenant, days=30):
        """Get dashboard metrics for tenant"""
        from .selectors import summary_statistics, trend_data
        
        return {
            "summary": summary_statistics(tenant),
            "trends": trend_data(tenant, days),
            "quality_issues": DataQualityService.run_data_quality_checks(tenant)
        }
