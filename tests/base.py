from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.tenancy.models import Tenant
from apps.remedial import models

User = get_user_model()


class BaseRemedialTestCase(TestCase):
    """Shared test setup for remedial UI tests."""

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Tenant.objects.create(name="Alpha Collections", code="alpha")
        cls.other_tenant = Tenant.objects.create(name="Beta Recoveries", code="beta")
        cls.user = User.objects.create_user(username="remedial_user", password="testpass123")
        cls.other_user = User.objects.create_user(username="other_user", password="testpass123")

        cls.remedial_account = models.RemedialAccount.objects.create(
            tenant=cls.tenant,
            loan_account_no="LN-0001",
            borrower_name="Jane Borrower",
            assigned_officer=cls.user,
        )

        cls.other_account = models.RemedialAccount.objects.create(
            tenant=cls.other_tenant,
            loan_account_no="LN-0002",
            borrower_name="John Other",
        )

        cls.compromise = models.CompromiseAgreement.objects.create(
            tenant=cls.tenant,
            remedial_account=cls.remedial_account,
            agreement_no="AG-001",
            settlement_amount=Decimal("1500.00"),
            created_by=cls.user,
        )

        cls.schedule_item_due = models.CompromiseScheduleItem.objects.create(
            tenant=cls.tenant,
            compromise_agreement=cls.compromise,
            seq_no=1,
            due_date=date.today(),
            amount_due=Decimal("500.00"),
        )

        cls.schedule_item_paid = models.CompromiseScheduleItem.objects.create(
            tenant=cls.tenant,
            compromise_agreement=cls.compromise,
            seq_no=2,
            due_date=date.today(),
            amount_due=Decimal("750.00"),
            status=models.ScheduleStatus.PAID,
        )

        cls.compromise_payment = models.CompromisePayment.objects.create(
            tenant=cls.tenant,
            compromise_agreement=cls.compromise,
            schedule_item=cls.schedule_item_due,
            amount=Decimal("250.00"),
            received_by=cls.user,
        )

    def login(self):
        return self.client.login(username=self.user.username, password="testpass123")
