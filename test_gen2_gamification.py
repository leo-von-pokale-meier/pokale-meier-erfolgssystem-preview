import os
import tempfile
import unittest

from gen2_foundation import FoundationStore, ValidationError


class GamificationFoundationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
        self.temp.close()
        self.store = FoundationStore(self.temp.name)
        self.admin = self.store.bootstrap_admin('Admin Team', 'admin@pokale-meier.test', 'sicheres-test-passwort')
        self.org = self.store.create_organisation(self.admin['id'], 'Impact Kunde GmbH', 'impact-kunde.example')

    def tearDown(self):
        os.unlink(self.temp.name)

    def test_only_verified_evidence_affects_score(self):
        self.store.record_achievement(self.admin['id'], self.org['id'], 'award_delivered', verified=False)
        self.assertEqual(self.store.organisation_score(self.org['id'])['points'], 0)
        self.store.record_achievement(self.admin['id'], self.org['id'], 'award_delivered', verified=True)
        self.assertEqual(self.store.organisation_score(self.org['id'])['points'], 12)

    def test_score_rewards_confirmed_rule_set_and_badges(self):
        for event_type in ['award_photo_uploaded', 'online_gallery_uploaded', 'referral_program_created', 'physical_incentive_system', 'bronze_completed', 'silver_completed', 'appointment_completed']:
            self.store.record_achievement(self.admin['id'], self.org['id'], event_type, verified=True)
        score = self.store.organisation_score(self.org['id'])
        self.assertEqual(score['points'], 57)
        self.assertIn('Bronze abgeschlossen', score['badges'])
        self.assertIn('Silber abgeschlossen', score['badges'])

    def test_leaderboard_uses_website_and_stage_for_public_profile(self):
        self.store.record_achievement(self.admin['id'], self.org['id'], 'award_delivered', verified=True)
        leaderboard = self.store.leaderboard()
        self.assertEqual(leaderboard[0]['name'], 'Impact Kunde GmbH')
        self.assertEqual(leaderboard[0]['website_url'], 'impact-kunde.example')
        self.assertEqual(leaderboard[0]['lifecycle_stage'], 'bronze')

    def test_public_leaderboard_only_shows_approved_partner_profiles_and_counts_successes(self):
        self.store.record_achievement(self.admin['id'], self.org['id'], 'award_delivered', verified=True)
        self.store.record_achievement(self.admin['id'], self.org['id'], 'award_photo_uploaded', verified=True)
        self.assertEqual(self.store.public_leaderboard(), [])

        self.store.update_public_profile(
            self.admin['id'], self.org['id'], enabled=True,
            description='Macht IT-Projekte für Mittelständler verlässlich.',
            partner_url='https://impact-kunde.example/partner',
        )
        leaderboard = self.store.public_leaderboard()
        self.assertEqual(leaderboard[0]['success_count'], 2)
        self.assertEqual(leaderboard[0]['public_description'], 'Macht IT-Projekte für Mittelständler verlässlich.')
        self.assertEqual(leaderboard[0]['partner_url'], 'https://impact-kunde.example/partner')

    def test_recent_public_successes_require_individual_approval(self):
        achievement = self.store.record_achievement(self.admin['id'], self.org['id'], 'award_delivered', verified=True)
        self.store.update_public_profile(self.admin['id'], self.org['id'], enabled=True)
        self.assertEqual(self.store.recent_public_successes(), [])

        self.store.approve_achievement_for_public(
            self.admin['id'], achievement['id'], 'Award persönlich übergeben',
        )
        success = self.store.recent_public_successes()[0]
        self.assertEqual(success['title'], 'Award persönlich übergeben')
        self.assertEqual(success['points'], 12)
        self.assertEqual(success['partner_url'], '')

    def test_appointment_only_scores_after_internal_verification(self):
        appointment = self.store.create_appointment(
            self.admin['id'], self.org['id'], 'Strategie-Check', '2026-08-11T10:00:00Z', 'Nachweis vorbereiten'
        )
        completed = self.store.complete_appointment(self.admin['id'], appointment['id'])
        self.assertEqual(completed['status'], 'completed')
        self.assertEqual(self.store.organisation_score(self.org['id'])['points'], 0)

        verified = self.store.verify_appointment_completion(self.admin['id'], appointment['id'])
        self.assertEqual(verified['status'], 'verified')
        self.assertEqual(self.store.organisation_score(self.org['id'])['points'], 1)
        with self.assertRaises(ValidationError):
            self.store.verify_appointment_completion(self.admin['id'], appointment['id'])

    def test_journey_makes_next_appointment_and_award_progress_visible(self):
        appointment = self.store.create_appointment(
            self.admin['id'], self.org['id'], 'Nachweis-Check', '2026-08-12T10:00:00Z', 'Screenshot einreichen'
        )
        journey = self.store.organisation_journey(self.org['id'])
        self.assertEqual(journey['next_appointment']['id'], appointment['id'])
        self.assertEqual(journey['next_appointment']['next_steps'], 'Screenshot einreichen')
        self.assertEqual(journey['points_to_next_award'], 10)


if __name__ == '__main__':
    unittest.main()
