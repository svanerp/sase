from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged


@tagged("sase")
class TestLatence(TransactionCase):

    def setUp(self):
        self.situation = self.env["sase.situation"].create(
            {
                "nom": "Test Situation",
                "date_notification": "2025-01-05",
            }
        )

    @freeze_time("2025-01-10")
    def test_latence_no_date(self):
        self.situation.date_notification = False
        self.assertEqual(self.situation.latence, 0)

    @freeze_time("2025-01-10")
    def test_latence_date_notification(self):
        self.assertEqual(self.situation.latence, 5)

    @freeze_time("2025-01-10")
    def test_latence_date_officialisation(self):
        self.situation.date_officialisation = fields.Date.from_string("2025-01-20")
        self.assertEqual(self.situation.latence, 15)

    @freeze_time("2025-01-10")
    def test_latence_date_annulation(self):
        self.situation.date_annulation = fields.Date.from_string("2025-01-25")
        self.assertEqual(self.situation.latence, 20)
