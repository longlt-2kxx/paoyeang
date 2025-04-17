from odoo import models
import logging
from odoo.osv import expression
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_domain_locations(self):
        """
        Luôn ép domain location theo user.x_allowed_location_ids và user.x_allowed_warehouse_ids
        """
        user = self.env.user

        location_ids = user.x_allowed_location_ids.ids

        # Nếu user có warehouse được gán → lấy thêm view_location_id của warehouse đó
        if user.x_allowed_warehouse_ids:
            warehouse_locations = user.x_allowed_warehouse_ids.mapped('view_location_id').filtered(
                lambda l: not l.company_id or l.company_id.id in user.company_ids.ids
            ).ids
            location_ids = list(set(location_ids + warehouse_locations))

        if location_ids:
            _logger.info("[a1_sale_location] Forced location domain: %s", location_ids)
            return self._get_domain_locations_new(
                list(location_ids),
                compute_child=self.env.context.get('compute_child', True)
            )
        else:
            # Nếu không được gán location nào → return domain trống để không hiển thị gì
            _logger.warning("[a1_sale_location] User has no allowed warehouse/location")
            return self._get_domain_locations_new([], compute_child=False)