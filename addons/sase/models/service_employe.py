from odoo import api
from odoo import fields
from odoo import models


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
        help="Le service auquel le délégué est associé.",
    )
    email = fields.Char(string="Email")
    telephone = fields.Char(string="Téléphone")
    is_directeur = fields.Boolean(
        string="Directeur/Conseiller",
        help="Indique si cet employé est directeur ou conseiller du service.",
    )
