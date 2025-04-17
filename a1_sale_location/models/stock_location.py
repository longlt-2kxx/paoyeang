from odoo import models, fields

class StockLocation(models.Model):
    _inherit = 'stock.location'

    x_assigned_user_ids = fields.Many2many(
        'res.users',
        'rel_location_user_assign',
        'location_id',
        'user_id',
        string='Assigned Users'
    )
