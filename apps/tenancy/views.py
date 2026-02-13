from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from . import models
from . import forms


class TenantListView(ListView):
    model = models.Tenant
    template_name = 'tenancy/tenant_list.html'
    context_object_name = 'tenants'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tenants'
        context['active_page'] = 'tenants'
        return context


class TenantCreateView(CreateView):
    model = models.Tenant
    form_class = forms.TenantForm
    template_name = 'tenancy/tenant_form.html'
    success_url = reverse_lazy('tenancy:tenant-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Tenant'
        context['active_page'] = 'tenants'
        return context


class TenantUpdateView(UpdateView):
    model = models.Tenant
    form_class = forms.TenantForm
    template_name = 'tenancy/tenant_form.html'
    success_url = reverse_lazy('tenancy:tenant-list')

    def get_queryset(self):
        return models.Tenant.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Tenant - {self.object.name}'
        context['active_page'] = 'tenants'
        return context


class TenantDetailView(DetailView):
    model = models.Tenant
    template_name = 'tenancy/tenant_detail.html'
    context_object_name = 'tenant'

    def get_queryset(self):
        return models.Tenant.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Tenant Details - {self.object.name}'
        context['active_page'] = 'tenants'
        # Add related domains and settings to context
        context['domains'] = self.object.domains.all()
        context['settings'] = self.object.settings.all()
        return context


class TenantDomainListView(ListView):
    """List all tenant domains"""
    model = models.TenantDomain
    template_name = 'tenancy/tenantdomain_list.html'
    context_object_name = 'domains'
    paginate_by = 20

    def get_queryset(self):
        return models.TenantDomain.objects.filter(tenant=self.request.tenant).select_related('tenant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tenant Domains'
        context['active_page'] = 'tenant-domains'
        return context


class TenantDomainCreateView(CreateView):
    """Create a new tenant domain"""
    model = models.TenantDomain
    form_class = forms.TenantDomainForm
    template_name = 'tenancy/tenantdomain_form.html'
    success_url = reverse_lazy('tenancy:tenantdomain-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Tenant Domain'
        context['active_page'] = 'tenant-domains'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        return super().form_valid(form)


class TenantDomainUpdateView(UpdateView):
    """Update an existing tenant domain"""
    model = models.TenantDomain
    form_class = forms.TenantDomainForm
    template_name = 'tenancy/tenantdomain_form.html'
    success_url = reverse_lazy('tenancy:tenantdomain-list')

    def get_queryset(self):
        return models.TenantDomain.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Domain - {self.object.domain}'
        context['active_page'] = 'tenant-domains'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs


class TenantDomainDeleteView(DeleteView):
    """Delete a tenant domain"""
    model = models.TenantDomain
    template_name = 'tenancy/tenantdomain_confirm_delete.html'
    success_url = reverse_lazy('tenancy:tenantdomain-list')

    def get_queryset(self):
        return models.TenantDomain.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Delete Domain - {self.object.domain}'
        context['active_page'] = 'tenant-domains'
        return context


class TenantSettingListView(ListView):
    """List all tenant settings"""
    model = models.TenantSetting
    template_name = 'tenancy/tenantsetting_list.html'
    context_object_name = 'settings'
    paginate_by = 20

    def get_queryset(self):
        return models.TenantSetting.objects.filter(tenant=self.request.tenant).select_related('tenant')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Tenant Settings'
        context['active_page'] = 'tenant-settings'
        return context


class TenantSettingCreateView(CreateView):
    """Create a new tenant setting"""
    model = models.TenantSetting
    form_class = forms.TenantSettingForm
    template_name = 'tenancy/tenantsetting_form.html'
    success_url = reverse_lazy('tenancy:tenantsetting-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create Tenant Setting'
        context['active_page'] = 'tenant-settings'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs

    def form_valid(self, form):
        form.instance.tenant = self.request.tenant
        return super().form_valid(form)


class TenantSettingDetailView(DetailView):
    """View tenant setting details"""
    model = models.TenantSetting
    template_name = 'tenancy/tenantsetting_detail.html'
    context_object_name = 'setting'

    def get_queryset(self):
        return models.TenantSetting.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Setting Details - {self.object.key}'
        context['active_page'] = 'tenant-settings'
        return context


class TenantSettingUpdateView(UpdateView):
    """Update an existing tenant setting"""
    model = models.TenantSetting
    form_class = forms.TenantSettingForm
    template_name = 'tenancy/tenantsetting_form.html'
    success_url = reverse_lazy('tenancy:tenantsetting-list')

    def get_queryset(self):
        return models.TenantSetting.objects.filter(tenant=self.request.tenant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Update Setting - {self.object.key}'
        context['active_page'] = 'tenant-settings'
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['tenant'] = self.request.tenant
        return kwargs