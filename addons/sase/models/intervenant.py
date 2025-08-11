import logging

from odoo import api
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)

nb_situation_atteindre = {
    "temps_complet": 21,
    "9_10": 21 * 0.9,
    "4_5": 21 * 0.8,
    "mi_temps": 21 * 0.5,
    "absence": 0,
}


class Intervenant(models.Model):
    _name = "sase.intervenant"
    _description = "Intervenant"

    nom = fields.Char(string="Nom", required=True)
    prenom = fields.Char(string="Prénom", required=True)
    email = fields.Char(string="Email")
    telephone = fields.Char(string="Téléphone")
    situation_principal_ids = fields.One2many(
        comodel_name="sase.situation",
        inverse_name="intervant_principal_id",
        string="Situations Principales",
        help="Situations où cet intervenant est le principal.",
    )
    situation_secondaire_ids = fields.One2many(
        comodel_name="sase.situation",
        inverse_name="intervenant_secondaire_id",
        string="Situations Secondaires",
        help="Situations où cet intervenant est secondaire.",
    )
    nb_situation_principal = fields.Integer(
        string="Nombre de situations principales",
        compute="_compute_nb_situation",
        store=True,
    )
    nb_situation_secondaire = fields.Integer(
        string="Nombre de situations secondaires",
        compute="_compute_nb_situation",
        store=True,
    )
    display_name = fields.Char(
        string="Nom complet",
        compute="_compute_display_name",
        store=True,
    )
    temps_travail = fields.Selection(
        [
            ("temps_complet", "Temps Complet"),
            ("9_10", "9/10ème temps"),
            ("4_5", "4/5ème temps"),
            ("mi_temps", "Mi-temps"),
            ("absence", "Absence longue durée"),
        ],
        string="Temps de travail",
        default="temps_complet",
        help="Indique le temps de travail de l'intervenant.",
    )
    total_pc = fields.Float(
        string="Total PC",
        compute="_compute_total_pc",
        store=True,
        help="Charge PC totale de l'intervenant.",
    )
    taux_occupation = fields.Integer(
        string="Taux d'occupation",
        compute="_compute_taux_occupation",
        store=True,
        help="Taux d'occupation de l'intervenant basé sur le total PC.",
    )
    nb_enfants = fields.Integer(
        string="Nombre d'enfants",
        compute="_compute_nb_enfants",
        store=True,
        help="Nombre d'enfants associés à l'intervenant.",
    )

    @api.depends(
        "situation_principal_ids",
        "situation_secondaire_ids",
        "situation_principal_ids.enfant_ids",
        "situation_secondaire_ids.enfant_ids",
    )
    def _compute_nb_enfants(self):
        for record in self:
            record.nb_enfants = len(
                record.situation_principal_ids.filtered(lambda s: s.state in ["running", "draft"]).enfant_ids
            ) + len(record.situation_secondaire_ids.filtered(lambda s: s.state in ["running", "draft"]).enfant_ids)

    @api.depends("temps_travail", "total_pc")
    def _compute_taux_occupation(self):
        for record in self:
            nb = nb_situation_atteindre.get(record.temps_travail, 0)
            record.taux_occupation = (
                (record.nb_situation_principal + record.nb_situation_secondaire) / nb * 100 if nb > 0 else 0
            )
            # record.taux_occupation = (record.total_pc / nb) * 100 if nb > 0 else 0

    @api.depends("situation_principal_ids.equivalent_situation", "situation_secondaire_ids.equivalent_situation")
    def _compute_total_pc(self):
        for record in self:
            record.total_pc = sum(
                situation.equivalent_situation
                for situation in record.situation_principal_ids.filtered(lambda s: s.state in ["running", "draft"])
            ) + sum(
                situation.equivalent_situation * 0.5
                for situation in record.situation_secondaire_ids.filtered(lambda s: s.state in ["running", "draft"])
            )

    @api.depends(
        "situation_principal_ids",
        "situation_secondaire_ids",
        "situation_principal_ids.state",
        "situation_secondaire_ids.state",
    )
    def _compute_nb_situation(self):
        _logger.info("Computing number of situations for each intervenant.")
        for record in self:
            record.nb_situation_principal = len(
                record.situation_principal_ids.filtered(lambda s: s.state in ["running", "draft"])
            )
            record.nb_situation_secondaire = len(
                record.situation_secondaire_ids.filtered(lambda s: s.state in ["running", "draft"])
            )

    @api.depends("nom", "prenom")
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.prenom} {record.nom}" if record.prenom and record.nom else ""
        for record in self:
            record.display_name = f"{record.prenom} {record.nom}" if record.prenom and record.nom else ""

    @api.onchange("temps_travail")
    def _onchange_temps_travail(self):
        self._compute_taux_occupation()
