from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = "tenancy"

urlpatterns = [
    # Tenant URLs
    path("tenants/", views.TenantListView.as_view(), name="tenant-list"),
    path("tenants/create/", views.TenantCreateView.as_view(), name="tenant-create"),
    path("tenants/<int:pk>/", views.TenantDetailView.as_view(), name="tenant-detail"),
    path("tenants/<int:pk>/edit/", views.TenantUpdateView.as_view(), name="tenant-update"),
    
    # Tenant Domain URLs
    path("domains/", views.TenantDomainListView.as_view(), name="tenantdomain-list"),
    path("domains/create/", views.TenantDomainCreateView.as_view(), name="tenantdomain-create"),
    path("domains/<int:pk>/edit/", views.TenantDomainUpdateView.as_view(), name="tenantdomain-update"),
    path("domains/<int:pk>/delete/", views.TenantDomainDeleteView.as_view(), name="tenantdomain-delete"),
    
    # Tenant Setting URLs
    path("settings/", views.TenantSettingListView.as_view(), name="tenantsetting-list"),
    path("settings/create/", views.TenantSettingCreateView.as_view(), name="tenantsetting-create"),
    path("settings/<int:pk>/", views.TenantSettingDetailView.as_view(), name="tenantsetting-detail"),
    path("settings/<int:pk>/edit/", views.TenantSettingUpdateView.as_view(), name="tenantsetting-update"),
]