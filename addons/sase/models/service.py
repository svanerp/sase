import logging

from odoo import api
from odoo import fields
from odoo import models

_logger = logging.getLogger(__name__)


class Service(models.Model):
    _name = "sase.service"
    _description = "Service Mandant"
    _rec_name = "nom"

    nom = fields.Char(string="Nom du service", required=True)
    employe_ids = fields.One2many(
        comodel_name="sase.service_employe",
        inverse_name="service_id",
        string="Personne de référence",
        help="Personnes associés à ce service mandant.",
    )
    nb_places_allouees = fields.Integer(
        string="Nombre de PC allouées",
        help="Nombre de PC allouées pour ce service.",
    )
    nb_places_occupees = fields.Integer(
        string="Nombre de PC occupées",
        compute="compute_nb_places",
        store=True,
        help="Nombre de PC actuellement occupées dans ce service.",
    )
    nb_places_reservees = fields.Integer(
        string="Nombre de PC réservées",
        compute="_compute_nb_places",
        store=True,
        help="Nombre de PC réservées pour ce service.",
    )
    delta_nb_places = fields.Integer(
        string="Delta nombre de PC",
        help="Delta entre le nombre de PC allouées et le nombre de PC occupées.",
    )
    situation_ids = fields.One2many(
        comodel_name="sase.situation",
        inverse_name="service_id",
        string="Situations",
        help="Situations associées à ce service.",
    )

    # def _compute_delta_nb_places(self):
    #     """Compute the delta number of places for each service."""
    #     _logger.info("Computing delta number of places for each service.")
    #     for service in self:
    #         service.delta_nb_places = service.nb_places_allouees - (
    #             service.nb_places_occupees + service.nb_places_reservees
    #         )

    @api.model
    def compute_nb_places(self):
        """Compute the number of occupied places for each service."""
        _logger.info("Computing number of occupied places for each service.")
        Service = self.env["sase.service"]
        Situation = self.env["sase.situation"]
        for service in Service.search([]):
            running = Situation.search_read(
                [
                    ("service_id", "=", service.id),
                    ("state", "in", ["running"]),
                ],
                ["equivalent_situation"],
            )
            service.nb_places_occupees = sum([record.get("equivalent_situation", 0) for record in running])
            reserved = Situation.search_read(
                [
                    ("service_id", "=", service.id),
                    ("state", "in", ["draft"]),
                ],
                ["equivalent_situation"],
            )
            _logger.info(
                "Service %s has %d places reserved.",
                service.nom,
                len(reserved),
            )

            total_reserved = 0
            for r in reserved:
                _logger.info("Reserved situation: %s", r)
                _logger.info("Reserved situation: %s", r.get("equivalent_situation", 1))
            for record in reserved:
                if record.get("equivalent_situation", 1) < 1:
                    total_reserved += 1
                else:
                    total_reserved += record.get("equivalent_situation")
            service.nb_places_reservees = total_reserved
            service.delta_nb_places = service.nb_places_allouees - (
                service.nb_places_occupees + service.nb_places_reservees
            )
