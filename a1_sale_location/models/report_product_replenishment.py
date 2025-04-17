from odoo import models, api
import logging

_logger = logging.getLogger(__name__)

class ReportProductProductReplenishment(models.AbstractModel):
    _inherit = 'report.stock.report_product_product_replenishment'
    _description = "Stock Replenishment Report Customization"

    print('stock.report_product_product_replenishment')

    @api.model
    def get_filter_state(self):
        # Lấy danh sách warehouse mà user được phép truy cập
        allowed_ids = self.env.user.x_allowed_warehouse_ids.ids

        # Lấy danh sách warehouses từ allowed_ids, chỉ lấy các trường id, name, code
        warehouses = self.env['stock.warehouse'].search_read(
            [('id', 'in', allowed_ids)],
            fields=['id', 'name', 'code']
        )

        # Lấy active warehouse từ context (đang được truyền dưới dạng ID nếu có)
        active_warehouse_id = self.env.context.get('warehouse', False)
        active_id = False
        if active_warehouse_id:
            # Nếu ID được truyền từ context thuộc trong danh sách warehouses, giữ lại nó
            if any(w['id'] == active_warehouse_id for w in warehouses):
                active_id = active_warehouse_id

        # Nếu active_id vẫn chưa có, tìm theo allowed_company_ids (nếu có)
        if not active_id:
            allowed_company_ids = self.env.context.get('allowed_company_ids', [])
            if allowed_company_ids:
                company_id = allowed_company_ids[0]
                warehouse_rec = self.env['stock.warehouse'].search([
                    ('company_id', '=', company_id),
                    ('id', 'in', allowed_ids)
                ], limit=1)
                if warehouse_rec:
                    active_id = warehouse_rec.id
        # Nếu vẫn không có active_id nhưng danh sách warehouses không rỗng, lấy phần tử đầu tiên
        if not active_id and warehouses:
            active_id = warehouses[0]['id']

        return {
            'warehouses': warehouses,
            'active_warehouse': active_id,  # Trả về ID (số)
        }

    def _get_report_data(self, product_template_ids=False, product_variant_ids=False):
        assert product_template_ids or product_variant_ids
        res = {}

        # 🔐 Lấy danh sách warehouse được phép truy cập
        allowed_warehouses = self.env.user.x_allowed_warehouse_ids
        allowed_ids = allowed_warehouses.ids

        warehouse = None
        context_warehouse_id = self.env.context.get('warehouse')

        if context_warehouse_id and context_warehouse_id in allowed_ids:
            warehouse = self.env['stock.warehouse'].browse(context_warehouse_id)
        elif allowed_ids:
            warehouse = allowed_warehouses[0]  # Chọn warehouse đầu tiên user được gán
        else:
            raise ValueError("You are not assigned to any warehouse and cannot view the forecast report.")

        # ⚠️ Cập nhật context nếu chưa có hoặc không hợp lệ
        if not context_warehouse_id or context_warehouse_id != warehouse.id:
            self = self.with_context(warehouse=warehouse.id)

        _logger.info("[a1_sale_location] Using warehouse: %s (ID: %s)", warehouse.name, warehouse.id)

        # ✅ Get the warehouse's internal locations (and children)
        wh_location_ids = [loc['id'] for loc in self.env['stock.location'].search_read(
            [('id', 'child_of', warehouse.view_location_id.id)],
            ['id'],
        )]
        res['active_warehouse'] = warehouse.display_name

        # ✅ Handle product template or product variant
        if product_template_ids:
            product_templates = self.env['product.template'].browse(product_template_ids)
            res['product_templates'] = product_templates
            res['product_variants'] = product_templates.product_variant_ids
            res['multiple_product'] = len(product_templates.product_variant_ids) > 1
            res['uom'] = product_templates[:1].uom_id.display_name
            res['quantity_on_hand'] = sum(product_templates.mapped('qty_available'))
            res['virtual_available'] = sum(product_templates.mapped('virtual_available'))
        elif product_variant_ids:
            product_variants = self.env['product.product'].browse(product_variant_ids)
            res['product_templates'] = False
            res['product_variants'] = product_variants
            res['multiple_product'] = len(product_variants) > 1
            res['uom'] = product_variants[:1].uom_id.display_name
            res['quantity_on_hand'] = sum(product_variants.mapped('qty_available'))
            res['virtual_available'] = sum(product_variants.mapped('virtual_available'))

        # ✅ Tính số lượng nháp & các dòng chi tiết
        res.update(self._compute_draft_quantity_count(product_template_ids, product_variant_ids, wh_location_ids))
        res['lines'] = self._get_report_lines(product_template_ids, product_variant_ids, wh_location_ids)

        return res