from odoo import models, fields


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    hobox_client_id = fields.Many2one(
        'res.partner',
        domain=[('is_hobox_client', '=', True)],
        string='HOBOX Client')
    carrier_tracking_state = fields.Selection([
        ('pending', 'Pending'),
        ('out_for_delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed Delivery'),
        ('postponed', 'Postponed'),
        ('returned_full', 'Fully Returned'),
        ('returned_partial', 'Partially Returned'),
        ('cancelled', 'Cancelled'),
    ], string='Carrier Status', default='pending')
    delivery_attempts = fields.Integer(string='Delivery Attempts', default=0)