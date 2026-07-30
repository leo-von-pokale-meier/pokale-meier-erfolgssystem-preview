import unittest
from pathlib import Path


class PortalStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).parent
        cls.landing = (cls.root / 'index.html').read_text(encoding='utf-8')
        cls.customer_pages = {
            'dashboard': 'kundenansicht.html',
            'etappen': 'kunden-etappen.html',
            'awards': 'kunden-awards.html',
            'kunden': 'kunden-erfolge.html',
            'bestenliste': 'kunden-bestenliste.html',
            'empfehlungen': 'kunden-empfehlungen.html',
            'partner': 'kunden-partner.html',
            'wissen': 'kunden-wissen.html',
            'profil': 'kunden-profil.html',
        }

    def test_public_landingpage_explains_process_and_routes_application(self):
        for marker in ['Jetzt bewerben', 'Impact Frames', 'Zielbild: Dein Weg zum Leuchtfeuer', 'zielbild-leuchtfeuer-1-1.webp']:
            self.assertIn(marker, self.landing)
        self.assertIn('https://www.pokale-meier.de/impact-frames', self.landing)
        self.assertIn('Dein Einstieg', self.landing)
        self.assertIn('Kundenportal erleben', self.landing)

    def test_public_gallery_uses_the_two_approved_reference_images(self):
        for image in ['trusted-advisor-scaling-champions.jpg', 'dirk-kreuter-sales-champion.jpg']:
            self.assertTrue((self.root / 'assets' / image).is_file(), image)
            self.assertIn(f'assets/{image}', self.landing)

    def test_customer_demo_is_real_multpage_navigation(self):
        for page in self.customer_pages.values():
            content = (self.root / page).read_text(encoding='utf-8')
            self.assertIn('demo.css', content)
            self.assertIn('Kundenansicht', content)
        self.assertIn('kundenansicht.html', self.landing)

    def test_customer_navigation_covers_the_approved_workspaces(self):
        dashboard = (self.root / self.customer_pages['dashboard']).read_text(encoding='utf-8')
        for target in self.customer_pages.values():
            self.assertIn(target, dashboard)
        for marker in ['Leuchtfeuer-Score', 'Mein Fortschritt', 'Dein nächster Termin', 'Nächste sinnvolle Aktion']:
            self.assertIn(marker, dashboard)

    def test_customer_successes_keep_upcoming_and_confirmed_records_separate(self):
        content = (self.root / self.customer_pages['kunden']).read_text(encoding='utf-8')
        for marker in ['Kommende Erfolgskunden', 'Bisherige Erfolgskunden', 'Erfolgskunden hinzufügen', 'Nachweis eingereicht', 'Interne Prüfung']:
            self.assertIn(marker, content)

    def test_public_preview_does_not_claim_a_real_login_or_data_processing(self):
        contents = [self.landing]
        contents.extend((self.root / page).read_text(encoding='utf-8') for page in self.customer_pages.values())
        for content in contents:
            self.assertIn('statische demo', content.lower())
            self.assertNotIn('MIRO_ACCESS_TOKEN', content)
            self.assertNotIn('client_secret', content.lower())


if __name__ == '__main__':
    unittest.main()