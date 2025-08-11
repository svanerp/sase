from odoo import api
from odoo import fields
from odoo import models


class SituationStats(models.TransientModel):
    _name = "sase.situation.stats"
    _description = "Situation Statistics"

    service_id = fields.Many2one(
        comodel_name="sase.service",
        string="Service",
        required=True,
        help="Service associated with this situation.",
    )
    pc_a_atteindre = fields.Integer(
        string="Number to Reach",
        default=21,
    )
