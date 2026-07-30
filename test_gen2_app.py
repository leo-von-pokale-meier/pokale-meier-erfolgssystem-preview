import io
import os
import tempfile
import unittest
from urllib.parse import urlencode

from gen2_app import create_app
from gen2_foundation import FoundationStore


def wsgi_request(app, path, method='GET', form=None, cookie=''):
    body = urlencode(form or {}).encode('utf-8')
    captured = {}

    def start_response(status, headers):
        captured['status'] = status
        captured['headers'] = dict(headers)

    environ = {
        'REQUEST_METHOD': method,
        'PATH_INFO': path,
        'CONTENT_LENGTH': str(len(body)),
        'CONTENT_TYPE': 'application/x-www-form-urlencoded',
        'wsgi.input': io.BytesIO(body),
        'HTTP_COOKIE': cookie,
    }
    response_body = b''.join(app(environ, start_response))
    return captured['status'], captured['headers'], response_body.decode('utf-8')


class Gen2WebAppTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp.close()
        self.store = FoundationStore(self.temp.name)
        self.admin = self.store.bootstrap_admin('Admin Team', 'admin@pokale-meier.test', 'sicheres-test-passwort')
        self.org = self.store.create_organisation(self.admin['id'], 'Impact Kunde GmbH', 'https://impact-kunde.example')
        self.app = create_app(self.store, session_secret='test-only-secret-that-is-long-enough')

    def tearDown(self):
        os.unlink(self.temp.name)

    def test_dashboard_requires_login(self):
        status, headers, _ = wsgi_request(self.app, '/')
        self.assertEqual(status, '303 See Other')
        self.assertEqual(headers['Location'], '/login')

    def test_login_opens_internal_dashboard_with_organisation(self):
        status, headers, _ = wsgi_request(self.app, '/login', 'POST', {
            'email': 'admin@pokale-meier.test',
            'password': 'sicheres-test-passwort',
        })
        self.assertEqual(status, '303 See Other')
        status, _, page = wsgi_request(self.app, '/', cookie=headers['Set-Cookie'].split(';', 1)[0])
        self.assertEqual(status, '200 OK')
        self.assertIn('Erfolgssoftware', page)
        self.assertIn('Impact Kunde GmbH', page)
        self.assertIn('href="https://impact-kunde.example"', page)

    def test_customer_sees_only_own_appointments_and_next_steps(self):
        customer = self.store.create_customer(self.admin['id'], self.org['id'], 'Kunde', 'kunde@test.invalid', 'kunde-test-passwort')
        other = self.store.create_organisation(self.admin['id'], 'Andere GmbH', 'https://andere.invalid')
        self.store.create_appointment(self.admin['id'], self.org['id'], 'Erfolgs-Check', '2026-08-10T10:00:00Z', 'Erfolgsbild hochladen')
        self.store.create_appointment(self.admin['id'], other['id'], 'Interner fremder Termin', '2026-08-11T10:00:00Z', 'Darf nicht sichtbar sein')

        status, headers, _ = wsgi_request(self.app, '/login', 'POST', {
            'email': customer['email'], 'password': 'kunde-test-passwort',
        })
        self.assertEqual(status, '303 See Other')
        _, _, page = wsgi_request(self.app, '/', cookie=headers['Set-Cookie'].split(';', 1)[0])
        self.assertIn('Erfolgs-Check', page)
        self.assertIn('Erfolgsbild hochladen', page)
        self.assertNotIn('Interner fremder Termin', page)

    def test_customer_dashboard_shows_journey_and_unverified_appointment_state(self):
        customer = self.store.create_customer(self.admin['id'], self.org['id'], 'Kunde', 'kunde@test.invalid', 'kunde-test-passwort')
        appointment = self.store.create_appointment(self.admin['id'], self.org['id'], 'Strategie-Check', '2026-08-12T10:00:00Z', 'Nachweis vorbereiten')
        self.store.complete_appointment(self.admin['id'], appointment['id'])
        _, headers, _ = wsgi_request(self.app, '/login', 'POST', {
            'email': customer['email'], 'password': 'kunde-test-passwort',
        })
        _, _, page = wsgi_request(self.app, '/', cookie=headers['Set-Cookie'].split(';', 1)[0])
        self.assertIn('Deine nächste Auszeichnung', page)
        self.assertIn('Bronze abschließen', page)
        self.assertIn('Termin abgeschlossen · Prüfung offen', page)

    def test_leaderboard_route_shows_only_approved_public_profiles_and_successes(self):
        hidden = self.store.create_organisation(self.admin['id'], 'Intern GmbH', 'https://intern.invalid')
        achievement = self.store.record_achievement(self.admin['id'], self.org['id'], 'award_delivered', verified=True)
        self.store.update_public_profile(
            self.admin['id'], self.org['id'], True, 'Wir machen Wirkung sichtbar.', 'https://impact-kunde.example/partner'
        )
        self.store.approve_achievement_for_public(self.admin['id'], achievement['id'], 'Erster Impact Frame übergeben')
        self.store.record_achievement(self.admin['id'], hidden['id'], 'award_delivered', verified=True)
        _, headers, _ = wsgi_request(self.app, '/login', 'POST', {
            'email': 'admin@pokale-meier.test', 'password': 'sicheres-test-passwort',
        })
        status, _, page = wsgi_request(self.app, '/rangliste', cookie=headers['Set-Cookie'].split(';', 1)[0])
        self.assertEqual(status, '200 OK')
        self.assertIn('Leuchtfeuer-Score', page)
        self.assertIn('Wir machen Wirkung sichtbar.', page)
        self.assertIn('Erster Impact Frame übergeben', page)
        self.assertNotIn('Intern GmbH', page)


if __name__ == '__main__':
    unittest.main()
