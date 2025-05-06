from odoo import models, fields,api

class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    x_assigned_user_ids = fields.Many2many(
        'res.users',
        'res_users_x_allowed_warehouse_rel',
        'warehouse_id', 'user_id',
        string='Assigned Users'
    )
    x_default_user_ids = fields.One2many(
        'res.users',
        'property_warehouse_id',
        string='Default for'
    )
