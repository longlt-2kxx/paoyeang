from odoo import models, fields,api

class StockRequest(models.Model):
    _name = 'x.stock.request'
    _description = 'Stock Request to Fulfill Shortage'

    name = fields.Char(string='Request Reference', required=True, default=lambda self:('New'))
    requester_id = fields.Many2one('res.users', string='Requested By', default=lambda self: self.env.user)
    order_id = fields.Many2one('sale.order', string='Related SO')
    order_line_id = fields.Many2one('sale.order.line', string='Related SO Line')

    product_id = fields.Many2one('product.product', string='Product', required=True)
    requested_qty = fields.Float(string='Requested Quantity')
    available_qty = fields.Float(string='Available in Assigned Warehouses')
    shortage_qty = fields.Float(string='Shortage', compute='_compute_shortage', store=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='draft')

    @api.depends('requested_qty', 'available_qty')
    def _compute_shortage(self):
        for rec in self:
            rec.shortage_qty = rec.requested_qty - rec.available_qty
