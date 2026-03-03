from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_hobox_sku = fields.Boolean(string='HOBOX SKU')
    sku_code = fields.Char(string='SKU Code')
    hobox_client_id = fields.Many2one(
        'res.partner',
        domain=[('is_hobox_client', '=', True)],
        string='Client')
    storage_type = fields.Selection([
        ('unit', 'Unit'),
        ('shelf', 'Shelf'),
        ('pallet', 'Pallet'),
    ], string='Storage Type', default='unit')
    storage_location_id = fields.Many2one('stock.location', string='Storage Location')
    low_stock_threshold = fields.Integer(string='Low Stock Alert Qty', default=10)
    hobox_notes = fields.Text(string='Notes')