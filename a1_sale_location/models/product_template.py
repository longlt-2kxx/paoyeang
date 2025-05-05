from email.policy import default

from odoo import api, models, fields
from odoo.addons.test_impex.models import field


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def action_open_forecast_by_location(self):
        # Lấy action của wizard
        action = self.env.ref('a1_sale_location.action_forecast_wizard').read()[0]
        # Truyền product_id mặc định
        action['context'] = dict(self.env.context or {}, default_product_id=self.id)
        return action


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def action_open_forecast_by_location(self):
        # Lấy action của wizard
        action = self.env.ref('a1_sale_location.action_forecast_wizard').read()[0]
        # Truyền product_id mặc định
        action['context'] = dict(self.env.context or {}, default_product_id=self.id)
        return action
