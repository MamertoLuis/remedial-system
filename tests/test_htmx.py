from django.test import RequestFactory

from apps.remedial import models
from apps.remedial.views import compromise_approve_action

from .base import BaseRemedialTestCase


class HTMXCompromiseActionsTest(BaseRemedialTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.compromise.refresh_from_db()
        self.compromise.status = models.CompromiseStatus.DRAFT
        self.compromise.approved_by = None
        self.compromise.approved_at = None
        self.compromise.save()

    def _build_request(self, http_method, tenant, user):
        method = getattr(self.factory, http_method)
        request = method(
            "/remedial/compromises/{}/approve-action/".format(self.compromise.pk)
        )
        request.user = user
        request.tenant = tenant
        request.get_full_name = user.get_full_name
        request.username = user.username
        return request

    def test_compromise_approve_action_returns_success_fragment(self):
        request = self._build_request("post", self.tenant, self.user)
        response = compromise_approve_action(request, pk=self.compromise.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Compromise AG-001 has been approved", response.content)

    def test_compromise_approve_action_rejects_wrong_tenant(self):
        request = self._build_request("post", self.other_tenant, self.other_user)
        response = compromise_approve_action(request, pk=self.compromise.pk)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Compromise not found", response.content)

    def test_compromise_approve_action_get_method_returns_error(self):
        request = self._build_request("get", self.tenant, self.user)
        response = compromise_approve_action(request, pk=self.compromise.pk)
        self.assertIn(b"Invalid request method", response.content)
