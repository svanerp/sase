from odoo import api
from odoo import fields
from odoo import models

mandant_qualites = [
    ("directrice", "Directeur.ice"),
    ("conseiller", "Conseiller.ère"),
    ("delegue", "Délégué.e"),
]


class ServiceEmploye(models.Model):
    _name = "sase.service_employe"
    _description = "Employés du Service"
    _rec_name = "nom"

    titre = fields.Char(string="Titre", required=True)
    nom = fields.Char(string="Nom", required=True)
    service_id = fields.Many2one(
        comodel_name="sase.service",
        string="Service",
        required=True,
        help="Le service mandant auquel ce responsable est affecté.",
    )
    email = fields.Char(string="Email")
    telephone = fields.Char(string="Téléphone")
    qualite = fields.Selection(
        string="Qualité",
        selection=mandant_qualites,
        help="La qualité de ce responsable dans le service mandant.",
    )
