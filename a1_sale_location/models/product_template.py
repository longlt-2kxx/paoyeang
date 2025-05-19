from email.policy import default

from odoo import api, models, fields
from odoo.addons.test_impex.models import field


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    irbm_classification_ids= fields.Many2many(
        'irbm.classification',
        string='IRBM Classification',
        help="IRBM classification for this product.",
    )

    def action_open_forecast_by_location(self):
        # Lấy action của wizard
        product_default = self.product_variant_ids[0].id if self.product_variant_ids[0].id else self.id
        action = self.env.ref('a1_sale_location.action_forecast_wizard').read()[0]
        action['context'] = dict(self.env.context or {}, default_product_id=product_default)
        return action