import logging

from odoo import api
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class Service(models.Model):
    _name = "sase.service"
    _description = "Service"
    _rec_name = "nom"

    nom = fields.Char(string="Nom", required=True)
    employe_ids = fields.One2many(
        comodel_name="sase.service_employe",
        inverse_name="service_id",
        string="Employés",
        help="Employés associés à ce service.",
    )
    nb_places_reservees = fields.Integer(
        string="Nombre de places réservées",
        help="Nombre de places réservées pour ce service.",
    )
    nb_places_occupees = fields.Integer(
        string="Nombre de places occupées",
        compute="compute_nb_places_occupees",
        store=True,
        help="Nombre de places actuellement occupées dans ce service.",
    )

    @api.model
    def compute_nb_places_occupees(self):
        Service = self.env["sase.service"]
        Situation = self.env["sase.situation"]
        for service in Service.search([]):
            total = Situation.search_read(
                [
                    ("service_id", "=", service.id),
                    ("state", "in", ["running"]),
                ],
                ["equivalent_situation"],
            )
            _logger.info(
                "Calculating occupied places for service %s: %d",
                service.nom,
                total,
            )
            # service.nb_places_occupees = sum(total)
