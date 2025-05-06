from odoo import models, api
from odoo.exceptions import UserError

class ReportProductProductReplenishment(models.AbstractModel):
    _inherit = 'report.stock.report_product_product_replenishment'
    _description = "Stock Replenishment Report Customization"

    @api.model
    def get_filter_state(self):
        # Lấy danh sách warehouse mà user được phép truy cập
        allowed_ids = self.env.user.x_allowed_warehouse_ids.ids
        warehouses = self.env['stock.warehouse'].search_read(
            [('id', 'in', allowed_ids)],
            fields=['id', 'name', 'code']
        )
        if not warehouses:
            raise UserError(
                "You are not assigned to any warehouse.\n"
                "Please go to your User Settings to select a default warehouse,\n"
                "or contact your manager to be assigned to at least one warehouse before viewing this report."
            )
        active_warehouse_id = self.env.context.get('warehouse', False)
        active_id = False
        if active_warehouse_id:
            if any(w['id'] == active_warehouse_id for w in warehouses):
                active_id = active_warehouse_id
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
        if not active_id and self.env.user.property_warehouse_id:
            active_id = self.env.user.property_warehouse_id.id
        elif not active_id and warehouses:
            active_id = warehouses[0]['id']

        return {
            'warehouses': warehouses,
            'active_warehouse': active_id,  # Trả về ID (số)
        }

    def _get_report_data(self, product_template_ids=False, product_variant_ids=False):
        assert product_template_ids or product_variant_ids
        res = {}
        if not self.env.context.get('warehouse') and self.env.user.x_allowed_warehouse_ids:
            self = self.with_context(warehouse=self.env.user.x_allowed_warehouse_ids[0].id)
        allowed_warehouses = self.env.user.x_allowed_warehouse_ids
        allowed_ids = allowed_warehouses.ids

        warehouse = None
        context_warehouse_id = self.env.context.get('warehouse')

        if context_warehouse_id and context_warehouse_id in allowed_ids:
            warehouse = self.env['stock.warehouse'].browse(context_warehouse_id)
        elif allowed_ids:
            warehouse = allowed_warehouses[0]
        else:
            raise UserError(
                "You are not assigned to any warehouse.\n"
                "Please go to your user preferences and assign at least one warehouse before viewing this report."
            )
        if not context_warehouse_id or context_warehouse_id != warehouse.id:
            self = self.with_context(warehouse=warehouse.id)
        wh_location_ids = [loc['id'] for loc in self.env['stock.location'].search_read(
            [('id', 'child_of', warehouse.view_location_id.id)],
            ['id'],
        )]
        res['active_warehouse'] = warehouse.display_name
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
        res.update(self._compute_draft_quantity_count(product_template_ids, product_variant_ids, wh_location_ids))
        res['lines'] = self._get_report_lines(product_template_ids, product_variant_ids, wh_location_ids)

        return res
