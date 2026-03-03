from odoo import models, fields


class HoboxPlatformIntegration(models.Model):
    _name = 'hobox.platform.integration'
    _description = 'HOBOX Platform Integration'
    _rec_name = 'name'

    name = fields.Char(string='Store Name', required=True)
    partner_id = fields.Many2one(
        'res.partner',
        domain=[('is_hobox_client', '=', True)],
        string='Client', required=True)
    platform_type = fields.Selection([
        ('shopify', 'Shopify'),
        ('woocommerce', 'WooCommerce'),
        ('salla', 'Salla'),
        ('zid', 'Zid'),
        ('tiktok_shop', 'TikTok Shop'),
        ('noon', 'Noon'),
        ('amazon', 'Amazon'),
        ('magento', 'Magento'),
        ('excel_manual', 'Manual (Excel)'),
        ('other', 'Other'),
    ], string='Platform', required=True)
    api_url = fields.Char(string='API URL')
    api_key = fields.Char(string='API Key', password=True)
    api_secret = fields.Char(string='API Secret', password=True)
    webhook_url = fields.Char(string='Webhook URL', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('connected', 'Connected'),
        ('error', 'Error'),
        ('disconnected', 'Disconnected'),
    ], string='Status', default='draft')
    last_sync = fields.Datetime(string='Last Sync', readonly=True)
    last_sync_status = fields.Text(string='Last Sync Status', readonly=True)
    auto_import = fields.Boolean(string='Auto Import Orders', default=True)
    test_mode = fields.Boolean(string='Test Mode')
    notes = fields.Text(string='Notes')