from django.contrib import admin

from . import models


@admin.register(models.RemedialAccount)
class RemedialAccountAdmin(admin.ModelAdmin):
    list_display = ("loan_account_no", "borrower_name", "stage", "status", "assigned_officer", "tenant")
    list_filter = ("stage", "status", "tenant")
    search_fields = ("loan_account_no", "borrower_name")


@admin.register(models.CompromiseAgreement)
class CompromiseAgreementAdmin(admin.ModelAdmin):
    list_display = ("agreement_no", "remedial_account", "status", "settlement_amount", "tenant")
    list_filter = ("status", "tenant")
    search_fields = ("agreement_no",)


@admin.register(models.CompromiseScheduleItem)
class CompromiseScheduleItemAdmin(admin.ModelAdmin):
    list_display = ("compromise_agreement", "seq_no", "due_date", "status")
    list_filter = ("status",)


@admin.register(models.LegalCase)
class LegalCaseAdmin(admin.ModelAdmin):
    list_display = ("case_number", "remedial_account", "status", "court_name")
    list_filter = ("status", "case_type")
    search_fields = ("case_number", "court_name")


@admin.register(models.RecoveryAction)
class RecoveryActionAdmin(admin.ModelAdmin):
    list_display = ("remedial_account", "action_type", "status")
    list_filter = ("action_type", "status")


@admin.register(models.WriteOffRequest)
class WriteOffRequestAdmin(admin.ModelAdmin):
    list_display = ("remedial_account", "status", "recommended_by")
    list_filter = ("status",)


@admin.register(models.RemedialDocument)
class RemedialDocumentAdmin(admin.ModelAdmin):
    list_display = ("doc_type", "entity_type", "version", "uploaded_by")
    list_filter = ("entity_type",)


@admin.register(models.NotificationRule)
class NotificationRuleAdmin(admin.ModelAdmin):
    list_display = ("rule_code", "status", "template_code")
    list_filter = ("status",)


@admin.register(models.NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ("rule_code", "entity_type", "sent_to", "status")
    list_filter = ("status",)
