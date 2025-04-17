from odoo import models, fields, api
import logging

from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Warehouse',
        default=lambda self: self.env.user.property_warehouse_id.id
    )

    @api.onchange('user_id')
    def _onchange_user_id_set_wh_domain(self):
        for order in self:
            user = order.user_id or self.env.user
            return {
                'domain': {
                    'warehouse_id': [('id', 'in', user.x_allowed_warehouse_ids.ids)]
                }
            }