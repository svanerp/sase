from odoo import api
from odoo import fields
from odoo import models


class Rapport(models.Model):
    _name = "sase.rapport"
    _description = "Rapport"
    _rec_name = "nom"

    nom = fields.Char(string="Nom", required=True)
    date_prevue = fields.Date(
        string="Date prévue",
        default=fields.Date.today,
        help="Date prévues pour le rapport.",
        readonly=True,
        required=True,
    )
    date_reelle = fields.Date(
        string="Date d'envoi",
    )

    situation_id = fields.Many2one(
        comodel_name="sase.situation",
        string="Situation",
        required=True,
        help="Situation associée à ce rapport.",
    )
