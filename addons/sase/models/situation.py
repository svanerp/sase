import datetime
import logging
import math

from dateutil.relativedelta import relativedelta

from odoo import api
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)

report_duedates = (3, 6, 12, 18, 24)


class Situation(models.Model):
    _name = "sase.situation"
    _description = "Situation"

    nom = fields.Char(string="Nom", required=True)
    description = fields.Text(string="Description")
    state = fields.Selection(
        [
            ("draft", "Admission"),
            ("running", "En cours"),
            ("done", "Terminé"),
            ("cancelled", "Annulé"),
        ],
        compute="_compute_state",
        default="draft",
        store=True,
    )
    enfant_ids = fields.Many2many(
        comodel_name="sase.enfant",
        string="Enfants",
        help="Enfants associés à cette situation.",
    )
    display_name = fields.Char(
        string="Display Name",
        compute="_compute_display_name",
        store=True,
    )
    enfant_nb = fields.Integer(
        string="Nombre d'enfants",
        compute="_compute_enfants_nb",
        store=True,
    )
    nb_jours = fields.Integer(
        string="Nombre de jours depuis l'officialisation",
        compute="_compute_nb_jours",
        store=True,
    )
    service_id = fields.Many2one(
        comodel_name="sase.service",
        string="Service",
        help="Le service auquel cette situation est associée.",
    )
    service_mandant = fields.Many2one(
        comodel_name="sase.service_employe",
        string="Mandant",
        domain="[('is_directeur', '=', True)]",
    )
    service_delegue = fields.Many2one(
        comodel_name="sase.service_employe",
        string="Délégué",
        domain="[('is_directeur', '=', False)]",
    )
    equivalent_situation = fields.Integer(
        string="PC (équivalent)",
        compute="_compute_equivalent_situation",
        store=True,
        help="Nombre d'équivalents PC pour cette situation en fonction du nombre d'enfants.",
    )
    notes = fields.Html(
        string="Notes",
        help="Notes supplémentaires concernant cette situation.",
    )
    latence = fields.Integer(
        string="Latence",
        compute="_compute_latence",
        help="Nombre de jours entre la notification et l'officialisation/annulation",
    )
    is_report_due = fields.Boolean(
        string="Rapport dû",
        compute="_compute_report_due",
        store=True,
    )
    intervant_principal_id = fields.Many2one(
        comodel_name="sase.intervenant",
        string="Intervenant Principal",
        help="Intervenant principal associé à cette situation.",
    )
    intervenant_secondaire_id = fields.Many2one(
        comodel_name="sase.intervenant",
        string="Intervenant Secondaire",
        help="Intervenant secondaire associé à cette situation.",
    )
    intervenant_ids = fields.Many2many(
        comodel_name="sase.intervenant",
        string="Intervenants",
        compute="_compute_intervenants",
        store=True,
    )
    # Dates
    date_notification = fields.Date(
        string="Date de notification",
        help="Date à laquelle la situation a été notifiée comme disponible au mandant.",
    )
    date_reservation = fields.Date(
        string="Date de réservation",
        help="Date à laquelle la situation a été réservée par le mandant.",
    )
    date_ep1 = fields.Date(
        string="Date EP1",
        help="Date de l'EP1 (Entretien Préliminaire 1).",
    )
    date_ep2 = fields.Date(
        string="Date EP2",
        help="Date de l'EP2 (Entretien Préliminaire 2).",
    )
    date_ep3 = fields.Date(
        string="Date EP3",
        help="Date de l'EP3 (Entretien Préliminaire 3).",
    )
    date_officialisation = fields.Date(
        string="Date d'officialisation",
        help="Date à laquelle la situation a été officialisé.",
    )
    date_sortie = fields.Date(string="Date de sortie", help="Date à laquelle la situation a pris fin.")
    date_annulation = fields.Date(
        string="Date d'annulation",
        help="Date à laquelle la situation a été annulée.",
    )
    date_fin = fields.Date(
        string="Date de fin",
        help="Date à laquelle la situation a pris fin.",
        compute="_compute_date_fin",
    )
    # Dates rapports
    report_ids = fields.One2many(
        comodel_name="sase.rapport",
        inverse_name="situation_id",
        string="Rapports",
        help="Rapports associés à cette situation.",
    )

    @api.model
    def create(self, vals):
        record = super(Situation, self).create(vals)
        _logger.info("Creating situation with values: %s", vals)
        if "service_id" in vals or "enfant_ids" in vals:
            record.service_id.compute_nb_places()

        # Handle report creation/update when date_officialisation changes
        if "date_officialisation" in vals:
            record._update_reports()
        return record

    def write(self, vals):
        _logger.info("Updating situation with values: %s", vals)
        res = super(Situation, self).write(vals)
        if "service_id" in vals or "enfant_ids" in vals:
            self.service_id.compute_nb_places()

        # Handle report creation/update when date_officialisation changes
        if "date_officialisation" in vals:
            self._update_reports()

        return res

    @api.depends("intervant_principal_id", "intervenant_secondaire_id")
    def _compute_intervenants(self):
        for record in self:
            record.intervenant_ids = record.intervant_principal_id | record.intervenant_secondaire_id

    @api.depends("date_officialisation")
    def _update_reports(self):
        """Helper method to update reports based on date_officialisation"""
        for record in self:
            if record.date_officialisation:
                # Clear existing reports first to avoid duplicates
                existing_reports = self.env["sase.rapport"].search(
                    [
                        ("situation_id", "=", record.id),
                        ("nom", "in", [f"Rapport {month}ème mois" for month in report_duedates]),
                    ]
                )
                if existing_reports:
                    existing_reports.unlink()

                # Create new reports
                for month in report_duedates:
                    vals = {
                        "nom": f"Rapport {month}ème mois",
                        "date_prevue": record.date_officialisation + relativedelta(months=month),
                        "situation_id": record.id,
                    }
                    _logger.info("Creating report with values: %s", vals)
                    self.env["sase.rapport"].create(vals)
            else:
                # If date_officialisation is cleared, remove all reports
                existing_reports = self.env["sase.rapport"].search(
                    [
                        ("situation_id", "=", record.id),
                        ("nom", "in", [f"Rapport {month}ème mois" for month in report_duedates]),
                    ]
                )
                if existing_reports:
                    existing_reports.unlink()

    @api.depends("date_officialisation", "date_fin", "date_notification")
    def _compute_latence(self):
        for record in self:
            if record.date_officialisation:
                d = record.date_officialisation
            elif record.date_annulation:
                d = record.date_annulation
            else:
                d = datetime.date.today()

            if record.date_notification:
                record.latence = (d - record.date_notification).days
            else:
                record.latence = 0

    @api.depends("date_annulation", "date_sortie")
    def _compute_date_fin(self):
        for record in self:
            record.date_fin = record.date_annulation if record.date_annulation else record.date_sortie

    @api.depends("date_officialisation", "date_sortie", "date_notification")
    def _compute_state(self):
        for record in self:
            record.state = "draft"
            if record.date_officialisation and record.date_officialisation <= fields.Date.context_today(self):
                record.state = "running"
            if record.date_sortie and record.date_sortie <= fields.Date.context_today(self):
                record.state = "done"
            if record.date_annulation:
                record.state = "cancelled"

            self.env["sase.service"].compute_nb_places()

    def cancel(self):
        self.ensure_one()
        self.date_annulation = fields.Date.context_today(self)

    @api.onchange("service_id")
    def change_service_id(self):
        self.service_mandant = None
        self.service_delegue = None

    @api.depends("date_officialisation", "date_fin", "date_notification")
    def _compute_nb_jours(self):
        for record in self:
            if record.date_officialisation and record.date_fin:
                record.nb_jours = (record.date_fin - record.date_officialisation).days + 1
            elif record.date_officialisation:
                record.nb_jours = (datetime.date.today() - record.date_officialisation).days + 1
            elif record.date_notification:
                record.nb_jours = (datetime.date.today() - record.date_notification).days + 1
            else:
                record.nb_jours = 0

    @api.depends("enfant_ids")
    def _compute_enfants_nb(self):
        for record in self:
            record.enfant_nb = len(record.enfant_ids)

    @api.depends("service_id", "enfant_ids", "date_fin")
    def _recompute_nb_places(self):
        for record in self:
            if record.service_id:
                record.service_id.compute_nb_places()

    @api.depends("nom", "date_officialisation", "date_fin")
    def _compute_display_name(self):
        for record in self:
            if record.date_officialisation:
                if record.date_officialisation:
                    record.display_name = f"{record.date_officialisation.strftime('%Y%m%d')} {record.nom}"
                if record.date_fin:
                    record.display_name = f"{record.date_officialisation.strftime('%Y%m%d')} - {record.date_fin.strftime('%Y%m%d')} {record.nom}"
            else:
                record.display_name = record.nom

    @api.depends("enfant_ids")
    def _compute_equivalent_situation(self):
        for record in self:
            record.equivalent_situation = math.ceil(len(record.enfant_ids) / 3) if record.enfant_ids else 0

    # @api.model
    # def _compute_report_due(self):
    #     """Check if the report is due based on the current date."""
    #     _logger.info("compute_report_due called")
    #     today = fields.Date.context_today(self)
    #     for record in self:
    #         record.is_report_due = (
    #             record.date_rapport_3_mois <= today
    #             or record.date_rapport_6_mois - relativedelta(months=1) <= today
    #             or record.date_rapport_12_mois - relativedelta(months=1) <= today
    #             or record.date_rapport_18_mois - relativedelta(months=1) <= today
    #             or record.date_rapport_24_mois - relativedelta(months=1) <= today
    #         )
