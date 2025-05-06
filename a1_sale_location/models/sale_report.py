from odoo import api, models,fields
from odoo.osv import expression

class SaleReport(models.Model):
    _inherit = 'sale.report'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, lazy=True, orderby=False, **kwargs):
        user = self.env.user
        if user.has_group('a1_sale_location.group_inventory_sales_admin'):
            wh = user.property_warehouse_id
            domain = expression.AND([
                domain,
                ['|',
                 ('user_id', '=', user.id),
                 ('warehouse_id', '=', wh.id if wh else -1)
                 ]
            ])
        return super().read_group(domain, fields, groupby,
                                  offset=offset, limit=limit,
                                  lazy=lazy, orderby=orderby, **kwargs)