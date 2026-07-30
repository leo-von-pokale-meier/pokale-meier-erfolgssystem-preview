import unittest
from pathlib import Path


class DemoExperienceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parent
        cls.script = (cls.root / 'portal-demo.js').read_text(encoding='utf-8')
        cls.css = (cls.root / 'demo.css').read_text(encoding='utf-8')
        cls.pages = {
            name: (cls.root / filename).read_text(encoding='utf-8')
            for name, filename in {
                'dashboard': 'kundenansicht.html',
                'journey': 'kunden-etappen.html',
                'awards': 'kunden-awards.html',
                'customers': 'kunden-erfolge.html',
                'league': 'kunden-bestenliste.html',
                'recommendations': 'kunden-empfehlungen.html',
                'profile': 'kunden-profil.html',
                'admin': 'interne-uebersicht.html',
            }.items()
        }

    def test_every_interactive_demo_page_loads_the_shared_demo_application(self):
        for name, page in self.pages.items():
            self.assertIn('portal-demo.js', page, name)
            self.assertIn('data-page=', page, name)

    def test_demo_has_realistic_client_side_workflows_and_clear_data_boundary(self):
        for marker in ['localStorage', 'addSuccessCustomer', 'saveAppointment', 'addRecommendation', 'completeTask', 'createDemoCustomer']:
            self.assertIn(marker, self.script)
        self.assertIn('nur in diesem Browser', self.script)
        self.assertNotIn('fetch(', self.script)
        self.assertNotIn('XMLHttpRequest', self.script)

    def test_customer_portal_covers_dashboard_journey_awards_customers_and_impact_league(self):
        required = {
            'dashboard': ['Fortschritt bis zur nächsten Stufe', 'Erfolgskunden-Agent', 'Letzte Aktivitäten', 'KPI-Übersicht'],
            'journey': ['Gesprächszusammenfassung', 'Offene Aufgaben', 'Zukünftige Termine'],
            'awards': ['Erfolgskriterien', 'Voraussetzungen', 'Award-Mockup'],
            'customers': ['Kunde hinzufügen', 'Individueller Erfolgsplan', 'Referenzbild hochladen'],
            'league': ['Impact League', 'Leuchtfeuer-Score'],
            'recommendations': ['Für Pokale Meier', 'Eigene Empfehlungen aufbauen', 'Warum lohnt sich das?'],
            'profile': ['Buchhaltung', 'Affiliate-Daten', 'Auszahlungsinformationen', 'Partnerstatus'],
        }
        for page_name, markers in required.items():
            for marker in markers:
                self.assertIn(marker, self.pages[page_name], f'{page_name}: {marker}')

    def test_internal_board_is_interactive_and_prepares_tldv_imports_without_claiming_live_ai(self):
        admin = self.pages['admin']
        for marker in ['Interne Übersicht', 'Termin dokumentieren', 'Stufenplanung', 'TL;DV', 'Prüfwarteschlange']:
            self.assertIn(marker, admin)
        self.assertIn('statische Demo', admin)

    def test_design_system_contains_progress_forms_dialogs_and_award_visuals(self):
        for marker in ['.progress-bar', '.dialog', '.form-grid', '.award-mockup', '.timeline-card']:
            self.assertIn(marker, self.css)


if __name__ == '__main__':
    unittest.main()
