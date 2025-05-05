from odoo import api, models,fields
from odoo.osv import expression

class SaleReport(models.Model):
    _inherit = 'sale.report'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, lazy=True, orderby=False, **kwargs):
        user = self.env.user
        # chỉ áp cho nhóm Sales Rep của bạn
        if user.has_group('a1_sale_location.group_inventory_sales_admin'):
            wh = user.property_warehouse_id
            # ghép thêm điều kiện: user_id=uid OR warehouse_id=default_wh
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