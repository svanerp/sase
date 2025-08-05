import logging

from odoo import api
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class Enfant(models.Model):
    _name = "sase.enfant"
    _description = "Enfant"
    _sql_constraints = [
        (
            "unique_name",
            "UNIQUE(nom, prenom, date_naissance)",
            "La combinaison de nom, prénom et date de naissance doit être unique.",
        ),
    ]
    nom = fields.Char(string="Nom", required=True)
    prenom = fields.Char(string="Prénom", required=True)
    date_naissance = fields.Date(string="Date de Naissance", required=True)
    genre = fields.Selection(
        selection=[
            ("male", "Masculin"),
            ("female", "Féminin"),
        ],
        string="Genre",
        required=True,
    )
    situation_ids = fields.Many2many(
        comodel_name="sase.situation",
        string="Situations",
        help="The situations associated with this child.",
    )
    notes = fields.Html(string="Notes")

    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )
    age = fields.Integer(
        string="Âge",
        compute="_compute_age",
        store=True,
    )
    is_dossier = fields.Boolean(
        string="Dossier",
        compute="_compute_dossier",
        store=True,
    )

    @api.depends("date_naissance")
    def _compute_age(self):
        for record in self:
            if record.date_naissance:
                today = fields.Date.context_today(record)
                age = today.year - record.date_naissance.year
                if (today.month, today.day) < (record.date_naissance.month, record.date_naissance.day):
                    age -= 1
                record.age = age
            else:
                record.age = 0

    @api.depends("nom", "prenom", "date_naissance")
    def _compute_display_name(self):
        for record in self:
            if record.nom and record.prenom and record.date_naissance:
                record.display_name = f"{record.nom} {record.prenom} ({record.date_naissance.strftime('%d/%m/%Y')})"
            elif record.nom and record.prenom:
                record.display_name = f"{record.nom} {record.prenom}"
            elif record.nom:
                record.display_name = record.nom
            else:
                record.display_name = ""

    def _compute_dossier(self):
        """Compute the dossier for each child based on their situations."""
        for record in self:
            record.is_dossier = record.situation_ids.mapped("state") in ["draft", "running", "done", "cancelled"]
