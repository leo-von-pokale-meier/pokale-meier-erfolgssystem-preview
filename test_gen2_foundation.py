import os
import tempfile
import unittest

from gen2_foundation import (
    ROLES,
    FoundationStore,
    PermissionDenied,
)


class Gen2FoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp.close()
        self.store = FoundationStore(self.temp.name)
        self.admin = self.store.bootstrap_admin('Admin Team', 'admin@pokale-meier.test', 'sicheres-test-passwort')
        self.org = self.store.create_organisation(self.admin['id'], 'Impact Kunde GmbH', 'impact-kunde.example')

    def tearDown(self):
        os.unlink(self.temp.name)

    def test_has_the_four_confirmed_internal_roles(self):
        self.assertEqual(set(ROLES), {'admin', 'designer', 'berater', 'kundenservice'})

    def test_customer_service_cannot_delete_customers(self):
        service = self.store.create_internal_user(
            self.admin['id'], 'Service Team', 'service@pokale-meier.test', 'kundenservice', 'test-passwort-2'
        )
        customer = self.store.create_customer(self.admin['id'], self.org['id'], 'Kundenzugang', 'kunde@impact-kunde.test', 'test-passwort-3')

        with self.assertRaises(PermissionDenied):
            self.store.archive_customer(service['id'], customer['id'])

    def test_customer_cannot_read_another_organisation(self):
        other_org = self.store.create_organisation(self.admin['id'], 'Andere GmbH', 'andere.example')
        own_customer = self.store.create_customer(self.admin['id'], self.org['id'], 'Eigener Zugang', 'eigen@impact-kunde.test', 'test-passwort-4')
        other_customer = self.store.create_customer(self.admin['id'], other_org['id'], 'Fremder Zugang', 'fremd@andere.test', 'test-passwort-5')
        self.store.create_appointment(self.admin['id'], other_org['id'], 'Datencheck', '2026-08-10T10:00:00Z', 'Datenexport senden')

        self.assertEqual(self.store.visible_appointments(own_customer['id']), [])
        self.assertEqual(len(self.store.visible_appointments(other_customer['id'])), 1)

    def test_appointment_keeps_next_steps_with_customer_visibility(self):
        appointment = self.store.create_appointment(
            self.admin['id'], self.org['id'], 'Onboarding', '2026-08-10T10:00:00Z', 'Logo senden'
        )
        self.assertEqual(appointment['next_steps'], 'Logo senden')
        self.assertTrue(appointment['next_steps_customer_visible'])

    def test_audit_log_records_a_customer_creation(self):
        self.store.create_customer(self.admin['id'], self.org['id'], 'Kundenzugang', 'kunde@impact-kunde.test', 'test-passwort-6')
        actions = [entry['action'] for entry in self.store.audit_entries(self.org['id'])]
        self.assertIn('customer.created', actions)


if __name__ == '__main__':
    unittest.main()
