from odoo import models, fields


class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    hobox_active = fields.Boolean(string='Active in HOBOX', default=True)
    delivery_success_rate = fields.Float(string='Success Rate (%)')
    avg_delivery_days = fields.Integer(string='Avg Delivery Days')
    coverage_zones = fields.Text(string='Coverage Zones')