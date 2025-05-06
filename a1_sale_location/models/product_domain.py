# file: a1_sale_location/models/stock_quant.py
from odoo import api, models, _
from odoo.exceptions import UserError


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def _get_child_ids_of_locations(self, locations):
        """Trả về tất cả ID của location + location con"""
        return self.env['stock.location'].search([('id', 'child_of', locations.ids)]).ids

    def _get_domain_locations(self, compute_child=True):
        """
        Forecast/report path: khi có context['warehouse'], trả về domain chuẩn của Odoo
        On Hand widget path: ép theo x_allowed_* của user
        """
        if self.env.context.get('warehouse'):
            return super()._get_domain_locations()

        user = self.env.user

        # 2.1. location gán thủ công
        allowed_location_ids = user.x_allowed_location_ids
        loc_ids = self._get_child_ids_of_locations(allowed_location_ids)

        # 2.2. thêm view_location của warehouse được gán
        warehouse_stock_ids = user.x_allowed_warehouse_ids.mapped('lot_stock_id.id')
        loc_ids += warehouse_stock_ids

        # Loại trùng
        loc_ids = list(set(loc_ids))

        if not loc_ids:
            return [('location_id', 'in', [])]
        op = 'child_of' if compute_child else 'in'
        return [('location_id', op, loc_ids)]

    def _search_on_hand(self, operator, value):
        """
        Chạy filter On Hand trên stock.quant dựa vào domain vừa override.
        """
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise UserError(_('Operation not supported'))
        domain = self._get_domain_locations(compute_child=False)
        if not domain:
            return [('id', 'in', [])]

        quant_ids = self.search(domain).ids
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('id', 'in', quant_ids)]
        else:
            return [('id', 'not in', quant_ids)]
