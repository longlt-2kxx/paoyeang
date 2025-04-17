from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.onchange('product_id', 'product_uom_qty', 'order_id.warehouse_id')
    def _onchange_check_stock(self):
        for line in self:
            if not line.product_id or not line.product_uom_qty:
                continue

            product = line.product_id
            requested_qty = line.product_uom_qty
            warehouse = line.order_id.warehouse_id

            # Tổng tồn kho toàn công ty
            total_qty = product.qty_available

            # Forecast theo warehouse đang chọn
            forecast_qty = product.with_context(warehouse=warehouse.id).virtual_available

            warnings = []

            if requested_qty > forecast_qty:
                warnings.append(_(
                    "Requested quantity (%s) exceeds forecasted stock at selected warehouse (%s). "
                    "Please consider creating a stock request to transfer from other warehouses."
                ) % (requested_qty, forecast_qty))

            if requested_qty > total_qty:
                warnings.append(_(
                    "Requested quantity (%s) exceeds total stock available in company (%s)."
                ) % (requested_qty, total_qty))

            if warnings:
                return {
                    'warning': {
                        'title': _('Stock Availability Warning'),
                        'message': '\n'.join(warnings)
                    }
                }
