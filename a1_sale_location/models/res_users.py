from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    x_allowed_warehouse_ids = fields.Many2many(
        'stock.warehouse',
        string='Allowed Warehouses'
    )

    x_allowed_location_ids = fields.Many2many(
        'stock.location',
        'rel_location_user_assign',
        'user_id',
        'location_id',
        string='Allowed Locations'
    )
