from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from . import models


@admin.register(models.RemedialAccount)
class RemedialAccountAdmin(admin.ModelAdmin):
    list_display = ('loan_account_no', 'borrower_name', 'stage', 'status', 'assigned_officer', 'created_at')
    list_filter = ('stage', 'status', 'created_at')
    search_fields = ('loan_account_no', 'borrower_name', 'borrower_id_ref')
    readonly_fields = ['id', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('loan_account_no', 'borrower_name', 'borrower_id_ref', 'outstanding_balance_ref')
        }),
        ('Status & Assignment', {
            'fields': ('stage', 'status', 'assigned_officer')
        }),
        ('Dates & Notes', {
            'fields': ('closed_at', 'remarks')
        }),
        ('Advanced', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )


@admin.register(models.CompromiseAgreement)
class CompromiseAgreementAdmin(admin.ModelAdmin):
    list_display = ('agreement_no', 'remedial_account', 'status', 'settlement_amount', 'approved_by', 'created_at')
    list_filter = ('status', 'created_at', 'approved_at')
    search_fields = ('agreement_no', 'remedial_account__loan_account_no', 'remedial_account__borrower_name')
    readonly_fields = ['id', 'created_at', 'updated_at', 'approved_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('agreement_no', 'remedial_account', 'settlement_amount')
        }),
        ('Terms & Conditions', {
            'fields': ('terms', 'grace_days', 'default_threshold_days')
        }),
        ('Status & Approval', {
            'fields': ('status', 'approved_by', 'approved_at', 'compromise_signed_date', 'is_active')
        }),
        ('Audit', {
            'fields': ('created_by',),
            'classes': ('collapse',)
        })
    )


@admin.register(models.CompromiseScheduleItem)
class CompromiseScheduleItemAdmin(admin.ModelAdmin):
    list_display = ('compromise_agreement', 'seq_no', 'due_date', 'amount_due', 'amount_paid', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('compromise_agreement__agreement_no', 'compromise_agreement__remedial_account__loan_account_no')
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(models.CompromisePayment)
class CompromisePaymentAdmin(admin.ModelAdmin):
    list_display = ('compromise_agreement', 'schedule_item', 'payment_date', 'amount', 'reference_no', 'received_by')
    list_filter = ('payment_date', 'received_by')
    search_fields = ('compromise_agreement__agreement_no', 'schedule_item__compromise_agreement__agreement_no', 'reference_no')
    readonly_fields = ['id', 'created_at', 'updated_at', 'received_by', 'payment_date']


@admin.register(models.LegalCase)
class LegalCaseAdmin(admin.ModelAdmin):
    list_display = ('remedial_account', 'case_type', 'status', 'case_number', 'court_name', 'created_at')
    list_filter = ('case_type', 'status', 'created_at')
    search_fields = ('remedial_account__loan_account_no', 'remedial_account__borrower_name', 'case_number')
    readonly_fields = ['id', 'created_at', 'updated_at', 'created_by']


@admin.register(models.CourtHearing)
class CourtHearingAdmin(admin.ModelAdmin):
    list_display = ('legal_case', 'hearing_date', 'hearing_type', 'status')
    list_filter = ('status', 'hearing_date')
    search_fields = ('legal_case__remedial_account__loan_account_no', 'hearing_type')
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(models.RecoveryAction)
class RecoveryActionAdmin(admin.ModelAdmin):
    list_display = ('remedial_account', 'action_type', 'status', 'initiated_by', 'initiated_at')
    list_filter = ('action_type', 'status', 'initiated_at')
    search_fields = ('remedial_account__loan_account_no', 'remedial_account__borrower_name')
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(models.RecoveryMilestone)
class RecoveryMilestoneAdmin(admin.ModelAdmin):
    list_display = ('recovery_action', 'milestone_type', 'target_date', 'actual_date', 'status')
    list_filter = ('status', 'target_date', 'actual_date')
    search_fields = ('recovery_action__remedial_account__loan_account_no', 'milestone_type')
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(models.WriteOffRequest)
class WriteOffRequestAdmin(admin.ModelAdmin):
    list_display = ('remedial_account', 'status', 'recommended_by', 'board_decision_date')
    list_filter = ('status', 'board_decision_date')
    search_fields = ('remedial_account__loan_account_no', 'remedial_account__borrower_name', 'board_resolution_ref')
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(models.RemedialDocument)
class RemedialDocumentAdmin(admin.ModelAdmin):
    list_display = ('doc_type', 'entity_type', 'entity_id', 'version', 'uploaded_by', 'uploaded_at')
    list_filter = ('entity_type', 'is_confidential', 'uploaded_at')
    search_fields = ('doc_type', 'entity_id')
    readonly_fields = ['id', 'created_at', 'updated_at', 'uploaded_at', 'file_hash']


@admin.register(models.NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ('rule_code', 'status', 'email_to_role', 'template_code', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('rule_code', 'template_code')
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(models.NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ('rule_code', 'entity_type', 'sent_to', 'status', 'sent_at')
    list_filter = ('status', 'sent_at')
    search_fields = ('rule_code', 'entity_type', 'entity_id')
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(models.AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('entity_type', 'entity_id', 'actor', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('entity_type', 'entity_id', 'notes')
    readonly_fields = ['id', 'created_at', 'updated_at', 'tenant', 'actor', 'entity_type', 'entity_id', 'action', 'before_json', 'after_json']
    exclude = ['tenant']
