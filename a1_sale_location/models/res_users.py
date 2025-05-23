from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import threading

class ResUsers(models.Model):
    _inherit = 'res.users'

    x_allowed_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Allowed Warehouses'
    )

    x_allowed_location_ids = fields.Many2many(
        'stock.location',
        'rel_location_user_assign',
        'user_id',
        'location_id',
        string='Allowed Locations'
    )
    @api.onchange('x_allowed_warehouse_ids', 'x_allowed_location_ids')
    def _trigger_tz_swap_same_gmt(self):
        if self.tz in ['Asia/Kuala_Lumpur', 'Asia/Singapore']:
            self.tz = 'Asia/Singapore' if self.tz == 'Asia/Kuala_Lumpur' else 'Asia/Kuala_Lumpur'
        else:
            # fallback mặc định
            self.tz = 'Asia/Kuala_Lumpur'

    @api.constrains('property_warehouse_id', 'x_allowed_warehouse_ids')
    def _check_default_warehouse_valid(self):
        for user in self:
            if user.property_warehouse_id and user.property_warehouse_id not in user.x_allowed_warehouse_ids:
                raise ValidationError(_(
                    "Your default warehouse must be one of the allowed warehouses."
                ))







