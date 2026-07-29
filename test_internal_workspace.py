import unittest
from pathlib import Path


class InternalWorkspaceStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = Path(__file__).with_name('pokale-meier-erfolgsportal.html').read_text(encoding='utf-8')

    def test_has_active_customer_dashboard_and_manual_customer_creation(self):
        self.assertIn('id="active-customer-list"', self.html)
        self.assertIn('id="customer-form"', self.html)
        self.assertIn('JTL-Kundennummer', self.html)
        self.assertIn('Miro-Board-Link', self.html)

    def test_has_customer_detail_tabs_for_addresses_and_agreements(self):
        self.assertIn("button.dataset.customerTab = key", self.html)
        self.assertIn("addTab(tabs, 'addresses', 'Adressen')", self.html)
        self.assertIn("addTab(tabs, 'agreements', 'Vereinbarungen')", self.html)
        self.assertIn('Lieferadresse', self.html)
        self.assertIn('Rechnungsadresse', self.html)
        self.assertIn('Einzelversand', self.html)

    def test_has_local_role_management_for_admin_designer_and_berater(self):
        self.assertIn('id="user-form"', self.html)
        self.assertIn('option value="admin">Admin', self.html)
        self.assertIn('option value="designer">Designer', self.html)
        self.assertIn('option value="berater">Berater', self.html)
        self.assertIn('PortalCore.can(workspace', self.html)


if __name__ == '__main__':
    unittest.main()
