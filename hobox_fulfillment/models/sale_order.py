from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    hobox_client_id = fields.Many2one(
        'res.partner',
        domain=[('is_hobox_client', '=', True)],
        string='HOBOX Client')
    source_platform_id = fields.Many2one(
        'hobox.platform.integration', string='Source Platform')
    source_order_ref = fields.Char(string='Platform Order Ref')
    is_cod = fields.Boolean(string='Cash on Delivery')
    cod_amount = fields.Float(string='COD Amount')
    delivery_zone = fields.Char(string='Delivery Zone')
    hobox_state = fields.Selection([
        ('received', 'Received'),
        ('processing', 'Processing'),
        ('ready', 'Ready for Shipment'),
        ('shipped', 'Shipped'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string='Fulfillment Status', default='received')