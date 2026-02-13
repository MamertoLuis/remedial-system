from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.http import Http404, HttpResponseForbidden
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

# Account views
from django.db.models import Count
from . import models
from . import forms
from .forms import RemedialAccountForm, CompromiseAgreementForm

class CompromiseListView(ListView):
    """List all compromise agreements"""
    model = models.CompromiseAgreement
    template_name = 'remedial/compromise_list.html'
    context_object_name = 'compromises'
    paginate_by = 20
    
    def get_queryset(self):
        return models.CompromiseAgreement.objects.filter(tenant=self.request.tenant).select_related('remedial_account').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Compromise Agreements'
        context['active_page'] = 'compromises'
        return context

class CompromiseCreateView(CreateView):
    """Create a new compromise agreement"""
    model = models.CompromiseAgreement
    form_class = CompromiseAgreementForm
    template_name = 'remedial/compromise_form.html'
    success_url = reverse_lazy('remedial:compromiseagreement-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Compromise Agreement'
        context['active_page'] = 'compromises'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class LegalCaseDetailView(DetailView):
    """View legal case details"""
    model = models.LegalCase
    template_name = 'remedial/legal_detail.html'
    context_object_name = 'legal_case'
    
    def get_queryset(self):
        return models.LegalCase.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Legal Case Details - {self.object.case_number}'
        context['active_page'] = 'legal-cases'
        return context

class LegalCaseUpdateView(UpdateView):
    """Update an existing legal case"""
    model = models.LegalCase
    form_class = forms.LegalCaseForm
    template_name = 'remedial/legalcase_form.html'
    success_url = reverse_lazy('remedial:legalcase-list')
    
    def get_queryset(self):
        return models.LegalCase.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Legal Case - {self.object.case_number}'
        context['active_page'] = 'legal-cases'
        return context

class LegalCaseListView(ListView):
    """List all legal cases"""
    model = models.LegalCase
    template_name = 'remedial/legal_list.html'
    context_object_name = 'legal_cases'
    paginate_by = 20
    
    def get_queryset(self):
        return models.LegalCase.objects.filter(tenant=self.request.tenant).select_related('remedial_account').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Legal Cases'
        context['active_page'] = 'legal-cases'
        return context

class LegalCaseCreateView(CreateView):
    """Create a new legal case"""
    model = models.LegalCase
    form_class = forms.LegalCaseForm
    template_name = 'remedial/legalcase_form.html'
    success_url = reverse_lazy('remedial:legalcase-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Legal Case'
        context['active_page'] = 'legal-cases'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
from django.db.models import Count

class AccountListView(ListView):
    """List all remedial accounts"""
    model = models.RemedialAccount
    template_name = 'remedial/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = models.RemedialAccount.objects.filter(tenant=self.request.tenant).select_related('assigned_officer').order_by('-created_at')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(Q(loan_account_no__icontains=query) | Q(borrower_name__icontains=query))
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Remedial Accounts'
        context['active_page'] = 'accounts'
        return context

class AccountCreateView(CreateView):
    """Create a new remedial account"""
    model = models.RemedialAccount
    form_class = RemedialAccountForm
    template_name = 'remedial/account_form.html'
    success_url = reverse_lazy('remedial:remedialaccount-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Remedial Account'
        context['active_page'] = 'accounts'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class MyCasesListView(ListView):
    """List of remedial accounts assigned to the current user."""
    model = models.RemedialAccount
    template_name = 'remedial/account_list.html'
    context_object_name = 'accounts'
    paginate_by = 20

    def get_queryset(self):
        return models.RemedialAccount.objects.filter(
            tenant=self.request.tenant,
            assigned_officer=self.request.user
        ).select_related('assigned_officer').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'My Assigned Cases'
        context['active_page'] = 'my-cases'
        return context

class AccountUpdateView(UpdateView):
    """Update an existing remedial account"""
    model = models.RemedialAccount
    form_class = RemedialAccountForm
    template_name = 'remedial/account_form.html'
    success_url = reverse_lazy('remedial:remedialaccount-list')
    
    def get_queryset(self):
        return models.RemedialAccount.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Remedial Account - {self.object.loan_account_no}'
        context['active_page'] = 'accounts'
        return context

class AccountDetailView(DetailView):
    """View account details"""
    model = models.RemedialAccount
    template_name = 'remedial/account_detail.html'
    context_object_name = 'account'
    
    def get_queryset(self):
        return models.RemedialAccount.objects.filter(tenant=self.request.tenant).prefetch_related(
            'compromise_agreements',
            'legal_cases',
            'recovery_actions'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        account = self.get_object()
        context['compromises'] = account.compromise_agreements.all()
        context['legal_cases'] = account.legal_cases.all()
        context['recovery_actions'] = account.recovery_actions.all()
        context['title'] = f'Account Details - {self.object.loan_account_no}'
        context['active_page'] = 'accounts'
        return context

def test_compromises_view(request):
    """Test compromises view for navigation"""
    if not request.user.is_authenticated:
        return redirect('remedial:login')
    
    return render(request, 'remedial/simple_list.html', {
        'title': 'Compromise Agreements',
        'message': 'Compromises section - This will show compromise agreements when they are created.'
    })

def test_legal_view(request):
    """Test legal view for navigation"""
    if not request.user.is_authenticated:
        return redirect('remedial:login')
    
    return render(request, 'remedial/simple_list.html', {
        'title': 'Legal Cases',
        'message': 'Legal section - This will show legal cases and court hearings when they are created.'
    })

def test_recovery_view(request):
    """Test recovery view for navigation"""
    if not request.user.is_authenticated:
        return redirect('remedial:login')
    
    return render(request, 'remedial/simple_list.html', {
        'title': 'Recovery Actions',
        'message': 'Recovery section - This will show recovery actions and milestones when they are created.'
    })

def test_writeoffs_view(request):
    """Test write-offs view for navigation"""
    if not request.user.is_authenticated:
        return redirect('remedial:login')
    
    return render(request, 'remedial/simple_list.html', {
        'title': 'Write-off Requests',
        'message': 'Write-offs section - This will show write-off requests when they are created.'
    })

# Compromise detail and update views
class CompromiseDetailView(DetailView):
    """View compromise agreement details"""
    model = models.CompromiseAgreement
    template_name = 'remedial/compromise_detail.html'
    context_object_name = 'compromise'
    
    def get_queryset(self):
        return models.CompromiseAgreement.objects.filter(tenant=self.request.tenant).prefetch_related(
            'schedule_items__payments'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Compromise Details - {self.object.agreement_no}'
        context['active_page'] = 'compromises'
        return context

class CompromiseUpdateView(UpdateView):
    """Update an existing compromise agreement"""
    model = models.CompromiseAgreement
    form_class = CompromiseAgreementForm
    template_name = 'remedial/compromise_form.html'
    success_url = reverse_lazy('remedial:compromiseagreement-list')
    
    def get_queryset(self):
        return models.CompromiseAgreement.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Compromise Agreement - {self.object.agreement_no}'
        context['active_page'] = 'compromises'
        return context

def custom_login_view(request):
    """Custom login view to bypass registration template issue"""
    if request.method == 'POST':
        # Bypass CSRF for testing
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        from django.contrib.auth import authenticate
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('remedial:dashboard')
    
    return render(request, 'custom_login.html', {'form': None})

def custom_logout_view(request):
    """Custom logout view"""
    logout(request)
    return redirect('remedial:login')

from . import selectors

@method_decorator(login_required, name='dispatch')
class DashboardView(TemplateView):
    """Dashboard view with overview of all items"""
    template_name = 'remedial/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        overview_data = selectors.get_dashboard_overview_data(self.request.tenant)
        
        context.update({
            'title': 'Dashboard',
            'active_page': 'dashboard',
            'overview_data': overview_data,
        })
        return context

# ===== COURT HEARING VIEWS =====

class CourtHearingListView(ListView):
    """List all court hearings"""
    model = models.CourtHearing
    template_name = 'remedial/courthearing_list.html'
    context_object_name = 'hearings'
    paginate_by = 20
    
    def get_queryset(self):
        return models.CourtHearing.objects.filter(tenant=self.request.tenant).select_related('legal_case__remedial_account').order_by('-hearing_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Court Hearings'
        context['active_page'] = 'hearings'
        return context

class CourtHearingCreateView(CreateView):
    """Create a new court hearing"""
    model = models.CourtHearing
    form_class = forms.CourtHearingForm
    template_name = 'remedial/court_hearing_form.html'
    success_url = reverse_lazy('remedial:courthearing-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Court Hearing'
        context['active_page'] = 'hearings'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class CourtHearingDetailView(DetailView):
    """View court hearing details"""
    model = models.CourtHearing
    template_name = 'remedial/court_hearing_detail.html'
    context_object_name = 'hearing'
    
    def get_queryset(self):
        return models.CourtHearing.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Court Hearing Details - {self.object.hearing_date}'
        context['active_page'] = 'hearings'
        return context

class CourtHearingUpdateView(UpdateView):
    """Update an existing court hearing"""
    model = models.CourtHearing
    form_class = forms.CourtHearingForm
    template_name = 'remedial/court_hearing_form.html'
    success_url = reverse_lazy('remedial:courthearing-list')
    
    def get_queryset(self):
        return models.CourtHearing.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Court Hearing - {self.object.hearing_date}'
        context['active_page'] = 'hearings'
        return context

# ===== RECOVERY ACTION VIEWS =====

class RecoveryActionListView(ListView):
    """List all recovery actions"""
    model = models.RecoveryAction
    template_name = 'remedial/recoveryaction_list.html'
    context_object_name = 'actions'
    paginate_by = 20
    
    def get_queryset(self):
        return models.RecoveryAction.objects.filter(tenant=self.request.tenant).select_related('remedial_account').order_by('-initiated_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Recovery Actions'
        context['active_page'] = 'recovery-actions'
        return context

class RecoveryActionCreateView(CreateView):
    """Create a new recovery action"""
    model = models.RecoveryAction
    form_class = forms.RecoveryActionForm
    template_name = 'remedial/recoveryaction_form.html'
    success_url = reverse_lazy('remedial:recoveryaction-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Recovery Action'
        context['active_page'] = 'recovery-actions'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class RecoveryActionDetailView(DetailView):
    """View recovery action details"""
    model = models.RecoveryAction
    template_name = 'remedial/recoveryaction_detail.html'
    context_object_name = 'action'
    
    def get_queryset(self):
        return models.RecoveryAction.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Recovery Action Details - {self.object.action_type}'
        context['active_page'] = 'recovery-actions'
        return context

class RecoveryActionUpdateView(UpdateView):
    """Update an existing recovery action"""
    model = models.RecoveryAction
    form_class = forms.RecoveryActionForm
    template_name = 'remedial/recoveryaction_form.html'
    success_url = reverse_lazy('remedial:recoveryaction-list')
    
    def get_queryset(self):
        return models.RecoveryAction.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Recovery Action - {self.object.action_type}'
        context['active_page'] = 'recovery-actions'
        return context

# ===== RECOVERY MILESTONE VIEWS =====

class RecoveryMilestoneListView(ListView):
    """List all recovery milestones"""
    model = models.RecoveryMilestone
    template_name = 'remedial/recoverymilestone_list.html'
    context_object_name = 'milestones'
    paginate_by = 20
    
    def get_queryset(self):
        return models.RecoveryMilestone.objects.filter(tenant=self.request.tenant).select_related('recovery_action__remedial_account').order_by('-target_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Recovery Milestones'
        context['active_page'] = 'milestones'
        return context

class RecoveryMilestoneCreateView(CreateView):
    """Create a new recovery milestone"""
    model = models.RecoveryMilestone
    form_class = forms.RecoveryMilestoneForm
    template_name = 'remedial/recoverymilestone_form.html'
    success_url = reverse_lazy('remedial:recoverymilestone-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Recovery Milestone'
        context['active_page'] = 'milestones'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class RecoveryMilestoneDetailView(DetailView):
    """View recovery milestone details"""
    model = models.RecoveryMilestone
    template_name = 'remedial/recoverymilestone_detail.html'
    context_object_name = 'milestone'
    
    def get_queryset(self):
        return models.RecoveryMilestone.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Recovery Milestone Details - {self.object.milestone_type}'
        context['active_page'] = 'milestones'
        return context

class RecoveryMilestoneUpdateView(UpdateView):
    """Update an existing recovery milestone"""
    model = models.RecoveryMilestone
    form_class = forms.RecoveryMilestoneForm
    template_name = 'remedial/recoverymilestone_form.html'
    success_url = reverse_lazy('remedial:recoverymilestone-list')
    
    def get_queryset(self):
        return models.RecoveryMilestone.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Recovery Milestone - {self.object.milestone_type}'
        context['active_page'] = 'milestones'
        return context



# ===== WRITE-OFF REQUEST VIEWS =====



class WriteOffRequestListView(ListView):

    """List all write-off requests"""

    model = models.WriteOffRequest

    template_name = 'remedial/writeoffrequest_list.html'

    context_object_name = 'writeoffs'

    paginate_by = 20

    

    def get_queryset(self):

        return models.WriteOffRequest.objects.filter(tenant=self.request.tenant).select_related('remedial_account').order_by('-board_decision_date')

    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['title'] = 'Write-off Requests'

        context['active_page'] = 'write-offs'

        return context



class WriteOffRequestCreateView(CreateView):

    """Create a new write-off request"""

    model = models.WriteOffRequest

    form_class = forms.WriteOffRequestForm

    template_name = 'remedial/writeoffrequest_form.html'

    success_url = reverse_lazy('remedial:writeoffrequest-list')

    

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['title'] = 'Create Write-off Request'

        context['active_page'] = 'write-offs'

        return context

    

    def form_valid(self, form):

        form.instance.created_by = self.request.user

        return super().form_valid(form)



class WriteOffRequestDetailView(DetailView):

    """View write-off request details"""

    model = models.WriteOffRequest

    template_name = 'remedial/writeoffrequest_detail.html'

    context_object_name = 'writeoff'

    

    def get_queryset(self):

        return models.WriteOffRequest.objects.filter(tenant=self.request.tenant)



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['title'] = f'Write-off Request Details - {self.object.board_resolution_ref}'

        context['active_page'] = 'write-offs'

        return context



class WriteOffRequestUpdateView(UpdateView):

    """Update an existing write-off request"""

    model = models.WriteOffRequest

    form_class = forms.WriteOffRequestForm

    template_name = 'remedial/writeoffrequest_form.html'

    success_url = reverse_lazy('remedial:writeoffrequest-list')

    

    def get_queryset(self):

        return models.WriteOffRequest.objects.filter(tenant=self.request.tenant)



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['title'] = f'Update Write-off Request - {self.object.board_resolution_ref}'

        context['active_page'] = 'write-offs'

        return context



# ===== DOCUMENT VIEWS =====



class RemedialDocumentListView(ListView):

    """List all documents"""

    model = models.RemedialDocument

    template_name = 'remedial/remedialdocument_list.html'

    context_object_name = 'documents'

    paginate_by = 20

    

    def get_queryset(self):

        return models.RemedialDocument.objects.filter(tenant=self.request.tenant, is_deleted=False).order_by('-uploaded_at')



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['title'] = 'All Documents'

        context['active_page'] = 'documents'

        return context



class RemedialDocumentCreateView(CreateView):

    """Upload a new document"""

    model = models.RemedialDocument

    form_class = forms.RemedialDocumentForm

    template_name = 'remedial/remedialdocument_form.html'

    success_url = reverse_lazy('remedial:remedialdocument-list')



    def get_form_kwargs(self):

        kwargs = super().get_form_kwargs()

        kwargs.update({

            'entity_type': self.request.GET.get('entity_type'),

        })

        return kwargs



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['title'] = 'Upload Document'

        context['active_page'] = 'documents'

        return context



    def form_valid(self, form):

        form.instance.tenant = self.request.tenant

        form.instance.uploaded_by = self.request.user

        return super().form_valid(form)



class RemedialDocumentUpdateView(UpdateView):

    """Update a document's details"""

    model = models.RemedialDocument

    form_class = forms.RemedialDocumentForm

    template_name = 'remedial/remedialdocument_form.html'

    success_url = reverse_lazy('remedial:remedialdocument-list')



    def get_queryset(self):

        return models.RemedialDocument.objects.filter(tenant=self.request.tenant, is_deleted=False)



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context['title'] = f'Update Document - {self.object.doc_type}'

        context['active_page'] = 'documents'

        return context



class RemedialDocumentDeleteView(DeleteView):



    """Mark a document as deleted"""



    model = models.RemedialDocument



    template_name = 'remedial/remedialdocument_confirm_delete.html'



    success_url = reverse_lazy('remedial:remedialdocument-list')







    def get_queryset(self):



        return models.RemedialDocument.objects.filter(tenant=self.request.tenant)







    def form_valid(self, form):



        self.object.is_deleted = True



        self.object.deleted_at = timezone.now()



        self.object.deleted_by = self.request.user



        self.object.save()



        return redirect(self.get_success_url())







# ===== NOTIFICATION VIEWS =====







class NotificationRuleListView(ListView):



    """List all notification rules"""



    model = models.NotificationRule



    template_name = 'remedial/notificationrule_list.html'



    context_object_name = 'rules'



    paginate_by = 20







    def get_queryset(self):



        return models.NotificationRule.objects.filter(tenant=self.request.tenant).order_by('rule_code')







    def get_context_data(self, **kwargs):



        context = super().get_context_data(**kwargs)



        context['title'] = 'Notification Rules'



        context['active_page'] = 'notification-rules'



        return context







class NotificationRuleCreateView(CreateView):



    """Create a new notification rule"""



    model = models.NotificationRule



    form_class = forms.NotificationRuleForm



    template_name = 'remedial/notificationrule_form.html'



    success_url = reverse_lazy('remedial:notificationrule-list')







    def get_context_data(self, **kwargs):



        context = super().get_context_data(**kwargs)



        context['title'] = 'Create Notification Rule'



        context['active_page'] = 'notification-rules'



        return context







    def form_valid(self, form):



        form.instance.tenant = self.request.tenant



        return super().form_valid(form)







class NotificationRuleUpdateView(UpdateView):



    """Update a notification rule"""



    model = models.NotificationRule



    form_class = forms.NotificationRuleForm



    template_name = 'remedial/notificationrule_form.html'



    success_url = reverse_lazy('remedial:notificationrule-list')







    def get_queryset(self):



        return models.NotificationRule.objects.filter(tenant=self.request.tenant)







    def get_context_data(self, **kwargs):



        context = super().get_context_data(**kwargs)



        context['title'] = f'Update Rule - {self.object.rule_code}'



        context['active_page'] = 'notification-rules'



        return context







class NotificationRuleDetailView(DetailView):


    """View notification rule details"""


    model = models.NotificationRule


    template_name = 'remedial/notificationrule_detail.html'


    context_object_name = 'rule'




    def get_queryset(self):


        return models.NotificationRule.objects.filter(tenant=self.request.tenant)




    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = f'Rule Details - {self.object.rule_code}'


        context['active_page'] = 'notification-rules'


        return context


# ===== COMPROMISE PAYMENT VIEWS =====


class CompromisePaymentListView(ListView):


    """List all compromise payments"""


    model = models.CompromisePayment


    template_name = 'remedial/compromisepayment_list.html'


    context_object_name = 'payments'


    paginate_by = 20


    


    def get_queryset(self):


        return models.CompromisePayment.objects.filter(tenant=self.request.tenant).select_related('compromise_agreement', 'schedule_item', 'received_by').order_by('-payment_date')


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = 'Compromise Payments'


        context['active_page'] = 'payments'


        return context




    


class CompromisePaymentCreateView(CreateView):


    """Create a new compromise payment"""


    model = models.CompromisePayment


    form_class = forms.CompromisePaymentForm


    template_name = 'remedial/compromisepayment_form.html'


    success_url = reverse_lazy('remedial:compromisepayment-list')


    def get_compromise_agreement(self):

        if not hasattr(self, '_compromise_agreement'):

            compromise_id = self.request.GET.get('compromise_id')

            if compromise_id:

                self._compromise_agreement = models.CompromiseAgreement.objects.filter(

                    id=compromise_id,

                    tenant=self.request.tenant,

                ).first()

            else:

                self._compromise_agreement = None

        return self._compromise_agreement


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = 'Record Compromise Payment'


        context['active_page'] = 'payments'


        return context


    


    def get_form_kwargs(self):


        kwargs = super().get_form_kwargs()


        kwargs['compromise_agreement'] = self.get_compromise_agreement()


        return kwargs


    


    def form_valid(self, form):


        compromise = self.get_compromise_agreement()


        if not compromise:


            form.add_error(None, 'Compromise agreement is required to record this payment.')


            return self.form_invalid(form)


        payment = form.save(commit=False)


        payment.compromise_agreement = compromise


        payment.tenant = self.request.tenant


        payment.received_by = self.request.user


        payment.save()


        

        # Update schedule item status if payment is assigned to one


        if payment.schedule_item:


            remaining_amount = payment.schedule_item.amount_due - payment.schedule_item.amount_paid


            if remaining_amount <= 0:


                payment.schedule_item.status = models.ScheduleStatus.PAID


            elif payment.schedule_item.amount_paid > 0:


                payment.schedule_item.status = models.ScheduleStatus.PARTIAL


            payment.schedule_item.save()


        

        return super().form_valid(form)


    


class CompromisePaymentDetailView(DetailView):


    """View compromise payment details"""


    model = models.CompromisePayment


    template_name = 'remedial/compromisepayment_detail.html'


    context_object_name = 'payment'


    


    def get_queryset(self):


        return models.CompromisePayment.objects.filter(tenant=self.request.tenant).select_related(


            'compromise_agreement', 'schedule_item', 'received_by'


        )


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = f'Payment Details - {self.object.reference_no or f"Payment {self.object.pk}"}'


        context['active_page'] = 'payments'


        return context


    


class CompromisePaymentUpdateView(UpdateView):


    """Update an existing compromise payment"""


    model = models.CompromisePayment


    form_class = forms.CompromisePaymentForm


    template_name = 'remedial/compromisepayment_form.html'


    success_url = reverse_lazy('remedial:compromisepayment-list')


    


    def get_queryset(self):


        return models.CompromisePayment.objects.filter(tenant=self.request.tenant)


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = f'Update Payment - {self.object.reference_no or f"Payment {self.object.pk}"}'


        context['active_page'] = 'payments'


        return context


    


    def form_valid(self, form):


        # Get old payment amount for recalculation


        old_payment = self.get_object()


        old_amount = old_payment.amount


        

        payment = form.save(commit=False)


        payment.tenant = self.request.tenant


        payment.save()


        

        # Recalculate schedule item status


        if payment.schedule_item:


            remaining_amount = payment.schedule_item.amount_due - payment.schedule_item.amount_paid


            if remaining_amount <= 0:


                payment.schedule_item.status = models.ScheduleStatus.PAID


            elif payment.schedule_item.amount_paid > 0:


                payment.schedule_item.status = models.ScheduleStatus.PARTIAL


            else:


                payment.schedule_item.status = models.ScheduleStatus.DUE


            payment.schedule_item.save()


        

        return super().form_valid(form)


# ===== COMPROMISE SCHEDULE ITEM VIEWS =====


class CompromiseScheduleItemListView(ListView):


    """List all compromise schedule items"""


    model = models.CompromiseScheduleItem


    template_name = 'remedial/scheduleitem_list.html'


    context_object_name = 'schedule_items'


    paginate_by = 20


    


    def get_compromise_agreement(self):


        if not hasattr(self, '_compromise_agreement'):


            compromise_id = self.request.GET.get('compromise_id')


            if not compromise_id:


                raise Http404('Compromise agreement is required to view schedule items.')


            self._compromise_agreement = get_object_or_404(


                models.CompromiseAgreement.objects.select_related('remedial_account'),


                pk=compromise_id,


                tenant=self.request.tenant,


            )


        return self._compromise_agreement


    


    def get_queryset(self):


        compromise = self.get_compromise_agreement()


        return models.CompromiseScheduleItem.objects.filter(


            tenant=self.request.tenant,


            compromise_agreement=compromise,


        ).select_related(


            'compromise_agreement__remedial_account'


        ).order_by('seq_no')


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        compromise = self.get_compromise_agreement()


        context['title'] = f'Schedule Items - {compromise.agreement_no}'


        context['compromise'] = compromise


        context['account'] = compromise.remedial_account


        context['active_page'] = 'schedule-items'


        return context


    


class CompromiseScheduleItemCreateView(CreateView):


    """Create a new compromise schedule item"""


    model = models.CompromiseScheduleItem


    form_class = forms.CompromiseScheduleItemForm


    template_name = 'remedial/scheduleitem_form.html'


    success_url = reverse_lazy('remedial:scheduleitem-list')


    

    
    def get_compromise_agreement(self):


        if not hasattr(self, '_compromise_agreement'):


            compromise_id = self.request.GET.get('compromise_id')


            if compromise_id:


                self._compromise_agreement = models.CompromiseAgreement.objects.filter(


                    id=compromise_id,


                    tenant=self.request.tenant,


                ).first()


            else:


                self._compromise_agreement = None


        return self._compromise_agreement


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        compromise = self.get_compromise_agreement()


        if compromise:


            context['title'] = f'Create Schedule Item - {compromise.agreement_no}'


            context['compromise'] = compromise


        else:


            context['title'] = 'Create Schedule Item'


        context['active_page'] = 'schedule-items'


        return context


    

    
    def get_form_kwargs(self):


        kwargs = super().get_form_kwargs()


        kwargs['compromise_agreement'] = self.get_compromise_agreement()


        return kwargs


    

    
    def form_valid(self, form):


        compromise = self.get_compromise_agreement()


        if not compromise:


            form.add_error(None, 'Compromise agreement is required to add a schedule item.')


            return self.form_invalid(form)


        schedule_item = form.save(commit=False)


        schedule_item.compromise_agreement = compromise


        schedule_item.tenant = self.request.tenant


        schedule_item.save()


        

        return super().form_valid(form)


    def get_success_url(self):


        base_url = reverse('remedial:scheduleitem-list')


        compromise = self.get_compromise_agreement()


        if compromise:


            return f"{base_url}?compromise_id={compromise.pk}"


        return base_url


    


class CompromiseScheduleItemDetailView(DetailView):


    """View compromise schedule item details"""


    model = models.CompromiseScheduleItem


    template_name = 'remedial/scheduleitem_detail.html'


    context_object_name = 'schedule_item'


    


    def get_queryset(self):


        return models.CompromiseScheduleItem.objects.filter(tenant=self.request.tenant).select_related(


            'compromise_agreement__remedial_account',


        ).prefetch_related('payments')


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = f'Schedule Details - {self.object.compromise_agreement.agreement_no} #{self.object.seq_no}'


        context['active_page'] = 'schedule-items'


        return context


    


class CompromiseScheduleItemUpdateView(UpdateView):


    """Update an existing compromise schedule item"""


    model = models.CompromiseScheduleItem


    form_class = forms.CompromiseScheduleItemForm


    template_name = 'remedial/scheduleitem_form.html'


    success_url = reverse_lazy('remedial:scheduleitem-list')


    


    def get_queryset(self):


        return models.CompromiseScheduleItem.objects.filter(tenant=self.request.tenant)


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = f'Update Schedule Item - {self.object.compromise_agreement.agreement_no} #{self.object.seq_no}'


        context['active_page'] = 'schedule-items'


        return context


    def get_success_url(self):


        base_url = reverse('remedial:scheduleitem-list')


        return f"{base_url}?compromise_id={self.object.compromise_agreement.pk}"


# ===== COMPROMISE APPROVAL WORKFLOW VIEWS =====


class CompromiseApproveView(UpdateView):


    """Approve a compromise agreement (maker-checker pattern)"""


    model = models.CompromiseAgreement


    form_class = forms.CompromiseAgreementForm


    template_name = 'remedial/compromise_approve.html'


    success_url = reverse_lazy('remedial:compromiseagreement-list')


    


    def get_queryset(self):


        return models.CompromiseAgreement.objects.filter(tenant=self.request.tenant, status=models.CompromiseStatus.DRAFT)


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = f'Approve Compromise - {self.object.agreement_no}'


        context['active_page'] = 'compromises'


        context['is_approval'] = True


        return context


    


    def form_valid(self, form):


        compromise = form.save(commit=False)


        # Change status to APPROVED


        compromise.status = models.CompromiseStatus.APPROVED


        compromise.approved_by = self.request.user


        compromise.approved_at = timezone.now()


        compromise.save()


        

        # Log the approval action


        models.AuditLog.objects.create(


            tenant=self.request.tenant,


            actor=self.request.user,


            entity_type='compromise_agreement',


            entity_id=str(compromise.id),


            action='STATE_CHANGE',


            before_json={'status': 'DRAFT'},


            after_json={'status': 'APPROVED', 'approved_by': str(self.request.user), 'approved_at': compromise.approved_at.isoformat()},


            notes=f'Compromise approved by {self.request.get_full_name() or self.request.username}'


        )


        

        return super().form_valid(form)


    


class CompromiseActivateView(UpdateView):


    """Activate a compromise agreement (maker-checker pattern)"""


    model = models.CompromiseAgreement


    form_class = forms.CompromiseAgreementForm


    template_name = 'remedial/compromise_approve.html'


    success_url = reverse_lazy('remedial:compromiseagreement-list')


    


    def get_queryset(self):


        return models.CompromiseAgreement.objects.filter(tenant=self.request.tenant, status=models.CompromiseStatus.APPROVED)


    


    def get_context_data(self, **kwargs):


        context = super().get_context_data(**kwargs)


        context['title'] = f'Activate Compromise - {self.object.agreement_no}'


        context['active_page'] = 'compromises'


        context['is_approval'] = True


        context['action'] = 'Activate'


        return context


    


    def form_valid(self, form):


        compromise = form.save(commit=False)


        # Change status to ACTIVE


        compromise.status = models.CompromiseStatus.ACTIVE


        compromise.is_active = True


        # Set start date if not set


        if not compromise.start_date:


            compromise.start_date = timezone.now().date()


        compromise.save()


        

        # Log the activation action


        models.AuditLog.objects.create(


            tenant=self.request.tenant,


            actor=self.request.user,


            entity_type='compromise_agreement',


            entity_id=str(compromise.id),


            action='STATE_CHANGE',


            before_json={'status': 'APPROVED'},


            after_json={'status': 'ACTIVE', 'start_date': compromise.start_date.isoformat()},


            notes=f'Compromise activated by {self.request.get_full_name() or self.request.username}'


        )


        

        return super().form_valid(form)


    


def compromise_approve_action(request, pk):


    """Ajax endpoint to approve a compromise agreement"""


    if request.method == 'POST':


        try:


            compromise = models.CompromiseAgreement.objects.get(id=pk, tenant=request.tenant, status=models.CompromiseStatus.DRAFT)


            compromise.status = models.CompromiseStatus.APPROVED


            compromise.approved_by = request.user


            compromise.approved_at = timezone.now()


            compromise.save()


            

            # Log the approval action


            models.AuditLog.objects.create(


                tenant=request.tenant,


                actor=request.user,


                entity_type='compromise_agreement',


                entity_id=str(compromise.id),


                action='STATE_CHANGE',


                before_json={'status': 'DRAFT'},


                after_json={'status': 'APPROVED', 'approved_by': str(request.user), 'approved_at': compromise.approved_at.isoformat()},


                notes=f'Compromise approved by {request.get_full_name() or request.username}'


            )


            

            return render(request, 'remedial/ajax_response.html', {


                'success': True,


                'message': f'Compromise {compromise.agreement_no} has been approved.'


            })


        except models.CompromiseAgreement.DoesNotExist:


            return render(request, 'remedial/ajax_response.html', {


                'success': False,


                'message': 'Compromise not found or not in draft status.'


            })


    


    return render(request, 'remedial/ajax_response.html', {


        'success': False,


        'message': 'Invalid request method.'


    })


    


def compromise_activate_action(request, pk):


    """Ajax endpoint to activate a compromise agreement"""


    if request.method == 'POST':


        try:


            compromise = models.CompromiseAgreement.objects.get(id=pk, tenant=request.tenant, status=models.CompromiseStatus.APPROVED)


            compromise.status = models.CompromiseStatus.ACTIVE


            compromise.is_active = True


            if not compromise.start_date:


                compromise.start_date = timezone.now().date()


            compromise.save()


            

            # Log the activation action


            models.AuditLog.objects.create(


                tenant=request.tenant,


                actor=request.user,


                entity_type='compromise_agreement',


                entity_id=str(compromise.id),


                action='STATE_CHANGE',


                before_json={'status': 'APPROVED'},


                after_json={'status': 'ACTIVE', 'start_date': compromise.start_date.isoformat()},


                notes=f'Compromise activated by {request.get_full_name() or request.username}'


            )


            

            return render(request, 'remedial/ajax_response.html', {


                'success': True,


                'message': f'Compromise {compromise.agreement_no} has been activated.'


            })


        except models.CompromiseAgreement.DoesNotExist:


            return render(request, 'remedial/ajax_response.html', {


                'success': False,


                'message': 'Compromise not found or not in approved status.'


            })


    


    return render(request, 'remedial/ajax_response.html', {


        'success': False,


        'message': 'Invalid request method.'


    })



        



def bootstrap_test_view(request):



    """Test Bootstrap loading"""



    return render(request, 'bootstrap_test.html')
