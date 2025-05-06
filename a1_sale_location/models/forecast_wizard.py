# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import timedelta

class ForecastLine(models.TransientModel):
    _name = 'forecast.by.location.line'
    _description = 'Forecast by Location Line'

    wizard_id = fields.Many2one('forecast.by.location.wizard', ondelete='cascade')
    location_id = fields.Many2one('stock.location', string='Location', readonly=True)
    onhand = fields.Float(string='On Hand', readonly=True)
    reserved = fields.Float(string='Reserved', readonly=True)
    incoming = fields.Float(string='Incoming', readonly=True)
    forecast_qty = fields.Float(
        string='Forecast Qty',
        compute='_compute_forecast_qty',
        readonly=True, store=True,
    )

    @api.depends('onhand', 'reserved','incoming')
    def _compute_forecast_qty(self):
        for line in self:
            line.forecast_qty = line.onhand - line.reserved + line.incoming


class ForecastMove(models.TransientModel):
    _name = 'forecast.by.location.move'
    _description = 'Forecast Move Details'

    wizard_id = fields.Many2one('forecast.by.location.wizard', ondelete='cascade')
    location_id = fields.Many2one('stock.location', readonly=True)
    move_id = fields.Many2one('stock.move', readonly=True)
    move_type = fields.Selection([
        ('reserved', 'Reserved'),
        ('incoming', 'Incoming'),
        ('outgoing', 'Outgoing'),
    ], readonly=True)
    qty = fields.Float(readonly=True)
    date = fields.Datetime(string='Expected Date', readonly=True)
    document_ref = fields.Char(string='Document', readonly=True)


class ForecastWizard(models.TransientModel):
    _name = 'forecast.by.location.wizard'
    _description = 'Wizard to compute Forecast by Location'

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        required=True,
        default=lambda self: self.env.context.get('default_product_id')
    )
    location_ids = fields.Many2many(
        'stock.location', string='Locations',
        default=lambda self: [(6, 0, self.env.user.x_allowed_location_ids.ids)],
    )
    allowed_location_ids = fields.Many2many(
        'stock.location', string='Allowed Locations',
        compute='_compute_allowed_locations',
    )
    line_ids = fields.One2many('forecast.by.location.line', 'wizard_id', string='Forecast Lines')
    move_ids = fields.One2many('forecast.by.location.move', 'wizard_id', string='Move Details')

    # KPI summary
    onhand_total = fields.Float(string='Total On Hand', readonly=True, compute='_compute_summary')
    reserved_total = fields.Float(string='Total Reserved', readonly=True, compute='_compute_summary')
    forecast_total = fields.Float(string='Total Forecast', readonly=True, compute='_compute_summary')

    @api.depends()
    def _compute_allowed_locations(self):
        for wiz in self:
            wiz.allowed_location_ids = wiz.env.user.x_allowed_location_ids

    @api.depends('line_ids.onhand', 'line_ids.reserved', 'line_ids.forecast_qty')
    def _compute_summary(self):
        for wiz in self:
            onh = resv = frc = 0.0
            for ln in wiz.line_ids:
                onh += ln.onhand
                resv += ln.reserved
                frc += ln.forecast_qty
            wiz.onhand_total = onh
            wiz.reserved_total = resv
            wiz.forecast_total = frc

    def action_compute(self):
        self.ensure_one()
        # clear old
        self.line_ids.unlink()
        self.move_ids.unlink()
        # 1) fetch quant groups
        quant_data = self.env['stock.quant'].read_group(
            [('product_id', '=', self.product_id.id),
             ('location_id', 'in', self.location_ids.ids)],
            ['quantity', 'reserved_quantity', 'location_id'],
            ['location_id'], lazy=False)
        # create lines
        location_map = {}
        for r in quant_data:
            loc = r['location_id'][0]
            line = self.env['forecast.by.location.line'].create({
                'wizard_id': self.id,
                'location_id': loc,
                'onhand': r.get('quantity', 0.0),
                'reserved': r.get('reserved_quantity', 0.0),
            })
            location_map[loc] = line
        incoming_moves = self.env['stock.move'].search([
            ('product_id', '=', self.product_id.id),
            ('state', 'in', ['confirmed', 'assigned']),
            ('location_dest_id', 'in', self.location_ids.ids),
            ('location_dest_id.usage', '=', 'internal'),
        ])
        for mv in incoming_moves:
            # Ghi vào tab chi tiết
            self.env['forecast.by.location.move'].create({
                'wizard_id': self.id,
                'location_id': mv.location_dest_id.id,
                'move_id': mv.id,
                'move_type': 'incoming',
                'qty': mv.product_uom_qty,
                'date': mv.date,
                'document_ref': mv.origin or '',
            })
            # Gộp vào dòng forecast nếu đã có
            line = location_map.get(mv.location_dest_id.id)
            if line:
                line.incoming += mv.product_uom_qty  # Cộng thêm incoming
            else:
                line = self.env['forecast.by.location.line'].create({
                    'wizard_id': self.id,
                    'location_id': mv.location_dest_id.id,
                    'onhand': 0.0,
                    'reserved': 0.0,
                    'incoming': mv.product_uom_qty,
                })
                location_map[mv.location_dest_id.id] = line
        outgoing_moves = self.env['stock.move'].search([
            ('product_id', '=', self.product_id.id),
            ('state', 'in', ['confirmed', 'assigned']),
            ('location_id', 'in', self.location_ids.ids),
        ])
        for mv in outgoing_moves:
            # Loại move reserved (có reserved_availability) → hiển thị riêng
            move_type = 'reserved' if mv.reserved_availability else 'outgoing'
            self.env['forecast.by.location.move'].create({
                'wizard_id': self.id,
                'location_id': mv.location_id.id,
                'move_id': mv.id,
                'move_type': move_type,
                'qty': mv.product_uom_qty,
                'date': mv.date,
                'document_ref': mv.origin or '',
            })
        # return view (computed fields auto‐refresh)
        return {
            'name': 'Forecast by Location',
            'type': 'ir.actions.act_window',
            'res_model': 'forecast.by.location.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }
