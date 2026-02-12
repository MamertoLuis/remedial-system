import json
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, Div, HTML
from crispy_forms.bootstrap import PrependedText

from . import models


# ===== CORE MODEL FORMS =====

class RemedialAccountForm(forms.ModelForm):
    """Form for managing remedial accounts"""
    
    class Meta:
        model = models.RemedialAccount
        fields = [
            "loan_account_no", "borrower_name", "borrower_id_ref", 
            "outstanding_balance_ref", "stage", "status", "assigned_officer", "remarks", "metadata"
        ]
        widgets = {
            "stage": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "metadata": forms.Textarea(attrs={"rows": 3, "placeholder": "JSON metadata"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("loan_account_no"),
                Field("borrower_name"),
                Field("borrower_id_ref"),
                Field("outstanding_balance_ref"),
                Field("stage"),
                Field("status"),
                Field("assigned_officer"),
                Field("remarks"),
                Field("metadata"),
                Submit("submit", "Save Account"),
            )
        )
    
    def clean_metadata(self):
        metadata = self.cleaned_data.get("metadata", "{}")
        if metadata:
            try:
                json.loads(metadata)
            except json.JSONDecodeError:
                raise ValidationError("Metadata must be valid JSON")
        return metadata


class CompromiseAgreementForm(forms.ModelForm):
    """Form for creating/editing compromise agreements"""
    
    class Meta:
        model = models.CompromiseAgreement
        fields = [
            "agreement_no", "remedial_account", "settlement_amount", "start_date", 
            "terms_json", "grace_days", "default_threshold_days", "compromise_signed_date"
        ]
        widgets = {
            "terms_json": forms.Textarea(attrs={"rows": 4, "placeholder": "JSON terms"}),
            "settlement_amount": forms.NumberInput(attrs={"step": "0.01"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                PrependedText("agreement_no", "AGREEMENT-"),
                Field("remedial_account"),
                Field("settlement_amount"),
                Field("start_date"),
                Field("terms_json"),
                Div(
                    Field("grace_days"),
                    Field("default_threshold_days"),
                    css_class="row"
                ),
                Field("compromise_signed_date"),
                Submit("submit", "Save Compromise"),
            )
        )
    
    def clean_agreement_no(self):
        agreement_no = self.cleaned_data["agreement_no"]
        if not agreement_no.startswith("AGREEMENT-"):
            self.cleaned_data["agreement_no"] = f"AGREEMENT-{agreement_no}"
        return self.cleaned_data["agreement_no"]
    
    def clean_settlement_amount(self):
        amount = self.cleaned_data["settlement_amount"]
        if amount <= 0:
            raise forms.ValidationError("Settlement amount must be positive.")
        return amount
    
    def clean_terms_json(self):
        terms = self.cleaned_data.get("terms_json", "{}")
        if terms:
            try:
                json.loads(terms)
            except json.JSONDecodeError:
                raise ValidationError("Terms must be valid JSON")
        return terms


class CompromiseScheduleItemForm(forms.ModelForm):
    """Form for creating compromise schedule items"""
    
    class Meta:
        model = models.CompromiseScheduleItem
        fields = ["seq_no", "due_date", "amount_due", "notes"]
        widgets = {
            "amount_due": forms.NumberInput(attrs={"step": "0.01"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.compromise_agreement = kwargs.pop("compromise_agreement", None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("seq_no"),
                Field("due_date"),
                Field("amount_due"),
                Field("notes"),
                Submit("submit", "Add Schedule Item"),
            )
        )
    
    def clean_seq_no(self):
        seq_no = self.cleaned_data["seq_no"]
        if self.compromise_agreement:
            existing = models.CompromiseScheduleItem.objects.filter(
                compromise_agreement=self.compromise_agreement,
                seq_no=seq_no
            ).exists()
            if existing:
                raise ValidationError("Schedule item with this sequence number already exists.")
        return seq_no
    
    def clean_amount_due(self):
        amount = self.cleaned_data["amount_due"]
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount


class CompromisePaymentForm(forms.ModelForm):
    """Form for recording compromise payments"""
    
    class Meta:
        model = models.CompromisePayment
        fields = ["schedule_item", "amount", "reference_no"]
        widgets = {
            "amount": forms.NumberInput(attrs={"step": "0.01"}),
        }
    
    def __init__(self, *args, **kwargs):
        self.compromise_agreement = kwargs.pop("compromise_agreement", None)
        super().__init__(*args, **kwargs)
        
        if self.compromise_agreement:
            self.fields["schedule_item"].queryset = (
                models.CompromiseScheduleItem.objects.filter(
                    compromise_agreement=self.compromise_agreement
                ).exclude(status=models.ScheduleStatus.PAID)
            )
        
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("schedule_item"),
                Div(
                    PrependedText("amount", "₱"),
                    css_class="col-md-6"
                ),
                Field("reference_no"),
                Submit("submit", "Record Payment"),
            )
        )
    
    def clean_amount(self):
        amount = self.cleaned_data["amount"]
        if amount <= 0:
            raise forms.ValidationError("Payment amount must be positive.")
        return amount


# ===== LEGAL FORMS =====

class LegalCaseForm(forms.ModelForm):
    """Form for managing legal cases"""
    
    class Meta:
        model = models.LegalCase
        fields = [
            "remedial_account", "case_type", "status", "case_number", "court_name",
            "court_branch", "filing_date", "assigned_counsel", "next_hearing_date"
        ]
        widgets = {
            "filing_date": forms.DateInput(attrs={"type": "date"}),
            "next_hearing_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("remedial_account"),
                Field("case_type"),
                Field("status"),
                Field("case_number"),
                Field("court_name"),
                Field("court_branch"),
                Field("filing_date"),
                Field("assigned_counsel"),
                Field("next_hearing_date"),
                Submit("submit", "Save Legal Case"),
            )
        )


class CourtHearingForm(forms.ModelForm):
    """Form for managing court hearings"""
    
    class Meta:
        model = models.CourtHearing
        fields = [
            "legal_case", "hearing_date", "hearing_type", "status", "notes"
        ]
        widgets = {
            "hearing_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("legal_case"),
                Field("hearing_date"),
                Field("hearing_type"),
                Field("status"),
                Field("notes"),
                Submit("submit", "Save Hearing"),
            )
        )


# ===== RECOVERY FORMS =====

class RecoveryActionForm(forms.ModelForm):
    """Form for managing recovery actions"""
    
    class Meta:
        model = models.RecoveryAction
        fields = [
            "remedial_account", "action_type", "status", "initiated_at"
        ]
        widgets = {
            "initiated_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("remedial_account"),
                Field("action_type"),
                Field("status"),
                Field("initiated_at"),
                Submit("submit", "Save Recovery Action"),
            )
        )


class RecoveryMilestoneForm(forms.ModelForm):
    """Form for managing recovery milestones"""
    
    class Meta:
        model = models.RecoveryMilestone
        fields = [
            "recovery_action", "milestone_type", "target_date", "actual_date", 
            "status", "notes"
        ]
        widgets = {
            "target_date": forms.DateInput(attrs={"type": "date"}),
            "actual_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("recovery_action"),
                Field("milestone_type"),
                Field("target_date"),
                Field("actual_date"),
                Field("status"),
                Field("notes"),
                Submit("submit", "Save Milestone"),
            )
        )


# ===== WRITE-OFF FORMS =====

class WriteOffRequestForm(forms.ModelForm):
    """Form for managing write-off requests"""
    
    class Meta:
        model = models.WriteOffRequest
        fields = [
            "remedial_account", "status", "board_resolution_ref", 
            "board_decision_date", "notes"
        ]
        widgets = {
            "board_decision_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("remedial_account"),
                Field("status"),
                Field("board_resolution_ref"),
                Field("board_decision_date"),
                Field("notes"),
                Submit("submit", "Save Write-off Request"),
            )
        )


# ===== DOCUMENT FORMS =====

class RemedialDocumentForm(forms.ModelForm):
    """Form for uploading remedial documents"""
    
    class Meta:
        model = models.RemedialDocument
        fields = ["entity_type", "entity_id", "doc_type", "file", "is_confidential"]
        widgets = {
            "entity_id": forms.HiddenInput(),
            "file": forms.FileInput(attrs={"accept": ".pdf,.doc,.docx,.jpg,.jpeg,.png"}),
        }
    
    def __init__(self, *args, **kwargs):
        self.entity_type = kwargs.pop("entity_type", None)
        super().__init__(*args, **kwargs)
        
        if self.entity_type:
            self.fields["entity_type"].initial = self.entity_type
            self.fields["entity_type"].widget = forms.HiddenInput()
        
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("entity_type"),
                Field("entity_id"),
                Field("doc_type"),
                Field("file"),
                Div(
                    Field("is_confidential"),
                    css_class="form-check"
                ),
                Submit("submit", "Upload Document"),
            )
        )
    
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get("file")
        
        if file:
            # Validate file size (10MB max)
            if file.size > 10 * 1024 * 1024:
                raise ValidationError("File size must be less than 10MB")
            
            # Validate file type
            allowed_extensions = {'.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png'}
            file_ext = file.name.lower().split('.')[-1]
            if f'.{file_ext}' not in allowed_extensions:
                raise ValidationError(f"File type .{file_ext} not allowed")
        
        return cleaned_data


# ===== SEARCH AND FILTER FORMS =====

class RemedialAccountSearchForm(forms.Form):
    """Search form for remedial accounts"""
    loan_account_no = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={"placeholder": "Loan Account No"})
    )
    borrower_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Borrower Name"})
    )
    stage = forms.ChoiceField(
        choices=[("", "All Stages")] + list(models.RemedialStage.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + list(models.RemedialStatus.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    assigned_officer = forms.ModelChoiceField(
        queryset=models.User.objects.all(),
        required=False,
        empty_label="All Officers",
        widget=forms.Select(attrs={"class": "form-select"})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "get"
        self.helper.layout = Layout(
            Div(
                Div(
                    Field("loan_account_no"),
                    css_class="col-md-4"
                ),
                Div(
                    Field("borrower_name"),
                    css_class="col-md-4"
                ),
                Div(
                    Field("stage"),
                    css_class="col-md-4"
                ),
                Div(
                    Field("status"),
                    css_class="col-md-4"
                ),
                Div(
                    Field("assigned_officer"),
                    css_class="col-md-4"
                ),
                Submit("search", "Search", css_class="btn-primary mt-2"),
            )
        )


class CompromiseFilterForm(forms.Form):
    """Filter form for compromise agreements"""
    status = forms.ChoiceField(
        choices=[("", "All Statuses")] + list(models.CompromiseStatus.choices),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )
    agreement_no = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Agreement No"})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_method = "get"
        self.helper.layout = Layout(
            Div(
                Field("status"),
                Field("agreement_no"),
                Submit("filter", "Filter", css_class="btn-primary"),
            )
        )
