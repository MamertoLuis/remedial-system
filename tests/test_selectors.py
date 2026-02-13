from apps.remedial import selectors

from .base import BaseRemedialTestCase


class TenantSelectorTest(BaseRemedialTestCase):
    def test_dashboard_counts_are_tenant_scoped(self):
        overview = selectors.get_dashboard_overview_data(self.tenant)
        self.assertEqual(overview["accounts_count"], 1)
        self.assertEqual(overview["compromises_count"], 1)
        self.assertEqual(overview["legal_cases_count"], 0)
        self.assertEqual(overview["write_offs_count"], 0)

        other_overview = selectors.get_dashboard_overview_data(self.other_tenant)
        self.assertEqual(other_overview["accounts_count"], 1)
        self.assertEqual(other_overview["compromises_count"], 0)
        self.assertEqual(other_overview["legal_cases_count"], 0)
        self.assertEqual(other_overview["write_offs_count"], 0)
