# file: a1_sale_location/models/stock_quant.py
from odoo import api, models, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _get_domain_locations(self, compute_child=True):
        """
        Forecast/report path: khi có context['warehouse'], trả về domain chuẩn của Odoo
        On Hand widget path: ép theo x_allowed_* của user
        """
        # 1) Forecast / Report → gọi super để lấy domain warehouse chuẩn
        if self.env.context.get('warehouse'):
            return super()._get_domain_locations()

        # 2) On Hand widget → domain do user phép
        user = self.env.user
        # 2.1. location gán thủ công
        loc_ids = user.x_allowed_location_ids.ids
        # 2.2. thêm view_location của warehouse được gán
        loc_ids += user.x_allowed_warehouse_ids.mapped('lot_stock_id.id')
        loc_ids = list(set(loc_ids))
        if not loc_ids:
            _logger.warning("User %s has no allowed locations", user.name)
            return [('location_id', 'in', [])]
        op = 'child_of' if compute_child else 'in'
        _logger.info("On Hand domain for %s = %s", user.name, loc_ids)
        return [('location_id', op, loc_ids)]

    def _search_on_hand(self, operator, value):
        """
        Chạy filter On Hand trên stock.quant dựa vào domain vừa override.
        """
        if operator not in ['=', '!='] or not isinstance(value, bool):
            raise UserError(_('Operation not supported'))

        # Dùng domain chính xác cho On Hand (compute_child=False)
        domain = self._get_domain_locations(compute_child=False)
        # Nếu domain rỗng, không hiện quant nào
        if not domain:
            return [('id', 'in', [])]

        # Lấy quant IDs phù hợp
        quant_ids = self.search(domain).ids

        # Chọn operator trả về
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('id', 'in', quant_ids)]
        else:
            return [('id', 'not in', quant_ids)]
