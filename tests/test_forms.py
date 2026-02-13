from apps.remedial.forms import CompromiseAgreementForm, CompromisePaymentForm

from .base import BaseRemedialTestCase


class CompromiseFormsTest(BaseRemedialTestCase):
    def _agreement_data(self, **overrides):
        base = {
            "agreement_no": "100",
            "remedial_account": self.remedial_account.pk,
            "settlement_amount": "1200.00",
            "terms": 'Initial payment plan notes',
            "grace_days": "3",
            "default_threshold_days": "30",
        }
        base.update(overrides)
        return base

    def test_agreement_form_auto_prefixes_agreement_no(self):
        form = CompromiseAgreementForm(data=self._agreement_data())
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["agreement_no"], "AGREEMENT-100")

    def test_agreement_form_requires_positive_settlement(self):
        form = CompromiseAgreementForm(data=self._agreement_data(settlement_amount="-50"))
        self.assertFalse(form.is_valid())
        self.assertIn("settlement_amount", form.errors)

    def test_agreement_form_strips_terms(self):
        form = CompromiseAgreementForm(data=self._agreement_data(terms="  final notes  "))
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["terms"], "final notes")

    def test_payment_form_amount_must_be_positive(self):
        form = CompromisePaymentForm(
            data={
                "schedule_item": self.schedule_item_due.pk,
                "amount": "-10.00",
                "reference_no": "REF-123",
            },
            compromise_agreement=self.compromise,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("amount", form.errors)

    def test_payment_form_filters_paid_schedule_items(self):
        form = CompromisePaymentForm(compromise_agreement=self.compromise)
        queryset = form.fields["schedule_item"].queryset
        self.assertIn(self.schedule_item_due, queryset)
        self.assertNotIn(self.schedule_item_paid, queryset)
