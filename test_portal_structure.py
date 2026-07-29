from pathlib import Path
import unittest

PORTAL = Path(__file__).with_name("pokale-meier-erfolgsportal.html")


class PortalStructureTests(unittest.TestCase):
    def setUp(self):
        self.html = PORTAL.read_text(encoding="utf-8")

    def test_portal_has_core_navigation_for_internal_work(self):
        for label in ["Übersicht", "Kunden", "Phasen", "Termine", "Auszeichnungen", "Empfehlungen", "Vereinbarungen"]:
            self.assertIn(label, self.html)

    def test_portal_models_the_three_success_phases(self):
        for phase in ["Bronze", "Silber", "Leuchtfeuer"]:
            self.assertIn(phase, self.html)
        self.assertIn('id="phase-visualization"', self.html)

    def test_portal_allows_adding_phases_and_appointments(self):
        self.assertIn('id="add-phase"', self.html)
        self.assertIn('id="add-appointment"', self.html)
        self.assertIn('id="appointment-phase"', self.html)
        self.assertIn('localStorage', self.html)

    def test_gen1_records_are_real_local_data_objects(self):
        for record_type in ["customers", "awards", "referrals", "agreements"]:
            self.assertIn(record_type, self.html)
        for dialog in ["customer-dialog", "award-dialog", "referral-dialog", "agreement-dialog"]:
            self.assertIn(f'id="{dialog}"', self.html)

    def test_gen1_has_renderers_and_add_actions_for_each_record_area(self):
        for marker in ["renderCustomers", "renderAwards", "renderReferrals", "renderAgreements",
                       "add-customer", "add-award", "add-referral", "add-agreement"]:
            self.assertIn(marker, self.html)

    def test_bronze_has_the_four_ordered_consulting_appointments(self):
        for marker in [
            "Onboarding: Dein Weg zum Kunden-Erfolgssystem",
            "Daten-Checkup: Deine erste Award-Stufe",
            "Follow Up: Deine ersten Übergaben im Erfolgs-System",
            "Strategietermin: Die Stufen deines Erfolgs-Systems",
            "bronzeAppointments",
        ]:
            self.assertIn(marker, self.html)

    def test_appointment_documents_have_editable_fields_and_persist_locally(self):
        for marker in [
            "Termin-Dokument", "fieldDefinitions", "appointmentNotes", "Notizen speichern",
            "localStorage", "Termin erledigen",
        ]:
            self.assertIn(marker, self.html)

    def test_sequential_unlocking_and_silver_lock_are_visible(self):
        for marker in [
            "Nächsten Termin buchen", "Termin freischalten", "Silber starten", "Bronze komplett abschließen",
            "locked", "isBronzeComplete",
        ]:
            self.assertIn(marker, self.html)


if __name__ == "__main__":
    unittest.main()
