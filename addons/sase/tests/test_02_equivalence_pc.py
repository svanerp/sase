import logging
import math

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("sase")
class TestLatence(TransactionCase):

    def create_enfant(self, nb):
        enfants = []
        for i in range(nb):
            enfant = self.env["sase.enfant"].create(
                {
                    "nom": f"Enfant_{i}",
                    "prenom": "Test",
                    "date_naissance": "2010-01-01",
                    "genre": "female" if i % 2 == 0 else "male",
                }
            )
            enfants.append(enfant)
        return enfants

    def setUp(self):
        self.situation = self.env["sase.situation"].create(
            {
                "nom": "Test Situation",
            }
        )
        for enfant in self.env["sase.enfant"].search([]):
            enfant.unlink()

    def test_equi(self):
        for i in range(8):
            _logger.info(f"{i} : {math.ceil(i/3)}")

    def test_equivalence_0(self):
        self.assertEqual(self.situation.equivalent_situation, 0)

    def test_equivalence_1(self):
        enfants = self.create_enfant(1)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]
        self.assertEqual(self.situation.equivalent_situation, 1)

    def test_equivalence_2(self):
        enfants = self.create_enfant(2)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]
        self.assertEqual(self.situation.equivalent_situation, 1)

    def test_equivalence_3(self):
        enfants = self.create_enfant(3)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]
        self.assertEqual(self.situation.equivalent_situation, 1)

    def test_equivalence_4(self):
        enfants = self.create_enfant(4)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]
        self.assertEqual(self.situation.equivalent_situation, 2)

    def test_equivalence_5(self):
        enfants = self.create_enfant(5)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]
        self.assertEqual(self.situation.equivalent_situation, 2)

    def test_equivalence_6(self):
        enfants = self.create_enfant(6)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]
        self.assertEqual(self.situation.equivalent_situation, 2)

    def test_equivalence_7(self):
        enfants = self.create_enfant(7)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]
        self.assertEqual(self.situation.equivalent_situation, 3)
