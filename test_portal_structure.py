import unittest
from pathlib import Path


class PortalStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parent
        cls.html = (cls.root / 'pokale-meier-erfolgsportal.html').read_text(encoding='utf-8')
        cls.core = (cls.root / 'portal-core.js').read_text(encoding='utf-8')

    def test_keeps_pokale_meier_branding_and_local_preview_asset(self):
        self.assertIn('assets/pokale-meier-logo.svg', self.html)
        self.assertIn('#0B233B', self.html)
        self.assertIn('#F05A28', self.html)
        self.assertIn('© 2026 | Meier Trophy GmbH', self.html)

    def test_dashboard_is_scoped_to_active_customers(self):
        self.assertIn('PortalCore.activeCustomers(workspace)', self.html)
        self.assertIn('id="active-customer-list"', self.html)
        self.assertIn('dashboard-search', self.html)
        self.assertIn('JTL-Kundennummer', self.html)

    def test_customer_workspace_contains_miro_addresses_contact_and_agreement_fields(self):
        for marker in ['Miro-Board öffnen', 'Lieferadresse', 'Rechnungsadresse', 'Ansprechpartner', 'Versandvereinbarung', 'Einzelversand']:
            self.assertIn(marker, self.html)

    def test_local_workspace_has_explicit_backup_and_security_boundary(self):
        self.assertIn('Lokale Sicherung exportieren', self.html)
        self.assertIn("pm-erfolgsportal-workspace-v1", self.html)
        self.assertIn('noch keine sichere Anmeldung', self.html)
        self.assertNotIn('MIRO_ACCESS_TOKEN', self.html)
        self.assertNotIn('client_secret', self.html.lower())

    def test_business_logic_is_separate_from_browser_ui(self):
        self.assertIn('createWorkspace', self.core)
        self.assertIn('createCustomer', self.core)
        self.assertIn('updateCustomer', self.core)
        self.assertIn('customerStatuses', self.core)
        self.assertIn("roles,", self.core)
        self.assertIn("<script src=\"portal-core.js\">", self.html)

    def test_gamification_is_prepared_without_fake_rankings(self):
        for marker in ['Bestenliste', 'Kundenaufträge · Monat', 'Kundenaufträge · Jahr', 'Kundenaufträge · Gesamt', 'Platz 1', 'Freischaltbare Belohnungen']:
            self.assertIn(marker, self.html)
        self.assertIn('leaderboards', self.core)
        self.assertIn('salesAttribution', self.core)
        self.assertIn('Noch keine Datengrundlage', self.html)


if __name__ == '__main__':
    unittest.main()
