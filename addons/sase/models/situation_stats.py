from logging import getLogger

from odoo import api
from odoo import fields
from odoo import models

_logger = getLogger(__name__)


class SituationStats(models.TransientModel):
    _name = "sase.situation.stats"
    _description = "Situation Statistics"

    date = fields.Date(
        string="Date",
        required=True,
        default=fields.Date.context_today,
    )
    service_id = fields.Many2one(
        comodel_name="sase.service",
        string="Service",
        required=True,
        help="Service associated with this situation.",
    )
    pc_allouees = fields.Integer(
        string="Number to Reach",
        required=True,
    )
    pc_assignees = fields.Integer(
        string="In Progress",
        required=True,
    )
    pc_reservees = fields.Integer(
        string="Reserved",
        required=True,
    )

    @api.model
    def cron_historisation(self):
        """Cron job for historisation."""
        _logger.info("Running cron job for historisation.")
        # Implement your historisation logic here
        for service in self.env["sase.service"].search([]):
            _logger.info("Historising service: %s", service.nom)
            self.env["sase.situation.stats"].create(
                {
                    "service_id": service.id,
                    "pc_allouees": service.nb_places_allouees,
                    "pc_assignees": service.nb_places_occupees,
                    "pc_reservees": service.nb_places_reservees,
                }
            )
