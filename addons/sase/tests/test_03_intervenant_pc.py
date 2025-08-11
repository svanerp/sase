import logging
import math

from odoo import fields
from odoo.tests.common import TransactionCase
from odoo.tests.common import tagged

_logger = logging.getLogger(__name__)


@tagged("sase", "steph")
class TestIntervenant(TransactionCase):

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
        self.intervenant = self.env["sase.intervenant"].create(
            {
                "nom": "Test Intervenant",
                "prenom": "Intervenant",
                "temps_travail": "temps_complet",
            }
        )

    def test_intervenant_pc_1(self):
        enfants = self.create_enfant(1)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]

        self.situation.intervant_principal_id = self.intervenant.id
        self.assertEqual(self.intervenant.nb_situation_principal, 1)
        self.assertEqual(self.intervenant.nb_situation_secondaire, 0)
        self.assertEqual(self.intervenant.total_pc, 1.0)

    def test_intervenant_pc_1(self):
        enfants = self.create_enfant(1)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]

        self.situation.intervant_principal_id = self.intervenant.id
        s2 = self.env["sase.situation"].create(
            {
                "nom": "Secondary Situation",
                "intervenant_secondaire_id": self.intervenant.id,
            }
        )
        enfants = self.create_enfant(1)
        for enfant in enfants:
            s2.enfant_ids = [(4, enfant.id)]
        s2.intervenant_secondaire_id = self.intervenant.id
        self.assertEqual(self.intervenant.nb_situation_principal, 1)
        self.assertEqual(self.intervenant.nb_situation_secondaire, 1)
        self.assertEqual(self.intervenant.total_pc, 1.5)

    def test_intervenant_pc_4(self):
        enfants = self.create_enfant(4)
        for enfant in enfants:
            self.situation.enfant_ids = [(4, enfant.id)]

        self.situation.intervant_principal_id = self.intervenant.id
        self.assertEqual(self.intervenant.nb_situation_principal, 1)
        self.assertEqual(self.intervenant.nb_situation_secondaire, 0)
        self.assertEqual(self.intervenant.total_pc, 2.0)
