from django.urls import path

from . import views

app_name = "remedial"

urlpatterns = [
    path("", views.custom_login_view, name="login"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("logout/", views.custom_logout_view, name="logout"),
    
    # Account URLs
    path("accounts/", views.AccountListView.as_view(), name="remedialaccount-list"),
    path("accounts/create/", views.AccountCreateView.as_view(), name="account-create"),
    path("accounts/<uuid:pk>/", views.AccountDetailView.as_view(), name="account-detail"),
    path("accounts/<uuid:pk>/edit/", views.AccountUpdateView.as_view(), name="account-update"),
    # Compromise URLs
    path("compromises/", views.CompromiseListView.as_view(), name="compromiseagreement-list"),
    path("compromises/create/", views.CompromiseCreateView.as_view(), name="compromise-create"),
    path("compromises/<int:pk>/", views.CompromiseDetailView.as_view(), name="compromise-detail"),
    path("compromises/<int:pk>/edit/", views.CompromiseUpdateView.as_view(), name="compromise-update"),
    # Legal URLs
    path("legal-cases/", views.LegalCaseListView.as_view(), name="legalcase-list"),
    path("legal-cases/create/", views.LegalCaseCreateView.as_view(), name="legalcase-create"),
    path("legal-cases/<int:pk>/", views.LegalCaseDetailView.as_view(), name="legalcase-detail"),
    path("legal-cases/<int:pk>/edit/", views.LegalCaseUpdateView.as_view(), name="legalcase-update"),
    # Court Hearing URLs
    path("hearings/", views.CourtHearingListView.as_view(), name="courthearing-list"),
    path("hearings/create/", views.CourtHearingCreateView.as_view(), name="courthearing-create"),
    path("hearings/<int:pk>/", views.CourtHearingDetailView.as_view(), name="courthearing-detail"),
    path("hearings/<int:pk>/edit/", views.CourtHearingUpdateView.as_view(), name="courthearing-update"),
    # Recovery Action URLs
    path("recovery-actions/", views.RecoveryActionListView.as_view(), name="recoveryaction-list"),
    path("recovery-actions/create/", views.RecoveryActionCreateView.as_view(), name="recoveryaction-create"),
    path("recovery-actions/<int:pk>/", views.RecoveryActionDetailView.as_view(), name="recoveryaction-detail"),
    path("recovery-actions/<int:pk>/edit/", views.RecoveryActionUpdateView.as_view(), name="recoveryaction-update"),
    # Recovery Milestone URLs
    path("milestones/", views.RecoveryMilestoneListView.as_view(), name="recoverymilestone-list"),
    path("milestones/create/", views.RecoveryMilestoneCreateView.as_view(), name="recoverymilestone-create"),
    path("milestones/<int:pk>/", views.RecoveryMilestoneDetailView.as_view(), name="recoverymilestone-detail"),
    path("milestones/<int:pk>/edit/", views.RecoveryMilestoneUpdateView.as_view(), name="recoverymilestone-update"),
    # Write-off Request URLs
    path("write-offs/", views.WriteOffRequestListView.as_view(), name="writeoffrequest-list"),
    path("write-offs/create/", views.WriteOffRequestCreateView.as_view(), name="writeoffrequest-create"),
    path("write-offs/<int:pk>/", views.WriteOffRequestDetailView.as_view(), name="writeoffrequest-detail"),
    path("write-offs/<int:pk>/edit/", views.WriteOffRequestUpdateView.as_view(), name="writeoffrequest-update"),
    # Test route
    path("bootstrap-test/", views.bootstrap_test_view, name="bootstrap-test"),
]
