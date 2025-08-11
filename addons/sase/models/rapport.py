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
    enfant_id = fields.Many2one(
        comodel_name="sase.enfant",
        string="Enfant",
        required=True,
        help="Enfant concerné par ce rapport.",
    )
    lien_rapport = fields.Char(
        string="Lien vers le rapport",
        help="Lien vers le rapport. Attention à ne pas le déplacer dans le système de fichiers.",
    )
    active = fields.Boolean(
        string="Actif",
        compute="_compute_active",
        store=True,
        default=True,
        help="Indique si le rapport est actif ou non.",
    )

    @api.depends("date_reelle")
    def _compute_active(self):
        for record in self:
            record.active = not record.date_reelle
