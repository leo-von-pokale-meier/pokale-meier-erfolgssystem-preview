import os
import tempfile
import unittest

from gen2_foundation import FoundationStore, PermissionDenied, ValidationError


class AwardProgramTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp.close()
        self.store = FoundationStore(self.temp.name)
        self.admin = self.store.bootstrap_admin('Admin Team', 'admin@pokale-meier.test', 'sicheres-test-passwort')
        self.org = self.store.create_organisation(self.admin['id'], 'Impact Kunde GmbH')

    def tearDown(self):
        os.unlink(self.temp.name)

    def test_admin_can_create_and_publish_the_three_initial_stages(self):
        program = self.store.create_award_program(self.admin['id'], self.org['id'], 'Kundenprogramm 2026')
        bronze = self.store.add_award_stage(self.admin['id'], program['id'], 1, 'Bronze', 50)
        silver = self.store.add_award_stage(self.admin['id'], program['id'], 2, 'Silber', 100)
        beacon = self.store.add_award_stage(self.admin['id'], program['id'], 3, 'Leuchtfeuer', 200)

        self.store.publish_award_stage(self.admin['id'], bronze['id'])
        self.store.publish_award_stage(self.admin['id'], silver['id'])
        self.store.publish_award_stage(self.admin['id'], beacon['id'])

        visible = self.store.visible_award_stages(self.org['id'])
        self.assertEqual([stage['name'] for stage in visible], ['Bronze', 'Silber', 'Leuchtfeuer'])
        self.assertEqual([stage['success_points'] for stage in visible], [50, 100, 200])
        self.assertEqual([stage['status'] for stage in visible], ['published', 'published', 'published'])

    def test_customer_cannot_create_or_publish_stages(self):
        customer = self.store.create_customer(
            self.admin['id'], self.org['id'], 'Kundenzugang', 'kunde@impact-kunde.test', 'kunde-test-passwort'
        )
        program = self.store.create_award_program(self.admin['id'], self.org['id'], 'Kundenprogramm 2026')
        stage = self.store.add_award_stage(self.admin['id'], program['id'], 1, 'Bronze', 50)

        with self.assertRaises(PermissionDenied):
            self.store.add_award_stage(customer['id'], program['id'], 2, 'Silber', 100)
        with self.assertRaises(PermissionDenied):
            self.store.publish_award_stage(customer['id'], stage['id'])

    def test_stages_are_scoped_to_their_own_organisation_and_limited_to_ten(self):
        other_org = self.store.create_organisation(self.admin['id'], 'Andere GmbH')
        program = self.store.create_award_program(self.admin['id'], self.org['id'], 'Kundenprogramm 2026')
        for position in range(1, 11):
            self.store.add_award_stage(self.admin['id'], program['id'], position, f'Stufe {position}', position * 10)

        with self.assertRaises(ValidationError):
            self.store.add_award_stage(self.admin['id'], program['id'], 11, 'Zu viel', 110)
        self.assertEqual(self.store.visible_award_stages(other_org['id']), [])


if __name__ == '__main__':
    unittest.main()
