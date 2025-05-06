from odoo import models, fields, api

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

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False):
        user = self.env.user
        # chỉ áp cho Sales Admin
        if user.has_group('a1_sale_location.group_inventory_sales_admin'):
            domain = ['|',
                      ('user_id', '=', user.id),
                      ('warehouse_id', '=', user.property_warehouse_id.id)
                      ]
            args = domain + args
        return super(SaleOrder, self)._search(args, offset=offset, limit=limit, order=order, count=count)